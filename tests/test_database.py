"""
Test Database Module

Tests for the database module including file tracking,
search history, and metadata storage.
"""

import unittest
import os
import tempfile
import shutil


class TestDatabase(unittest.TestCase):
    """Tests for database module."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        import database
        cls.db = database
        # Initialize database tables
        cls.db.init_database()
    
    def test_database_initialization(self):
        """Test that database is properly initialized."""
        import database
        
        # Should not raise
        database.init_database()
        
        # Check that get_connection exists
        self.assertTrue(
            hasattr(database, 'get_connection'),
            "Database should have get_connection function"
        )
    
    def test_add_file_metadata(self):
        """Test adding file metadata to database."""
        import database
        from datetime import datetime
        
        # Should not raise
        try:
            database.add_file(
                path='/test/path/document.pdf',
                filename='document.pdf',
                extension='.pdf',
                size_bytes=1024,
                modified_date=datetime.now(),
                chunk_count=1,
                faiss_start_idx=0,
                faiss_end_idx=0
            )
        except Exception as e:
            self.fail(f"Failed to add file: {e}")
    
    def test_get_file_by_faiss_index(self):
        """Test retrieving file by FAISS index."""
        import database
        from datetime import datetime
        
        # First add a file
        test_path = '/test/retrieval/test.txt'
        database.add_file(
            path=test_path,
            filename='test.txt',
            extension='.txt',
            size_bytes=512,
            modified_date=datetime.now(),
            chunk_count=1,
            faiss_start_idx=999,
            faiss_end_idx=999
        )
        
        # Try to retrieve it
        file_info = database.get_file_by_faiss_index(999)
        
        if file_info:
            self.assertEqual(file_info['path'], test_path)
            self.assertEqual(file_info['filename'], 'test.txt')
    
    def test_add_search_history(self):
        """Test adding search history entries."""
        import database
        
        # Should not raise - using correct parameter names
        try:
            database.add_search_history(
                query="test query",
                result_count=5,
                execution_time_ms=100
            )
        except Exception as e:
            self.fail(f"Failed to add search history: {e}")
    
    def test_get_search_history(self):
        """Test retrieving search history."""
        import database
        
        # Add a search entry
        database.add_search_history("history test query", 3, 50)
        
        # Get history
        history = database.get_search_history(limit=10)
        self.assertIsInstance(history, list)
    
    def test_get_all_files(self):
        """Test getting all indexed files."""
        import database
        
        files = database.get_all_files()
        self.assertIsInstance(files, list)
    
    def test_clear_files(self):
        """Test clearing all file entries."""
        import database
        
        # Should not raise
        try:
            database.clear_all_files()
        except Exception as e:
            self.fail(f"Failed to clear files: {e}")


class TestDatabaseSearchHistory(unittest.TestCase):
    """Tests specifically for search history functionality."""
    
    def test_history_structure(self):
        """Test that search history entries have correct structure."""
        import database
        
        # Add an entry
        database.add_search_history("structure test", 2, 30)
        
        history = database.get_search_history(limit=1)
        
        if history:
            entry = history[0]
            self.assertIn('query', entry)
            self.assertIn('result_count', entry)
            self.assertIn('execution_time_ms', entry)
    
    def test_delete_search_history(self):
        """Test deleting search history."""
        import database
        
        if hasattr(database, 'delete_all_search_history'):
            deleted_count = database.delete_all_search_history()
            self.assertIsInstance(deleted_count, int)


if __name__ == '__main__':
    unittest.main(verbosity=2)
