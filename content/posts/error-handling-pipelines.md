---
title: "Error Handling in Data Pipelines"
slug: error-handling-pipelines
date: 2026-02-19
description: "How to handle errors in data pipelines. Retry logic, failure modes, alerts, graceful degradation. Build resilient pipelines."
categories: ["data-engineering"]
tags: ["reliability", "error-handling", "pipelines", "best-practices"]
draft: false
---

## Why Pipelines Fail

Pipelines fail constantly:
- API rate limits
- Database timeouts
- Network issues
- Out of memory
- Malformed data
- Schema changes

Failures are normal. Bad error handling is not.

## The Problem: Silent Failures

```python
def extract_data(api_url):
    try:
        response = requests.get(api_url)
        return response.json()
    except:
        return []  # Silent failure
```

This returns empty data when the API fails. Nobody notices. Dashboards show zeros. Reports are wrong. Trust erodes.

## Principle 1: Fail Loudly

```python
import requests
import logging

logger = logging.getLogger(__name__)


class DataExtractionError(Exception):
    """Raised when data extraction fails."""
    pass


def extract_data(api_url: str) -> dict:
    """Extract data from API."""
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()  # Raise error for 4xx/5xx
        return response.json()
        
    except requests.Timeout:
        logger.error(f"API timeout: {api_url}")
        raise DataExtractionError(f"API timeout after 30s: {api_url}")
        
    except requests.HTTPError as e:
        logger.error(f"API HTTP error: {e.response.status_code}")
        raise DataExtractionError(f"API returned {e.response.status_code}: {api_url}")
        
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise DataExtractionError(f"Failed to connect to API: {api_url}")
        
    except ValueError:  # JSON decode error
        logger.error(f"Invalid JSON response from {api_url}")
        raise DataExtractionError(f"API returned invalid JSON: {api_url}")
```

When something fails, the pipeline stops. Loudly. You fix it before bad data propagates.

## Principle 2: Retry Transient Failures

Some errors are temporary:
- Network blip
- Database connection timeout
- API rate limit (temporary)

Retry these. Don't retry permanent failures (bad credentials, 404).

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=5, backoff=2, exceptions=(Exception,)):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay in seconds
        backoff: Backoff multiplier
        exceptions: Exceptions to catch and retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator


# Usage
@retry(max_attempts=3, delay=5, exceptions=(requests.Timeout, requests.ConnectionError))
def extract_data(api_url: str) -> dict:
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    return response.json()
```

Transient failures: retried automatically. Permanent failures: fail immediately.

## Principle 3: Categorize Failures

Not all errors are equal:

**Transient**: Retry
- Network timeout
- Database connection reset
- API rate limit

**Permanent**: Fail immediately
- Invalid credentials
- 404 Not Found
- Schema mismatch

**Partial**: Continue with partial data
- Some records are malformed
- Optional enrichment fails

```python
class TransientError(Exception):
    """Temporary error, should retry."""
    pass

class PermanentError(Exception):
    """Permanent error, don't retry."""
    pass

class PartialFailure(Exception):
    """Some data failed, but can proceed."""
    def __init__(self, message, successful_count, failed_count):
        super().__init__(message)
        self.successful_count = successful_count
        self.failed_count = failed_count


def process_records(records):
    """Process records, handle partial failures."""
    
    successful = []
    failed = []
    
    for record in records:
        try:
            processed = transform_record(record)
            successful.append(processed)
        except ValueError as e:
            logger.warning(f"Failed to process record {record.get('id')}: {e}")
            failed.append(record)
    
    if failed:
        logger.warning(f"Processed {len(successful)}/{len(records)} records successfully")
        
        # If more than 10% fail, something is wrong
        failure_rate = len(failed) / len(records)
        if failure_rate > 0.1:
            raise PartialFailure(
                f"High failure rate: {failure_rate:.1%}",
                len(successful),
                len(failed)
            )
    
    return successful
```

## Principle 4: Graceful Degradation

When optional enrichments fail, continue with core data:

```python
def enrich_customer_data(customers_df):
    """Enrich customer data with external sources."""
    
    df = customers_df.copy()
    
    # Core data: must succeed
    df = calculate_ltv(df)
    
    # Optional enrichment: can fail
    try:
        credit_scores = fetch_credit_scores(df['customer_id'])
        df = df.merge(credit_scores, on='customer_id', how='left')
        logger.info("Successfully enriched with credit scores")
    except Exception as e:
        logger.warning(f"Credit score enrichment failed: {e}. Continuing without it.")
        # Pipeline continues, just without credit scores
    
    return df
