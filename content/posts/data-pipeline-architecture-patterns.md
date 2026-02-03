---
title: "Data Pipeline Architecture: From Batch to Streaming"
slug: data-pipeline-architecture-patterns
date: 2026-02-01
description: "A practical guide to data pipeline architecture patterns. Compare batch, micro-batch, and streaming approaches. Learn when to use each pattern and how to design for reliability."
category: data-engineering
tags: architecture, data-pipelines, etl, streaming, batch
draft: false
---

## The Architecture Decision That Defines Your Platform

Every data platform makes a fundamental choice early on: how does data flow from source to destination? This choice ripples through every subsequent decision—tooling, staffing, cost structure, capability limitations.

Get it right, and your platform scales gracefully. Get it wrong, and you'll spend years working around architectural constraints.

This article walks through the major pipeline architecture patterns, when to use each, and how to evolve from one to another as requirements change.

## Pattern 1: Batch Processing

Batch processing is the oldest and most common pattern. Data accumulates over a period, then gets processed in bulk.

### How It Works

```
[Source Systems] --> [Staging Area] --> [Batch Job] --> [Data Warehouse]
                          ↑                  |
                          |                  | (scheduled)
                          +------------------+
                              Next day
```

1. Data accumulates in source systems throughout the day
2. At a scheduled time (often overnight), a batch job extracts all new/changed data
3. The job transforms and loads data into the warehouse
4. Users see updated data the next morning

### Implementation Example

```python
"""
Batch pipeline for daily order processing.
Runs nightly to process previous day's orders.
"""

from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

def extract_daily_orders(source_engine, process_date: datetime) -> pd.DataFrame:
    """Extract orders for a specific date from source system."""
    
    query = """
    SELECT 
        order_id,
        customer_id,
        order_date,
        total_amount,
        status,
        created_at,
        updated_at
    FROM orders
    WHERE DATE(order_date) = %(process_date)s
    """
    
    return pd.read_sql(
        query, 
        source_engine, 
        params={'process_date': process_date.date()}
    )


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Apply business transformations to order data."""
    
    transformed = df.copy()
    
    # Calculate derived metrics
    transformed['is_high_value'] = transformed['total_amount'] > 1000
    transformed['order_month'] = pd.to_datetime(transformed['order_date']).dt.to_period('M')
    
    # Standardize status values
    status_mapping = {
        'complete': 'completed',
        'done': 'completed',
        'cancelled': 'canceled',
        'cancel': 'canceled'
    }
    transformed['status'] = transformed['status'].str.lower().replace(status_mapping)
    
    # Add processing metadata
    transformed['etl_loaded_at'] = datetime.now()
    
    return transformed


def load_to_warehouse(df: pd.DataFrame, warehouse_engine, target_table: str):
    """Load transformed data to warehouse, replacing existing date partition."""
    
    # Delete existing data for this date (idempotent reload)
    process_date = df['order_date'].iloc[0]
    
    with warehouse_engine.begin() as conn:
        conn.execute(
            f"DELETE FROM {target_table} WHERE DATE(order_date) = %(d)s",
            {'d': process_date}
        )
    
    # Insert new data
    df.to_sql(
        target_table,
        warehouse_engine,
        if_exists='append',
        index=False
    )


def run_daily_batch(process_date: datetime = None):
    """
    Run daily batch pipeline.
    
    Args:
        process_date: Date to process. Defaults to yesterday.
    """
    if process_date is None:
        process_date = datetime.now() - timedelta(days=1)
    
    source_engine = create_engine(SOURCE_CONNECTION)
    warehouse_engine = create_engine(WAREHOUSE_CONNECTION)
    
    # Extract
    print(f"Extracting orders for {process_date.date()}")
    orders = extract_daily_orders(source_engine, process_date)
    print(f"Extracted {len(orders)} orders")
    
    if len(orders) == 0:
        print("No orders to process")
        return
    
    # Transform
    print("Applying transformations")
    transformed = transform_orders(orders)
    
    # Load
    print("Loading to warehouse")
    load_to_warehouse(transformed, warehouse_engine, 'fact_orders')
    
    print(f"Pipeline complete: {len(transformed)} orders loaded")


if __name__ == "__main__":
    run_daily_batch()
```

