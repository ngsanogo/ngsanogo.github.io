---
title: "Incremental Data Processing: Process Only What Changed"
slug: incremental-data-processing
date: 2026-02-22
description: "How to process only new or changed data. Learn incremental patterns for efficient pipelines. Stop reprocessing everything."
categories: ["data-engineering"]
tags: ["incremental-processing", "performance", "pipelines", "best-practices"]
draft: false
---

## Why Incremental Processing

Full reprocessing is slow:
- Scan entire source table
- Transform everything
- Load everything

For a 10M row orders table, this takes hours. Daily.

Incremental processing:
- Scan only new/changed rows
- Transform only what's new
- Load only what's different

Same result. 100x faster.

## The Problem: Full Refresh

```python
def daily_pipeline_full_refresh(date):
    """Process all orders - SLOW."""
    
    # Extract ALL orders
    df = pd.read_sql('SELECT * FROM orders', engine)  # 10M rows
    
    # Transform everything
    transformed = transform(df)  # 2 hours
    
    # Replace entire table
    transformed.to_sql('orders_processed', engine, if_exists='replace')  # 1 hour
    
    # Total: 3+ hours
```

This works for small tables. Not for production.

## Pattern 1: Time-Based Incremental

Process only records created/updated since last run:

```python
def daily_pipeline_incremental(process_date):
    """Process only today's orders - FAST."""
    
    # Extract only today
    query = """
    SELECT * FROM orders
    WHERE DATE(created_at) = :process_date
       OR DATE(updated_at) = :process_date
    """
    
    df = pd.read_sql(query, engine, params={'process_date': process_date})  # 10k rows
    
    # Transform
    transformed = transform(df)  # 10 seconds
    
    # Load idempotently
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM orders_processed WHERE DATE(created_at) = :date"),
            {'date': process_date}
        )
    
    transformed.to_sql('orders_processed', engine, if_exists='append')  # 5 seconds
    
    # Total: 15 seconds instead of 3 hours
```

**Requirements:**
- Source table has `created_at` or `updated_at` timestamp
- Records don't get deleted (or you handle deletes separately)

## Pattern 2: Watermark-Based Incremental

Track the last processed timestamp:

```python
def get_last_watermark(engine, pipeline_name: str) -> datetime:
    """Get last successfully processed timestamp."""
    
    query = """
    SELECT MAX(watermark) as last_watermark
    FROM pipeline_watermarks
    WHERE pipeline_name = :pipeline_name
    """
    
    with engine.connect() as conn:
        result = conn.execute(
            text(query),
            {'pipeline_name': pipeline_name}
        ).fetchone()
    
    if result and result[0]:
        return result[0]
    
    # Default: 30 days ago
    return datetime.now() - timedelta(days=30)


def save_watermark(engine, pipeline_name: str, watermark: datetime):
    """Save current watermark."""
    
    query = """
    INSERT INTO pipeline_watermarks (pipeline_name, watermark, updated_at)
    VALUES (:pipeline_name, :watermark, NOW())
    ON CONFLICT (pipeline_name)
    DO UPDATE SET watermark = :watermark, updated_at = NOW()
    """
    
    with engine.begin() as conn:
        conn.execute(
            text(query),
            {'pipeline_name': pipeline_name, 'watermark': watermark}
        )


def incremental_pipeline_watermark():
    """Process only new records since last watermark."""
    
    pipeline_name = 'orders_pipeline'
    
    # Get last processed timestamp
    last_watermark = get_last_watermark(engine, pipeline_name)
    current_watermark = datetime.now()
    
    logger.info(f"Processing records from {last_watermark} to {current_watermark}")
    
    # Extract only new/updated records
    query = """
    SELECT * FROM orders
    WHERE updated_at > :last_watermark
      AND updated_at <= :current_watermark
    """
    
    df = pd.read_sql(
        query,
        engine,
        params={
            'last_watermark': last_watermark,
            'current_watermark': current_watermark
        }
    )
    
    if len(df) == 0:
        logger.info("No new records to process")
        return
    
    # Transform
    transformed = transform(df)
    
    # Load (upsert based on order_id)
    upsert_records(transformed, engine, 'orders_processed')
    
    # Update watermark
    save_watermark(engine, pipeline_name, current_watermark)
    
    logger.info(f"Processed {len(df)} records")
```

**Watermark table:**