```

Core features fail loudly. Optional features degrade gracefully.

## Principle 5: Alert on Failures

```python
import smtplib
from email.message import EmailMessage


def send_alert(subject: str, body: str, to: list[str]):
    """Send alert email."""
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'pipeline-alerts@company.com'
    msg['To'] = ', '.join(to)
    msg.set_content(body)
    
    with smtplib.SMTP('smtp.company.com') as smtp:
        smtp.send_message(msg)


def run_pipeline_with_alerts(process_date):
    """Run pipeline with alerting."""
    
    try:
        run_pipeline(process_date)
        
    except DataExtractionError as e:
        send_alert(
            subject=f"Pipeline FAILED: Data extraction error",
            body=f"Pipeline failed to extract data for {process_date}.\n\nError: {e}",
            to=['data-team@company.com']
        )
        raise
        
    except Exception as e:
        send_alert(
            subject=f"Pipeline FAILED: Unexpected error",
            body=f"Pipeline failed for {process_date}.\n\nError: {e}",
            to=['data-team@company.com', 'oncall@company.com']
        )
        raise
```

Failures trigger alerts. Teams respond immediately.

## Real Example: Robust API Extraction

```python
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Robust API client with error handling."""
    
    def __init__(self, base_url: str, api_key: str, max_retries: int = 3):
        self.base_url = base_url
        self.api_key = api_key
        self.max_retries = max_retries
    
    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        GET request with retry logic and error handling.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited. Retrying after {retry_after}s")
                    time.sleep(retry_after)
                    continue
                
                # Check for errors
                response.raise_for_status()
                
                return response.json()
                
            except requests.Timeout:
                if attempt == self.max_retries:
                    logger.error(f"API timeout after {self.max_retries} attempts")
                    raise TransientError(f"API timeout: {url}")
                
                logger.warning(f"Timeout (attempt {attempt}/{self.max_retries}), retrying...")
                time.sleep(5 * attempt)
                
            except requests.HTTPError as e:
                # Don't retry 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    logger.error(f"Client error: {e.response.status_code}")
                    raise PermanentError(f"API error {e.response.status_code}: {url}")
                
                # Retry 5xx errors (server errors)
                if attempt == self.max_retries:
                    raise TransientError(f"API error after retries: {url}")
                
                logger.warning(f"Server error (attempt {attempt}/{self.max_retries}), retrying...")
                time.sleep(5 * attempt)
                
            except requests.RequestException as e:
                if attempt == self.max_retries:
                    raise TransientError(f"Network error: {url}")
                
                logger.warning(f"Network error (attempt {attempt}/{self.max_retries}), retrying...")
                time.sleep(5 * attempt)
        
        raise TransientError(f"Failed after {self.max_retries} attempts: {url}")
```

## Testing Error Handling

```python
import pytest
from unittest.mock import patch, Mock


def test_retry_on_timeout():
    """Test that transient errors are retried."""
    
    with patch('requests.get') as mock_get:
        # Fail twice, succeed third time
        mock_get.side_effect = [
            requests.Timeout(),
            requests.Timeout(),
            Mock(status_code=200, json=lambda: {'data': 'success'})
        ]
        
        client = APIClient('https://api.example.com', 'key')
        result = client.get('endpoint')
        
        assert result == {'data': 'success'}
        assert mock_get.call_count == 3


def test_no_retry_on_404():
    """Test that permanent errors are not retried."""
    
    with patch('requests.get') as mock_get:
        response = Mock()
        response.status_code = 404
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
        mock_get.return_value = response
        
        client = APIClient('https://api.example.com', 'key')
        
        with pytest.raises(PermanentError):
            client.get('endpoint')
        
        assert mock_get.call_count == 1  # No retry
```

## Summary

Handle errors properly:

1. **Fail loudly**: Don't return empty data silently
2. **Retry transient errors**: Network issues, timeouts
3. **Fail fast on permanent errors**: Bad credentials, 404
4. **Graceful degradation**: Core succeeds, optional fails
5. **Alert immediately**: Teams respond fast

Resilient pipelines = production-ready pipelines.
