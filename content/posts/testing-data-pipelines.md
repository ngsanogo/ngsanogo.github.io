---
title: "Testing Data Pipelines: What Actually Matters"
slug: testing-data-pipelines
date: 2026-02-15
description: "How to test data pipelines. Unit tests, integration tests, data tests. What works in production, what doesn't."
categories: ["testing"]
tags: ["testing", "data-quality", "python", "best-practices"]
draft: false
---

## Why Data Pipelines Need Tests

Untested pipelines break in production. You find out when the CEO asks why revenue dropped 50% overnight.

The data didn't change. Your pipeline broke. Nobody noticed until it was too late.

Tests prevent this. Not all tests—some tests waste time. But the right tests catch problems before production.

## Three Levels of Testing

**Level 1: Unit Tests**
Test individual functions. Does this transformation work correctly?

**Level 2: Integration Tests**
Test the full pipeline. Does extract→transform→load work end-to-end?

**Level 3: Data Tests**
Test the data itself. Does the output make business sense?

Most data engineers focus on Level 1. That's a mistake. Level 3 matters more.

## What to Test (and What Not To)

**Test this:**
- Business logic transformations
- Data quality rules
- Known edge cases
- Schema expectations

**Don't test this:**
- Library functions (Pandas already tested)
- Database connections (integration tests cover this)
- Obvious code (if it's trivial, skip it)

## Unit Tests: Testing Transformations

```python
"""
Test your transformation logic.
"""

import pandas as pd
import pytest

def calculate_customer_ltv(orders: pd.DataFrame) -> pd.DataFrame:
    """Calculate customer lifetime value."""
    return (
        orders
        .groupby('customer_id')
        .agg({
            'amount': 'sum',
            'order_id': 'count'
        })
        .rename(columns={'amount': 'total_spent', 'order_id': 'order_count'})
        .reset_index()
    )


def test_ltv_calculation():
    """Test LTV calculation with known data."""
    orders = pd.DataFrame({
        'customer_id': [1, 1, 2, 2, 2],
        'order_id': [101, 102, 103, 104, 105],
        'amount': [100.0, 50.0, 200.0, 150.0, 50.0]
    })

    result = calculate_customer_ltv(orders)

    assert len(result) == 2
    assert result[result['customer_id'] == 1]['total_spent'].iloc[0] == 150.0
    assert result[result['customer_id'] == 1]['order_count'].iloc[0] == 2
    assert result[result['customer_id'] == 2]['total_spent'].iloc[0] == 400.0
    assert result[result['customer_id'] == 2]['order_count'].iloc[0] == 3


def test_ltv_handles_empty_data():
    """Test LTV with no orders."""
    orders = pd.DataFrame(columns=['customer_id', 'order_id', 'amount'])
    result = calculate_customer_ltv(orders)

    assert len(result) == 0
    assert list(result.columns) == ['customer_id', 'total_spent', 'order_count']


def test_ltv_handles_single_customer():
    """Test LTV with one customer."""
    orders = pd.DataFrame({
        'customer_id': [1],
        'order_id': [101],
        'amount': [100.0]
    })

    result = calculate_customer_ltv(orders)

    assert len(result) == 1
    assert result['total_spent'].iloc[0] == 100.0
```

These tests are fast. Run them every commit. They catch logic errors immediately.

## Integration Tests: Testing the Full Pipeline

```python
"""
Test the complete pipeline with a test database.
"""

import pytest
from sqlalchemy import create_engine, text
import pandas as pd

from pipeline import extract, transform, load


@pytest.fixture
def test_db():
    """Create a test database."""
    engine = create_engine('postgresql://test:test@localhost/test_db')

    # Setup
    with engine.begin() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                amount DECIMAL,
                order_date DATE
            )
        '''))

        conn.execute(text('''
            INSERT INTO orders VALUES
            (1, 1, 100.0, '2025-01-01'),
            (2, 1, 50.0, '2025-01-02'),
            (3, 2, 200.0, '2025-01-03')
        '''))

    yield engine

    # Teardown
    with engine.begin() as conn:
        conn.execute(text('DROP TABLE IF EXISTS orders CASCADE'))
        conn.execute(text('DROP TABLE IF EXISTS customer_summary CASCADE'))


def test_full_pipeline(test_db):
    """Test extract→transform→load pipeline."""

    # Run pipeline
    df = extract(test_db)
    transformed = transform(df)
    load(transformed, test_db, 'customer_summary')

    # Verify results
    with test_db.connect() as conn:
        result = pd.read_sql('SELECT * FROM customer_summary ORDER BY customer_id', conn)

    assert len(result) == 2
    assert result.loc[0, 'customer_id'] == 1
    assert result.loc[0, 'total_spent'] == 150.0
    assert result.loc[1, 'customer_id'] == 2
    assert result.loc[1, 'total_spent'] == 200.0
```

Integration tests are slower but catch connection issues, SQL errors, schema problems.

## Data Tests: Testing the Output

These tests check if the data makes business sense.

```python
"""
Data quality tests - run after pipeline completes.
"""

def test_revenue_within_expected_range(warehouse_engine):
    """Revenue should be within historical norms."""
    query = """
    SELECT SUM(amount) as total_revenue
    FROM orders
    WHERE order_date = CURRENT_DATE
    """

    result = pd.read_sql(query, warehouse_engine)
    daily_revenue = result['total_revenue'].iloc[0]

    # Historical average is $50k/day, should be within 3x
    assert 10_000 < daily_revenue < 150_000, f"Revenue ${daily_revenue} is suspicious"


def test_no_future_dates(warehouse_engine):
    """Orders shouldn't have future dates."""
    query = """
    SELECT COUNT(*) as future_count
    FROM orders
    WHERE order_date > CURRENT_DATE
    """

    result = pd.read_sql(query, warehouse_engine)
    assert result['future_count'].iloc[0] == 0, "Found orders with future dates"


def test_no_negative_amounts(warehouse_engine):
    """Order amounts must be positive."""
    query = """
    SELECT COUNT(*) as negative_count
    FROM orders
    WHERE amount < 0
    """

    result = pd.read_sql(query, warehouse_engine)
    assert result['negative_count'].iloc[0] == 0, "Found negative order amounts"


def test_referential_integrity(warehouse_engine):
    """All orders must reference valid customers."""
    query = """
    SELECT COUNT(*) as orphan_count
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.id
    WHERE c.id IS NULL
    """

    result = pd.read_sql(query, warehouse_engine)
    assert result['orphan_count'].iloc[0] == 0, "Found orders with invalid customer_id"
```

These tests catch data problems that unit tests miss.

## How to Run Tests

```bash
# Unit tests (fast, run always)
pytest tests/unit/

# Integration tests (slower, run before deploy)
pytest tests/integration/

# Data tests (after pipeline runs in production)
pytest tests/data/ --db=production
```

## What I Don't Test

**Library code**: Pandas is already tested. Don't test `df.groupby()`.

**Configuration**: Testing `DATABASE_URL = "postgres://..."` wastes time.

**Trivial code**: If it's 2 lines and obvious, skip it.

**Everything**: 100% coverage is pointless. Test what matters.

## When Tests Are Worth It

**Worth testing:**
- Revenue calculations
- Customer matching logic
- Data quality rules
- Complex transformations

**Not worth testing:**
- Simple field renaming
- Direct pass-through functions
- Database connection setup
- Logging statements

## Tests That Actually Run

Tests that never run are useless.

```yaml
# .github/workflows/test.yml
name: Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/
```

Tests run automatically on every commit. Problems caught immediately.

## Summary

Test data pipelines. But test smart:

- Unit tests for transformation logic
- Integration tests for the full pipeline
- Data tests for business rules

Don't test everything. Test what breaks in production.

Tests slow you down initially. They save you later.
