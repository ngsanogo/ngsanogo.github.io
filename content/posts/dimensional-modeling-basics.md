---
title: "Dimensional Modeling: How to Structure a Data Warehouse"
slug: dimensional-modeling-basics
date: 2026-02-20
description: "Learn dimensional modeling for data warehouses. Fact tables, dimension tables, star schema. Build warehouses analysts can query easily."
category: data-modeling
tags: data-modeling, data-warehouse, dimensional-modeling, star-schema
draft: false
---

## Why Data Warehouse Structure Matters

You've loaded raw data into your warehouse. Tables everywhere. Complex joins. Queries are slow. Analysts can't find what they need.

The problem isn't the data—it's the structure.

Dimensional modeling solves this. It organizes data so queries are fast and intuitive.

## Two Types of Tables

**Fact tables**: Measurable events. Orders, page views, transactions.

**Dimension tables**: Context about events. Customers, products, time.

That's it. Facts and dimensions.

## Example: E-Commerce Warehouse

**Fact: Orders**

```sql
CREATE TABLE fact_orders (
    order_id INTEGER PRIMARY KEY,
    customer_key INTEGER,      -- Links to dim_customers
    product_key INTEGER,       -- Links to dim_products
    date_key INTEGER,          -- Links to dim_dates
    quantity INTEGER,
    amount DECIMAL(10,2),
    discount DECIMAL(10,2),
    tax DECIMAL(10,2)
);
```

**Dimension: Customers**

```sql
CREATE TABLE dim_customers (
    customer_key INTEGER PRIMARY KEY,  -- Surrogate key
    customer_id VARCHAR(50),           -- Natural key
    name VARCHAR(100),
    email VARCHAR(100),
    country VARCHAR(50),
    signup_date DATE,
    customer_segment VARCHAR(20)
);
```

**Dimension: Products**

```sql
CREATE TABLE dim_products (
    product_key INTEGER PRIMARY KEY,
    product_id VARCHAR(50),
    product_name VARCHAR(200),
    category VARCHAR(50),
    brand VARCHAR(50),
    price DECIMAL(10,2)
);
```

**Dimension: Dates**

```sql
CREATE TABLE dim_dates (
    date_key INTEGER PRIMARY KEY,  -- YYYYMMDD format
    date DATE,
    day_of_week VARCHAR(10),
    month VARCHAR(10),
    quarter VARCHAR(2),
    year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);
```

## Star Schema

Facts in the center. Dimensions around it. Looks like a star.

```
         dim_customers
               |
               |
dim_products - fact_orders - dim_dates
               |
               |
          dim_stores
```

Analysts join facts to dimensions. Simple. Fast.

```sql
-- Revenue by customer segment
SELECT
    c.customer_segment,
    SUM(f.amount) as total_revenue
FROM fact_orders f
JOIN dim_customers c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment;
```

One join. Easy to understand. Fast to execute.

## Facts: Measurable Events

Facts store metrics:
- Order amount
- Quantity sold
- Page views
- Session duration

Facts are often large (millions/billions of rows).

**Fact table characteristics:**
- Many rows
- Narrow (few columns)
- Mostly foreign keys and metrics
- Immutable (append-only)

**Good fact table:**

```sql
fact_sales (
    -- Keys
    order_id,
    customer_key,
    product_key,
    date_key,
    store_key,
    
    -- Metrics
    quantity,
    unit_price,
    total_amount,
    discount,
    tax
)
```

**Bad fact table:**

```sql
fact_sales (
    order_id,
    customer_name,        -- Should be in dim_customers
    customer_email,       -- Should be in dim_customers
    product_name,         -- Should be in dim_products
    product_category,     -- Should be in dim_products
    ...
)
```

Denormalized facts = large tables = slow queries.

## Dimensions: Context

Dimensions describe facts:
- Who made the purchase? (customer)
- What was purchased? (product)
- When? (date)
- Where? (store)

**Dimension characteristics:**
- Fewer rows (thousands, not billions)
- Wide (many columns)
- Descriptive attributes
- Changes slowly (SCD - Slowly Changing Dimensions)

## Surrogate Keys

Use surrogate keys, not natural keys:

**Natural key**: `customer_id` from source system (e.g., "CUST-12345")

**Surrogate key**: `customer_key` generated in warehouse (e.g., 1, 2, 3...)

**Why surrogate keys:**

