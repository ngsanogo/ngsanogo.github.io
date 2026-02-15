---
title: "Modern Data Stack Architecture: A Practical Guide"
slug: modern-data-stack-architecture
date: 2026-01-30
description: "Understand the modern data stack from ingestion to visualization. Learn how ELT, cloud warehouses, and transformation tools work together. Build a stack that scales."
categories: ["architecture"]
tags: ["architecture", "modern-data-stack", "elt", "cloud", "data-warehouse"]
draft: false
---

## The Evolution of Data Architecture

Ten years ago, data architecture meant expensive on-premise servers running Oracle or Teradata. ETL tools cost millions. Scaling required hardware purchases months in advance.

Today's modern data stack is different. Cloud-native, pay-per-use, composable. A startup can build a sophisticated data platform for hundreds of dollars per month.

This article walks through the components of a modern data stack, how they work together, and how to choose the right tools for your situation.

## The Modern Data Stack Components

```
┌──────────────────────────────────────────────────────────────────────┐
│                        MODERN DATA STACK                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [Sources] ──► [Ingestion] ──► [Storage] ──► [Transform] ──► [Serve]│
│                                                                      │
│  Databases      Fivetran       Snowflake      dbt            Looker │
│  SaaS APIs      Airbyte        BigQuery       Spark          Metabase│
│  Files          Stitch         Databricks     Python         Tableau │
│  Streams        Custom         Redshift                      Mode    │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                      [Orchestration: Airflow/Dagster]                │
│                      [Observability: Monte Carlo/Datadog]            │
│                      [Catalog: Atlan/DataHub]                        │
└──────────────────────────────────────────────────────────────────────┘
```

Let's examine each layer.

## Layer 1: Data Sources

Data sources are everything you want to analyze. They fall into categories:

### Operational Databases
Your application databases: PostgreSQL, MySQL, MongoDB. These store transactional data that needs analytics.

### SaaS Applications
Third-party tools generate data: Salesforce, HubSpot, Stripe, Zendesk. Each has APIs that need integration.

### Event Streams
User behavior, IoT sensors, application logs. High-volume, continuous data requiring special handling.

### Files
CSV exports, Excel files, PDFs. Often from partners or legacy systems.

### Source Inventory Example

```python
"""
Document your data sources systematically.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class SourceType(Enum):
    DATABASE = "database"
    SAAS = "saas"
    API = "api"
    FILE = "file"
    STREAM = "stream"


class UpdateFrequency(Enum):
    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"


@dataclass
class DataSource:
    """Document a data source for your stack."""

    name: str
    source_type: SourceType
    description: str
    owner: str
    tables: List[str]
    update_frequency: UpdateFrequency
    volume_rows_per_day: int
    pii_present: bool
    ingestion_method: str
    notes: Optional[str] = None


# Example source inventory
source_inventory = [
    DataSource(
        name="Production PostgreSQL",
        source_type=SourceType.DATABASE,
        description="Main application database",
        owner="Backend Team",
        tables=["users", "orders", "products", "payments"],
        update_frequency=UpdateFrequency.REALTIME,
        volume_rows_per_day=50000,
        pii_present=True,
        ingestion_method="Fivetran CDC",
        notes="Peak load 6-8 PM UTC"
    ),
    DataSource(
        name="Salesforce",
        source_type=SourceType.SAAS,
        description="CRM and sales pipeline",
        owner="Sales Operations",
        tables=["Account", "Contact", "Opportunity", "Lead"],
        update_frequency=UpdateFrequency.HOURLY,
        volume_rows_per_day=1000,
        pii_present=True,
        ingestion_method="Fivetran connector"
    ),
    DataSource(
        name="Segment Events",
        source_type=SourceType.STREAM,
        description="User behavior tracking",
        owner="Product Analytics",
        tables=["tracks", "identifies", "pages"],
        update_frequency=UpdateFrequency.REALTIME,
        volume_rows_per_day=5000000,
        pii_present=True,
        ingestion_method="Segment warehouse sync"
    )
]
```

## Layer 2: Data Ingestion

Ingestion moves data from sources to your warehouse. The modern approach: ELT (Extract, Load, Transform) instead of ETL.

### ELT vs ETL

```
ETL (Traditional):
[Source] ──► [Extract] ──► [Transform] ──► [Load] ──► [Warehouse]
                              │
                              └── Complex ETL server needed

ELT (Modern):
[Source] ──► [Extract] ──► [Load] ──► [Warehouse] ──► [Transform]
                                           │
                                           └── Warehouse does heavy lifting
```

**Why ELT won:**
- Cloud warehouses are cheap and powerful
- Separates concerns (ingestion vs transformation)
- Raw data preserved for flexibility
- Easier to maintain and debug

### Ingestion Tool Comparison

