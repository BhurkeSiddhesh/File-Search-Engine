import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api import app


class TestAPI(unittest.TestCase):
    """Test cases for API module"""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)
    
    @patch('api.load_index')
    @patch('api.create_index')
    @patch('api.save_index')
    @patch('api.search')
    @patch('api.extract_text')
    def test_search_files_endpoint(self, mock_extract_text, mock_search, 
                                   mock_create_index, mock_load_index, mock_save_index):
        """Test the search endpoint."""
        # Mock the index loading to fail (to trigger index creation)
        mock_load_index.side_effect = Exception("Index not found")
        
        # Mock index creation
        mock_created_index = MagicMock()
        mock_create_index.return_value = mock_created_index
        
        # Mock search results
        mock_search.return_value = [("file1.txt", "snippet1"), ("file2.txt", "snippet2")]
        
        # Mock text extraction
        mock_extract_text.return_value = "Sample text content"
        
        # Make a request to the search endpoint
        response = self.client.post("/api/search", json={
            "query": "test query",
            "folder_path": "/test/folder",
            "use_llm": False
        })
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
    
    @patch('api.create_index')
    @patch('api.save_index')
    def test_index_folder_endpoint(self, mock_save_index, mock_create_index):
        """Test the index endpoint."""
        # Mock index creation and saving
        mock_index = MagicMock()
        mock_create_index.return_value = mock_index
        
        # Make a request to the index endpoint
        response = self.client.post("/api/index", params={
            "folder_path": "/test/folder"
        })
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["status"], "success")
        self.assertIn("Folder indexed successfully", response_data["message"])
        
        # Verify that create_index and save_index were called
        mock_create_index.assert_called_once_with("/test/folder")
        mock_save_index.assert_called_once_with(mock_index, "/test/folder")


if __name__ == '__main__':
    unittest.main()