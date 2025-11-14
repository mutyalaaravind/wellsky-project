import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from google.cloud import logging
from google.cloud.logging_v2.services.metrics_service_v2 import MetricsServiceV2Client
from google.cloud.logging_v2.services.logging_service_v2 import LoggingServiceV2Client
from google.cloud.monitoring_v3 import MetricServiceClient
from google.cloud.monitoring_v3.types import TimeSeries, TimeInterval, Aggregation
from google.protobuf.timestamp_pb2 import Timestamp


class MetricsAdapter:
    """Google Cloud Logging and Monitoring metrics adapter"""

    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize the metrics adapter.
        
        Args:
            project_id: GCP project ID. If None, uses environment variable or default.
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'viki-dev-app-wsky')
        
        # Initialize clients - check for specific metrics emulator flag
        # Use METRICS_EMULATOR_MODE instead of FIRESTORE_EMULATOR_HOST
        metrics_emulator_mode = os.getenv("METRICS_EMULATOR_MODE", "false").lower() == "true"
        
        if metrics_emulator_mode:
            # In metrics emulator mode, we'll return mock data
            self._emulator_mode = True
            self._logging_client = None
            self._metrics_client = None
            self._monitoring_client = None
            print(f"🔥 Metrics adapter using EMULATOR mode (METRICS_EMULATOR_MODE=true)")
        else:
            self._emulator_mode = False
            try:
                self._logging_client = logging.Client(project=self.project_id)
                self._metrics_client = MetricsServiceV2Client()
                self._monitoring_client = MetricServiceClient()
                print(f"🔥 Metrics adapter using PRODUCTION - Project: {self.project_id}")
            except Exception as e:
                print(f"⚠️ Failed to initialize production metrics clients: {e}")
                print(f"🔥 Falling back to EMULATOR mode")
                self._emulator_mode = True
                self._logging_client = None
                self._metrics_client = None
                self._monitoring_client = None

    async def get_log_metric_stats(
        self, 
        metric_name: str,
        hours_back: int = 24,
        aggregation_period_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get statistics for a Google Cloud Logging metric.
        
        Args:
            metric_name: Name of the log metric
            hours_back: How many hours back to look for data
            aggregation_period_minutes: Period for aggregating data points
            
        Returns:
            Dictionary containing metric statistics
        """
        if self._emulator_mode:
            return self._get_mock_metric_stats(metric_name, hours_back, aggregation_period_minutes)
        
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Convert to protobuf timestamps
            start_timestamp = Timestamp()
            start_timestamp.FromDatetime(start_time)
            
            end_timestamp = Timestamp()
            end_timestamp.FromDatetime(end_time)
            
            # Build time interval
            interval = TimeInterval(
                start_time=start_timestamp,
                end_time=end_timestamp
            )
            
            # Build metric filter - log metrics are stored in Cloud Monitoring
            metric_filter = f'metric.type="logging.googleapis.com/user/{metric_name}"'
            
            # Query the monitoring API
            project_name = f"projects/{self.project_id}"
            
            # Build aggregation
            aggregation = Aggregation(
                alignment_period={"seconds": aggregation_period_minutes * 60},
                per_series_aligner=Aggregation.Aligner.ALIGN_RATE,
                cross_series_reducer=Aggregation.Reducer.REDUCE_SUM
            )
            
            # Execute query
            try:
                results = self._monitoring_client.list_time_series(
                    request={
                        "name": project_name,
                        "filter": metric_filter,
                        "interval": interval,
                        "aggregation": aggregation
                    }
                )
            except Exception as e:
                # If the monitoring query fails, return empty results instead of error
                return {
                    "metric_name": metric_name,
                    "project_id": self.project_id,
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "hours_back": hours_back
                    },
                    "aggregation_period_minutes": aggregation_period_minutes,
                    "statistics": {
                        "total_count": 0,
                        "data_points": 0,
                        "average": 0,
                        "min": 0,
                        "max": 0
                    },
                    "time_series": [],
                    "status": "success",
                    "note": f"No metrics data available: {str(e)}"
                }
            
            # Process results
            time_series_data = []
            total_count = 0
            
            try:
                for series in results:
                    for point in series.points:
                        # Handle different timestamp types from Google Cloud Monitoring
                        try:
                            if hasattr(point.interval.end_time, 'ToDatetime'):
                                timestamp = point.interval.end_time.ToDatetime()
                            else:
                                # Convert from seconds/nanos format
                                timestamp = datetime.utcfromtimestamp(
                                    point.interval.end_time.seconds + point.interval.end_time.nanos / 1e9
                                )
                        except AttributeError:
                            # Fallback if timestamp format is unexpected
                            timestamp = datetime.utcnow()
                        
                        value = point.value.double_value if hasattr(point.value, 'double_value') else point.value.int64_value
                        
                        time_series_data.append({
                            "timestamp": timestamp.isoformat(),
                            "value": value
                        })
                        total_count += value
            except Exception as e:
                # If data processing fails, return empty results
                return {
                    "metric_name": metric_name,
                    "project_id": self.project_id,
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "hours_back": hours_back
                    },
                    "aggregation_period_minutes": aggregation_period_minutes,
                    "statistics": {
                        "total_count": 0,
                        "data_points": 0,
                        "average": 0,
                        "min": 0,
                        "max": 0
                    },
                    "time_series": [],
                    "status": "success",
                    "note": f"Data processing error: {str(e)}"
                }
            
            # Sort by timestamp
            time_series_data.sort(key=lambda x: x["timestamp"])
            
            # Calculate statistics
            values = [point["value"] for point in time_series_data]
            
            stats = {
                "metric_name": metric_name,
                "project_id": self.project_id,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours_back": hours_back
                },
                "aggregation_period_minutes": aggregation_period_minutes,
                "statistics": {
                    "total_count": total_count,
                    "data_points": len(time_series_data),
                    "average": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                },
                "time_series": time_series_data,
                "status": "success"
            }
            
            return stats
            
        except Exception as e:
            return {
                "metric_name": metric_name,
                "project_id": self.project_id,
                "error": str(e),
                "status": "error"
            }

    def _get_mock_metric_stats(
        self, 
        metric_name: str, 
        hours_back: int, 
        aggregation_period_minutes: int
    ) -> Dict[str, Any]:
        """
        Generate mock metric statistics for emulator mode.
        
        Args:
            metric_name: Name of the log metric
            hours_back: How many hours back to look for data
            aggregation_period_minutes: Period for aggregating data points
            
        Returns:
            Mock metric statistics
        """
        import random
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Generate mock time series data
        time_series_data = []
        current_time = start_time
        total_count = 0
        
        while current_time < end_time:
            # Generate realistic counts based on metric type and business hours
            hour = current_time.hour
            if 8 <= hour <= 18:  # Business hours
                base_count = random.randint(5, 20)
            elif 6 <= hour <= 8 or 18 <= hour <= 22:  # Peak transition hours
                base_count = random.randint(2, 10)
            else:  # Night hours
                base_count = random.randint(0, 3)
            
            # Adjust counts based on metric type
            if metric_name == "pipeline_success_metric":
                # Success rate is typically 80-95% of starts
                count = max(0, int(base_count * random.uniform(0.8, 0.95)))
            elif metric_name == "pipeline_failed_metric":
                # Failure rate is typically 5-20% of starts
                count = max(0, int(base_count * random.uniform(0.05, 0.2)))
            else:
                # Default behavior for other metrics (like pipeline_start_metric)
                count = max(0, base_count + random.randint(-2, 5))
            
            time_series_data.append({
                "timestamp": current_time.isoformat(),
                "value": count
            })
            
            total_count += count
            current_time += timedelta(minutes=aggregation_period_minutes)
        
        # Calculate statistics
        values = [point["value"] for point in time_series_data]
        
        return {
            "metric_name": metric_name,
            "project_id": self.project_id,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours_back": hours_back
            },
            "aggregation_period_minutes": aggregation_period_minutes,
            "statistics": {
                "total_count": total_count,
                "data_points": len(time_series_data),
                "average": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0
            },
            "time_series": time_series_data,
            "status": "success",
            "mode": "emulator"
        }

    async def list_available_metrics(self) -> List[Dict[str, Any]]:
        """
        List available log metrics.
        
        Returns:
            List of available metrics
        """
        if self._emulator_mode:
            return [
                {
                    "name": "pipeline_start_metric",
                    "description": "Tracks pipeline execution starts",
                    "filter": 'jsonPayload.event="pipeline_start"',
                    "created": "2024-01-01T00:00:00Z"
                },
                {
                    "name": "pipeline_success_metric",
                    "description": "Tracks successful pipeline completions",
                    "filter": 'jsonPayload.event="pipeline_complete" AND jsonPayload.status="success"',
                    "created": "2024-01-01T00:00:00Z"
                },
                {
                    "name": "pipeline_failed_metric",
                    "description": "Tracks failed pipeline executions",
                    "filter": 'jsonPayload.event="pipeline_complete" AND jsonPayload.status="failed"',
                    "created": "2024-01-01T00:00:00Z"
                },
                {
                    "name": "pipeline_complete_metric", 
                    "description": "Tracks pipeline execution completions",
                    "filter": 'jsonPayload.event="pipeline_complete"',
                    "created": "2024-01-01T00:00:00Z"
                },
                {
                    "name": "error_metric",
                    "description": "Tracks application errors",
                    "filter": 'severity="ERROR"',
                    "created": "2024-01-01T00:00:00Z"
                }
            ]
        
        try:
            project_name = f"projects/{self.project_id}"
            metrics = self._metrics_client.list_log_metrics(parent=project_name)
            
            result = []
            for metric in metrics:
                result.append({
                    "name": metric.name.split('/')[-1],  # Get just the metric name
                    "description": metric.description or "No description",
                    "filter": metric.filter,
                    "created": metric.create_time.isoformat() if metric.create_time else None
                })
            
            return result
            
        except Exception as e:
            return [{
                "error": str(e),
                "status": "error"
            }]

    async def get_metric_definition(self, metric_name: str) -> Dict[str, Any]:
        """
        Get the definition of a specific log metric.
        
        Args:
            metric_name: Name of the log metric
            
        Returns:
            Metric definition details
        """
        if self._emulator_mode:
            metric_definitions = {
                "pipeline_start_metric": {
                    "name": metric_name,
                    "description": "Tracks pipeline execution starts",
                    "filter": 'jsonPayload.event="pipeline_start"',
                    "created": "2024-01-01T00:00:00Z",
                    "mode": "emulator"
                },
                "pipeline_success_metric": {
                    "name": metric_name,
                    "description": "Tracks successful pipeline completions",
                    "filter": 'jsonPayload.event="pipeline_complete" AND jsonPayload.status="success"',
                    "created": "2024-01-01T00:00:00Z",
                    "mode": "emulator"
                },
                "pipeline_failed_metric": {
                    "name": metric_name,
                    "description": "Tracks failed pipeline executions",
                    "filter": 'jsonPayload.event="pipeline_complete" AND jsonPayload.status="failed"',
                    "created": "2024-01-01T00:00:00Z",
                    "mode": "emulator"
                }
            }
            
            if metric_name in metric_definitions:
                return metric_definitions[metric_name]
            else:
                return {
                    "name": metric_name,
                    "error": "Metric not found",
                    "status": "not_found"
                }
        
        try:
            metric_path = f"projects/{self.project_id}/metrics/{metric_name}"
            metric = self._metrics_client.get_log_metric(name=metric_path)
            
            return {
                "name": metric.name.split('/')[-1],
                "description": metric.description or "No description",
                "filter": metric.filter,
                "created": metric.create_time.isoformat() if metric.create_time else None,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "name": metric_name,
                "error": str(e),
                "status": "error"
            }