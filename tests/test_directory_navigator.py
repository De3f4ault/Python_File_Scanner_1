import os
import pytest
from core.directory_navigator import DirectoryNavigator

def test_directory_navigation(tmpdir):
    # Create test directories
    tmpdir.mkdir("dir1")
    tmpdir.mkdir("dir2")
    tmpdir.join("file1.txt").write("test")

    nav = DirectoryNavigator(start_path=str(tmpdir))
    assert nav.current_path == tmpdir

    # Test selection
    nav.select_next()
    nav.enter()
    assert nav.current_path == tmpdir / "dir1"

    # Test going up
    nav.go_up()
    assert nav.current_path == tmpdir
