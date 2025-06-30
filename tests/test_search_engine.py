import os
import types
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

mock_sg = types.ModuleType('PySimpleGUI')
mock_sg.ChangeLookAndFeel = lambda *args, **kwargs: None
mock_sg.change_look_and_feel = lambda *args, **kwargs: None
sys.modules['PySimpleGUI'] = mock_sg
from file_search_engine import SearchEngine

@pytest.fixture
def search_engine(tmp_path):
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    files = [
        dir1 / "alpha.txt",
        dir1 / "alphabet.txt",
        dir2 / "beta.txt",
        dir2 / "gamma.py",
    ]
    for f in files:
        f.write_text("data")

    file_index = []
    for root, _, fs in os.walk(tmp_path):
        if fs:
            file_index.append((str(root), fs))

    engine = SearchEngine()
    engine.file_index = file_index
    yield engine, tmp_path
    if os.path.exists("search_results.txt"):
        os.remove("search_results.txt")

def test_search_contains(search_engine):
    engine, tmp = search_engine
    values = {"TERM": "alpha", "CONTAINS": True, "STARTSWITH": False, "ENDSWITH": False}
    engine.search(values)
    expected = sorted([
        f"{tmp}/dir1/alpha.txt",
        f"{tmp}/dir1/alphabet.txt",
    ])
    assert sorted(engine.results) == expected
    assert engine.matches == 2
    assert engine.records == 4

def test_search_startswith(search_engine):
    engine, tmp = search_engine
    values = {"TERM": "beta", "CONTAINS": False, "STARTSWITH": True, "ENDSWITH": False}
    engine.search(values)
    expected = [f"{tmp}/dir2/beta.txt"]
    assert engine.results == expected
    assert engine.matches == 1
    assert engine.records == 4

def test_search_endswith(search_engine):
    engine, tmp = search_engine
    values = {"TERM": ".py", "CONTAINS": False, "STARTSWITH": False, "ENDSWITH": True}
    engine.search(values)
    expected = [f"{tmp}/dir2/gamma.py"]
    assert engine.results == expected
    assert engine.matches == 1
    assert engine.records == 4


def test_case_sensitive_no_match(search_engine):
    engine, tmp = search_engine
    values = {"TERM": "Alpha.txt", "CONTAINS": True, "STARTSWITH": False, "ENDSWITH": False, "CASE": True}
    engine.search(values)
    assert engine.results == []
    assert engine.matches == 0
    assert engine.records == 4


def test_case_insensitive_match(search_engine):
    engine, tmp = search_engine
    values = {"TERM": "Alpha.txt", "CONTAINS": True, "STARTSWITH": False, "ENDSWITH": False, "CASE": False}
    engine.search(values)
    expected = [f"{tmp}/dir1/alpha.txt"]
    assert engine.results == expected
    assert engine.matches == 1
    assert engine.records == 4
