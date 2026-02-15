---
title: "MinIO and Airflow: Building a Local Data Lake"
slug: minio-airflow-data-lake
date: 2026-02-03
description: "Learn how to use MinIO as an S3-compatible object storage with Apache Airflow. Build a local data lake for development and testing. Complete setup guide with practical examples."
categories: ["data-engineering"]
tags: ["minio", "airflow", "object-storage", "data-lake", "s3"]
draft: false
---

## Why MinIO for Data Engineering

Every data engineer eventually needs object storage. S3 is the standard, but developing locally against AWS is painful: credentials management, cost concerns, network latency, and the risk of accidentally touching production buckets.

MinIO solves this. It's S3-compatible, runs anywhere, and gives you a production-like environment on your laptop.

This article shows you how to set up MinIO, integrate it with Airflow, and build data pipelines that work identically in development and production.

## What is MinIO?

MinIO is a high-performance, S3-compatible object storage system. Key characteristics:

- **S3 API compatible**: Use any S3 SDK or tool
- **Lightweight**: Single binary, runs anywhere
- **Fast**: Designed for high throughput
- **Open source**: Apache 2.0 license
- **Production ready**: Used by companies at scale

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR DATA PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Development          │          Production               │
│   ───────────          │          ──────────               │
│                        │                                    │
│   ┌─────────┐          │          ┌─────────┐              │
│   │  MinIO  │          │          │   S3    │              │
│   └────┬────┘          │          └────┬────┘              │
│        │               │               │                    │
│        ▼               │               ▼                    │
│   ┌─────────┐          │          ┌─────────┐              │
│   │ Airflow │          │          │ Airflow │              │
│   └─────────┘          │          └─────────┘              │
│                        │                                    │
│   Same code            │          Same code                │
│   Same SDK             │          Same SDK                 │
│   Different endpoint   │          Different endpoint       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Setting Up MinIO

### Option 1: Docker (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  minio:
    image: minio/minio:latest
    container_name: minio
    ports:
      - "9000:9000"   # API
      - "9001:9001"   # Console
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  minio_data:
```

Start MinIO:

```bash
docker-compose up -d minio
```

Access the console at `http://localhost:9001` with credentials `minioadmin/minioadmin`.

### Option 2: Binary Installation

```bash
# Linux
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server /data --console-address ":9001"

# macOS
brew install minio/stable/minio
minio server /data --console-address ":9001"
```

### Initial Configuration

Create buckets for your data lake:

```bash
# Install MinIO client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Configure alias
mc alias set local http://localhost:9000 minioadmin minioadmin

# Create buckets
mc mb local/raw-data
mc mb local/staging
mc mb local/processed
mc mb local/artifacts
```

## Integrating MinIO with Airflow

### Airflow Connection Setup

Add MinIO as an S3-compatible connection in Airflow:

```python
# Via Airflow CLI
airflow connections add 'minio_conn' \
    --conn-type 'aws' \
    --conn-extra '{
        "endpoint_url": "http://minio:9000",
        "aws_access_key_id": "minioadmin",
        "aws_secret_access_key": "minioadmin"
    }'
```

Or via environment variable:

```bash
AIRFLOW_CONN_MINIO_CONN='aws://?endpoint_url=http%3A%2F%2Fminio%3A9000&aws_access_key_id=minioadmin&aws_secret_access_key=minioadmin'
```

### Docker Compose with Airflow and MinIO

```yaml
# docker-compose.yml - Complete setup
version: '3.8'

x-airflow-common: &airflow-common
  image: apache/airflow:2.8.0-python3.11
  environment:
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    # MinIO connection
    AIRFLOW_CONN_MINIO_CONN: 'aws://?endpoint_url=http%3A%2F%2Fminio%3A9000&aws_access_key_id=minioadmin&aws_secret_access_key=minioadmin'
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
  depends_on:
    postgres:
      condition: service_healthy
    minio:
      condition: service_healthy

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
      interval: 10s
      timeout: 10s
      retries: 5

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command:
      - -c
      - |
        airflow db init
        airflow users create \
          --username admin \
          --password admin \
          --firstname Admin \
          --lastname User \
          --role Admin \
          --email admin@example.com

volumes:
  postgres_data:
  minio_data:
```

## Building Data Pipelines with MinIO

### Basic File Operations

