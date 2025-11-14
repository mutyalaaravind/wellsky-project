import os
from typing import Optional, Dict, Any, List, Union
from google.cloud import monitoring_dashboard_v1
from google.cloud.monitoring_dashboard_v1.types import Dashboard
from google.cloud.monitoring_dashboard_v1.services.dashboards_service import DashboardsServiceClient
from google.cloud.exceptions import NotFound, GoogleCloudError
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from settings import GCP_PROJECT_ID
from util.custom_logger import getLogger
from util.exception import exceptionToMap

LOGGER = getLogger(__name__)

MONITORING_SINGLETON_ENABLE = False

class MonitoringAdapter:
    """Adapter for interacting with Google Cloud Monitoring to manage dashboards."""
    
    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize the Monitoring adapter.
        
        Args:
            project_id: Google Cloud project ID. If None, uses settings value.
        """
        self.project_id = project_id or GCP_PROJECT_ID
        
        # Initialize Monitoring Dashboard client
        self.client = DashboardsServiceClient()
        self.parent = f"projects/{self.project_id}"
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def _run_in_executor(self, func, *args, **kwargs):
        """Run a synchronous function in the thread pool executor."""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    async def create_dashboard(self, 
                             dashboard_config: Dict[str, Any],
                             dashboard_id: Optional[str] = None) -> str:
        """
        Create a new monitoring dashboard.
        
        Args:
            dashboard_config: Dashboard configuration dictionary containing:
                - display_name: Dashboard display name
                - mosaicLayout: Layout configuration with tiles
                - labels: Optional labels dictionary
            dashboard_id: Optional custom dashboard ID. If None, GCP generates one.
            
        Returns:
            The full dashboard resource name (projects/{project}/dashboards/{id})
            
        Raises:
            Exception: If there's an error creating the dashboard
        """
        try:
            extra = {
                "project_id": self.project_id,
                "dashboard_id": dashboard_id,
                "display_name": dashboard_config.get("display_name", "Unknown")
            }
            
            LOGGER.debug(f"Creating monitoring dashboard: {dashboard_config.get('display_name')}", extra=extra)
            
            def _create():
                # Create Dashboard object
                dashboard = Dashboard()
                dashboard.display_name = dashboard_config.get("display_name", "Untitled Dashboard")
                
                # Set mosaic layout if provided
                if "mosaicLayout" in dashboard_config:
                    dashboard.mosaic_layout = dashboard_config["mosaicLayout"]
                elif "gridLayout" in dashboard_config:
                    dashboard.grid_layout = dashboard_config["gridLayout"]
                elif "rowLayout" in dashboard_config:
                    dashboard.row_layout = dashboard_config["rowLayout"]
                elif "columnLayout" in dashboard_config:
                    dashboard.column_layout = dashboard_config["columnLayout"]
                
                # Set labels if provided
                if "labels" in dashboard_config:
                    dashboard.labels = dashboard_config["labels"]
                
                # Set etag if provided (for updates)
                if "etag" in dashboard_config:
                    dashboard.etag = dashboard_config["etag"]
                
                # Create the dashboard
                request = monitoring_dashboard_v1.CreateDashboardRequest(
                    parent=self.parent,
                    dashboard=dashboard
                )
                
                if dashboard_id:
                    request.dashboard_id = dashboard_id
                
                response = self.client.create_dashboard(request=request)
                return response.name
            
            dashboard_name = await self._run_in_executor(_create)
            
            extra["dashboard_name"] = dashboard_name
            LOGGER.info(f"Successfully created monitoring dashboard: {dashboard_name}", extra=extra)
            return dashboard_name
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error creating monitoring dashboard", extra=extra)
            raise Exception(f"Error creating monitoring dashboard: {str(e)}")
    
    async def update_dashboard(self, 
                             dashboard_name: str, 
                             dashboard_config: Dict[str, Any]) -> str:
        """
        Update an existing monitoring dashboard.
        
        Args:
            dashboard_name: Full dashboard resource name (projects/{project}/dashboards/{id})
            dashboard_config: Updated dashboard configuration dictionary
            
        Returns:
            The updated dashboard resource name
            
        Raises:
            Exception: If there's an error updating the dashboard
        """
        try:
            extra = {
                "project_id": self.project_id,
                "dashboard_name": dashboard_name,
                "display_name": dashboard_config.get("display_name", "Unknown")
            }
            
            LOGGER.debug(f"Updating monitoring dashboard: {dashboard_name}", extra=extra)
            
            def _update():
                # Get current dashboard to preserve etag
                current_dashboard = self.client.get_dashboard(name=dashboard_name)
                
                # Create updated Dashboard object
                dashboard = Dashboard()
                dashboard.name = dashboard_name
                dashboard.display_name = dashboard_config.get("display_name", current_dashboard.display_name)
                dashboard.etag = current_dashboard.etag  # Required for updates
                
                # Set layout
                if "mosaicLayout" in dashboard_config:
                    dashboard.mosaic_layout = dashboard_config["mosaicLayout"]
                elif "gridLayout" in dashboard_config:
                    dashboard.grid_layout = dashboard_config["gridLayout"]
                elif "rowLayout" in dashboard_config:
                    dashboard.row_layout = dashboard_config["rowLayout"]
                elif "columnLayout" in dashboard_config:
                    dashboard.column_layout = dashboard_config["columnLayout"]
                else:
                    # Preserve existing layout if none specified
                    if current_dashboard.mosaic_layout:
                        dashboard.mosaic_layout = current_dashboard.mosaic_layout
                    elif current_dashboard.grid_layout:
                        dashboard.grid_layout = current_dashboard.grid_layout
                    elif current_dashboard.row_layout:
                        dashboard.row_layout = current_dashboard.row_layout
                    elif current_dashboard.column_layout:
                        dashboard.column_layout = current_dashboard.column_layout
                
                # Set labels
                if "labels" in dashboard_config:
                    dashboard.labels = dashboard_config["labels"]
                else:
                    dashboard.labels = current_dashboard.labels
                
                # Update the dashboard
                request = monitoring_dashboard_v1.UpdateDashboardRequest(
                    dashboard=dashboard
                )
                
                response = self.client.update_dashboard(request=request)
                return response.name
            
            updated_name = await self._run_in_executor(_update)
            
            LOGGER.info(f"Successfully updated monitoring dashboard: {updated_name}", extra=extra)
            return updated_name
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error updating monitoring dashboard: {dashboard_name}", extra=extra)
            raise Exception(f"Error updating monitoring dashboard '{dashboard_name}': {str(e)}")
    
    async def get_dashboard(self, dashboard_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a monitoring dashboard by name.
        
        Args:
            dashboard_name: Full dashboard resource name (projects/{project}/dashboards/{id})
            
        Returns:
            Dashboard configuration as dictionary, or None if not found
            
        Raises:
            Exception: If there's an error retrieving the dashboard
        """
        try:
            extra = {
                "project_id": self.project_id,
                "dashboard_name": dashboard_name
            }
            
            LOGGER.debug(f"Retrieving monitoring dashboard: {dashboard_name}", extra=extra)
            
            def _get():
                try:
                    request = monitoring_dashboard_v1.GetDashboardRequest(
                        name=dashboard_name
                    )
                    dashboard = self.client.get_dashboard(request=request)
                    
                    # Convert to dictionary
                    dashboard_dict = {
                        "name": dashboard.name,
                        "display_name": dashboard.display_name,
                        "etag": dashboard.etag,
                        "labels": dict(dashboard.labels) if dashboard.labels else {}
                    }
                    
                    # Add layout information
                    if dashboard.mosaic_layout:
                        dashboard_dict["mosaicLayout"] = dashboard.mosaic_layout
                    elif dashboard.grid_layout:
                        dashboard_dict["gridLayout"] = dashboard.grid_layout
                    elif dashboard.row_layout:
                        dashboard_dict["rowLayout"] = dashboard.row_layout
                    elif dashboard.column_layout:
                        dashboard_dict["columnLayout"] = dashboard.column_layout
                    
                    return dashboard_dict
                    
                except NotFound:
                    return None
            
            dashboard_dict = await self._run_in_executor(_get)
            
            if dashboard_dict:
                LOGGER.debug(f"Successfully retrieved monitoring dashboard: {dashboard_name}", extra=extra)
            else:
                LOGGER.debug(f"Monitoring dashboard not found: {dashboard_name}", extra=extra)
            
            return dashboard_dict
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error retrieving monitoring dashboard: {dashboard_name}", extra=extra)
            raise Exception(f"Error retrieving monitoring dashboard '{dashboard_name}': {str(e)}")
    
    async def delete_dashboard(self, dashboard_name: str) -> bool:
        """
        Delete a monitoring dashboard.
        
        Args:
            dashboard_name: Full dashboard resource name (projects/{project}/dashboards/{id})
            
        Returns:
            True if dashboard was deleted, False if not found
            
        Raises:
            Exception: If there's an error deleting the dashboard
        """
        try:
            extra = {
                "project_id": self.project_id,
                "dashboard_name": dashboard_name
            }
            
            LOGGER.debug(f"Deleting monitoring dashboard: {dashboard_name}", extra=extra)
            
            def _delete():
                try:
                    request = monitoring_dashboard_v1.DeleteDashboardRequest(
                        name=dashboard_name
                    )
                    self.client.delete_dashboard(request=request)
                    return True
                except NotFound:
                    return False
            
            success = await self._run_in_executor(_delete)
            
            if success:
                LOGGER.info(f"Successfully deleted monitoring dashboard: {dashboard_name}", extra=extra)
            else:
                LOGGER.debug(f"Monitoring dashboard not found for deletion: {dashboard_name}", extra=extra)
            
            return success
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error deleting monitoring dashboard: {dashboard_name}", extra=extra)
            raise Exception(f"Error deleting monitoring dashboard '{dashboard_name}': {str(e)}")
    
    async def list_dashboards(self, 
                            page_size: Optional[int] = None,
                            page_token: Optional[str] = None) -> Dict[str, Any]:
        """
        List monitoring dashboards in the project.
        
        Args:
            page_size: Maximum number of dashboards to return per page
            page_token: Token for pagination (from previous response)
            
        Returns:
            Dictionary containing:
                - dashboards: List of dashboard dictionaries
                - next_page_token: Token for next page (if any)
            
        Raises:
            Exception: If there's an error listing dashboards
        """
        try:
            extra = {
                "project_id": self.project_id,
                "page_size": page_size,
                "page_token": page_token
            }
            
            LOGGER.debug(f"Listing monitoring dashboards in project: {self.project_id}", extra=extra)
            
            def _list():
                request = monitoring_dashboard_v1.ListDashboardsRequest(
                    parent=self.parent
                )
                
                if page_size:
                    request.page_size = page_size
                if page_token:
                    request.page_token = page_token
                
                response = self.client.list_dashboards(request=request)
                
                dashboards = []
                for dashboard in response.dashboards:
                    dashboard_dict = {
                        "name": dashboard.name,
                        "display_name": dashboard.display_name,
                        "etag": dashboard.etag,
                        "labels": dict(dashboard.labels) if dashboard.labels else {}
                    }
                    
                    # Add basic layout type information
                    if dashboard.mosaic_layout:
                        dashboard_dict["layout_type"] = "mosaic"
                    elif dashboard.grid_layout:
                        dashboard_dict["layout_type"] = "grid"
                    elif dashboard.row_layout:
                        dashboard_dict["layout_type"] = "row"
                    elif dashboard.column_layout:
                        dashboard_dict["layout_type"] = "column"
                    else:
                        dashboard_dict["layout_type"] = "unknown"
                    
                    dashboards.append(dashboard_dict)
                
                return {
                    "dashboards": dashboards,
                    "next_page_token": response.next_page_token
                }
            
            result = await self._run_in_executor(_list)
            
            extra["dashboard_count"] = len(result["dashboards"])
            LOGGER.debug(f"Successfully listed {len(result['dashboards'])} monitoring dashboards", extra=extra)
            return result
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error listing monitoring dashboards", extra=extra)
            raise Exception(f"Error listing monitoring dashboards: {str(e)}")
    
    async def dashboard_exists(self, dashboard_name: str) -> bool:
        """
        Check if a monitoring dashboard exists.
        
        Args:
            dashboard_name: Full dashboard resource name (projects/{project}/dashboards/{id})
            
        Returns:
            True if dashboard exists, False otherwise
            
        Raises:
            Exception: If there's an error checking dashboard existence
        """
        try:
            dashboard = await self.get_dashboard(dashboard_name)
            return dashboard is not None
        except Exception as e:
            # If it's a NotFound error, return False
            if "not found" in str(e).lower():
                return False
            # Re-raise other errors
            raise e
    
    async def create_or_update_dashboard(self, 
                                       dashboard_config: Dict[str, Any],
                                       dashboard_id: Optional[str] = None,
                                       dashboard_name: Optional[str] = None) -> str:
        """
        Create a new dashboard or update an existing one.
        
        Args:
            dashboard_config: Dashboard configuration dictionary
            dashboard_id: Dashboard ID for creation (if creating new)
            dashboard_name: Full dashboard name for update (if updating existing)
            
        Returns:
            The dashboard resource name
            
        Raises:
            Exception: If there's an error creating or updating the dashboard
        """
        try:
            if dashboard_name:
                # Try to update existing dashboard
                exists = await self.dashboard_exists(dashboard_name)
                if exists:
                    return await self.update_dashboard(dashboard_name, dashboard_config)
                else:
                    # Dashboard doesn't exist, extract ID from name and create
                    dashboard_id = dashboard_name.split("/")[-1]
                    return await self.create_dashboard(dashboard_config, dashboard_id)
            else:
                # Create new dashboard
                return await self.create_dashboard(dashboard_config, dashboard_id)
                
        except Exception as e:
            LOGGER.error(f"Error in create_or_update_dashboard: {str(e)}")
            raise Exception(f"Error creating or updating dashboard: {str(e)}")


