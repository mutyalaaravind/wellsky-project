import pytest
import asyncio
import os
from datetime import datetime
from typing import List, Union, Tuple

# Set up required environment variables before importing modules
os.environ.setdefault('VERSION', '1.0.0')
os.environ.setdefault('SERVICE', 'entity-extraction')
os.environ.setdefault('STAGE', 'test')
os.environ.setdefault('DEBUG', 'false')
os.environ.setdefault('CLOUD_PROVIDER', 'gcp')
os.environ.setdefault('GCP_PROJECT_ID', 'test-project')
os.environ.setdefault('GCP_PUBSUB_PROJECT_ID', 'test-project')
os.environ.setdefault('GCS_BUCKET_NAME', 'test-bucket')
os.environ.setdefault('GCP_LOCATION', 'us-central1')
os.environ.setdefault('GCP_LOCATION_2', 'us-central1')
os.environ.setdefault('GCP_LOCATION_3', 'us-central1')
os.environ.setdefault('GCP_MULTI_REGION_FIRESTORE_LOCATON', 'nam5')
os.environ.setdefault('GCP_FIRESTORE_DB', 'default')
os.environ.setdefault('SERVICE_ACCOUNT_EMAIL', 'test@test-project.iam.gserviceaccount.com')
os.environ.setdefault('SELF_API_URL', 'http://localhost:8000')
os.environ.setdefault('SELF_API_URL_2', 'http://localhost:8001')
os.environ.setdefault('PAPERGLASS_API_URL', 'http://localhost:8002')
os.environ.setdefault('PAPERGLASS_INTEGRATION_TOPIC', 'test-topic')

from adapters.llm import StandardPromptAdapter, PromptStats


