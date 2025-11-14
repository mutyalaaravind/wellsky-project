"""
Cloud Task Adapter for Admin API

This adapter provides functionality to interact with Google Cloud Tasks
including retrieving metrics for specific Cloud Task queues.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from google.cloud import monitoring_v3
from google.cloud import tasks_v2
from google.cloud.exceptions import NotFound
import google.auth

from settings import Settings

logger = logging.getLogger(__name__)


class CloudTaskAdapter:
    """Adapter for interacting with Google Cloud Tasks and retrieving metrics."""
    
    def __init__(self, settings: Settings):
        """
        Initialize the Cloud Task adapter.
        
        Args:
            settings: Application settings containing GCP configuration
        """
        self.settings = settings
        self.project_id = settings.GCP_PROJECT_ID
        self.location = settings.GCP_LOCATION_2  # us-east4
        
        # Initialize clients
        self.tasks_client = tasks_v2.CloudTasksClient()
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{self.project_id}"
        
        logger.info(f"CloudTaskAdapter initialized for project: {self.project_id}")
    
    async def get_queue_metrics(
        self,
        queue_name: str,
        location: Optional[str] = None,
        hours_back: int = 24,
        metric_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive Cloud Task metrics for a specific queue.
        
        Args:
            queue_name: Name of the Cloud Task queue
            location: GCP location (defaults to settings location)
            hours_back: How many hours of metrics to retrieve
            metric_types: Specific metric types to retrieve (None for all)
            
        Returns:
            Dictionary containing Cloud Task metrics and queue information
        """
        location = location or self.location
        
        if metric_types is None:
            metric_types = [
                "cloudtasks.googleapis.com/queue/depth",
                "cloudtasks.googleapis.com/task/attempt_count", 
                "cloudtasks.googleapis.com/api/request_count",
                "cloudtasks.googleapis.com/queue/task_attempt_delays",
                "cloudtasks.googleapis.com/queue/task_attempt_count"
            ]
        
        logger.info(f"Fetching metrics for queue: {queue_name} in location: {location}")
        
        # Get queue information
        queue_info = await self._get_queue_info(queue_name, location)
        
        # Get metrics data
        metrics_data = await self._fetch_metrics_data(
            queue_name, location, hours_back, metric_types
        )
        
        # Calculate summary statistics
        summary = self._calculate_summary(metrics_data)
        
        return {
            "queue_name": queue_name,
            "location": location,
            "time_range": {
                "start": (datetime.utcnow() - timedelta(hours=hours_back)).isoformat(),
                "end": datetime.utcnow().isoformat(),
                "hours_back": hours_back
            },
            "queue_info": queue_info,
            "metrics": metrics_data,
            "summary": summary
        }
    
    async def _get_queue_info(self, queue_name: str, location: str) -> Dict[str, Any]:
        """Get basic information about the Cloud Task queue."""
        try:
            queue_path = self.tasks_client.queue_path(
                self.project_id, location, queue_name
            )
            
            queue = self.tasks_client.get_queue(name=queue_path)
            
            return {
                "name": queue.name,
                "state": queue.state.name,
                "purge_time": queue.purge_time.timestamp() if queue.purge_time else None,
                "rate_limits": {
                    "max_dispatches_per_second": getattr(queue.rate_limits, 'max_dispatches_per_second', None),
                    "max_burst_size": getattr(queue.rate_limits, 'max_burst_size', None),
                    "max_concurrent_dispatches": getattr(queue.rate_limits, 'max_concurrent_dispatches', None)
                } if hasattr(queue, 'rate_limits') else None,
                "retry_config": {
                    "max_attempts": getattr(queue.retry_config, 'max_attempts', None),
                    "max_retry_duration": getattr(queue.retry_config, 'max_retry_duration', None),
                    "min_backoff": getattr(queue.retry_config, 'min_backoff', None),
                    "max_backoff": getattr(queue.retry_config, 'max_backoff', None),
                    "max_doublings": getattr(queue.retry_config, 'max_doublings', None)
                } if hasattr(queue, 'retry_config') else None
            }
            
        except NotFound:
            logger.warning(f"Queue {queue_name} not found in location {location}")
            return {"error": f"Queue {queue_name} not found"}
        except Exception as e:
            logger.error(f"Error getting queue info: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_metrics_data(
        self,
        queue_name: str,
        location: str,
        hours_back: int,
        metric_types: List[str]
    ) -> Dict[str, Any]:
        """Fetch metrics data from Cloud Monitoring."""
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Convert to protocol buffer timestamps
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end_time.timestamp())},
            "start_time": {"seconds": int(start_time.timestamp())}
        })
        
        metrics_data = {}
        
        for metric_type in metric_types:
            try:
                logger.debug(f"Fetching metric: {metric_type}")
                
                # Create filter for the specific queue
                filter_str = (
                    f'resource.type="gce_instance" AND '
                    f'metric.type="{metric_type}" AND '
                    f'resource.labels.queue_id="{queue_name}" AND '
                    f'resource.labels.location="{location}"'
                )
                
                # Alternative filter for Cloud Tasks resource type
                if "cloudtasks" in metric_type:
                    filter_str = (
                        f'resource.type="cloudtasks_queue" AND '
                        f'metric.type="{metric_type}" AND '
                        f'resource.labels.queue_id="{queue_name}" AND '
                        f'resource.labels.location="{location}"'
                    )
                
                # Create the request
                request = monitoring_v3.ListTimeSeriesRequest({
                    "name": self.project_name,
                    "filter": filter_str,
                    "interval": interval,
                    "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
                })
                
                # Execute the request
                results = self.monitoring_client.list_time_series(request=request)
                
                # Process results
                metric_data = []
                for result in results:
                    for point in result.points:
                        metric_data.append({
                            "timestamp": point.interval.end_time.timestamp(),
                            "value": self._extract_point_value(point.value),
                            "labels": dict(result.metric.labels),
                            "resource_labels": dict(result.resource.labels)
                        })
                
                metrics_data[metric_type] = {
                    "data_points": metric_data,
                    "count": len(metric_data),
                    "latest_value": metric_data[0]["value"] if metric_data else None,
                    "unit": self._get_metric_unit(metric_type)
                }
                
                logger.debug(f"Retrieved {len(metric_data)} data points for {metric_type}")
                
            except Exception as e:
                logger.error(f"Error fetching metric {metric_type}: {str(e)}")
                metrics_data[metric_type] = {
                    "error": str(e),
                    "data_points": [],
                    "count": 0,
                    "latest_value": None
                }
        
        return metrics_data
    
    def _extract_point_value(self, value) -> float:
        """Extract numeric value from a monitoring point value."""
        if hasattr(value, 'double_value'):
            return float(value.double_value)
        elif hasattr(value, 'int64_value'):
            return float(value.int64_value)
        elif hasattr(value, 'distribution_value'):
            return float(value.distribution_value.mean)
        else:
            return 0.0
    
    def _get_metric_unit(self, metric_type: str) -> str:
        """Get the unit for a specific metric type."""
        unit_map = {
            "cloudtasks.googleapis.com/queue/depth": "tasks",
            "cloudtasks.googleapis.com/task/attempt_count": "attempts",
            "cloudtasks.googleapis.com/api/request_count": "requests",
            "cloudtasks.googleapis.com/queue/task_attempt_delays": "seconds",
            "cloudtasks.googleapis.com/queue/task_attempt_count": "attempts"
        }
        return unit_map.get(metric_type, "unknown")
    
    def _calculate_summary(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics from metrics data."""
        summary = {}
        
        # Queue depth summary
        depth_data = metrics_data.get("cloudtasks.googleapis.com/queue/depth", {})
        if depth_data.get("data_points"):
            depth_values = [point["value"] for point in depth_data["data_points"] if point["value"] is not None]
            if depth_values:
                summary["queue_depth"] = {
                    "current": depth_data.get("latest_value") or 0.0,
                    "max": max(depth_values),
                    "min": min(depth_values),
                    "avg": sum(depth_values) / len(depth_values)
                }
        
        # Task attempt summary
        attempt_data = metrics_data.get("cloudtasks.googleapis.com/task/attempt_count", {})
        if attempt_data.get("data_points"):
            summary["task_attempts"] = {
                "total_data_points": attempt_data.get("count", 0),
                "latest_value": attempt_data.get("latest_value") or 0.0
            }
        
        # Delay summary
        delay_data = metrics_data.get("cloudtasks.googleapis.com/queue/task_attempt_delays", {})
        if delay_data.get("data_points"):
            delay_values = [point["value"] for point in delay_data["data_points"] if point["value"] is not None]
            if delay_values:
                summary["task_delays"] = {
                    "avg_delay": sum(delay_values) / len(delay_values),
                    "max_delay": max(delay_values),
                    "min_delay": min(delay_values),
                    "total_delays": len(delay_values)
                }
        
        # API request summary
        api_data = metrics_data.get("cloudtasks.googleapis.com/api/request_count", {})
        if api_data.get("data_points"):
            api_values = [point["value"] for point in api_data["data_points"] if point["value"] is not None]
            if api_values:
                summary["api_requests"] = {
                    "total_requests": sum(api_values),
                    "avg_requests": sum(api_values) / len(api_values),
                    "latest_value": api_data.get("latest_value") or 0.0
                }
        
        return summary
    
    async def get_queue_depth(self, queue_name: str, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current queue depth for a specific queue.
        
        Args:
            queue_name: Name of the Cloud Task queue
            location: GCP location (defaults to settings location)
            
        Returns:
            Dictionary with current queue depth information
        """
        location = location or self.location
        
        # Get queue depth from the last hour
        metrics = await self.get_queue_metrics(
            queue_name=queue_name,
            location=location,
            hours_back=1,
            metric_types=["cloudtasks.googleapis.com/queue/depth"]
        )
        
        depth_metric = metrics["metrics"].get("cloudtasks.googleapis.com/queue/depth", {})
        
        return {
            "queue_name": queue_name,
            "location": location,
            "current_depth": depth_metric.get("latest_value") or 0.0,
            "data_points_available": depth_metric.get("count", 0),
            "queue_info": metrics.get("queue_info", {})
        }
    
    async def list_queues(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all Cloud Task queues in the specified location.
        
        Args:
            location: GCP location (defaults to settings location)
            
        Returns:
            List of queue information dictionaries
        """
        location = location or self.location
        
        try:
            parent = self.tasks_client.location_path(self.project_id, location)
            queues = self.tasks_client.list_queues(parent=parent)
            
            queue_list = []
            for queue in queues:
                queue_info = {
                    "name": queue.name.split("/")[-1],  # Extract queue name from full path
                    "full_path": queue.name,
                    "state": queue.state.name,
                    "purge_time": queue.purge_time.timestamp() if queue.purge_time else None
                }
                queue_list.append(queue_info)
            
            logger.info(f"Found {len(queue_list)} queues in location {location}")
            return queue_list
            
        except Exception as e:
            logger.error(f"Error listing queues: {str(e)}")
            return []


# Example usage functions for testing
async def example_get_queue_metrics(queue_name: str = "default"):
    """Example function showing how to get Cloud Task queue metrics."""
    from settings import Settings
    
    settings = Settings()
    adapter = CloudTaskAdapter(settings)
    
    try:
        # Get comprehensive metrics
        metrics = await adapter.get_queue_metrics(
            queue_name=queue_name,
            hours_back=24
        )
        
        print(f"📊 Cloud Task Metrics for {queue_name}")
        print("=" * 50)
        print(f"Queue State: {metrics['queue_info'].get('state', 'Unknown')}")
        print(f"Time Range: {metrics['time_range']['hours_back']} hours")
        
        # Print summary
        summary = metrics.get("summary", {})
        if "queue_depth" in summary:
            depth = summary["queue_depth"]
            print(f"Queue Depth - Current: {depth['current']}, Max: {depth['max']}, Avg: {depth['avg']:.2f}")
        
        if "task_delays" in summary:
            delays = summary["task_delays"]
            print(f"Task Delays - Avg: {delays['avg_delay']:.2f}s, Max: {delays['max_delay']:.2f}s")
        
        # Print metrics availability
        for metric_type, data in metrics["metrics"].items():
            status = "✅" if data.get("count", 0) > 0 else "❌"
            print(f"{status} {metric_type}: {data.get('count', 0)} data points")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error in example: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Example usage
    asyncio.run(example_get_queue_metrics("paperglass-extraction-queue"))