### When to Use Batch

**Good fit when:**
- Data freshness of hours/daily is acceptable
- Volume is high but not continuous
- Processing requires full dataset context (e.g., calculating daily ranks)
- Cost optimization matters more than latency
- Team is small and simplicity is priority

**Poor fit when:**
- Business needs real-time or near-real-time data
- Data arrives continuously and must be processed immediately
- Late-arriving data causes reconciliation nightmares
- Processing windows are shrinking (batch can't complete in time)

### Batch Advantages and Disadvantages

| Advantages | Disadvantages |
|------------|---------------|
| Simple to understand and debug | Data is always stale |
| Efficient for large volumes | Long recovery time after failures |
| Cost-effective (runs during off-peak) | All-or-nothing processing |
| Easy to implement idempotency | Doesn't handle late data well |
| Mature tooling | Difficult to scale down latency |

## Pattern 2: Micro-Batch Processing

Micro-batch is batch processing with shorter intervals—minutes instead of hours or days.

### How It Works

```
[Source] --> [Queue/Buffer] --> [Micro-batch] --> [Warehouse]
                                    |
                                    | (every 5-15 min)
                                    v
                              [Process batch]
```

Instead of processing once daily, process every 5, 10, or 15 minutes. You get fresher data while keeping batch semantics.

### Implementation with Airflow

```python
"""
Micro-batch pipeline using Airflow.
Processes orders every 15 minutes.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'orders_micro_batch',
    default_args=default_args,
    description='Process orders every 15 minutes',
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,  # Prevent overlapping runs
)


def extract_incremental(**context):
    """Extract orders since last successful run."""
    
    execution_date = context['execution_date']
    prev_execution = context['prev_execution_date_success'] or execution_date - timedelta(hours=1)
    
    # Extract orders modified since last run
    query = """
    SELECT *
    FROM orders
    WHERE updated_at >= %(start)s
      AND updated_at < %(end)s
    """
    
    orders = pd.read_sql(query, SOURCE_ENGINE, params={
        'start': prev_execution,
        'end': execution_date
    })
    
    # Store for next task
    context['ti'].xcom_push(key='order_count', value=len(orders))
    
    # Save to staging
    orders.to_parquet(f'/tmp/orders_{execution_date.isoformat()}.parquet')


def transform(**context):
    """Transform staged orders."""
    
    execution_date = context['execution_date']
    
    orders = pd.read_parquet(f'/tmp/orders_{execution_date.isoformat()}.parquet')
    
    # Apply transformations (same as batch)
    transformed = transform_orders(orders)
    
    transformed.to_parquet(f'/tmp/orders_transformed_{execution_date.isoformat()}.parquet')


def load(**context):
    """Load to warehouse with upsert logic."""
    
    execution_date = context['execution_date']
    
    transformed = pd.read_parquet(
        f'/tmp/orders_transformed_{execution_date.isoformat()}.parquet'
    )
    
    # Upsert: update existing, insert new
    upsert_to_warehouse(transformed, 'fact_orders', key_columns=['order_id'])


# Define task dependencies
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_incremental,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag,
)

extract_task >> transform_task >> load_task
```

### When to Use Micro-Batch

**Good fit when:**
- Need fresher data than daily batch provides
- Can't justify streaming infrastructure complexity
- Data naturally arrives in bursts
- Team familiar with batch patterns
- Latency of 5-15 minutes is acceptable

**Poor fit when:**
- Need sub-minute latency
- Data arrives as continuous stream
- Events must trigger immediate actions

## Pattern 3: Stream Processing

Stream processing handles data as it arrives, record by record or in small windows.

### How It Works

```
[Source] --> [Message Queue] --> [Stream Processor] --> [Real-time Store]
   |              |                     |                      |
   |              |                     |                      v
   |              |                     |                [Dashboard]
   |              |                     v
   |              |              [Process each event]
   |              v
   |         [Kafka/Kinesis]
   v
[Event generated]
```

### Conceptual Implementation

```python
"""
Stream processing conceptual example.
Processes order events as they arrive.

Note: Production would use Kafka/Flink/Spark Streaming.
This illustrates the pattern.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Generator
import json


@dataclass
class OrderEvent:
    """Represents an order event from the stream."""
    event_id: str
    order_id: str
    customer_id: str
    amount: float
    status: str
    timestamp: datetime


class StreamProcessor:
    """
    Simple stream processor demonstrating the pattern.
    
    In production, this would be Kafka Streams, Flink, or Spark Streaming.
    """
    
    def __init__(self):
        self.handlers: list[Callable] = []
        self.state: dict = {}  # Would be state store in production
    
    def register_handler(self, handler: Callable):
        """Register a handler for processing events."""
        self.handlers.append(handler)
    
    def process(self, event_stream: Generator[OrderEvent, None, None]):
        """Process events from stream."""
        
        for event in event_stream:
            for handler in self.handlers:
                try:
                    handler(event, self.state)
                except Exception as e:
                    # In production: dead letter queue, retry logic
                    print(f"Error processing {event.event_id}: {e}")


# --- Event Handlers ---

def calculate_customer_total(event: OrderEvent, state: dict):
    """
    Maintain running total per customer.
    
    This demonstrates stateful stream processing.
    """
    customer_key = f"customer_total:{event.customer_id}"
    
    current_total = state.get(customer_key, 0)
    new_total = current_total + event.amount
    state[customer_key] = new_total
    
    # Would emit to downstream or update real-time store
    print(f"Customer {event.customer_id} total: {new_total}")


def detect_high_value_order(event: OrderEvent, state: dict):
    """
    Detect and alert on high-value orders.
    
    This demonstrates event-driven alerting.
    """
    if event.amount > 10000:
        alert = {
            'type': 'high_value_order',
            'order_id': event.order_id,
            'amount': event.amount,
            'customer_id': event.customer_id,
            'timestamp': event.timestamp.isoformat()
        }
        # Would send to alerting system
        print(f"ALERT: High value order detected: {alert}")


def track_order_velocity(event: OrderEvent, state: dict):
    """
    Track order velocity in sliding window.
    
    This demonstrates windowed aggregation.
    """
    window_key = "order_velocity"
    window_duration = 300  # 5 minutes in seconds
    
    # Get current window
    current_window = state.get(window_key, [])
    
    # Add new event
    current_window.append({
        'timestamp': event.timestamp.timestamp(),
        'amount': event.amount
    })
    
    # Remove events outside window
    cutoff = datetime.now().timestamp() - window_duration
    current_window = [e for e in current_window if e['timestamp'] > cutoff]
    
    state[window_key] = current_window
    
    # Calculate metrics
    order_count = len(current_window)
    total_amount = sum(e['amount'] for e in current_window)
    
    print(f"5-min window: {order_count} orders, ${total_amount:.2f} total")


# --- Usage ---

def simulate_event_stream() -> Generator[OrderEvent, None, None]:
    """Simulate an event stream for demonstration."""
    
    events = [
        OrderEvent('e1', 'o1', 'c1', 150.00, 'created', datetime.now()),
        OrderEvent('e2', 'o2', 'c2', 15000.00, 'created', datetime.now()),
        OrderEvent('e3', 'o3', 'c1', 75.00, 'created', datetime.now()),
    ]
    
    for event in events:
        yield event


if __name__ == "__main__":
    processor = StreamProcessor()
    processor.register_handler(calculate_customer_total)
    processor.register_handler(detect_high_value_order)
    processor.register_handler(track_order_velocity)
    
    processor.process(simulate_event_stream())
```

### When to Use Streaming

**Good fit when:**
- Need sub-minute data freshness
- Use cases require event-driven triggers
- Data naturally streams continuously
- Team has streaming expertise
- Budget supports streaming infrastructure

**Poor fit when:**
- Daily freshness is sufficient
- Data arrives in natural batches
- Team lacks streaming experience
- Processing requires full dataset context
- Cost is primary concern

### Streaming Advantages and Disadvantages

| Advantages | Disadvantages |
|------------|---------------|
| Real-time data freshness | Complex to build and operate |
| Event-driven architecture | Higher infrastructure cost |
| Handles continuous data naturally | Harder to debug |
| Scales horizontally | State management is tricky |
| Enables real-time analytics | Team needs specialized skills |

## Choosing the Right Pattern

### Decision Framework

```
                          ┌─────────────────────────────┐
                          │ What's your latency need?   │
                          └─────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
              Hours/Days         Minutes            Seconds
                    │                  │                  │
                    ▼                  ▼                  ▼
               ┌────────┐        ┌──────────┐      ┌───────────┐
               │ BATCH  │        │ MICRO-   │      │ STREAMING │
               │        │        │ BATCH    │      │           │
               └────────┘        └──────────┘      └───────────┘
```

### Practical Considerations

**Start with batch** if:
- You're building your first data platform
- Team is small (< 5 data engineers)
- Use cases are primarily analytical (dashboards, reports)
- Budget is constrained

**Graduate to micro-batch** when:
- Stakeholders need fresher data
- You have Airflow or similar scheduler in place
- Batch jobs are taking too long
- You need to process more frequently but team isn't ready for streaming

**Adopt streaming** when:
- Business requires real-time decisions
- You're building operational data products
- You have dedicated infrastructure team
- ROI of real-time justifies complexity

## Hybrid Architectures: The Lambda and Kappa Patterns

Real platforms often combine patterns.

### Lambda Architecture

Run batch and streaming in parallel:

```
                    ┌─────────────────┐
     ┌─────────────►│  Batch Layer   │──────────┐
     │              │  (accurate)    │          │
     │              └─────────────────┘          │
[Source]                                         ├──►[Query]
     │              ┌─────────────────┐          │
     └─────────────►│  Speed Layer   │──────────┘
                    │  (fast)        │
                    └─────────────────┘
```

- Batch layer provides accurate historical data
- Speed layer provides real-time updates
- Query layer merges both views

**Pros:** Best of both worlds
**Cons:** Maintaining two pipelines with same logic

### Kappa Architecture

Use streaming for everything:

```
[Source] ──► [Event Log] ──► [Stream Processor] ──► [Serving Layer]
                 │
                 │ (replayable)
                 ▼
            [Reprocess from beginning if needed]
```

- Single streaming pipeline for all processing
- Event log enables replay for corrections
- Simpler than Lambda (one codebase)

**Pros:** Single system to maintain
**Cons:** Requires robust streaming infrastructure

## Migration Path: Batch to Streaming

Most platforms evolve from batch to streaming. Here's a practical migration path:

### Phase 1: Solid Batch Foundation
- Reliable daily batch pipelines
- Good monitoring and alerting
- Idempotent, rerunnable jobs

### Phase 2: Micro-Batch for Critical Paths
- Identify high-value use cases needing fresher data
- Convert those specific pipelines to micro-batch
- Keep everything else on daily batch

### Phase 3: Streaming for Real-Time Needs
- Identify use cases requiring true real-time
- Implement streaming for those specific flows
- Batch continues for analytical workloads

### Phase 4: Hybrid Optimization
- Streaming for operational data
- Batch for analytical data
- Clear boundaries and data contracts between layers

## Conclusion

There's no universally correct pipeline architecture. The right choice depends on:

- **Latency requirements:** How fresh must data be?
- **Team capability:** What can your team build and operate?
- **Budget:** What infrastructure can you afford?
- **Use cases:** What are you trying to enable?

Start simple. Batch pipelines running on a schedule solve most problems. Add complexity only when specific use cases demand it.

The goal isn't the most sophisticated architecture—it's the simplest architecture that meets your requirements while remaining operable by your team.

---

*Part of a series on data platform architecture. See also: [Data Quality Fundamentals](/posts/data-quality-fundamentals) and [The Zen of Data Engineering](/posts/zen-of-data-engineering).*
