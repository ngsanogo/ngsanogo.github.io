---
title: "Monitoring Data Pipelines in Production"
slug: monitoring-data-pipelines
date: 2026-02-21
description: "How to monitor data pipelines. Track success rates, latency, data quality. Build observable pipelines you can trust."
categories: ["observability"]
tags: ["monitoring", "observability", "data-engineering", "production"]
draft: false
---

## Why Monitoring Matters

Your pipeline runs daily. Sometimes it succeeds. Sometimes it fails silently. Sometimes it succeeds but loads bad data.

Without monitoring, you find out when users complain. Too late.

Monitoring answers:
- Did the pipeline run?
- Did it succeed?
- How long did it take?
- Is the data correct?

## What to Monitor

**Execution monitoring:**
- Did pipeline start?
- Did it complete?
- How long did it take?

**Data monitoring:**
- How many records processed?
- Are values in expected ranges?
- Are there anomalies?

**Quality monitoring:**
- Are there nulls where there shouldn't be?
- Are there duplicates?
- Does data match source?

## Basic Logging

Start with structured logging:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing."""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        
        # Add extra fields
        if hasattr(record, 'pipeline'):
            log_data['pipeline'] = record.pipeline
        if hasattr(record, 'execution_date'):
            log_data['execution_date'] = record.execution_date
        if hasattr(record, 'rows_processed'):
            log_data['rows_processed'] = record.rows_processed
        
        return json.dumps(log_data)


# Setup
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Usage
def extract_orders(date):
    logger.info(
        "Extracting orders",
        extra={
            'pipeline': 'daily_orders',
            'execution_date': str(date),
            'step': 'extract'
        }
    )
    
    df = fetch_orders(date)
    
    logger.info(
        "Extraction complete",
        extra={
            'pipeline': 'daily_orders',
            'execution_date': str(date),
            'step': 'extract',
            'rows_processed': len(df)
        }
    )
    
    return df
```

Structured logs = easy to parse = easy to alert on.

## Metrics Collection

Track key metrics:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


@dataclass
class PipelineMetrics:
    """Metrics for a pipeline run."""
    
    pipeline_name: str
    execution_date: str
    start_time: datetime
    end_time: datetime
    status: str  # success, failed, partial
    
    # Data metrics
    rows_extracted: int
    rows_transformed: int
    rows_loaded: int
    rows_failed: int
    
    # Performance metrics
    extract_duration_sec: float
    transform_duration_sec: float
    load_duration_sec: float
    
    # Quality metrics
    null_count: int
    duplicate_count: int
    
    @property
    def total_duration_sec(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def success_rate(self) -> float:
        total = self.rows_extracted
        if total == 0:
            return 0.0
        return (self.rows_loaded / total) * 100
    
    def to_json(self) -> str:
        """Serialize metrics to JSON."""
        return json.dumps({
            'pipeline_name': self.pipeline_name,
            'execution_date': self.execution_date,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'rows_extracted': self.rows_extracted,
            'rows_transformed': self.rows_transformed,
            'rows_loaded': self.rows_loaded,
            'rows_failed': self.rows_failed,
            'extract_duration_sec': self.extract_duration_sec,
            'transform_duration_sec': self.transform_duration_sec,
            'load_duration_sec': self.load_duration_sec,
            'total_duration_sec': self.total_duration_sec,
            'success_rate': self.success_rate,
            'null_count': self.null_count,
            'duplicate_count': self.duplicate_count
        })
    
    def save(self, engine):
        """Save metrics to database."""
        query = """
        INSERT INTO pipeline_metrics (
            pipeline_name, execution_date, start_time, end_time, status,
            rows_extracted, rows_transformed, rows_loaded, rows_failed,
            extract_duration_sec, transform_duration_sec, load_duration_sec,
            null_count, duplicate_count
        ) VALUES (
            :pipeline_name, :execution_date, :start_time, :end_time, :status,
            :rows_extracted, :rows_transformed, :rows_loaded, :rows_failed,
            :extract_duration_sec, :transform_duration_sec, :load_duration_sec,
            :null_count, :duplicate_count
        )
        """
        
        with engine.begin() as conn:
            conn.execute(text(query), {
                'pipeline_name': self.pipeline_name,
                'execution_date': self.execution_date,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'status': self.status,
                'rows_extracted': self.rows_extracted,
                'rows_transformed': self.rows_transformed,
                'rows_loaded': self.rows_loaded,
                'rows_failed': self.rows_failed,
                'extract_duration_sec': self.extract_duration_sec,
                'transform_duration_sec': self.transform_duration_sec,
                'load_duration_sec': self.load_duration_sec,
                'null_count': self.null_count,
                'duplicate_count': self.duplicate_count
            })
```

## Pipeline with Monitoring

```python
import time
from datetime import datetime

def run_pipeline_with_monitoring(process_date, engine):
    """Run pipeline with full monitoring."""
    
    metrics = PipelineMetrics(
        pipeline_name='daily_orders',
        execution_date=str(process_date),
        start_time=datetime.now(),
        end_time=None,
        status='running',
        rows_extracted=0,
        rows_transformed=0,
        rows_loaded=0,
        rows_failed=0,
        extract_duration_sec=0,
        transform_duration_sec=0,
        load_duration_sec=0,
        null_count=0,
        duplicate_count=0
    )
    
    try:
        # Extract
        extract_start = time.time()
        df = extract_orders(process_date)
        metrics.extract_duration_sec = time.time() - extract_start
        metrics.rows_extracted = len(df)
        
        # Transform
        transform_start = time.time()
        df_transformed = transform_orders(df)
        metrics.transform_duration_sec = time.time() - transform_start
        metrics.rows_transformed = len(df_transformed)
        
        # Quality checks
        metrics.null_count = df_transformed.isnull().sum().sum()
        metrics.duplicate_count = df_transformed.duplicated().sum()
        
        # Load
        load_start = time.time()
        load_orders(df_transformed, engine, process_date)
        metrics.load_duration_sec = time.time() - load_start
        metrics.rows_loaded = len(df_transformed)
        
        # Success
        metrics.status = 'success'
        metrics.end_time = datetime.now()
        
    except Exception as e:
        metrics.status = 'failed'
        metrics.end_time = datetime.now()
        logger.error(f"Pipeline failed: {e}")
        raise
        
    finally:
        # Always save metrics
        metrics.save(engine)
        logger.info(metrics.to_json())
    
    return metrics
```

## Anomaly Detection

Detect when metrics are unusual:

```python
def check_for_anomalies(metrics: PipelineMetrics, engine):
    """Check if current metrics are anomalous."""
    
    # Get historical metrics (last 30 days)
    query = """
    SELECT
        AVG(rows_loaded) as avg_rows,
        STDDEV(rows_loaded) as stddev_rows,
        AVG(total_duration_sec) as avg_duration,
        STDDEV(total_duration_sec) as stddev_duration
    FROM pipeline_metrics
    WHERE pipeline_name = :pipeline_name
      AND status = 'success'
      AND start_time > NOW() - INTERVAL '30 days'
    """
    
    with engine.connect() as conn:
        result = conn.execute(
            text(query),
            {'pipeline_name': metrics.pipeline_name}
        ).fetchone()
    
    if not result:
        return  # Not enough history
    
    avg_rows, stddev_rows, avg_duration, stddev_duration = result
    
    # Check row count
    if stddev_rows > 0:
        row_z_score = abs((metrics.rows_loaded - avg_rows) / stddev_rows)
        if row_z_score > 3:  # More than 3 standard deviations
            logger.warning(
                f"Anomaly detected: row count {metrics.rows_loaded} "
                f"is unusual (avg: {avg_rows:.0f}, stddev: {stddev_rows:.0f})"
            )
            send_alert(
                f"Pipeline {metrics.pipeline_name}: Unusual row count",
                f"Loaded {metrics.rows_loaded} rows (expected ~{avg_rows:.0f})"
            )
    
    # Check duration
    if stddev_duration > 0:
        duration_z_score = abs((metrics.total_duration_sec - avg_duration) / stddev_duration)
        if duration_z_score > 3:
            logger.warning(
                f"Anomaly detected: duration {metrics.total_duration_sec:.1f}s "
                f"is unusual (avg: {avg_duration:.1f}s)"
            )
            send_alert(
                f"Pipeline {metrics.pipeline_name}: Unusually slow",
                f"Took {metrics.total_duration_sec:.1f}s (expected ~{avg_duration:.1f}s)"
            )
```

## Dashboard Queries

Track pipeline health:

```sql
-- Pipeline success rate (last 30 days)
SELECT
    pipeline_name,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
    (SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END)::FLOAT / COUNT(*)) * 100 as success_rate
FROM pipeline_metrics
WHERE start_time > NOW() - INTERVAL '30 days'
GROUP BY pipeline_name;

-- Average duration trend
SELECT
    DATE(start_time) as date,
    pipeline_name,
    AVG(extract_duration_sec + transform_duration_sec + load_duration_sec) as avg_duration_sec
FROM pipeline_metrics
WHERE status = 'success'
  AND start_time > NOW() - INTERVAL '30 days'
GROUP BY DATE(start_time), pipeline_name
ORDER BY date DESC;

-- Data volume trend
SELECT
    DATE(start_time) as date,
    pipeline_name,
    AVG(rows_loaded) as avg_rows_loaded
FROM pipeline_metrics
WHERE status = 'success'
  AND start_time > NOW() - INTERVAL '30 days'
GROUP BY DATE(start_time), pipeline_name
ORDER BY date DESC;
```

## Airflow Integration

Airflow has built-in monitoring:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email
from datetime import datetime, timedelta


def on_failure_callback(context):
    """Send alert on failure."""
    send_email(
        to=['data-team@company.com'],
        subject=f"Pipeline FAILED: {context['task_instance'].task_id}",
        html_content=f"""
        <h3>Pipeline Failed</h3>
        <p><strong>DAG:</strong> {context['task_instance'].dag_id}</p>
        <p><strong>Task:</strong> {context['task_instance'].task_id}</p>
        <p><strong>Execution Date:</strong> {context['execution_date']}</p>
        <p><strong>Log:</strong> <a href="{context['task_instance'].log_url}">View Log</a></p>
        """
    )


default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': False,
    'on_failure_callback': on_failure_callback
}

with DAG(
    'monitored_pipeline',
    default_args=default_args,
    schedule='@daily'
) as dag:
    
    task = PythonOperator(
        task_id='run_pipeline',
        python_callable=run_pipeline_with_monitoring
    )
```

## Summary

Monitor pipelines:
- **Execution**: Did it run? Did it succeed?
- **Performance**: How long? Any slowdowns?
- **Data**: How many records? Any anomalies?
- **Quality**: Nulls? Duplicates?

Collect metrics. Store them. Alert on anomalies.

Monitored pipelines = reliable pipelines.