```sql
CREATE TABLE pipeline_watermarks (
    pipeline_name VARCHAR(100) PRIMARY KEY,
    watermark TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## Pattern 3: Change Data Capture (CDC)

Track every change in source system:

```sql
-- Source system has a CDC log table
CREATE TABLE orders_changelog (
    change_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    operation VARCHAR(10),  -- INSERT, UPDATE, DELETE
    changed_at TIMESTAMP,
    old_values JSONB,
    new_values JSONB
);
```

Process only changes:

```python
def cdc_incremental_pipeline(last_change_id: int):
    """Process using CDC log."""
    
    # Get changes since last run
    query = """
    SELECT * FROM orders_changelog
    WHERE change_id > :last_change_id
    ORDER BY change_id
    """
    
    changes = pd.read_sql(query, engine, params={'last_change_id': last_change_id})
    
    for _, change in changes.iterrows():
        if change['operation'] == 'INSERT':
            # Handle new record
            insert_record(change['new_values'])
        elif change['operation'] == 'UPDATE':
            # Handle updated record
            update_record(change['order_id'], change['new_values'])
        elif change['operation'] == 'DELETE':
            # Handle deleted record
            delete_record(change['order_id'])
    
    # Save last processed change_id
    save_last_change_id(changes['change_id'].max())
```

**Pros:** Captures deletes. Accurate.
**Cons:** Requires CDC setup in source system.

## Handling Late-Arriving Data

Problem: Data arrives late. Yesterday's pipeline already ran.

Solution: Reprocess recent partitions:

```python
def incremental_with_lookback(process_date: date, lookback_days: int = 3):
    """
    Process today + last N days to catch late arrivals.
    """
    
    start_date = process_date - timedelta(days=lookback_days)
    
    query = """
    SELECT * FROM orders
    WHERE DATE(created_at) >= :start_date
      AND DATE(created_at) <= :process_date
    """
    
    df = pd.read_sql(
        query,
        engine,
        params={'start_date': start_date, 'process_date': process_date}
    )
    
    # Transform
    transformed = transform(df)
    
    # Load idempotently (delete + insert for date range)
    with engine.begin() as conn:
        conn.execute(
            text("""
            DELETE FROM orders_processed
            WHERE DATE(created_at) >= :start_date
              AND DATE(created_at) <= :process_date
            """),
            {'start_date': start_date, 'process_date': process_date}
        )
    
    transformed.to_sql('orders_processed', engine, if_exists='append')
```

Reprocesses last 3 days. Catches late data. Still faster than full refresh.

## Incremental Aggregations

Aggregations are trickier. Can't just add today's data.

**Wrong:**

```python
# This doesn't work for customer lifetime value
today_orders = extract_today()
today_ltv = calculate_ltv(today_orders)
append(today_ltv)  # Wrong: cumulative metric
```

**Right approach 1: Rebuild affected partitions**

```python
def incremental_aggregation_rebuild(process_date):
    """Rebuild aggregations for affected customers."""
    
    # Get today's orders
    today_orders = extract_orders(process_date)
    
    # Get affected customers
    affected_customers = today_orders['customer_id'].unique()
    
    # Get ALL orders for affected customers
    query = """
    SELECT * FROM orders
    WHERE customer_id IN :customer_ids
    """
    
    all_orders = pd.read_sql(
        query,
        engine,
        params={'customer_ids': tuple(affected_customers)}
    )
    
    # Calculate LTV for affected customers
    ltv = calculate_ltv_per_customer(all_orders)
    
    # Upsert (update or insert)
    upsert_ltv(ltv, engine)
```

**Right approach 2: Use dbt for incremental models**

```sql
-- models/customer_ltv.sql
{{
  config(
    materialized='incremental',
    unique_key='customer_id'
  )
}}

SELECT
    customer_id,
    SUM(amount) as lifetime_value,
    COUNT(*) as order_count,
    MAX(order_date) as last_order_date
FROM {{ ref('orders') }}

{% if is_incremental() %}
  -- Only recalculate for customers with new orders
  WHERE customer_id IN (
    SELECT DISTINCT customer_id
    FROM {{ ref('orders') }}
    WHERE created_at > (SELECT MAX(last_order_date) FROM {{ this }})
  )
{% endif %}

GROUP BY customer_id
```

dbt handles the incremental logic.

## When to Use Incremental

**Use incremental when:**
- Source table is large (millions of rows)
- Only small portion changes daily
- Pipeline takes hours with full refresh
- Source has timestamps (created_at, updated_at)

**Use full refresh when:**
- Table is small (thousands of rows)
- Most data changes frequently
- Simplicity matters more than speed
- Source doesn't have timestamps

## Summary

Incremental processing patterns:
1. **Time-based**: Process today's data only
2. **Watermark**: Track last processed timestamp
3. **CDC**: Process change log
4. **Lookback**: Reprocess recent days for late data

Incremental = faster pipelines = lower costs = happier team.
