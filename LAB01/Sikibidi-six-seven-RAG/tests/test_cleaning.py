import os
import shutil
import tempfile
from pathlib import Path

import pytest
from src.collection.collector import CollectionOutput
from src.cleaning.cleaner import Cleaner, CleaningOutput


@pytest.fixture
def temp_cleaning_env():
    """Creates a temporary workspace with raw files of various types."""
    temp_dir = tempfile.mkdtemp()
    raw_dir = Path(temp_dir) / "raw"
    clean_dir = Path(temp_dir) / "clean"
    raw_dir.mkdir()
    clean_dir.mkdir()

    # 1. TXT File
    txt_path = raw_dir / "doc.txt"
    txt_path.write_text(
        "Header noise\n\nPage 1 of 3\n\nActual plain text content for testing.\n\n\n\nFooter note",
        encoding="utf-8"
    )

    # 2. Markdown File
    md_path = raw_dir / "doc.md"
    md_path.write_text(
        "# Title\n![image](http://example.com/img.png)\n[Link Text](http://example.com)\n\nMarkdown paragraph text.",
        encoding="utf-8"
    )

    # 3. HTML File
    html_path = raw_dir / "doc.html"
    html_path.write_text(
        "<html><head><style>body {color: red;}</style></head>"
        "<body><nav>Menu link</nav><main><h1>Main Heading</h1><p>HTML paragraph text content.</p></main></body></html>",
        encoding="utf-8"
    )

    yield {
        "root": temp_dir,
        "raw": raw_dir,
        "clean": clean_dir,
        "files": [str(txt_path), str(md_path), str(html_path)]
    }

    shutil.rmtree(temp_dir)


def test_cleaner_noise_reduction(temp_cleaning_env):
    cleaner = Cleaner(config_path="non_existent_config.yaml")

    raw_text = "Line 1\n\nPage 2 of 10\n\nLine 2   \n\n\n\n\nLine 3"
    cleaned = cleaner.clean_text(raw_text)

    assert "Page 2 of 10" not in cleaned
    assert "Line 1\nLine 2\nLine 3" in cleaned or "Line 1\n\nLine 2\n\nLine 3" in cleaned
    assert not cleaned.endswith(" ")


def test_cleaner_execute_with_collection_output(temp_cleaning_env):
    clean_dir = temp_cleaning_env["clean"]
    raw_dir = temp_cleaning_env["raw"]
    file_list = temp_cleaning_env["files"]

    collection_output = CollectionOutput(
        raw_files_directory=str(raw_dir),
        file_list=file_list
    )

    cleaner = Cleaner(config_path="non_existent_config.yaml")
    cleaner.config["clean_directory"] = str(clean_dir)
    cleaner.config["raw_directory"] = str(raw_dir)

    result = cleaner.execute(collection_output)

    assert isinstance(result, CleaningOutput)
    assert result.clean_files_directory == str(clean_dir.resolve())
    assert len(result.cleaned_file_list) == 3

    cleaned_names = [Path(p).name for p in result.cleaned_file_list]
    assert "doc.txt" in cleaned_names

    # Check HTML extracted content does not contain script/style/nav
    cleaned_html_txt = (clean_dir / "doc.txt").read_text(encoding="utf-8")
    assert "Main Heading" in cleaned_html_txt or "HTML paragraph text content" in cleaned_html_txt


def test_cleaner_execute_with_empty_input(temp_cleaning_env):
    clean_dir = temp_cleaning_env["clean"]
    raw_dir = temp_cleaning_env["raw"]

    cleaner = Cleaner(config_path="non_existent_config.yaml")
    cleaner.config["clean_directory"] = str(clean_dir)
    cleaner.config["raw_directory"] = str(raw_dir)

    result = cleaner.execute(None)

    assert isinstance(result, CleaningOutput)
    assert len(result.cleaned_file_list) == 3
