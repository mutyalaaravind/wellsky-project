import pytest
from unittest.mock import Mock, patch, AsyncMock
from google.cloud.exceptions import NotFound, GoogleCloudError
from google.cloud.monitoring_dashboard_v1.types import Dashboard
from google.cloud.monitoring_dashboard_v1.services.dashboards_service import DashboardsServiceClient
import asyncio

# Import test environment setup first
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

from adapters.monitoring import (
    MonitoringAdapter,
    get_monitoring_adapter,
    create_dashboard,
    update_dashboard,
    get_dashboard,
    delete_dashboard,
    list_dashboards,
    dashboard_exists,
    create_or_update_dashboard
)


class TestMonitoringAdapter:
    """Test cases for MonitoringAdapter class."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock DashboardsServiceClient."""
        with patch('adapters.monitoring.DashboardsServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def adapter(self, mock_client):
        """Create MonitoringAdapter instance with mocked client."""
        return MonitoringAdapter(project_id="test-project")
    
    @pytest.fixture
    def sample_dashboard_config(self):
        """Sample dashboard configuration for testing."""
        return {
            "display_name": "Test Dashboard",
            "mosaicLayout": {
                "tiles": []
            },
            "labels": {
                "environment": "test",
                "team": "engineering"
            }
        }
    
    @pytest.fixture
    def sample_dashboard_response(self):
        """Sample dashboard response from GCP API."""
        dashboard = Dashboard()
        dashboard.name = "projects/test-project/dashboards/test-dashboard-id"
        dashboard.display_name = "Test Dashboard"
        dashboard.etag = "test-etag-123"
        dashboard.labels = {"environment": "test", "team": "engineering"}
        return dashboard
    
    def test_init(self, mock_client):
        """Test MonitoringAdapter initialization."""
        adapter = MonitoringAdapter(project_id="test-project")
        
        assert adapter.project_id == "test-project"
        assert adapter.parent == "projects/test-project"
        assert adapter.client is not None
        assert adapter.executor is not None
    
    def test_init_default_project(self, mock_client):
        """Test MonitoringAdapter initialization with default project from settings."""
        with patch('adapters.monitoring.GCP_PROJECT_ID', 'default-project'):
            adapter = MonitoringAdapter()
            assert adapter.project_id == "default-project"
    
    @pytest.mark.asyncio
    async def test_create_dashboard_success(self, adapter, mock_client, sample_dashboard_config, sample_dashboard_response):
        """Test successful dashboard creation."""
        # Setup mock responses
        mock_client.create_dashboard.return_value = sample_dashboard_response
        mock_client.get_dashboard.return_value = sample_dashboard_response

        # Create request object
        request = Mock()
        request.parent = "projects/test-project"
        request.dashboard_id = "test-dashboard-id"
        request.dashboard = Mock()
        request.dashboard.display_name = "Test Dashboard"
        mock_client.create_dashboard.call_args = ((), {'request': request})
        
        with patch.object(adapter, '_run_in_executor', new_callable=AsyncMock) as mock_executor:
            mock_executor.return_value = sample_dashboard_response.name
            
            result = await adapter.create_dashboard(sample_dashboard_config, "test-dashboard-id")
            
            assert result == sample_dashboard_response.name
            mock_executor.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_dashboard_without_id(self, adapter, mock_client, sample_dashboard_config, sample_dashboard_response):
        """Test dashboard creation without specifying dashboard ID."""
        # Setup mock responses
        mock_client.create_dashboard.return_value = sample_dashboard_response
        mock_client.get_dashboard.return_value = sample_dashboard_response

        # Create request object
        request = Mock()
        request.parent = "projects/test-project"
        request.dashboard = Mock()
        request.dashboard.display_name = "Test Dashboard"
        mock_client.create_dashboard.call_args = ((), {'request': request})
        
        with patch.object(adapter, '_run_in_executor', new_callable=AsyncMock) as mock_executor:
            mock_executor.return_value = sample_dashboard_response.name
            
            result = await adapter.create_dashboard(sample_dashboard_config)
            
            assert result == sample_dashboard_response.name
            mock_executor.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_dashboard_error(self, adapter, mock_client, sample_dashboard_config):
        """Test dashboard creation with error."""
        mock_client.create_dashboard.side_effect = GoogleCloudError("API Error")
        
        with pytest.raises(Exception) as exc_info:
            await adapter.create_dashboard(sample_dashboard_config)
        
        assert "Error creating monitoring dashboard" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_dashboard_invalid_layout(self, adapter, mock_client):
        """Test dashboard creation with invalid layout configuration."""
        invalid_config = {
            "display_name": "Invalid Layout Dashboard",
            "mosaicLayout": {
                "invalid_field": "value"  # Invalid field for MosaicLayout
            }
        }
        
        with pytest.raises(Exception) as exc_info:
            await adapter.create_dashboard(invalid_config)
        
        assert "Error creating monitoring dashboard: Unknown field for MosaicLayout: invalid_field" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_dashboard_missing_layout(self, adapter, mock_client):
        """Test dashboard creation without any layout configuration."""
        invalid_config = {
            "display_name": "No Layout Dashboard"
        }
        
        mock_client.create_dashboard.side_effect = ValueError("Dashboard configuration must include one of: mosaicLayout, gridLayout, rowLayout, columnLayout")
        
        with pytest.raises(Exception) as exc_info:
            await adapter.create_dashboard(invalid_config)
        
        assert "Error creating monitoring dashboard: Dashboard configuration must include one of" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_dashboard_success(self, adapter, mock_client, sample_dashboard_config, sample_dashboard_response):
        """Test successful dashboard update."""
        # Mock get_dashboard call for etag
        mock_client.get_dashboard.return_value = sample_dashboard_response
        mock_client.update_dashboard.return_value = sample_dashboard_response
        
        dashboard_name = "projects/test-project/dashboards/test-dashboard-id"
        result = await adapter.update_dashboard(dashboard_name, sample_dashboard_config)
        
        assert result == dashboard_name
        mock_client.get_dashboard.assert_called_once()
        mock_client.update_dashboard.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_dashboard_not_found(self, adapter, mock_client, sample_dashboard_config):
        """Test dashboard update when dashboard doesn't exist."""
        mock_client.get_dashboard.side_effect = NotFound("Dashboard not found")
        
        dashboard_name = "projects/test-project/dashboards/nonexistent"
        
        with pytest.raises(Exception) as exc_info:
            await adapter.update_dashboard(dashboard_name, sample_dashboard_config)
        
        assert "Error updating monitoring dashboard" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_dashboard_success(self, adapter, mock_client, sample_dashboard_response):
        """Test successful dashboard retrieval."""
        mock_client.get_dashboard.return_value = sample_dashboard_response
        
        dashboard_name = "projects/test-project/dashboards/test-dashboard-id"
        result = await adapter.get_dashboard(dashboard_name)
        
        assert result is not None
        assert result["name"] == dashboard_name
        assert result["display_name"] == "Test Dashboard"
        assert result["etag"] == "test-etag-123"
        assert result["labels"]["environment"] == "test"
    
    @pytest.mark.asyncio
    async def test_get_dashboard_not_found(self, adapter, mock_client):
        """Test dashboard retrieval when dashboard doesn't exist."""
        mock_client.get_dashboard.side_effect = NotFound("Dashboard not found")
        
        dashboard_name = "projects/test-project/dashboards/nonexistent"
        result = await adapter.get_dashboard(dashboard_name)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_dashboard_success(self, adapter, mock_client):
        """Test successful dashboard deletion."""
        mock_client.delete_dashboard.return_value = None
        
        dashboard_name = "projects/test-project/dashboards/test-dashboard-id"
        result = await adapter.delete_dashboard(dashboard_name)
        
        assert result is True
        mock_client.delete_dashboard.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_dashboard_not_found(self, adapter, mock_client):
        """Test dashboard deletion when dashboard doesn't exist."""
        mock_client.delete_dashboard.side_effect = NotFound("Dashboard not found")
        
        dashboard_name = "projects/test-project/dashboards/nonexistent"
        result = await adapter.delete_dashboard(dashboard_name)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_list_dashboards_success(self, adapter, mock_client, sample_dashboard_response):
        """Test successful dashboard listing."""
        mock_response = Mock()
        mock_response.dashboards = [sample_dashboard_response]
        mock_response.next_page_token = "next-token"
        mock_client.list_dashboards.return_value = mock_response
        
        result = await adapter.list_dashboards(page_size=10)
        
        assert "dashboards" in result
        assert "next_page_token" in result
        assert len(result["dashboards"]) == 1
        assert result["dashboards"][0]["name"] == "projects/test-project/dashboards/test-dashboard-id"
        assert result["next_page_token"] == "next-token"
    
    @pytest.mark.asyncio
    async def test_list_dashboards_empty(self, adapter, mock_client):
        """Test dashboard listing with no dashboards."""
        mock_response = Mock()
        mock_response.dashboards = []
        mock_response.next_page_token = ""
        mock_client.list_dashboards.return_value = mock_response
        
        result = await adapter.list_dashboards()
        
        assert result["dashboards"] == []
        assert result["next_page_token"] == ""
    
    @pytest.mark.asyncio
    async def test_dashboard_exists_true(self, adapter, mock_client, sample_dashboard_response):
        """Test dashboard_exists when dashboard exists."""
        mock_client.get_dashboard.return_value = sample_dashboard_response
        
        dashboard_name = "projects/test-project/dashboards/test-dashboard-id"
        result = await adapter.dashboard_exists(dashboard_name)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_dashboard_exists_false(self, adapter, mock_client):
        """Test dashboard_exists when dashboard doesn't exist."""
        mock_client.get_dashboard.side_effect = NotFound("Dashboard not found")
        
        dashboard_name = "projects/test-project/dashboards/nonexistent"
        result = await adapter.dashboard_exists(dashboard_name)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_create_or_update_dashboard_create(self, adapter, mock_client, sample_dashboard_config, sample_dashboard_response):
        """Test create_or_update_dashboard when creating new dashboard."""
        # Setup mock responses
        mock_client.create_dashboard.return_value = sample_dashboard_response
        mock_client.get_dashboard.side_effect = NotFound("Dashboard not found")

        # Create request object
        request = Mock()
        request.parent = "projects/test-project"
        request.dashboard_id = "test-dashboard-id"
        request.dashboard = Mock()
        request.dashboard.display_name = "Test Dashboard"
        mock_client.create_dashboard.call_args = ((), {'request': request})
        
        with patch.object(adapter, '_run_in_executor', new_callable=AsyncMock) as mock_executor:
            mock_executor.return_value = sample_dashboard_response.name
            
            result = await adapter.create_or_update_dashboard(
                sample_dashboard_config,
                dashboard_id="test-dashboard-id"
            )
            
            assert result == sample_dashboard_response.name
            mock_executor.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_or_update_dashboard_update(self, adapter, mock_client, sample_dashboard_config, sample_dashboard_response):
        """Test create_or_update_dashboard when updating existing dashboard."""
        # Mock dashboard exists
        mock_client.get_dashboard.return_value = sample_dashboard_response
        mock_client.update_dashboard.return_value = sample_dashboard_response
        
        with patch.object(adapter, '_run_in_executor', new_callable=AsyncMock) as mock_executor:
            dashboard_name = sample_dashboard_response.name
            mock_executor.return_value = dashboard_name
            
            result = await adapter.create_or_update_dashboard(
                sample_dashboard_config,
                dashboard_name=dashboard_name
            )
            
            assert result == dashboard_name
            mock_executor.assert_called()
    
    @pytest.mark.asyncio
    async def test_create_or_update_dashboard_create_from_name(self, adapter, mock_client, sample_dashboard_config, sample_dashboard_response):
        """Test create_or_update_dashboard when dashboard name provided but doesn't exist."""
        # Setup mock responses
        mock_client.get_dashboard.side_effect = NotFound("Dashboard not found")
        mock_client.create_dashboard.return_value = sample_dashboard_response
        
        with patch.object(adapter, '_run_in_executor', new_callable=AsyncMock) as mock_executor:
            mock_executor.side_effect = [NotFound("Dashboard not found"), sample_dashboard_response.name]
            
            result = await adapter.create_or_update_dashboard(
                sample_dashboard_config,
                dashboard_name="projects/test-project/dashboards/test-dashboard-id"
            )
            
            assert result == sample_dashboard_response.name
            assert mock_executor.call_count == 2  # One for get, one for create


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    @pytest.mark.asyncio
    async def test_create_dashboard_convenience(self):
        """Test create_dashboard convenience function."""
        with patch('adapters.monitoring.get_monitoring_adapter') as mock_get_adapter:
            mock_adapter = Mock()
            mock_adapter.create_dashboard = AsyncMock(return_value="test-result")
            mock_get_adapter.return_value = mock_adapter
            
            config = {"display_name": "Test"}
            result = await create_dashboard(config, "test-id")
            
            assert result == "test-result"
            mock_adapter.create_dashboard.assert_called_once_with(config, "test-id")
    
    @pytest.mark.asyncio
    async def test_update_dashboard_convenience(self):
        """Test update_dashboard convenience function."""
        with patch('adapters.monitoring.get_monitoring_adapter') as mock_get_adapter:
            mock_adapter = Mock()
            mock_adapter.update_dashboard = AsyncMock(return_value="test-result")
            mock_get_adapter.return_value = mock_adapter
            
            name = "projects/test/dashboards/test"
            config = {"display_name": "Updated"}
            result = await update_dashboard(name, config)
            
            assert result == "test-result"
            mock_adapter.update_dashboard.assert_called_once_with(name, config)
    
    @pytest.mark.asyncio
    async def test_get_dashboard_convenience(self):
        """Test get_dashboard convenience function."""
        with patch('adapters.monitoring.get_monitoring_adapter') as mock_get_adapter:
            mock_adapter = Mock()
            mock_adapter.get_dashboard = AsyncMock(return_value={"name": "test"})
            mock_get_adapter.return_value = mock_adapter
            
            name = "projects/test/dashboards/test"
            result = await get_dashboard(name)
            
            assert result == {"name": "test"}
            mock_adapter.get_dashboard.assert_called_once_with(name)
    
    @pytest.mark.asyncio
    async def test_delete_dashboard_convenience(self):
        """Test delete_dashboard convenience function."""
        with patch('adapters.monitoring.get_monitoring_adapter') as mock_get_adapter:
            mock_adapter = Mock()
            mock_adapter.delete_dashboard = AsyncMock(return_value=True)
            mock_get_adapter.return_value = mock_adapter
            
            name = "projects/test/dashboards/test"
            result = await delete_dashboard(name)
            
            assert result is True
            mock_adapter.delete_dashboard.assert_called_once_with(name)
    
    @pytest.mark.asyncio
    async def test_list_dashboards_convenience(self):
        """Test list_dashboards convenience function."""
        with patch('adapters.monitoring.get_monitoring_adapter') as mock_get_adapter:
            mock_adapter = Mock()
            mock_adapter.list_dashboards = AsyncMock(return_value={"dashboards": []})
            mock_get_adapter.return_value = mock_adapter
            
            result = await list_dashboards(page_size=10, page_token="token")
            
            assert result == {"dashboards": []}
            mock_adapter.list_dashboards.assert_called_once_with(10, "token")
    
    @pytest.mark.asyncio
    async def test_dashboard_exists_convenience(self):
        """Test dashboard_exists convenience function."""
        with patch('adapters.monitoring.get_monitoring_adapter') as mock_get_adapter:
            mock_adapter = Mock()
            mock_adapter.dashboard_exists = AsyncMock(return_value=True)
            mock_get_adapter.return_value = mock_adapter
            
            name = "projects/test/dashboards/test"
            result = await dashboard_exists(name)
            
            assert result is True
            mock_adapter.dashboard_exists.assert_called_once_with(name)
    
    @pytest.mark.asyncio
    async def test_create_or_update_dashboard_convenience(self):
        """Test create_or_update_dashboard convenience function."""
        with patch('adapters.monitoring.get_monitoring_adapter') as mock_get_adapter:
            mock_adapter = Mock()
            mock_adapter.create_or_update_dashboard = AsyncMock(return_value="test-result")
            mock_get_adapter.return_value = mock_adapter
            
            config = {"display_name": "Test"}
            result = await create_or_update_dashboard(config, "test-id", "test-name")
            
            assert result == "test-result"
            mock_adapter.create_or_update_dashboard.assert_called_once_with(config, "test-id", "test-name")


class TestGetMonitoringAdapter:
    """Test cases for get_monitoring_adapter function."""
    
    def test_get_monitoring_adapter_singleton_disabled(self):
        """Test get_monitoring_adapter when singleton is disabled."""
        with patch('adapters.monitoring.MONITORING_SINGLETON_ENABLE', False):
            with patch('adapters.monitoring.GCP_PROJECT_ID', 'test-project'):
                adapter1 = get_monitoring_adapter()
                adapter2 = get_monitoring_adapter()
                
                # Should create new instances each time
                assert adapter1 is not adapter2
                assert adapter1.project_id == 'test-project'
                assert adapter2.project_id == 'test-project'
    
    def test_get_monitoring_adapter_singleton_enabled(self):
        """Test get_monitoring_adapter when singleton is enabled."""
        with patch('adapters.monitoring.MONITORING_SINGLETON_ENABLE', True):
            with patch('adapters.monitoring._monitoring_adapter', None):
                adapter1 = get_monitoring_adapter()
                adapter2 = get_monitoring_adapter()
                
                # Should return same instance
                assert adapter1 is adapter2


class TestDashboardLayoutTypes:
    """Test cases for different dashboard layout types."""
    
    @pytest.fixture
    def adapter(self):
        """Create MonitoringAdapter instance with mocked client."""
        with patch('adapters.monitoring.DashboardsServiceClient'):
            return MonitoringAdapter(project_id="test-project")
    
    @pytest.mark.asyncio
    async def test_create_dashboard_with_grid_layout(self, adapter):
        """Test dashboard creation with grid layout."""
        mock_dashboard = Mock()
        mock_dashboard.name = "projects/test-project/dashboards/test"
        adapter.client.create_dashboard.return_value = mock_dashboard
        
        config = {
            "display_name": "Grid Dashboard",
            "gridLayout": {"widgets": []}
        }
        
        with patch.object(adapter, '_run_in_executor', new_callable=AsyncMock) as mock_executor:
            mock_executor.return_value = "projects/test-project/dashboards/test"
            result = await adapter.create_dashboard(config)
            assert result == "projects/test-project/dashboards/test"
    
    @pytest.mark.asyncio
    async def test_create_dashboard_with_row_layout(self, adapter):
        """Test dashboard creation with row layout."""
        mock_dashboard = Mock()
        mock_dashboard.name = "projects/test-project/dashboards/test"
        adapter.client.create_dashboard.return_value = mock_dashboard
        
        config = {
            "display_name": "Row Dashboard",
            "rowLayout": {"rows": []}
        }
        
        with patch.object(adapter, '_run_in_executor', new_callable=AsyncMock) as mock_executor:
            mock_executor.return_value = "projects/test-project/dashboards/test"
            result = await adapter.create_dashboard(config)
            assert result == "projects/test-project/dashboards/test"
    
    @pytest.mark.asyncio
    async def test_create_dashboard_with_column_layout(self, adapter):
        """Test dashboard creation with column layout."""
        mock_dashboard = Mock()
        mock_dashboard.name = "projects/test-project/dashboards/test"
        adapter.client.create_dashboard.return_value = mock_dashboard
        
        config = {
            "display_name": "Column Dashboard",
            "columnLayout": {"columns": []}
        }
        
        with patch.object(adapter, '_run_in_executor', new_callable=AsyncMock) as mock_executor:
            mock_executor.return_value = "projects/test-project/dashboards/test"
            result = await adapter.create_dashboard(config)
            assert result == "projects/test-project/dashboards/test"
            mock_executor.assert_called_once()
            mock_executor.side_effect = lambda f, *args, **kwargs: f(*args, **kwargs)
            mock_dashboard = Mock()
            mock_dashboard.name = "projects/test-project/dashboards/test"
            adapter.client.create_dashboard.return_value = mock_dashboard
            
            config = {
                "display_name": "Column Dashboard",
                "columnLayout": {"columns": []}
            }
            
            result = await adapter.create_dashboard(config)
            assert result == "projects/test-project/dashboards/test"
