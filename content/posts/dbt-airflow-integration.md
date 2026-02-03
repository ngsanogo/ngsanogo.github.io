---
title: "dbt and Airflow: Production-Ready Data Transformation"
slug: dbt-airflow-integration
date: 2026-02-03
description: "Learn how to orchestrate dbt with Apache Airflow. Build reliable transformation pipelines with proper scheduling, dependencies, and monitoring. Complete integration guide with examples."
category: data-engineering
tags: dbt, airflow, data-transformation, elt, orchestration
draft: false
---

## Why Combine dbt and Airflow

dbt transforms data. Airflow orchestrates workflows. Together, they form the backbone of modern data platforms.

dbt excels at SQL-based transformations with built-in testing and documentation. But dbt alone doesn't handle:

- Scheduling and dependencies with non-dbt tasks
- Upstream data ingestion coordination
- Downstream alerting and notifications
- Complex branching logic
- Retry policies and SLA monitoring

Airflow fills these gaps. The combination gives you reliable, observable, maintainable transformation pipelines.

```
┌────────────────────────────────────────────────────────────────────┐
│                    AIRFLOW + dbt ARCHITECTURE                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   Airflow handles:              dbt handles:                       │
│   ────────────────              ────────────                       │
│   • Scheduling                  • SQL transformations              │
│   • Task dependencies           • Data tests                       │
│   • Retries                     • Documentation                    │
│   • Alerting                    • Lineage                          │
│   • SLA monitoring              • Incremental logic                │
│   • Cross-system orchestration  • Ref() dependencies               │
│                                                                    │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐    │
│   │ Ingest  │────►│   dbt   │────►│ Export  │────►│ Alert   │    │
│   │ (Python)│     │ (models)│     │ (Python)│     │ (Slack) │    │
│   └─────────┘     └─────────┘     └─────────┘     └─────────┘    │
│        ▲               │                                          │
│        │               │                                          │
│        └───────────────┴──── Airflow orchestrates all ────────   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Integration Approaches

There are three main ways to run dbt from Airflow:

### Approach 1: BashOperator (Simple)

Run dbt CLI commands directly:

```python
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /path/to/dbt && dbt run --profiles-dir /path/to/profiles',
    dag=dag
)
```

**Pros:** Simple, no extra dependencies
**Cons:** Limited visibility, error handling is basic

### Approach 2: Cosmos (Recommended)

Astronomer's Cosmos library renders dbt models as native Airflow tasks:

```python
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig

dbt_transform = DbtTaskGroup(
    project_config=ProjectConfig("/path/to/dbt"),
    profile_config=ProfileConfig(
        profile_name="default",
        target_name="dev"
    ),
    dag=dag
)
```

**Pros:** Each model is a task, full visibility, native Airflow features
**Cons:** Requires additional library

### Approach 3: dbt Cloud API

Call dbt Cloud jobs via API:

```python
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

dbt_cloud_run = DbtCloudRunJobOperator(
    task_id='dbt_cloud_run',
    job_id=12345,
    check_interval=60,
    dag=dag
)
```

**Pros:** Managed infrastructure, built-in CI
**Cons:** Requires dbt Cloud subscription

## Setup: BashOperator Approach

Let's start with the simplest integration.

### Project Structure

```
airflow_dbt_project/
├── dags/
│   └── dbt_pipeline.py
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_orders.sql
│   │   └── marts/
│   │       └── fct_orders.sql
│   └── tests/
├── docker-compose.yml
└── Dockerfile
```

### Docker Setup

```dockerfile
# Dockerfile
FROM apache/airflow:2.8.0-python3.11

USER root
RUN apt-get update && apt-get install -y git

USER airflow

# Install dbt
RUN pip install dbt-postgres==1.7.0
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  warehouse:
    image: postgres:15
    environment:
      POSTGRES_USER: warehouse
      POSTGRES_PASSWORD: warehouse
      POSTGRES_DB: warehouse
    volumes:
      - warehouse_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  airflow-webserver:
    build: .
    command: webserver
    ports:
      - "8080:8080"
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      DBT_PROFILES_DIR: /opt/airflow/dbt
    volumes:
      - ./dags:/opt/airflow/dags
      - ./dbt:/opt/airflow/dbt
      - ./logs:/opt/airflow/logs

  airflow-scheduler:
    build: .
    command: scheduler
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      DBT_PROFILES_DIR: /opt/airflow/dbt
    volumes:
      - ./dags:/opt/airflow/dags
      - ./dbt:/opt/airflow/dbt
      - ./logs:/opt/airflow/logs

