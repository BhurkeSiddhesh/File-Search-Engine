import unittest
from unittest.mock import patch, MagicMock
from llm_integration import get_llm, get_embeddings, summarize, get_tags


class TestLLMIntegration(unittest.TestCase):
    """Test cases for llm_integration module"""

    @patch('llm_integration.OpenAI')
    def test_get_llm_openai_success(self, mock_openai):
        """Test getting OpenAI LLM with valid API key."""
        mock_llm_instance = MagicMock()
        mock_openai.return_value = mock_llm_instance
        
        result = get_llm('openai', api_key='test_api_key')
        
        self.assertEqual(result, mock_llm_instance)
        mock_openai.assert_called_once_with(api_key='test_api_key')
    
    def test_get_llm_openai_missing_api_key(self):
        """Test getting OpenAI LLM without API key raises ValueError."""
        with self.assertRaises(ValueError) as context:
            get_llm('openai', api_key=None)
        
        self.assertIn("API key is required for OpenAI provider", str(context.exception))
    
    @patch('llm_integration.LlamaCpp')
    def test_get_llm_local_success(self, mock_llama):
        """Test getting local LLM with valid model path."""
        mock_llm_instance = MagicMock()
        mock_llama.return_value = mock_llm_instance
        
        result = get_llm('local', model_path='/path/to/model')
        
        self.assertEqual(result, mock_llm_instance)
        mock_llama.assert_called_once_with(model_path='/path/to/model')
    
    def test_get_llm_local_missing_model_path(self):
        """Test getting local LLM without model path raises ValueError."""
        with self.assertRaises(ValueError) as context:
            get_llm('local', model_path=None)
        
        self.assertIn("Model path is required for local provider", str(context.exception))
    
    def test_get_llm_invalid_provider(self):
        """Test getting LLM with invalid provider raises ValueError."""
        with self.assertRaises(ValueError) as context:
            get_llm('invalid_provider')
        
        self.assertIn("Invalid LLM provider", str(context.exception))
    
    @patch('llm_integration.OpenAIEmbeddings')
    def test_get_embeddings_openai_success(self, mock_openai_embeddings):
        """Test getting OpenAI embeddings with valid API key."""
        mock_embeddings_instance = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings_instance
        
        result = get_embeddings('openai', api_key='test_api_key')
        
        self.assertEqual(result, mock_embeddings_instance)
        mock_openai_embeddings.assert_called_once_with(api_key='test_api_key')
    
    def test_get_embeddings_openai_missing_api_key(self):
        """Test getting OpenAI embeddings without API key raises ValueError."""
        with self.assertRaises(ValueError) as context:
            get_embeddings('openai', api_key=None)
        
        self.assertIn("API key is required for OpenAI provider", str(context.exception))
    
    @patch('llm_integration.LlamaCppEmbeddings')
    def test_get_embeddings_local_success(self, mock_llama_embeddings):
        """Test getting local embeddings with valid model path."""
        mock_embeddings_instance = MagicMock()
        mock_llama_embeddings.return_value = mock_embeddings_instance
        
        result = get_embeddings('local', model_path='/path/to/model')
        
        self.assertEqual(result, mock_embeddings_instance)
        mock_llama_embeddings.assert_called_once_with(model_path='/path/to/model')
    
    def test_get_embeddings_local_missing_model_path(self):
        """Test getting local embeddings without model path raises ValueError."""
        with self.assertRaises(ValueError) as context:
            get_embeddings('local', model_path=None)
        
        self.assertIn("Model path is required for local provider", str(context.exception))
    
    def test_get_embeddings_invalid_provider(self):
        """Test getting embeddings with invalid provider raises ValueError."""
        with self.assertRaises(ValueError) as context:
            get_embeddings('invalid_provider')
        
        self.assertIn("Invalid LLM provider", str(context.exception))
    
    @patch('llm_integration.get_llm')
    def test_summarize_success(self, mock_get_llm):
        """Test successful text summarization."""
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "This is a summary"
        mock_get_llm.return_value = mock_llm_instance
        
        text = "Original text to summarize"
        result = summarize(text, 'openai', api_key='test_key')
        
        self.assertEqual(result, "This is a summary")
        mock_get_llm.assert_called_once_with('openai', 'test_key', None)
        mock_llm_instance.assert_called_once_with(
            f"Summarize the following text:\n\n{text}"
        )
    
    @patch('llm_integration.get_llm')
    def test_summarize_none_llm(self, mock_get_llm):
        """Test summarization when LLM is None."""
        mock_get_llm.return_value = None
        
        text = "Original text to summarize"
        result = summarize(text, 'openai', api_key='test_key')
        
        self.assertEqual(result, "Error: Could not summarize text.")
    
    @patch('llm_integration.get_llm')
    def test_get_tags_success(self, mock_get_llm):
        """Test successful tag generation."""
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "tag1, tag2, tag3"
        mock_get_llm.return_value = mock_llm_instance
        
        text = "Text to generate tags for"
        result = get_tags(text, 'openai', api_key='test_key')
        
        self.assertEqual(result, "tag1, tag2, tag3")
        mock_get_llm.assert_called_once_with('openai', 'test_key', None)
        mock_llm_instance.assert_called_once_with(
            f"Generate a list of comma-separated tags for the following text:\n\n{text}"
        )
    
    @patch('llm_integration.get_llm')
    def test_get_tags_none_llm(self, mock_get_llm):
        """Test tag generation when LLM is None."""
        mock_get_llm.return_value = None
        
        text = "Text to generate tags for"
        result = get_tags(text, 'openai', api_key='test_key')
        
        self.assertEqual(result, "Error: Could not generate tags.")


if __name__ == '__main__':
    unittest.main()