# Singleton instance for easy access
_monitoring_adapter: Optional[MonitoringAdapter] = None

def get_monitoring_adapter() -> MonitoringAdapter:
    """Get a singleton instance of the MonitoringAdapter."""
    if MONITORING_SINGLETON_ENABLE:
        global _monitoring_adapter
        if _monitoring_adapter is None:
            _monitoring_adapter = MonitoringAdapter()
        return _monitoring_adapter
    else:
        return MonitoringAdapter(project_id=GCP_PROJECT_ID)


# Convenience functions
async def create_dashboard(dashboard_config: Dict[str, Any], dashboard_id: Optional[str] = None) -> str:
    """Convenience function to create a monitoring dashboard."""
    adapter = get_monitoring_adapter()
    return await adapter.create_dashboard(dashboard_config, dashboard_id)


async def update_dashboard(dashboard_name: str, dashboard_config: Dict[str, Any]) -> str:
    """Convenience function to update a monitoring dashboard."""
    adapter = get_monitoring_adapter()
    return await adapter.update_dashboard(dashboard_name, dashboard_config)


async def get_dashboard(dashboard_name: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get a monitoring dashboard."""
    adapter = get_monitoring_adapter()
    return await adapter.get_dashboard(dashboard_name)


async def delete_dashboard(dashboard_name: str) -> bool:
    """Convenience function to delete a monitoring dashboard."""
    adapter = get_monitoring_adapter()
    return await adapter.delete_dashboard(dashboard_name)


async def list_dashboards(page_size: Optional[int] = None, page_token: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to list monitoring dashboards."""
    adapter = get_monitoring_adapter()
    return await adapter.list_dashboards(page_size, page_token)


async def dashboard_exists(dashboard_name: str) -> bool:
    """Convenience function to check if a monitoring dashboard exists."""
    adapter = get_monitoring_adapter()
    return await adapter.dashboard_exists(dashboard_name)


async def create_or_update_dashboard(dashboard_config: Dict[str, Any], 
                                   dashboard_id: Optional[str] = None,
                                   dashboard_name: Optional[str] = None) -> str:
    """Convenience function to create or update a monitoring dashboard."""
    adapter = get_monitoring_adapter()
    return await adapter.create_or_update_dashboard(dashboard_config, dashboard_id, dashboard_name)