volumes:
  postgres_data:
  warehouse_data:
```

### dbt Configuration

```yaml
# dbt/dbt_project.yml
name: 'analytics'
version: '1.0.0'
config-version: 2

profile: 'analytics'

model-paths: ["models"]
test-paths: ["tests"]
analysis-paths: ["analyses"]
macro-paths: ["macros"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  analytics:
    staging:
      +materialized: view
      +schema: staging
    marts:
      +materialized: table
      +schema: marts
```

```yaml
# dbt/profiles.yml
analytics:
  target: dev
  outputs:
    dev:
      type: postgres
      host: warehouse
      port: 5432
      user: warehouse
      password: warehouse
      dbname: warehouse
      schema: public
      threads: 4
    
    prod:
      type: postgres
      host: "{{ env_var('WAREHOUSE_HOST') }}"
      port: 5432
      user: "{{ env_var('WAREHOUSE_USER') }}"
      password: "{{ env_var('WAREHOUSE_PASSWORD') }}"
      dbname: warehouse
      schema: public
      threads: 8
```

### Basic DAG with BashOperator

```python
"""
dags/dbt_pipeline_bash.py
Basic dbt integration using BashOperator.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

DBT_PROJECT_DIR = '/opt/airflow/dbt'


def check_source_freshness(**context):
    """Verify source data is fresh before transformation."""
    
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    hook = PostgresHook(postgres_conn_id='warehouse')
    
    result = hook.get_first("""
        SELECT MAX(updated_at) as latest
        FROM raw.orders
    """)
    
    latest = result[0]
    
    if latest is None:
        raise ValueError("No data in source table")
    
    age_hours = (datetime.now() - latest).total_seconds() / 3600
    
    if age_hours > 24:
        raise ValueError(f"Source data is {age_hours:.1f} hours old")
    
    print(f"Source data is fresh: {age_hours:.1f} hours old")


with DAG(
    'dbt_pipeline_bash',
    default_args=default_args,
    description='dbt transformation pipeline using BashOperator',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['dbt', 'transformation'],
) as dag:

    check_freshness = PythonOperator(
        task_id='check_source_freshness',
        python_callable=check_source_freshness,
    )

    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt deps',
    )

    dbt_run_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --select staging.*',
    )

    dbt_test_staging = BashOperator(
        task_id='dbt_test_staging',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --select staging.*',
    )

    dbt_run_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --select marts.*',
    )

    dbt_test_marts = BashOperator(
        task_id='dbt_test_marts',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --select marts.*',
    )

    dbt_docs = BashOperator(
        task_id='dbt_docs_generate',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt docs generate',
    )

    # Task dependencies
    check_freshness >> dbt_deps >> dbt_run_staging >> dbt_test_staging
    dbt_test_staging >> dbt_run_marts >> dbt_test_marts >> dbt_docs
```

## Setup: Cosmos Approach (Recommended)

Cosmos renders each dbt model as an Airflow task, giving you granular visibility and control.

### Installation

```bash
pip install astronomer-cosmos[dbt-postgres]
```

### DAG with Cosmos

```python
"""
dags/dbt_pipeline_cosmos.py
dbt integration using Astronomer Cosmos.
Each dbt model becomes an Airflow task.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping


default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


profile_config = ProfileConfig(
    profile_name="analytics",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="warehouse",
        profile_args={"schema": "public"},
    ),
)

execution_config = ExecutionConfig(
    dbt_executable_path="/home/airflow/.local/bin/dbt",
)


def notify_completion(**context):
    """Send notification on pipeline completion."""
    
    ti = context['ti']
    dag_run = context['dag_run']
    
    message = f"""
    dbt Pipeline Complete
    =====================
    DAG: {dag_run.dag_id}
    Run ID: {dag_run.run_id}
    Execution Date: {context['ds']}
    Status: Success
    """
    
    print(message)
    # Could send to Slack, email, etc.


