import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from main import load_config, save_config, create_main_window, create_settings_window


class TestMain(unittest.TestCase):
    """Test cases for main module"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.ini")
    
    @patch('main.configparser.ConfigParser.read')
    def test_load_config(self, mock_read):
        """Test loading configuration."""
        mock_read.return_value = None
        config = load_config()
        
        # Verify that ConfigParser was used
        self.assertIsNotNone(config)
        mock_read.assert_called_once_with('config.ini')
    
    def test_save_config(self):
        """Test saving configuration."""
        # Create test values to save
        test_values = {
            '-FOLDER-': '/test/folder',
            '-AUTO-INDEX-': True,
            '-OPENAI-API-KEY-': 'test_api_key',
            '-LOCAL-MODEL-PATH-': '/path/to/model',
            '-OPENAI-': True,
            '-LOCAL-': False
        }
        
        config_path = os.path.join(self.temp_dir, "test_config.ini")
        
        # Patch the open function to write to our temp file
        with patch('main.open', create=True) as mock_open:
            # Mock the file object returned by open
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            save_config(test_values)
        
        # Verify that open was called
        mock_open.assert_called_once()
    
    @patch('main.sg')
    def test_create_main_window(self, mock_sg):
        """Test creation of main window."""
        # Mock the PySimpleGUI elements
        mock_window = MagicMock()
        mock_sg.Window.return_value = mock_window
        mock_sg.Multiline.return_value = "multiline_element"
        mock_sg.Button.return_value = "button_element"
        mock_sg.Text.return_value = "text_element"
        
        window = create_main_window()
        
        # Verify that the window was created
        mock_sg.Window.assert_called_once()
        self.assertEqual(window, mock_window)
    
    @patch('main.configparser.ConfigParser.get')
    @patch('main.configparser.ConfigParser.getboolean')
    @patch('main.sg')
    def test_create_settings_window(self, mock_sg, mock_getboolean, mock_get):
        """Test creation of settings window."""
        # Mock configuration values
        mock_get.side_effect = [
            '/default/folder',  # folder
            '',  # openai_api_key (fallback)
            '',  # model_path (fallback)
            'openai'  # provider
        ]
        mock_getboolean.return_value = False  # auto_index
        
        # Mock the PySimpleGUI elements
        mock_window = MagicMock()
        mock_sg.Window.return_value = mock_window
        mock_sg.Text.return_value = "text_element"
        mock_sg.Input.return_value = "input_element"
        mock_sg.FolderBrowse.return_value = "folder_browse_element"
        mock_sg.Checkbox.return_value = "checkbox_element"
        mock_sg.Radio.return_value = "radio_element"
        mock_sg.Tab.return_value = "tab_element"
        mock_sg.TabGroup.return_value = "tab_group_element"
        mock_sg.Button.return_value = "button_element"
        
        # Create a mock config object
        mock_config = MagicMock()
        
        window = create_settings_window(mock_config)
        
        # Verify that the window was created
        mock_sg.Window.assert_called_once()
        self.assertEqual(window, mock_window)


if __name__ == '__main__':
    unittest.main()