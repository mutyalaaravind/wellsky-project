import pytest
from unittest.mock import patch, ANY
from model_metric import Metric
from utils.json import JsonUtil

@pytest.fixture
def clean_tags():
    with patch('model_metric.JsonUtil.clean') as mock_clean:
        mock_clean.side_effect = lambda x: x  # Return input unchanged for testing
        yield mock_clean

def test_send_with_enum_type(clean_tags):
    with patch('model_metric.LOGGER') as mock_logger:
        # Test with enum type
        Metric.send(Metric.MetricType.HEARTBEAT, {"tag1": "value1"})
        mock_logger.info.assert_called_once_with(
            "METRIC::Heartbeat",
            extra={"tag1": "value1"}
        )

def test_send_with_string_type(clean_tags):
    with patch('model_metric.LOGGER') as mock_logger:
        # Test with string type
        Metric.send("TEST_METRIC", {"tag1": "value1"})
        mock_logger.info.assert_called_once_with(
            "METRIC::TEST_METRIC",
            extra={"tag1": "value1"}
        )

def test_send_with_branch(clean_tags):
    with patch('model_metric.LOGGER') as mock_logger:
        # Test with branch
        Metric.send(Metric.MetricType.HEARTBEAT, {"tag1": "value1"}, branch="main")
        mock_logger.info.assert_called_once_with(
            "METRIC::Heartbeat:main",
            extra={"tag1": "value1", "branch": "main"}
        )

def test_send_without_tags(clean_tags):
    with patch('model_metric.LOGGER') as mock_logger:
        # Test without tags
        Metric.send(Metric.MetricType.HEARTBEAT)
        mock_logger.info.assert_called_once_with(
            "METRIC::Heartbeat",
            extra={}
        )

def test_send_with_empty_tags(clean_tags):
    with patch('model_metric.LOGGER') as mock_logger:
        # Test with empty tags
        Metric.send(Metric.MetricType.HEARTBEAT, {})
        mock_logger.info.assert_called_once_with(
            "METRIC::Heartbeat",
            extra={}
        )

def test_all_metric_types():
    # Verify all enum values are accessible and formatted correctly
    assert Metric.MetricType.HEARTBEAT.value == "Heartbeat"
    assert Metric.MetricType.DOCUMENT_CREATED.value == "DOCUMENT::CREATED"
    assert Metric.MetricType.DOCUMENT_PAGE_CREATED.value == "DOCUMENTPAGE::CREATED"
    assert Metric.MetricType.MEDICATIONEXTRACTION_STEP_PREFIX.value == "PIPELINE::MEDICATIONEXTRACTION::"
    assert Metric.MetricType.PIPELINE_CLOUDTASK_PREFIX.value == "PIPELINE::CLOUDTASK::"

def test_metric_type_values():
    # Test enum values directly instead of string conversion
    assert Metric.MetricType.HEARTBEAT.value == "Heartbeat"
    assert Metric.MetricType.DOCUMENT_CREATED.value == "DOCUMENT::CREATED"

def test_custom_metric_type():
    with patch('model_metric.LOGGER') as mock_logger:
        # Test with custom metric type using the prefix
        custom_metric = f"{Metric.MetricType.MEDICATIONEXTRACTION_STEP_PREFIX.value}CUSTOM_STEP"
        Metric.send(custom_metric, {"status": "success"})
        mock_logger.info.assert_called_once_with(
            f"METRIC::{custom_metric}",
            extra={"status": "success"}
        )