```python
"""
dags/minio_basics.py
Basic MinIO operations with Airflow.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator
import json


default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def get_minio_hook():
    """Get S3Hook configured for MinIO."""
    return S3Hook(aws_conn_id='minio_conn')


def upload_to_minio(**context):
    """Upload data to MinIO bucket."""

    hook = get_minio_hook()

    # Sample data
    data = {
        'timestamp': datetime.now().isoformat(),
        'records': [
            {'id': 1, 'name': 'Alice', 'value': 100},
            {'id': 2, 'name': 'Bob', 'value': 200},
            {'id': 3, 'name': 'Charlie', 'value': 300},
        ]
    }

    # Generate key with date partitioning
    execution_date = context['ds']
    key = f"data/year={execution_date[:4]}/month={execution_date[5:7]}/day={execution_date[8:10]}/records.json"

    # Upload
    hook.load_string(
        string_data=json.dumps(data, indent=2),
        key=key,
        bucket_name='raw-data',
        replace=True
    )

    print(f"Uploaded to s3://raw-data/{key}")
    return key


def list_bucket_contents(**context):
    """List contents of a MinIO bucket."""

    hook = get_minio_hook()

    keys = hook.list_keys(
        bucket_name='raw-data',
        prefix='data/'
    )

    print(f"Found {len(keys)} objects:")
    for key in keys:
        print(f"  - {key}")

    return keys


def download_and_process(**context):
    """Download file from MinIO and process it."""

    hook = get_minio_hook()
    ti = context['ti']

    # Get the key from previous task
    key = ti.xcom_pull(task_ids='upload_data')

    # Download content
    content = hook.read_key(
        key=key,
        bucket_name='raw-data'
    )

    data = json.loads(content)

    # Process: calculate total
    total = sum(r['value'] for r in data['records'])

    result = {
        'source_key': key,
        'record_count': len(data['records']),
        'total_value': total,
        'processed_at': datetime.now().isoformat()
    }

    # Upload processed result
    processed_key = key.replace('raw-data', 'processed').replace('records.json', 'summary.json')

    hook.load_string(
        string_data=json.dumps(result, indent=2),
        key=processed_key,
        bucket_name='processed',
        replace=True
    )

    print(f"Processed result: {result}")
    return result


with DAG(
    'minio_basic_operations',
    default_args=default_args,
    description='Basic MinIO operations demo',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['minio', 'demo'],
) as dag:

    upload_task = PythonOperator(
        task_id='upload_data',
        python_callable=upload_to_minio,
    )

    list_task = PythonOperator(
        task_id='list_contents',
        python_callable=list_bucket_contents,
    )

    process_task = PythonOperator(
        task_id='process_data',
        python_callable=download_and_process,
    )

    upload_task >> list_task >> process_task
```

### Data Lake Ingestion Pipeline