with DAG(
    'dbt_pipeline_cosmos',
    default_args=default_args,
    description='dbt transformation pipeline using Cosmos',
    schedule_interval='0 6 * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['dbt', 'cosmos', 'transformation'],
) as dag:

    # Pre-dbt tasks
    pre_check = PythonOperator(
        task_id='pre_flight_check',
        python_callable=lambda: print("Starting dbt pipeline"),
    )

    # dbt models as task group
    dbt_transform = DbtTaskGroup(
        group_id="dbt_transform",
        project_config=ProjectConfig("/opt/airflow/dbt"),
        profile_config=profile_config,
        execution_config=execution_config,
        operator_args={
            "install_deps": True,
        },
        default_args={"retries": 2},
    )

    # Post-dbt tasks
    notify = PythonOperator(
        task_id='notify_completion',
        python_callable=notify_completion,
    )

    pre_check >> dbt_transform >> notify
```

### Selective Model Execution

```python
"""
dags/dbt_selective.py
Run specific dbt models or tags.
"""

from datetime import datetime
from airflow import DAG
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, RenderConfig
from cosmos.constants import TestBehavior


# Only run models with specific tags
staging_models = DbtTaskGroup(
    group_id="staging",
    project_config=ProjectConfig("/opt/airflow/dbt"),
    profile_config=profile_config,
    render_config=RenderConfig(
        select=["tag:staging"],  # Only models tagged 'staging'
        test_behavior=TestBehavior.AFTER_EACH,  # Test after each model
    ),
)

# Run specific models by path
marts_models = DbtTaskGroup(
    group_id="marts",
    project_config=ProjectConfig("/opt/airflow/dbt"),
    profile_config=profile_config,
    render_config=RenderConfig(
        select=["path:models/marts"],  # Only models in marts folder
        exclude=["tag:wip"],  # Exclude work-in-progress
    ),
)

# Incremental-only run
incremental_refresh = DbtTaskGroup(
    group_id="incremental",
    project_config=ProjectConfig("/opt/airflow/dbt"),
    profile_config=profile_config,
    render_config=RenderConfig(
        select=["config.materialized:incremental"],
    ),
    operator_args={
        "full_refresh": False,
    },
)
```

## Production Patterns

### Pattern 1: Full Pipeline with Ingestion

```python
"""
dags/full_data_pipeline.py
Complete pipeline: Ingest → Transform → Export
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig


default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'sla': timedelta(hours=2),
}


def extract_orders(**context):
    """Extract orders from source system."""
    
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    import pandas as pd
    
    execution_date = context['ds']
    
    # Extract from source
    source_hook = PostgresHook(postgres_conn_id='source_db')
    
    df = source_hook.get_pandas_df("""
        SELECT * FROM orders
        WHERE DATE(created_at) = %(date)s
    """, parameters={'date': execution_date})
    
    # Load to warehouse raw layer
    warehouse_hook = PostgresHook(postgres_conn_id='warehouse')
    
    df.to_sql(
        'orders',
        warehouse_hook.get_sqlalchemy_engine(),
        schema='raw',
        if_exists='append',
        index=False
    )
    
    return {'rows_extracted': len(df)}


def export_to_bi(**context):
    """Export aggregated data to BI tool."""
    
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    import requests
    
    hook = PostgresHook(postgres_conn_id='warehouse')
    
    # Get aggregated data
    df = hook.get_pandas_df("""
        SELECT * FROM marts.daily_revenue
        WHERE report_date = %(date)s
    """, parameters={'date': context['ds']})
    
    # Push to BI API (example)
    # requests.post('https://bi-tool.com/api/data', json=df.to_dict())
    
    print(f"Exported {len(df)} rows to BI")


with DAG(
    'full_data_pipeline',
    default_args=default_args,
    description='Complete ELT pipeline with dbt',
    schedule_interval='0 6 * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['dbt', 'elt', 'production'],
) as dag:

    # 1. Extract and load raw data
    extract = PythonOperator(
        task_id='extract_orders',
        python_callable=extract_orders,
    )

    # 2. Transform with dbt
    transform = DbtTaskGroup(
        group_id="transform",
        project_config=ProjectConfig("/opt/airflow/dbt"),
        profile_config=profile_config,
    )

    # 3. Export to downstream systems
    export = PythonOperator(
        task_id='export_to_bi',
        python_callable=export_to_bi,
    )

    extract >> transform >> export
```

### Pattern 2: Incremental Loads with Full Refresh Option

```python
"""
dags/dbt_incremental.py
Support both incremental and full refresh modes.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule


DBT_DIR = '/opt/airflow/dbt'