| Tool | Best For | Pricing Model | Connectors |
|------|----------|---------------|------------|
| Fivetran | Enterprise, reliability | Per row | 300+ |
| Airbyte | Cost-conscious, open source | Self-host or cloud | 300+ |
| Stitch | SMB, simplicity | Per row | 100+ |
| Custom | Unique sources | Engineering time | Unlimited |

### When to Build Custom Ingestion

Build custom only when:
- No connector exists for your source
- You need real-time (sub-minute) latency
- Data requires complex pre-processing
- Volume makes connector pricing prohibitive

```python
"""
Custom ingestion pattern for APIs without connectors.
"""

import requests
from datetime import datetime, timedelta
from typing import Generator, Dict, Any
import json


class APIIngestor:
    """
    Generic API ingestion pattern.

    Handles pagination, rate limiting, incremental extraction.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def extract_incremental(
        self,
        endpoint: str,
        since: datetime,
        page_size: int = 100
    ) -> Generator[Dict[Any, Any], None, None]:
        """
        Extract records modified since given timestamp.

        Yields records one page at a time for memory efficiency.
        """

        page = 1
        has_more = True

        while has_more:
            params = {
                "updated_since": since.isoformat(),
                "page": page,
                "per_page": page_size
            }

            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params
            )
            response.raise_for_status()

            data = response.json()
            records = data.get("results", [])

            if records:
                yield records
                page += 1

            has_more = len(records) == page_size

    def load_to_warehouse(self, records: list, table_name: str):
        """Load records to warehouse. Implementation depends on warehouse."""

        # Example: Load to BigQuery
        from google.cloud import bigquery

        client = bigquery.Client()
        table_ref = client.dataset("raw").table(table_name)

        errors = client.insert_rows_json(table_ref, records)

        if errors:
            raise Exception(f"Load errors: {errors}")


def run_incremental_ingestion():
    """Run incremental ingestion job."""

    # Get last successful run time (from state store)
    last_run = get_last_run_time("custom_api_orders")

    ingestor = APIIngestor(
        base_url="https://api.example.com/v1",
        api_key=os.environ["API_KEY"]
    )

    total_records = 0

    for page in ingestor.extract_incremental("orders", since=last_run):
        ingestor.load_to_warehouse(page, "raw_orders")
        total_records += len(page)

    # Update state
    update_last_run_time("custom_api_orders", datetime.now())

    print(f"Ingested {total_records} records")
```

## Layer 3: Data Storage (Warehouse)

The warehouse is the heart of the modern stack. All data lives here; all transformations run here.

### Major Cloud Warehouses

**Snowflake:**
- Separates storage and compute
- Per-second billing
- Excellent for variable workloads
- Premium pricing

**BigQuery:**
- Serverless (no cluster management)
- Pay per query (or flat rate)
- Best Google ecosystem integration
- Slot-based scaling can be complex

**Databricks:**
- Lake + warehouse combined (lakehouse)
- Best for ML/AI workloads
- Open formats (Delta Lake)
- More complex to operate

**Redshift:**
- AWS native
- Predictable pricing (provisioned)
- Good for consistent workloads
- Requires capacity planning

### Choosing a Warehouse

```
Decision Tree:

1. Do you need ML/AI capabilities integrated?
   YES → Databricks
   NO → Continue

2. Are you all-in on Google Cloud?
   YES → BigQuery
   NO → Continue

3. Are you all-in on AWS?
   YES → Redshift (or Snowflake on AWS)
   NO → Continue

4. Do you need multi-cloud flexibility?
   YES → Snowflake
   NO → Snowflake or BigQuery (both excellent)
```

### Warehouse Organization

```sql
-- Standard warehouse structure

-- RAW layer: Exactly as ingested
CREATE SCHEMA raw;
-- Tables: raw.salesforce_accounts, raw.postgres_orders, etc.
-- Rule: Never transform. Append-only or full reload.

-- STAGING layer: Cleaned and typed
CREATE SCHEMA staging;
-- Tables: stg_accounts, stg_orders
-- Rule: 1:1 with source tables. Rename, cast, dedupe.

-- MARTS layer: Business-focused
CREATE SCHEMA marts;
-- Tables: dim_customers, fct_orders, agg_daily_sales
-- Rule: Modeled for analytics. Join dimensions to facts.

-- ANALYTICS layer: Ready for BI
CREATE SCHEMA analytics;
-- Views and tables exposed to BI tools
-- Rule: User-friendly names. Pre-joined where helpful.
```

## Layer 4: Data Transformation

Transformation turns raw data into analytics-ready datasets. dbt dominates this layer.

### Why dbt Won

dbt (data build tool) became standard because it:
- Uses SQL (analysts can contribute)
- Versions transformations in git
- Handles dependencies automatically
- Documents as you build
- Tests data quality inline