```python
"""
dags/data_lake_ingestion.py
Ingest data from multiple sources into MinIO data lake.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO


default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


class DataLakeWriter:
    """Write data to MinIO data lake in Parquet format."""

    def __init__(self, minio_conn_id: str = 'minio_conn'):
        self.hook = S3Hook(aws_conn_id=minio_conn_id)

    def write_parquet(
        self,
        df: pd.DataFrame,
        bucket: str,
        key: str,
        partition_cols: list = None
    ):
        """Write DataFrame to MinIO as Parquet."""

        table = pa.Table.from_pandas(df)

        buffer = BytesIO()
        pq.write_table(table, buffer)
        buffer.seek(0)

        self.hook.load_file_obj(
            file_obj=buffer,
            key=key,
            bucket_name=bucket,
            replace=True
        )

        print(f"Wrote {len(df)} rows to s3://{bucket}/{key}")

    def read_parquet(self, bucket: str, key: str) -> pd.DataFrame:
        """Read Parquet file from MinIO."""

        obj = self.hook.get_key(key=key, bucket_name=bucket)
        buffer = BytesIO(obj.get()['Body'].read())

        return pd.read_parquet(buffer)


def ingest_postgres_table(**context):
    """Ingest a table from PostgreSQL to MinIO data lake."""

    execution_date = context['ds']

    # Extract from Postgres
    pg_hook = PostgresHook(postgres_conn_id='postgres_conn')

    query = """
    SELECT
        id,
        customer_name,
        email,
        created_at,
        total_orders,
        lifetime_value
    FROM customers
    WHERE updated_at >= %(start_date)s
      AND updated_at < %(end_date)s
    """

    df = pg_hook.get_pandas_df(
        sql=query,
        parameters={
            'start_date': execution_date,
            'end_date': (datetime.strptime(execution_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        }
    )

    if df.empty:
        print("No new records to ingest")
        return {'rows': 0}

    # Add metadata
    df['_ingested_at'] = datetime.now()
    df['_source'] = 'postgres.customers'

    # Write to data lake
    writer = DataLakeWriter()

    key = f"customers/year={execution_date[:4]}/month={execution_date[5:7]}/day={execution_date[8:10]}/data.parquet"

    writer.write_parquet(
        df=df,
        bucket='raw-data',
        key=key
    )

    return {
        'rows': len(df),
        'key': key
    }


def ingest_api_data(**context):
    """Ingest data from external API to MinIO."""

    import requests

    execution_date = context['ds']

    # Fetch from API (example with JSONPlaceholder)
    response = requests.get(
        'https://jsonplaceholder.typicode.com/posts',
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data)

    # Add metadata
    df['_ingested_at'] = datetime.now()
    df['_source'] = 'api.jsonplaceholder'

    # Write to data lake
    writer = DataLakeWriter()

    key = f"api_posts/year={execution_date[:4]}/month={execution_date[5:7]}/day={execution_date[8:10]}/data.parquet"

    writer.write_parquet(
        df=df,
        bucket='raw-data',
        key=key
    )

    return {
        'rows': len(df),
        'key': key
    }


def consolidate_daily_data(**context):
    """Consolidate all daily ingested data into a summary."""

    execution_date = context['ds']
    ti = context['ti']

    # Get results from upstream tasks
    postgres_result = ti.xcom_pull(task_ids='ingest_postgres')
    api_result = ti.xcom_pull(task_ids='ingest_api')

    summary = {
        'execution_date': execution_date,
        'sources': [
            {
                'name': 'postgres_customers',
                'rows': postgres_result.get('rows', 0) if postgres_result else 0,
                'key': postgres_result.get('key', '') if postgres_result else ''
            },
            {
                'name': 'api_posts',
                'rows': api_result.get('rows', 0) if api_result else 0,
                'key': api_result.get('key', '') if api_result else ''
            }
        ],
        'total_rows': (postgres_result.get('rows', 0) if postgres_result else 0) +
                      (api_result.get('rows', 0) if api_result else 0),
        'completed_at': datetime.now().isoformat()
    }

    # Write summary
    import json
    hook = S3Hook(aws_conn_id='minio_conn')

    key = f"manifests/{execution_date}/ingestion_summary.json"

    hook.load_string(
        string_data=json.dumps(summary, indent=2),
        key=key,
        bucket_name='artifacts',
        replace=True
    )

    print(f"Daily ingestion complete: {summary['total_rows']} total rows")
    return summary


with DAG(
    'data_lake_ingestion',
    default_args=default_args,
    description='Ingest data from multiple sources to MinIO data lake',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['minio', 'ingestion', 'data-lake'],
) as dag:

    ingest_postgres = PythonOperator(
        task_id='ingest_postgres',
        python_callable=ingest_postgres_table,
    )

    ingest_api = PythonOperator(
        task_id='ingest_api',
        python_callable=ingest_api_data,
    )

    consolidate = PythonOperator(
        task_id='consolidate_daily',
        python_callable=consolidate_daily_data,
    )

    [ingest_postgres, ingest_api] >> consolidate
```

### Sensor for Waiting on MinIO Files