def check_full_refresh_needed(**context):
    """Determine if full refresh is needed."""
    
    # Check DAG params
    params = context['params']
    if params.get('full_refresh', False):
        return 'dbt_full_refresh'
    
    # Check if it's first of month (example logic)
    execution_date = context['ds']
    if execution_date.endswith('-01'):
        return 'dbt_full_refresh'
    
    # Check for schema changes (example)
    # if schema_changed():
    #     return 'dbt_full_refresh'
    
    return 'dbt_incremental'


with DAG(
    'dbt_incremental_pipeline',
    default_args={'owner': 'data-engineering', 'retries': 2},
    description='dbt with incremental/full refresh options',
    schedule_interval='0 6 * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    params={'full_refresh': False},
    tags=['dbt', 'incremental'],
) as dag:

    check_mode = BranchPythonOperator(
        task_id='check_refresh_mode',
        python_callable=check_full_refresh_needed,
    )

    dbt_incremental = BashOperator(
        task_id='dbt_incremental',
        bash_command=f'cd {DBT_DIR} && dbt run',
    )

    dbt_full_refresh = BashOperator(
        task_id='dbt_full_refresh',
        bash_command=f'cd {DBT_DIR} && dbt run --full-refresh',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'cd {DBT_DIR} && dbt test',
        trigger_rule=TriggerRule.ONE_SUCCESS,  # Run after either path
    )

    check_mode >> [dbt_incremental, dbt_full_refresh] >> dbt_test
```

### Pattern 3: dbt with Data Quality Gates

```python
"""
dags/dbt_quality_gates.py
Stop pipeline if dbt tests fail.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator


DBT_DIR = '/opt/airflow/dbt'


def check_test_results(**context):
    """Check dbt test results and decide next step."""
    
    import json
    
    # Read dbt run results
    with open(f'{DBT_DIR}/target/run_results.json') as f:
        results = json.load(f)
    
    failures = [r for r in results['results'] if r['status'] == 'fail']
    
    if failures:
        context['ti'].xcom_push(key='failures', value=failures)
        return 'handle_failures'
    
    return 'continue_pipeline'


def handle_test_failures(**context):
    """Handle dbt test failures."""
    
    failures = context['ti'].xcom_pull(key='failures', task_ids='check_tests')
    
    # Log failures
    for f in failures:
        print(f"FAILED: {f['unique_id']}")
    
    # Send alert
    # send_slack_alert(f"dbt tests failed: {len(failures)} failures")
    
    # Raise to fail the task
    raise ValueError(f"dbt tests failed: {len(failures)} tests")


with DAG(
    'dbt_quality_gates',
    default_args={'owner': 'data-engineering'},
    description='dbt with quality gates',
    schedule_interval='0 6 * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['dbt', 'quality'],
) as dag:

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'cd {DBT_DIR} && dbt run',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'cd {DBT_DIR} && dbt test --store-failures',
    )

    check_tests = BranchPythonOperator(
        task_id='check_tests',
        python_callable=check_test_results,
    )

    handle_failures = PythonOperator(
        task_id='handle_failures',
        python_callable=handle_test_failures,
    )

    continue_pipeline = PythonOperator(
        task_id='continue_pipeline',
        python_callable=lambda: print("All tests passed, continuing..."),
    )

    downstream = PythonOperator(
        task_id='downstream_tasks',
        python_callable=lambda: print("Running downstream tasks"),
    )

    dbt_run >> dbt_test >> check_tests
    check_tests >> handle_failures
    check_tests >> continue_pipeline >> downstream
```

### Pattern 4: Parallel Model Groups

```python
"""
dags/dbt_parallel.py
Run independent dbt model groups in parallel.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup


DBT_DIR = '/opt/airflow/dbt'


with DAG(
    'dbt_parallel_groups',
    default_args={'owner': 'data-engineering'},
    description='Parallel dbt model execution',
    schedule_interval='0 6 * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['dbt', 'parallel'],
) as dag:

    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=f'cd {DBT_DIR} && dbt deps',
    )

    # Staging models (run in parallel by source)
    with TaskGroup(group_id='staging') as staging_group:
        
        stg_orders = BashOperator(
            task_id='stg_orders',
            bash_command=f'cd {DBT_DIR} && dbt run --select stg_orders+',
        )
        
        stg_customers = BashOperator(
            task_id='stg_customers',
            bash_command=f'cd {DBT_DIR} && dbt run --select stg_customers+',
        )
        
        stg_products = BashOperator(
            task_id='stg_products',
            bash_command=f'cd {DBT_DIR} && dbt run --select stg_products+',
        )

    # Intermediate models (depend on staging)
    with TaskGroup(group_id='intermediate') as int_group:
        
        int_orders = BashOperator(
            task_id='int_orders_enriched',
            bash_command=f'cd {DBT_DIR} && dbt run --select int_orders_enriched',
        )

    # Mart models (depend on intermediate)
    with TaskGroup(group_id='marts') as marts_group:
        
        fct_orders = BashOperator(
            task_id='fct_orders',
            bash_command=f'cd {DBT_DIR} && dbt run --select fct_orders',
        )
        
        dim_customers = BashOperator(
            task_id='dim_customers',
            bash_command=f'cd {DBT_DIR} && dbt run --select dim_customers',
        )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'cd {DBT_DIR} && dbt test',
    )

    dbt_deps >> staging_group >> int_group >> marts_group >> dbt_test
