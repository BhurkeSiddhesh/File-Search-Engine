import types
import sys
from unittest.mock import MagicMock, patch

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# create a minimal PySimpleGUI stub
mock_sg = types.ModuleType('PySimpleGUI')
mock_sg.change_look_and_feel = lambda *a, **k: None
mock_sg.Text = lambda *a, **k: None
mock_sg.Input = lambda *a, **k: None
mock_sg.Radio = lambda *a, **k: None
mock_sg.FolderBrowse = lambda *a, **k: None
mock_sg.Button = lambda *a, **k: None
mock_sg.Listbox = lambda *a, **k: None
sys.modules['PySimpleGUI'] = mock_sg

import file_search_engine

class DummyWindow:
    def __init__(self):
        self.read = MagicMock(side_effect=[
            ('_RESULTS_', {'_RESULTS_': ['foo']}),
            (None, None),
        ])
    def __getitem__(self, key):
        return MagicMock(update=MagicMock())


def test_open_file_called():
    window = DummyWindow()
    gui = MagicMock()
    gui.window = window
    with patch.object(file_search_engine, 'Gui', return_value=gui), \
         patch.object(file_search_engine.SearchEngine, 'load_existing_index'), \
         patch('file_search_engine.open_file') as mock_open:
        file_search_engine.main()
        mock_open.assert_called_once_with('foo')