```python
"""
dags/minio_sensors.py
Wait for files to appear in MinIO before processing.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'retries': 1,
}


def process_uploaded_file(**context):
    """Process file after it appears in MinIO."""

    from airflow.providers.amazon.aws.hooks.s3 import S3Hook
    import pandas as pd
    from io import BytesIO

    execution_date = context['ds']

    hook = S3Hook(aws_conn_id='minio_conn')

    key = f"uploads/{execution_date}/data.csv"

    obj = hook.get_key(key=key, bucket_name='raw-data')
    content = obj.get()['Body'].read()

    df = pd.read_csv(BytesIO(content))

    print(f"Processing {len(df)} rows from uploaded file")

    # Your processing logic here

    return {'rows_processed': len(df)}


with DAG(
    'minio_file_sensor',
    default_args=default_args,
    description='Wait for file upload then process',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['minio', 'sensor'],
) as dag:

    wait_for_file = S3KeySensor(
        task_id='wait_for_upload',
        bucket_key='uploads/{{ ds }}/data.csv',
        bucket_name='raw-data',
        aws_conn_id='minio_conn',
        timeout=60 * 60 * 2,  # Wait up to 2 hours
        poke_interval=60,  # Check every minute
        mode='poke',
    )

    process_file = PythonOperator(
        task_id='process_file',
        python_callable=process_uploaded_file,
    )

    wait_for_file >> process_file
```

## Advanced Patterns

### Multi-Environment Configuration

Use environment variables to switch between MinIO (dev) and S3 (prod):

```python
"""
dags/utils/storage.py
Environment-aware storage configuration.
"""

import os
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


def get_storage_config() -> dict:
    """Get storage configuration based on environment."""

    env = os.getenv('ENVIRONMENT', 'development')

    if env == 'production':
        return {
            'conn_id': 'aws_default',
            'endpoint_url': None,  # Use AWS S3
            'bucket_prefix': 'prod-'
        }
    else:
        return {
            'conn_id': 'minio_conn',
            'endpoint_url': 'http://minio:9000',
            'bucket_prefix': ''
        }


def get_bucket_name(logical_name: str) -> str:
    """Get actual bucket name with environment prefix."""

    config = get_storage_config()
    return f"{config['bucket_prefix']}{logical_name}"


class StorageClient:
    """Unified storage client for MinIO and S3."""

    def __init__(self):
        self.config = get_storage_config()
        self.hook = S3Hook(aws_conn_id=self.config['conn_id'])

    def upload(self, data: bytes, bucket: str, key: str):
        """Upload data to storage."""

        actual_bucket = get_bucket_name(bucket)

        self.hook.load_bytes(
            bytes_data=data,
            key=key,
            bucket_name=actual_bucket,
            replace=True
        )

    def download(self, bucket: str, key: str) -> bytes:
        """Download data from storage."""

        actual_bucket = get_bucket_name(bucket)

        return self.hook.read_key(
            key=key,
            bucket_name=actual_bucket
        )

    def list_keys(self, bucket: str, prefix: str = '') -> list:
        """List keys in bucket."""

        actual_bucket = get_bucket_name(bucket)

        return self.hook.list_keys(
            bucket_name=actual_bucket,
            prefix=prefix
        )
```

### Data Quality Checks on Upload

```python
"""
dags/quality_checked_ingestion.py
Validate data before storing in data lake.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
from io import BytesIO


def validate_data(**context):
    """Validate incoming data quality."""

    ti = context['ti']
    df = ti.xcom_pull(task_ids='extract_data')

    issues = []

    # Check for nulls in required columns
    required_cols = ['id', 'customer_id', 'amount']
    for col in required_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            issues.append(f"Column {col} has {null_count} null values")

    # Check for duplicates
    dup_count = df.duplicated(subset=['id']).sum()
    if dup_count > 0:
        issues.append(f"Found {dup_count} duplicate IDs")

    # Check value ranges
    if (df['amount'] < 0).any():
        issues.append("Found negative amounts")

    # Store validation result
    validation_result = {
        'passed': len(issues) == 0,
        'issues': issues,
        'row_count': len(df),
        'validated_at': datetime.now().isoformat()
    }

    ti.xcom_push(key='validation_result', value=validation_result)

    # Return branch decision
    if validation_result['passed']:
        return 'store_valid_data'
    else:
        return 'quarantine_invalid_data'


def store_valid_data(**context):
    """Store validated data in main data lake."""

    ti = context['ti']
    execution_date = context['ds']

    df = ti.xcom_pull(task_ids='extract_data')

    # Write to main data lake
    hook = S3Hook(aws_conn_id='minio_conn')

    buffer = BytesIO()
    df.to_parquet(buffer)
    buffer.seek(0)

    key = f"validated/orders/{execution_date}/data.parquet"

    hook.load_file_obj(
        file_obj=buffer,
        key=key,
        bucket_name='processed',
        replace=True
    )

    print(f"Stored {len(df)} validated records")


def quarantine_invalid_data(**context):
    """Store invalid data in quarantine for review."""

    ti = context['ti']
    execution_date = context['ds']

    df = ti.xcom_pull(task_ids='extract_data')
    validation = ti.xcom_pull(task_ids='validate_data', key='validation_result')

    hook = S3Hook(aws_conn_id='minio_conn')

    # Store the data
    buffer = BytesIO()
    df.to_parquet(buffer)
    buffer.seek(0)

    key = f"quarantine/orders/{execution_date}/data.parquet"

    hook.load_file_obj(
        file_obj=buffer,
        key=key,
        bucket_name='raw-data',
        replace=True
    )

    # Store validation report
    import json
    report_key = f"quarantine/orders/{execution_date}/validation_report.json"

    hook.load_string(
        string_data=json.dumps(validation, indent=2),
        key=report_key,
        bucket_name='raw-data',
        replace=True
    )

    print(f"Quarantined {len(df)} records with issues: {validation['issues']}")

    # Could also send alert here


with DAG(
    'quality_checked_ingestion',
    default_args={'owner': 'data-engineering', 'retries': 2},
    description='Ingest with data quality validation',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['minio', 'quality'],
) as dag:

    # Extract task would go here
    # For demo, assuming data comes from upstream

    validate = BranchPythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )

    store_valid = PythonOperator(
        task_id='store_valid_data',
        python_callable=store_valid_data,
    )

    quarantine = PythonOperator(
        task_id='quarantine_invalid_data',
        python_callable=quarantine_invalid_data,
    )

    validate >> [store_valid, quarantine]
```

