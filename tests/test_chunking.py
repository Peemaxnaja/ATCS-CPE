import json
from pathlib import Path

import pytest
from src.chunking.chunker import Chunker
from src.chunking.schemas import ChunkItem, ChunkingOutput

def test_chunker_count_tokens():
    chunker = Chunker()
    text = "Hello world! This is a test."
    tokens = chunker.count_tokens(text)
    assert tokens > 0

def test_chunker_single_chunk():
    chunker = Chunker()
    short_text = "Short sentence for testing chunking."
    chunks = chunker.chunk_text(short_text, filename_stem="test_doc", chunk_size=50, chunk_overlap=10)
    
    assert len(chunks) == 1
    assert chunks[0].chunk_id == "test_doc_c001"
    assert chunks[0].text == short_text
    assert chunks[0].token_count == chunker.count_tokens(short_text)

def test_chunker_sliding_window():
    chunker = Chunker()
    # Create long text that exceeds chunk size
    long_text = "คำว่า AI ย่อมาจาก Artificial Intelligence หรือ ปัญญาประดิษฐ์ " * 20
    chunk_size = 30
    chunk_overlap = 10

    chunks = chunker.chunk_text(long_text, filename_stem="long_doc", chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    assert len(chunks) > 1
    assert chunks[0].chunk_id == "long_doc_c001"
    assert chunks[1].chunk_id == "long_doc_c002"
    
    # Check chunk size limits
    for chunk in chunks:
        assert chunk.token_count <= chunk_size

def test_chunker_execute_with_files(tmp_path):
    norm_dir = tmp_path / "normalized"
    chunks_dir = tmp_path / "chunks"
    norm_dir.mkdir()
    chunks_dir.mkdir()

    sample_file = norm_dir / "doc1.txt"
    sample_text = "ระบบ RAG เป็นเทคโนโลยีสำคัญในการค้นหาข้อมูลและตอบคำถามได้อย่างแม่นยำ " * 15
    sample_file.write_text(sample_text, encoding="utf-8")

    chunker = Chunker()
    chunker.config["pipeline"] = {
        "normalized_data_dir": str(norm_dir),
        "chunks_data_dir": str(chunks_dir),
    }
    chunker.config["chunking"] = {
        "chunk_size": 40,
        "chunk_overlap": 10,
        "tokenizer": "cl100k_base",
    }

    result = chunker.execute()

    assert isinstance(result, ChunkingOutput)
    assert "doc1.txt" in result.chunks_by_file
    assert len(result.chunks_by_file["doc1.txt"]) > 0

    json_file = chunks_dir / "doc1_chunks.json"
    assert json_file.exists()

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == len(result.chunks_by_file["doc1.txt"])
        assert data[0]["chunk_id"] == "doc1_c001"