1. **Source systems change**: Customer IDs might change format
2. **Multiple sources**: Same customer might have different IDs in different systems
3. **Performance**: Integer joins faster than string joins
4. **History tracking**: Track changes over time

```sql
dim_customers (
    customer_key INTEGER PRIMARY KEY,  -- Surrogate key (warehouse)
    customer_id VARCHAR(50),           -- Natural key (source system)
    name VARCHAR(100),
    ...
)
```

## Date Dimension

Every fact that has a timestamp needs a date dimension.

```sql
CREATE TABLE dim_dates AS
SELECT
    TO_CHAR(date, 'YYYYMMDD')::INTEGER as date_key,
    date,
    EXTRACT(YEAR FROM date) as year,
    EXTRACT(QUARTER FROM date) as quarter,
    EXTRACT(MONTH FROM date) as month,
    TO_CHAR(date, 'Month') as month_name,
    EXTRACT(DAY FROM date) as day,
    TO_CHAR(date, 'Day') as day_name,
    EXTRACT(DOW FROM date) as day_of_week_num,
    CASE WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN TRUE ELSE FALSE END as is_weekend
FROM generate_series('2020-01-01'::DATE, '2030-12-31'::DATE, '1 day') as date;
```

**Why a date dimension?**

Instead of this:

```sql
SELECT EXTRACT(YEAR FROM order_date), COUNT(*)
FROM orders
GROUP BY EXTRACT(YEAR FROM order_date);
```

Do this:

```sql
SELECT d.year, COUNT(*)
FROM fact_orders f
JOIN dim_dates d ON f.date_key = d.date_key
GROUP BY d.year;
```

Pre-computed date attributes = faster queries.

## Loading Dimensions

```python
import pandas as pd
from sqlalchemy import create_engine

def load_customer_dimension(source_engine, warehouse_engine):
    """Load customer dimension from source system."""
    
    # Extract from source
    query = """
    SELECT
        customer_id,
        name,
        email,
        country,
        signup_date,
        CASE
            WHEN total_spent > 10000 THEN 'VIP'
            WHEN total_spent > 1000 THEN 'Premium'
            ELSE 'Standard'
        END as customer_segment
    FROM customers
    """
    
    df = pd.read_sql(query, source_engine)
    
    # Assign surrogate keys
    df['customer_key'] = range(1, len(df) + 1)
    
    # Load to warehouse
    df.to_sql('dim_customers', warehouse_engine, if_exists='replace', index=False)
```

## Loading Facts

```python
def load_orders_fact(source_engine, warehouse_engine, process_date):
    """Load orders fact table."""
    
    query = """
    SELECT
        o.order_id,
        o.customer_id,
        o.product_id,
        o.order_date,
        o.quantity,
        o.amount,
        o.discount,
        o.tax
    FROM orders o
    WHERE DATE(o.order_date) = :process_date
    """
    
    orders = pd.read_sql(query, source_engine, params={'process_date': process_date})
    
    # Lookup dimension keys
    customers = pd.read_sql('SELECT customer_key, customer_id FROM dim_customers', warehouse_engine)
    products = pd.read_sql('SELECT product_key, product_id FROM dim_products', warehouse_engine)
    
    # Join to get surrogate keys
    orders_enriched = (
        orders
        .merge(customers, on='customer_id', how='left')
        .merge(products, on='product_id', how='left')
    )
    
    # Add date key
    orders_enriched['date_key'] = pd.to_datetime(orders_enriched['order_date']).dt.strftime('%Y%m%d').astype(int)
    
    # Select final columns
    fact_orders = orders_enriched[[
        'order_id',
        'customer_key',
        'product_key',
        'date_key',
        'quantity',
        'amount',
        'discount',
        'tax'
    ]]
    
    # Load to warehouse
    fact_orders.to_sql('fact_orders', warehouse_engine, if_exists='append', index=False)
```

## When Dimensional Modeling Helps

**Good for:**
- Analytical queries (aggregations, grouping)
- BI tools (Tableau, Looker)
- Reporting
- Consistent definitions

**Not ideal for:**
- Operational systems (use normalized tables)
- Real-time transactional queries
- Rapidly changing schemas

## Summary

Dimensional modeling organizes warehouses:

- **Facts**: Measurable events (orders, clicks)
- **Dimensions**: Context (customers, products, dates)
- **Star schema**: Facts connected to dimensions
- **Surrogate keys**: Warehouse-generated integers
- **Date dimension**: Pre-computed date attributes

Structured warehouses = fast queries = happy analysts.