## Best Practices

### 1. Use Consistent Naming Conventions

```
Bucket structure:
- raw-data/           # Unprocessed source data
- staging/            # Intermediate processing
- processed/          # Ready for consumption
- artifacts/          # Manifests, configs, logs

Key structure:
- {source}/{entity}/year={YYYY}/month={MM}/day={DD}/{filename}
- Example: postgres/orders/year=2026/month=02/day=03/data.parquet
```

### 2. Always Add Metadata

```python
def add_ingestion_metadata(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Add standard metadata columns."""

    df = df.copy()
    df['_ingested_at'] = datetime.now()
    df['_source'] = source
    df['_airflow_run_id'] = '{{ run_id }}'

    return df
```

### 3. Implement Lifecycle Policies

```python
"""
Manage data lifecycle in MinIO.
"""

def setup_lifecycle_policy():
    """Configure automatic data expiration."""

    import json
    from minio import Minio

    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    # Delete raw data after 90 days
    lifecycle_config = {
        "Rules": [
            {
                "ID": "expire-raw-data",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "Expiration": {"Days": 90}
            }
        ]
    }

    client.set_bucket_lifecycle('raw-data', lifecycle_config)
```

### 4. Monitor Bucket Usage

```python
"""
dags/minio_monitoring.py
Monitor MinIO bucket health.
"""

def check_bucket_health(**context):
    """Check bucket sizes and alert on anomalies."""

    from minio import Minio

    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    buckets = ['raw-data', 'staging', 'processed']

    for bucket_name in buckets:
        objects = client.list_objects(bucket_name, recursive=True)

        total_size = 0
        object_count = 0

        for obj in objects:
            total_size += obj.size
            object_count += 1

        size_gb = total_size / (1024 ** 3)

        print(f"Bucket {bucket_name}: {object_count} objects, {size_gb:.2f} GB")

        # Alert if bucket is growing unexpectedly
        if size_gb > 100:
            send_alert(f"Bucket {bucket_name} exceeds 100GB: {size_gb:.2f} GB")
```

## Conclusion

MinIO gives you S3-compatible storage that runs anywhere. Combined with Airflow, you can build data pipelines that work identically in development and production.

Key takeaways:

- **Same code, different endpoint**: Your pipeline code stays the same
- **Local development**: Test with real object storage, not mocks
- **Cost effective**: No cloud charges during development
- **Production ready**: MinIO scales for production use too

Start with the basic setup in this article, then expand as your data lake grows.

---

*Related articles: [Data Pipeline Architecture Patterns](/posts/data-pipeline-architecture-patterns) and [Apache Airflow Orchestration](/posts/apache-airflow-orchestration).*
