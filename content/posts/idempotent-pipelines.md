---
title: "Idempotent Pipelines: Run Twice, Get Same Result"
slug: idempotent-pipelines
date: 2026-02-16
description: "How to build idempotent data pipelines. Run them multiple times safely. Prevent duplicate data and ensure reliable reprocessing."
categories: ["data-engineering"]
tags: ["pipelines", "best-practices", "reliability"]
draft: false
---

## What Idempotency Means

An idempotent pipeline produces the same result when run multiple times with the same input.

Run it once: 100 records loaded.
Run it again: Still 100 records, not 200.

## Why It Matters

**Pipelines fail.** Network issues. Database timeouts. Out of memory. Bugs.

When a pipeline fails halfway through, you need to rerun it. If it's not idempotent, you get:
- Duplicate records
- Wrong totals
- Corrupted aggregations
- Lost trust

Idempotent pipelines are safe to rerun. Always.

## The Problem: Non-Idempotent Pipeline

```python
def load_orders(df, engine):
    """Load orders to warehouse - WRONG."""
    df.to_sql('orders', engine, if_exists='append', index=False)
```

Run this twice with the same data:
- First run: 100 records
- Second run: 200 records (100 duplicates)

This breaks everything downstream.

## Solution 1: Replace the Whole Table

```python
def load_orders_replace(df, engine):
    """Load orders - replace entire table."""
    df.to_sql('orders', engine, if_exists='replace', index=False)
```

**Pros:** Simple. Always idempotent.
**Cons:** Slow for large tables. Downtime while replacing.

**When to use:** Small tables, infrequent runs, simplicity matters.

## Solution 2: Delete Before Insert

```python
from sqlalchemy import text

def load_orders_delete_first(df, engine, process_date):
    """Load orders - delete date partition first."""

    with engine.begin() as conn:
        # Delete existing data for this date
        conn.execute(
            text("DELETE FROM orders WHERE DATE(order_date) = :date"),
            {'date': process_date}
        )

    # Insert new data
    df.to_sql('orders', engine, if_exists='append', index=False)
```

**Pros:** Fast. Safe to rerun. Common pattern.
**Cons:** Slight complexity.

**When to use:** Partitioned data, daily/hourly loads.

## Solution 3: Upsert (Insert or Update)

```python
from sqlalchemy.dialects.postgresql import insert

def upsert_orders(df, engine):
    """Load orders - upsert based on primary key."""

    records = df.to_dict('records')

    with engine.begin() as conn:
        stmt = insert(orders_table).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['order_id'],
            set_={
                'customer_id': stmt.excluded.customer_id,
                'amount': stmt.excluded.amount,
                'order_date': stmt.excluded.order_date,
                'updated_at': func.now()
            }
        )
        conn.execute(stmt)
```

**Pros:** Handles updates correctly. True idempotency.
**Cons:** More complex. Slower than delete+insert.

**When to use:** Data changes over time, need to track updates.

## Solution 4: Staging Table Pattern

```python
def load_orders_staging(df, engine, target_table, process_date):
    """Load orders via staging table."""

    staging_table = f"{target_table}_staging"

    # Load to staging
    df.to_sql(staging_table, engine, if_exists='replace', index=False)

    # Atomic swap
    with engine.begin() as conn:
        conn.execute(text(f"BEGIN"))

        # Delete from target
        conn.execute(
            text(f"DELETE FROM {target_table} WHERE DATE(order_date) = :date"),
            {'date': process_date}
        )

        # Insert from staging
        conn.execute(
            text(f"""
            INSERT INTO {target_table}
            SELECT * FROM {staging_table}
            """)
        )

        conn.execute(text(f"COMMIT"))

    # Clean up staging
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE {staging_table}"))
```

**Pros:** Atomic. Safe. Production-grade.
**Cons:** Most complex.

**When to use:** Production pipelines, large datasets, need atomicity.

## Real Example: Daily Sales Summary

Non-idempotent (broken):

```python
def daily_summary_broken(engine, date):
    """Calculate daily summary - WRONG."""

    query = f"""
    INSERT INTO daily_sales
    SELECT
        DATE(order_date) as date,
        COUNT(*) as orders,
        SUM(amount) as revenue
    FROM orders
    WHERE DATE(order_date) = '{date}'
    GROUP BY DATE(order_date)
    """

    with engine.begin() as conn:
        conn.execute(text(query))
```

Rerun this: duplicates in `daily_sales`.

Idempotent (correct):

```python
def daily_summary_idempotent(engine, date):
    """Calculate daily summary - idempotent."""

    with engine.begin() as conn:
        # Delete existing summary for this date
        conn.execute(
            text("DELETE FROM daily_sales WHERE date = :date"),
            {'date': date}
        )

        # Insert new summary
        conn.execute(
            text("""
            INSERT INTO daily_sales
            SELECT
                DATE(order_date) as date,
                COUNT(*) as orders,
                SUM(amount) as revenue
            FROM orders
            WHERE DATE(order_date) = :date
            GROUP BY DATE(order_date)
            """),
            {'date': date}
        )
```

Rerun this 10 times: same result every time.

## Idempotency in Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def process_date_partition(**context):
    """Process a specific date partition idempotently."""

    # Execution date from Airflow
    execution_date = context['ds']  # YYYY-MM-DD string

    # Extract
    df = extract_orders(engine, execution_date)

    # Transform
    transformed = transform(df)

    # Load idempotently (delete + insert)
    load_idempotent(transformed, engine, execution_date)


with DAG(
    'daily_orders',
    start_date=datetime(2025, 1, 1),
    schedule='@daily',
    catchup=True  # Can safely backfill - pipeline is idempotent
) as dag:

    process = PythonOperator(
        task_id='process_orders',
        python_callable=process_date_partition,
        provide_context=True
    )
```

**catchup=True** is safe because the pipeline is idempotent. Backfilling works correctly.

## Testing Idempotency

```python
def test_pipeline_idempotency(test_engine):
    """Test that running pipeline twice produces same result."""

    test_data = pd.DataFrame({
        'order_id': [1, 2, 3],
        'amount': [100, 200, 150],
        'order_date': ['2025-01-01', '2025-01-01', '2025-01-01']
    })

    # Run pipeline first time
    load_orders_idempotent(test_data, test_engine, '2025-01-01')
    result1 = pd.read_sql('SELECT * FROM orders ORDER BY order_id', test_engine)

    # Run pipeline second time (same data)
    load_orders_idempotent(test_data, test_engine, '2025-01-01')
    result2 = pd.read_sql('SELECT * FROM orders ORDER BY order_id', test_engine)

    # Results should be identical
    assert len(result1) == len(result2) == 3
    assert result1.equals(result2)
```

## When Idempotency Is Hard

**Incrementing counters:**

```sql
-- NOT idempotent
UPDATE metrics SET view_count = view_count + 1 WHERE id = 123;
```

Solution: Store raw events, calculate aggregates separately.

**Timestamps:**

```python
# NOT idempotent
df['loaded_at'] = datetime.now()
```

Solution: Use execution time from orchestrator, not current time.

**Random values:**

```python
# NOT idempotent
df['sample_group'] = df.apply(lambda x: random.choice(['A', 'B']), axis=1)
```

Solution: Use deterministic randomness (seed based on record ID).

## Summary

Build idempotent pipelines:
- Run multiple times safely
- Enable reliable backfilling
- Simplify error recovery

**Patterns:**
- Replace entire table (simple, small data)
- Delete then insert (common, fast)
- Upsert (correct updates)
- Staging table (production-grade)

Idempotency is not optional. It's how production pipelines work.