### dbt Project Structure

```
dbt_project/
├── dbt_project.yml
├── models/
│   ├── staging/
│   │   ├── salesforce/
│   │   │   ├── stg_salesforce__accounts.sql
│   │   │   └── stg_salesforce__opportunities.sql
│   │   └── postgres/
│   │       ├── stg_postgres__orders.sql
│   │       └── stg_postgres__users.sql
│   └── marts/
│       ├── core/
│       │   ├── dim_customers.sql
│       │   └── fct_orders.sql
│       └── marketing/
│           └── marketing_attributed_conversions.sql
├── tests/
│   └── generic/
├── macros/
└── seeds/
```

### dbt Model Examples

```sql
-- models/staging/postgres/stg_postgres__orders.sql
-- Staging model: clean and type raw data

{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('postgres', 'orders') }}
),

cleaned AS (
    SELECT
        -- Primary key
        id AS order_id,

        -- Foreign keys
        user_id AS customer_id,

        -- Attributes
        LOWER(status) AS order_status,

        -- Amounts (convert cents to dollars)
        total_cents / 100.0 AS order_total,
        discount_cents / 100.0 AS discount_amount,

        -- Dates
        created_at::timestamp AS ordered_at,
        updated_at::timestamp AS updated_at

    FROM source
    WHERE id IS NOT NULL  -- Defensive filter
)

SELECT * FROM cleaned
```

```sql
-- models/marts/core/fct_orders.sql
-- Fact table: enriched with dimensions

{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='sync_all_columns'
) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_postgres__orders') }}
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

final AS (
    SELECT
        -- Order grain
        orders.order_id,
        orders.ordered_at,

        -- Customer attributes
        orders.customer_id,
        customers.customer_segment,
        customers.acquisition_channel,
        customers.first_order_date,

        -- Order attributes
        orders.order_status,
        orders.order_total,
        orders.discount_amount,

        -- Calculated fields
        orders.order_total - orders.discount_amount AS net_revenue,
        CASE
            WHEN orders.ordered_at = customers.first_order_date
            THEN TRUE ELSE FALSE
        END AS is_first_order,

        -- Metadata
        orders.updated_at,
        CURRENT_TIMESTAMP AS dbt_loaded_at

    FROM orders
    LEFT JOIN customers
        ON orders.customer_id = customers.customer_id
)

SELECT * FROM final
```

```yaml
# models/marts/core/fct_orders.yml
# Documentation and tests

version: 2

models:
  - name: fct_orders
    description: "Order fact table at order grain. Includes customer dimensions."

    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null

      - name: customer_id
        description: "Foreign key to dim_customers"
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id

      - name: order_total
        description: "Order total in dollars"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 100000

      - name: order_status
        description: "Current order status"
        tests:
          - accepted_values:
              values: ['pending', 'processing', 'shipped', 'delivered', 'canceled']
```

## Layer 5: Data Serving

Serving delivers data to end users through BI tools, APIs, or applications.

### BI Tool Landscape

| Tool | Best For | Pricing | Self-Service Level |
|------|----------|---------|-------------------|
| Looker | Governed metrics | $$$ | Medium |
| Tableau | Visual exploration | $$$ | High |
| Metabase | Open source, simple | Free-$$ | High |
| Mode | SQL + notebooks | $$ | Medium-High |
| Superset | Open source, technical | Free | Medium |

### Semantic Layer

A semantic layer defines metrics once, uses everywhere. Critical for data consistency.

```yaml
# Example: Semantic layer definition (Cube.js style)

cubes:
  - name: Orders
    sql_table: analytics.fct_orders

    dimensions:
      - name: order_id
        sql: order_id
        type: string
        primary_key: true

      - name: ordered_at
        sql: ordered_at
        type: time

      - name: customer_segment
        sql: customer_segment
        type: string

      - name: acquisition_channel
        sql: acquisition_channel
        type: string

    measures:
      - name: order_count
        type: count

      - name: total_revenue
        type: sum
        sql: net_revenue

      - name: average_order_value
        type: number
        sql: "{total_revenue} / NULLIF({order_count}, 0)"

      - name: first_order_count
        type: count
        filters:
          - sql: "{CUBE}.is_first_order = TRUE"

    pre_aggregations:
      - name: daily_by_channel
        dimensions:
          - acquisition_channel
        measures:
          - order_count
          - total_revenue
        time_dimension: ordered_at
        granularity: day
        refresh_key:
          every: 1 hour
```

## Cross-Cutting Concerns

### Orchestration

Orchestration coordinates when jobs run and handles dependencies.

