import os
import pytest
from src.usecases.token_estimation import TokenEstimator


class TestTokenEstimatorIntegration:
    """Integration tests for TokenEstimator class"""
    
    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up environment variables for Vertex AI authentication"""
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'viki-dev-app-wsky'
        os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
        yield
        # Cleanup after tests (optional)
        os.environ.pop('GOOGLE_GENAI_USE_VERTEXAI', None)
        os.environ.pop('GOOGLE_CLOUD_PROJECT', None)
        os.environ.pop('GOOGLE_CLOUD_LOCATION', None)
    
    @pytest.fixture
    def token_estimator(self):
        """Create a TokenEstimator instance for testing"""
        return TokenEstimator()
    
    @pytest.mark.integration
    def test_compute_tokens_with_document_uri(self, token_estimator):
        """
        Test token computation with both text prompt and document URI.
        This is an integration test that makes actual API calls to Google GenAI.
        """
        # Test parameters as specified
        model_id = "gemini-2.5-flash-lite"
        text_prompt = "Extract insurance information from the provided document."
        document_uri = "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/53636f8ead6a4dbf9b5b5e814d76fe79/38bebdec633b11f0ada242004e494300/document.pdf"
        
        # Execute the token computation
        response = token_estimator.compute_tokens(
            model_id=model_id,
            text_prompt=text_prompt,
            document_uri=document_uri
        )
        
        # Assertions
        assert response is not None, "Response should not be None"
        
        # The response should contain token count information
        # Note: The exact structure may vary based on the GenAI API response format
        # Common fields to check for:
        if hasattr(response, 'total_tokens'):
            assert response.total_tokens > 0, "Total tokens should be greater than 0"
        
        if hasattr(response, 'prompt_tokens'):
            assert response.prompt_tokens > 0, "Prompt tokens should be greater than 0"
            
        # Print response for debugging/verification
        print(f"Token estimation response: {response}")

        
        documents_per_minute = 8.5
        total_token_count = response.get('total_token_count', 0)
        token_throughput_per_second_per_gsu = 8070

        print(f"\n=== GSU Calculation Steps ===")
        print(f"Input parameters:")
        print(f"  documents_per_minute: {documents_per_minute}")
        print(f"  total_token_count: {total_token_count}")
        print(f"  token_throughput_per_second_per_gsu: {token_throughput_per_second_per_gsu}")
        
        # Step 1: Calculate total tokens needed per minute
        tokens_per_minute = documents_per_minute * total_token_count
        print(f"\nStep 1: Calculate tokens per minute")
        print(f"  tokens_per_minute = documents_per_minute × total_token_count")
        print(f"  tokens_per_minute = {documents_per_minute} × {total_token_count} = {tokens_per_minute}")
        
        # Step 2: Convert to tokens per second
        tokens_per_second = tokens_per_minute / 60
        print(f"\nStep 2: Convert to tokens per second")
        print(f"  tokens_per_second = tokens_per_minute ÷ 60")
        print(f"  tokens_per_second = {tokens_per_minute} ÷ 60 = {tokens_per_second}")
        
        # Step 3: Calculate required GSUs
        estimated_gsu = tokens_per_second / token_throughput_per_second_per_gsu
        print(f"\nStep 3: Calculate estimated GSUs")
        print(f"  estimated_gsu = tokens_per_second ÷ token_throughput_per_second_per_gsu")
        print(f"  estimated_gsu = {tokens_per_second} ÷ {token_throughput_per_second_per_gsu} = {estimated_gsu}")
        
        print(f"\n=== Final Result ===")
        print(f"Estimated GSUs required: {estimated_gsu}")

        cost_per_gsu = 2400
        estimated_cost = estimated_gsu * cost_per_gsu
        print(f"Estimated monthly cost for {estimated_gsu} GSUs: ${estimated_cost}")
       
    
    
    
    def test_mime_type_inference(self, token_estimator):
        """Test the MIME type inference method"""
        # Test PDF
        pdf_uri = "gs://bucket/document.pdf"
        assert token_estimator._infer_mime_type(pdf_uri) == "application/pdf"
        
        # Test TXT
        txt_uri = "gs://bucket/document.txt"
        assert token_estimator._infer_mime_type(txt_uri) == "text/plain"
        
        # Test DOCX
        docx_uri = "gs://bucket/document.docx"
        assert token_estimator._infer_mime_type(docx_uri) == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # Test JPG
        jpg_uri = "gs://bucket/image.jpg"
        assert token_estimator._infer_mime_type(jpg_uri) == "image/jpeg"
        
        # Test PNG
        png_uri = "gs://bucket/image.png"
        assert token_estimator._infer_mime_type(png_uri) == "image/png"
        
        # Test unknown extension (should default to PDF)
        unknown_uri = "gs://bucket/document.xyz"
        assert token_estimator._infer_mime_type(unknown_uri) == "application/pdf"