import unittest
import tempfile
import os
import numpy as np
import pickle
from unittest.mock import patch, MagicMock
from indexing import create_index, save_index, load_index


class TestIndexing(unittest.TestCase):
    """Test cases for indexing module"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_folder = os.path.join(self.temp_dir, "test_folder")
        os.makedirs(self.test_folder, exist_ok=True)
        
        # Create a test file
        self.test_file = os.path.join(self.test_folder, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("This is test content for indexing.")
    
    @patch('indexing.get_embeddings')
    @patch('indexing.extract_text')
    def test_create_index(self, mock_extract_text, mock_get_embeddings):
        """Test creating an index."""
        # Mock the extract_text function to return test content
        mock_extract_text.return_value = "This is test content for indexing."
        
        # Mock the embeddings model
        mock_embeddings_model = MagicMock()
        mock_embeddings_model.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_get_embeddings.return_value = mock_embeddings_model
        
        # Mock the get_tags function
        with patch('indexing.get_tags', return_value="test, indexing"):
            index, docs, tags = create_index(self.test_folder, "openai", "fake_api_key")
            
            # Verify the index was created
            self.assertIsNotNone(index)
            self.assertIsNotNone(docs)
            self.assertIsNotNone(tags)
            self.assertEqual(len(docs), 1)
            self.assertIn(["test", "indexing"], tags)
    
    @patch('indexing.get_embeddings')
    @patch('indexing.extract_text')
    def test_create_index_empty_folder(self, mock_extract_text, mock_get_embeddings):
        """Test creating an index with empty folder."""
        empty_folder = os.path.join(self.temp_dir, "empty_folder")
        os.makedirs(empty_folder, exist_ok=True)
        
        # Mock the extract_text function to return None
        mock_extract_text.return_value = None
        mock_embeddings_model = MagicMock()
        mock_get_embeddings.return_value = mock_embeddings_model
        
        with patch('indexing.get_tags', return_value=""):
            index, docs, tags = create_index(empty_folder, "openai", "fake_api_key")
            
            # Verify the result is None, None, None
            self.assertIsNone(index)
            self.assertIsNone(docs)
            self.assertIsNone(tags)
    
    def test_save_and_load_index(self):
        """Test saving and loading an index."""
        # Create a mock FAISS index and documents
        import faiss
        dimension = 3
        index = faiss.IndexFlatL2(dimension)
        embeddings = np.array([[1.0, 2.0, 3.0]], dtype='float32')
        index.add(embeddings)
        
        docs = ["Test document"]
        tags = [["test", "tag"]]
        
        # Save the index
        index_path = os.path.join(self.temp_dir, "test_index.faiss")
        save_index(index, docs, tags, index_path)
        
        # Check that files were created
        self.assertTrue(os.path.exists(index_path))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_index_docs.pkl")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_index_tags.pkl")))
        
        # Load the index
        loaded_index, loaded_docs, loaded_tags = load_index(index_path)
        
        # Verify the loaded data matches the original
        self.assertIsNotNone(loaded_index)
        self.assertEqual(loaded_docs, docs)
        self.assertEqual(loaded_tags, tags)
    
    @patch('faiss.read_index')
    @patch('builtins.open')
    @patch('pickle.load')
    def test_load_index(self, mock_pickle_load, mock_open, mock_read_index):
        """Test loading an index."""
        # Mock the index reading
        mock_faiss_index = MagicMock()
        mock_read_index.return_value = mock_faiss_index
        
        # Mock pickle loading
        mock_pickle_load.side_effect = [
            ["Test document"],
            [["test", "tag"]]
        ]
        
        index_path = "fake_index.faiss"
        loaded_index, loaded_docs, loaded_tags = load_index(index_path)
        
        # Verify the functions were called
        mock_read_index.assert_called_once_with(index_path)
        self.assertEqual(mock_pickle_load.call_count, 2)
        
        # Verify the results
        self.assertEqual(loaded_index, mock_faiss_index)
        self.assertEqual(loaded_docs, ["Test document"])
        self.assertEqual(loaded_tags, [["test", "tag"]])


if __name__ == '__main__':
    unittest.main()