class TestLLMGenerateContentAsyncIntegration:
    """Integration test suite for StandardPromptAdapter.generate_content_async() method.
    
    These tests require actual Google Cloud credentials and will make real API calls.
    They should be run in an environment with proper authentication set up.
    """

    @pytest.fixture
    def llm_adapter(self):
        """Create a real StandardPromptAdapter instance for integration testing."""
        return StandardPromptAdapter(
            model_name="gemini-1.5-flash-002",
            max_tokens=1024,  # Keep small for testing
            temperature=0.1,
            top_p=0.9
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_simple_text(self, llm_adapter):
        """Test generate_content_async with simple text input."""
        # Arrange
        items = ["What is the capital of France? Please respond with just the city name."]
        
        # Act
        result = await llm_adapter.generate_content_async(items=items)
        
        # Assert
        assert result is not None
        assert len(result) > 0
        assert "Paris" in result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_with_system_prompt(self, llm_adapter):
        """Test generate_content_async with system prompts."""
        # Arrange
        items = ["Extract the medication name from: Patient takes Aspirin 81mg daily."]
        system_prompts = ["You are a medical entity extraction assistant. Return only the medication name."]
        
        # Act
        result = await llm_adapter.generate_content_async(
            items=items,
            system_prompts=system_prompts
        )
        
        # Assert
        assert result is not None
        assert len(result) > 0
        assert "Aspirin" in result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_json_response(self, llm_adapter):
        """Test generate_content_async with JSON response format."""
        # Arrange
        items = ["List three colors in JSON format with a 'colors' array."]
        
        # Act
        result = await llm_adapter.generate_content_async(
            items=items,
            response_mime_type="application/json"
        )
        
        # Assert
        assert result is not None
        assert len(result) > 0
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        assert "colors" in parsed
        assert isinstance(parsed["colors"], list)
        assert len(parsed["colors"]) == 3

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_with_metadata(self, llm_adapter):
        """Test generate_content_async with metadata for tracking."""
        # Arrange
        items = ["What is 2 + 2? Respond with just the number."]
        metadata = {
            "app_id": "test_app",
            "run_id": "test_run_123",
            "step": "math_test",
            "page_number": 1,
            "iteration": 1
        }
        
        # Act
        result = await llm_adapter.generate_content_async(
            items=items,
            metadata=metadata
        )
        
        # Assert
        assert result is not None
        assert "4" in result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_multiple_system_prompts(self, llm_adapter):
        """Test generate_content_async with multiple system prompts."""
        # Arrange
        items = ["Patient information: John Doe, age 45, takes Metformin 500mg twice daily."]
        system_prompts = [
            "You are a medical information extractor.",
            "Focus only on medication information.",
            "Return the medication name and dosage."
        ]
        
        # Act
        result = await llm_adapter.generate_content_async(
            items=items,
            system_prompts=system_prompts
        )
        
        # Assert
        assert result is not None
        assert len(result) > 0
        assert "Metformin" in result
        assert "500mg" in result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_longer_content(self, llm_adapter):
        """Test generate_content_async with longer input content."""
        # Arrange
        long_text = """
        Patient History: John Smith is a 65-year-old male with a history of hypertension and diabetes.
        Current medications include:
        1. Lisinopril 10mg once daily for blood pressure
        2. Metformin 1000mg twice daily for diabetes
        3. Atorvastatin 20mg once daily for cholesterol
        
        Recent lab results show HbA1c of 7.2% and blood pressure readings averaging 135/85.
        Patient reports good medication compliance and no significant side effects.
        """
        
        items = [f"Extract all medication names from the following text: {long_text}"]
        system_prompts = ["You are a medical assistant. List only the medication names, one per line."]
        
        # Act
        result = await llm_adapter.generate_content_async(
            items=items,
            system_prompts=system_prompts
        )
        
        # Assert
        assert result is not None
        assert len(result) > 0
        assert "Lisinopril" in result
        assert "Metformin" in result
        assert "Atorvastatin" in result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_custom_temperature(self, llm_adapter):
        """Test generate_content_async with different temperature settings."""
        # Create adapter with higher temperature for more creative responses
        creative_adapter = StandardPromptAdapter(
            model_name="gemini-1.5-flash-002",
            max_tokens=512,
            temperature=0.8,  # Higher temperature
            top_p=0.9
        )
        
        # Arrange
        items = ["Write a very short creative story about a robot doctor."]
        
        # Act
        result = await creative_adapter.generate_content_async(items=items)
        
        # Assert
        assert result is not None
        assert len(result) > 0
        # Should contain story elements
        assert any(word in result.lower() for word in ["robot", "doctor", "patient", "medical"])

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_streaming_response(self, llm_adapter):
        """Test that streaming responses are properly concatenated."""
        # Arrange
        items = ["Count from 1 to 5, with each number on a new line."]
        
        # Act
        result = await llm_adapter.generate_content_async(items=items)
        
        # Assert
        assert result is not None
        assert len(result) > 0
        # Should contain all numbers
        for i in range(1, 6):
            assert str(i) in result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content_async_performance_timing(self, llm_adapter):
        """Test that the method completes within reasonable time."""
        # Arrange
        items = ["What is the weather like today? Just say 'I cannot check current weather.'"]
        start_time = datetime.now()
        
        # Act
        result = await llm_adapter.generate_content_async(items=items)
        end_time = datetime.now()
        
        # Assert
        assert result is not None
        elapsed_time = (end_time - start_time).total_seconds()
        # Should complete within 30 seconds for a simple query
        assert elapsed_time < 30.0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_extract_json_from_response_integration(self, llm_adapter):
        """Test JSON extraction with real API response."""
        # Arrange
        items = ["Return a JSON object with 'name': 'test' and 'value': 42"]
        
        # Act
        result = await llm_adapter.generate_content_async(
            items=items,
            response_mime_type="application/json"
        )
        
        # Extract JSON using the adapter's method
        parsed_json = StandardPromptAdapter.extract_json_from_response(result)
        
        # Assert
        assert parsed_json is not None
        assert isinstance(parsed_json, dict)
        assert "name" in parsed_json
        assert "value" in parsed_json
        assert parsed_json["name"] == "test"
        assert parsed_json["value"] == 42

    def test_prompt_stats_creation(self):
        """Test PromptStats model creation and validation."""
        # Arrange & Act
        stats = PromptStats(
            model_name="gemini-1.5-flash-002",
            max_output_tokens=1024,
            temperature=0.1,
            top_p=0.9,
            prompt_length=100,
            prompt_tokens=25,
            response_length=200,
            response_tokens=50,
            elapsed_time=1.5,
            has_image=False,
            has_binary_data=False
        )
        
        # Assert
        assert stats.model_name == "gemini-1.5-flash-002"
        assert stats.max_output_tokens == 1024
        assert stats.temperature == 0.1
        assert stats.top_p == 0.9
        assert stats.elapsed_time == 1.5
        assert stats.has_image is False
        assert stats.has_binary_data is False

    def test_adapter_initialization(self):
        """Test StandardPromptAdapter initialization with various settings."""
        # Test with default settings
        adapter1 = StandardPromptAdapter()
        assert adapter1.model_name is not None
        assert adapter1.max_tokens > 0
        assert 0.0 <= adapter1.temperature <= 1.0
        assert 0.0 <= adapter1.top_p <= 1.0
        
        # Test with custom settings
        adapter2 = StandardPromptAdapter(
            model_name="gemini-1.5-pro",
            max_tokens=2048,
            temperature=0.5,
            top_p=0.8,
            response_mime_type="text/plain"
        )
        assert adapter2.model_name == "gemini-1.5-pro"
        assert adapter2.max_tokens == 2048
        assert adapter2.temperature == 0.5
        assert adapter2.top_p == 0.8
        assert adapter2.response_mime_type == "text/plain"


if __name__ == "__main__":
    # Run a simple integration test to verify the structure
    async def run_simple_integration_test():
        """Run a simple integration test to verify the structure."""
        print("Running simple LLM integration test...")
        
        try:
            # Create adapter
            adapter = StandardPromptAdapter(
                model_name="gemini-1.5-flash-002",
                max_tokens=100,
                temperature=0.0
            )
            
            print(f"Created adapter with model: {adapter.model_name}")
            
            # Test simple query (this would require actual credentials)
            # result = await adapter.generate_content_async(["What is 1+1?"])
            # print(f"Result: {result}")
            
            print("Integration test structure is ready!")
            print("Note: Actual API tests require Google Cloud credentials.")
            
        except Exception as e:
            print(f"Error in integration test setup: {e}")
            print("This is expected if Google Cloud credentials are not configured.")

    asyncio.run(run_simple_integration_test())