```

## dbt Model Examples

### Staging Model

```sql
-- models/staging/stg_orders.sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),

cleaned AS (
    SELECT
        id AS order_id,
        user_id AS customer_id,
        LOWER(status) AS order_status,
        total_cents / 100.0 AS order_total,
        created_at::timestamp AS ordered_at,
        updated_at::timestamp AS updated_at
    FROM source
    WHERE id IS NOT NULL
)

SELECT * FROM cleaned
```

### Incremental Model

```sql
-- models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='sync_all_columns'
) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

final AS (
    SELECT
        orders.order_id,
        orders.customer_id,
        customers.customer_segment,
        orders.order_status,
        orders.order_total,
        orders.ordered_at,
        orders.updated_at,
        CURRENT_TIMESTAMP AS dbt_loaded_at
    FROM orders
    LEFT JOIN customers USING (customer_id)
)

SELECT * FROM final
```

### Tests

```yaml
# models/marts/schema.yml
version: 2

models:
  - name: fct_orders
    description: "Order fact table"
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: order_total
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
```

## Best Practices

### 1. Separate Concerns

- Airflow: Scheduling, dependencies, notifications
- dbt: Transformations, tests, documentation

### 2. Use Tags for Selective Runs

```yaml
# dbt_project.yml
models:
  analytics:
    staging:
      +tags: ['staging', 'daily']
    marts:
      core:
        +tags: ['core', 'daily']
      marketing:
        +tags: ['marketing', 'weekly']
```

```python
# Airflow DAG - daily run
dbt_daily = BashOperator(
    task_id='dbt_daily',
    bash_command='dbt run --select tag:daily',
)
```

### 3. Store dbt Artifacts

```python
def store_dbt_artifacts(**context):
    """Store dbt artifacts for debugging."""
    
    import shutil
    from datetime import datetime
    
    execution_date = context['ds']
    
    source = '/opt/airflow/dbt/target'
    dest = f'/opt/airflow/artifacts/dbt/{execution_date}'
    
    shutil.copytree(source, dest)
    print(f"Stored artifacts to {dest}")
```

### 4. Monitor dbt Metrics

```python
def log_dbt_metrics(**context):
    """Extract and log metrics from dbt run."""
    
    import json
    
    with open('/opt/airflow/dbt/target/run_results.json') as f:
        results = json.load(f)
    
    total = len(results['results'])
    success = sum(1 for r in results['results'] if r['status'] == 'success')
    failed = sum(1 for r in results['results'] if r['status'] == 'fail')
    skipped = sum(1 for r in results['results'] if r['status'] == 'skipped')
    
    total_time = sum(r['execution_time'] for r in results['results'])
    
    metrics = {
        'total_models': total,
        'success': success,
        'failed': failed,
        'skipped': skipped,
        'total_execution_time': total_time
    }
    
    print(f"dbt Metrics: {metrics}")
    
    # Push to monitoring system
    # statsd.gauge('dbt.models.total', total)
    # statsd.gauge('dbt.execution_time', total_time)
```

## Conclusion

dbt and Airflow together give you reliable, observable data transformation pipelines. dbt handles the SQL transformations and testing; Airflow handles everything around it.

Key recommendations:

- **Start with BashOperator** for simplicity
- **Graduate to Cosmos** when you need per-model visibility
- **Always run dbt tests** as part of your pipeline
- **Store artifacts** for debugging
- **Use tags** for selective execution

The combination scales from single-person teams to enterprise data platforms.

---

*Related articles: [Apache Airflow Orchestration](/posts/apache-airflow-orchestration) and [Data Pipeline Architecture Patterns](/posts/data-pipeline-architecture-patterns).*