```python
"""
Modern orchestration with Dagster (alternative: Airflow).
"""

from dagster import asset, Definitions, AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets


# Define dbt project as assets
@dbt_assets(manifest_path="target/manifest.json")
def my_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


# Define upstream extraction as asset
@asset(
    group_name="ingestion",
    compute_kind="python"
)
def raw_salesforce_accounts():
    """Extract Salesforce accounts to warehouse."""
    # Trigger Fivetran sync or run custom extraction
    run_fivetran_sync("salesforce")
    return "synced"


# Define downstream reporting asset
@asset(
    deps=["fct_orders"],  # Depends on dbt model
    group_name="reporting"
)
def daily_revenue_report():
    """Generate and send daily revenue report."""
    # Query warehouse, format, send email
    data = query_warehouse("SELECT * FROM analytics.daily_revenue")
    send_report(data, recipients=["team@company.com"])
    return "sent"


defs = Definitions(
    assets=[raw_salesforce_accounts, my_dbt_assets, daily_revenue_report],
    resources={"dbt": DbtCliResource(project_dir="dbt_project")}
)
```

### Data Observability

Monitor data quality and pipeline health.

**What to Monitor:**
- Freshness: Is data arriving on time?
- Volume: Are row counts in expected range?
- Schema: Did columns change unexpectedly?
- Distribution: Are values within normal ranges?
- Lineage: What depends on what?

```python
"""
Basic observability checks (production would use Monte Carlo, etc.)
"""

def freshness_check(table: str, column: str, max_age_hours: int) -> bool:
    """Check if data is fresh."""

    query = f"""
    SELECT
        MAX({column}) as latest,
        CURRENT_TIMESTAMP as now,
        TIMESTAMPDIFF(HOUR, MAX({column}), CURRENT_TIMESTAMP) as age_hours
    FROM {table}
    """

    result = execute_query(query)

    if result['age_hours'] > max_age_hours:
        alert(f"Table {table} is {result['age_hours']} hours old (max: {max_age_hours})")
        return False

    return True


def volume_check(table: str, min_rows: int, max_rows: int) -> bool:
    """Check if row count is in expected range."""

    query = f"SELECT COUNT(*) as row_count FROM {table}"
    result = execute_query(query)

    if not (min_rows <= result['row_count'] <= max_rows):
        alert(f"Table {table} has {result['row_count']} rows (expected {min_rows}-{max_rows})")
        return False

    return True
```

## Putting It Together: Reference Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPLETE MODERN DATA STACK                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SOURCES              INGESTION           WAREHOUSE                 │
│  ─────────            ─────────           ─────────                 │
│  PostgreSQL ─────────► Fivetran ─────────► Snowflake               │
│  Salesforce ─────────►          ─────────►   │                     │
│  Stripe ─────────────►          ─────────►   │                     │
│  Segment ────────────► (direct) ─────────►   │                     │
│                                              │                      │
│                                              ▼                      │
│                                         TRANSFORM                   │
│                                         ─────────                   │
│                                            dbt                      │
│                                              │                      │
│                                              ▼                      │
│                                          SERVING                    │
│                                          ───────                    │
│                                     ┌────────────┐                  │
│                                     │   Looker   │ ◄── Executives  │
│                                     │   Metabase │ ◄── Analysts    │
│                                     │   Cube.js  │ ◄── Applications│
│                                     └────────────┘                  │
│                                                                     │
│  ORCHESTRATION: Dagster (schedules, dependencies, monitoring)      │
│  OBSERVABILITY: Monte Carlo (freshness, volume, schema)            │
│  CATALOG: Atlan (discovery, lineage, governance)                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Migration Path

If you're modernizing from legacy systems:

### Phase 1: Foundation (1-2 months)
- Set up cloud warehouse
- Configure ingestion for critical sources
- Establish basic dbt project

### Phase 2: Migration (2-4 months)
- Migrate existing reports to new stack
- Build staging and mart models
- Train analysts on dbt

### Phase 3: Optimization (Ongoing)
- Add observability
- Implement semantic layer
- Build self-service capabilities

## Cost Optimization

Modern stack costs can grow quickly. Control them:

1. **Warehouse:** Use auto-suspend, right-size clusters
2. **Ingestion:** Reduce sync frequency where possible
3. **Storage:** Implement retention policies
4. **Transformation:** Optimize expensive queries, use incremental models

## Conclusion

The modern data stack is not one tool—it's a composable architecture. The components work together through clear interfaces.

Key principles:
- ELT over ETL: Transform in the warehouse
- Composability: Best-of-breed tools, not monoliths
- SQL-first: Analysts can contribute
- Version control: Everything in git
- Testing: Quality built in, not bolted on

Start simple. Add complexity only when needed. The best stack is the one your team can operate.

---

*Part of a series on data architecture. Related: [Data Pipeline Architecture Patterns](/posts/data-pipeline-architecture-patterns) and [Building Data Products](/posts/building-data-products).*
