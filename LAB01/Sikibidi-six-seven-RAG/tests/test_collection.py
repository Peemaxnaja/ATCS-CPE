import os
import shutil
import tempfile
from pathlib import Path

import pytest
from src.collection.collector import Collector, CollectionOutput


@pytest.fixture
def temp_environment():
    """Creates a temporary workspace directory with sample files and raw output directory."""
    temp_dir = tempfile.mkdtemp()
    source_dir = Path(temp_dir) / "source"
    raw_dir = Path(temp_dir) / "raw"
    source_dir.mkdir()
    raw_dir.mkdir()

    # Create valid sample files
    (source_dir / "valid_doc.txt").write_text("Hello World Content", encoding="utf-8")
    (source_dir / "valid_doc.md").write_text("# Markdown Title\nContent here.", encoding="utf-8")
    (source_dir / "valid_doc.html").write_text("<html><body><p>HTML</p></body></html>", encoding="utf-8")

    # Create invalid (empty) file
    (source_dir / "empty_doc.txt").write_text("", encoding="utf-8")

    # Create unsupported file format
    (source_dir / "ignored_file.exe").write_bytes(b"\x00\x01\x02")

    yield {
        "root": temp_dir,
        "source": source_dir,
        "raw": raw_dir,
    }

    shutil.rmtree(temp_dir)


def test_collector_execution(temp_environment):
    source_path = temp_environment["source"]
    raw_path = temp_environment["raw"]

    collector = Collector(config_path="non_existent_config.yaml")

    input_data = {
        "source_directory": str(source_path),
        "raw_directory": str(raw_path),
    }

    # Override config for testing
    collector.config["source_directory"] = str(source_path)
    collector.config["raw_directory"] = str(raw_path)

    result = collector.execute(input_data)

    assert isinstance(result, CollectionOutput)
    assert result.raw_files_directory == str(raw_path.resolve())

    # Should collect valid_doc.txt, valid_doc.md, valid_doc.html (3 files)
    # Should skip empty_doc.txt and ignored_file.exe
    assert len(result.file_list) == 3

    collected_filenames = [Path(p).name for p in result.file_list]
    assert "valid_doc.txt" in collected_filenames
    assert "valid_doc.md" in collected_filenames
    assert "valid_doc.html" in collected_filenames
    assert "empty_doc.txt" not in collected_filenames
    assert "ignored_file.exe" not in collected_filenames


def test_collector_missing_source_directory(temp_environment):
    raw_path = temp_environment["raw"]
    non_existent_source = Path(temp_environment["root"]) / "does_not_exist"

    collector = Collector(config_path="non_existent_config.yaml")
    collector.config["source_directory"] = str(non_existent_source)
    collector.config["raw_directory"] = str(raw_path)

    result = collector.execute()

    assert isinstance(result, CollectionOutput)
    assert len(result.file_list) == 0


def test_collector_integrity_check(temp_environment):
    collector = Collector(config_path="non_existent_config.yaml")
    source_dir = temp_environment["source"]

    valid_file = source_dir / "valid_doc.txt"
    empty_file = source_dir / "empty_doc.txt"
    non_file = source_dir / "dir_item"
    non_file.mkdir()

    assert collector._verify_file_integrity(valid_file) is True
    assert collector._verify_file_integrity(empty_file) is False
    assert collector._verify_file_integrity(non_file) is False
