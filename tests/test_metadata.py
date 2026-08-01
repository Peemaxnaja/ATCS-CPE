import json
from pathlib import Path
import pytest

from src.chunking.schemas import ChunkItem, ChunkingOutput
from src.metadata.metadata_enricher import MetadataEnricher
from src.metadata.schemas import EnrichedChunkItem, MetadataOutput

def test_detect_language():
    enricher = MetadataEnricher()
    assert enricher.detect_language("ข้อความภาษาไทยสำหรับทดสอบ") == "th"
    assert enricher.detect_language("This is an English test text.") == "en"
    assert enricher.detect_language("12345 !@#$%") == "th"

def test_enrich_chunk_validation():
    enricher = MetadataEnricher()
    chunk = enricher.enrich_chunk(
        chunk_id="test_doc_c001",
        text="สวัสดีครับ AI LAB Pipeline",
        stem_name="test_doc"
    )

    assert isinstance(chunk, EnrichedChunkItem)
    assert chunk.chunk_id == "test_doc_c001"
    assert chunk.text == "สวัสดีครับ AI LAB Pipeline"
    assert chunk.language == "th"
    assert chunk.filename is not None
    assert chunk.source is not None
    assert chunk.created_at is not None

def test_extract_page_number():
    enricher = MetadataEnricher()
    text_with_page = "เนื้อหาสำคัญ หน้า: 5"
    page = enricher.extract_page_number("doc_c005", text_with_page)
    assert page == 5

    page_from_id = enricher.extract_page_number("doc_c012", "ไม่มีคำว่าหน้า")
    assert page_from_id == 12

def test_metadata_enricher_execute_with_files(tmp_path):
    chunks_dir = tmp_path / "chunks"
    meta_dir = tmp_path / "metadata"
    raw_dir = tmp_path / "raw"
    chunks_dir.mkdir()
    meta_dir.mkdir()
    raw_dir.mkdir()

    raw_file = raw_dir / "sample_doc.txt"
    raw_file.write_text("Raw text file", encoding="utf-8")

    sample_chunks_json = chunks_dir / "sample_doc_chunks.json"
    chunk_data = [
        {"chunk_id": "sample_doc_c001", "text": "ชิ้นส่วนข้อความที่ 1 ภาษาไทย", "token_count": 10},
        {"chunk_id": "sample_doc_c002", "text": "Second chunk text in English", "token_count": 8}
    ]
    sample_chunks_json.write_text(json.dumps(chunk_data, ensure_ascii=False), encoding="utf-8")

    enricher = MetadataEnricher()
    enricher.chunks_dir = chunks_dir
    enricher.metadata_dir = meta_dir
    enricher.raw_dir = raw_dir

    result = enricher.execute()

    assert isinstance(result, MetadataOutput)
    assert len(result.enriched_chunks) == 2

    out_meta_file = meta_dir / "sample_doc_metadata.json"
    assert out_meta_file.exists()

    with open(out_meta_file, "r", encoding="utf-8") as f:
        meta_items = json.load(f)
        assert len(meta_items) == 2
        assert meta_items[0]["chunk_id"] == "sample_doc_c001"
        assert meta_items[0]["language"] == "th"
        assert meta_items[1]["chunk_id"] == "sample_doc_c002"
        assert meta_items[1]["language"] == "en"

def test_metadata_enricher_with_chunking_output_contract(tmp_path):
    meta_dir = tmp_path / "metadata"
    meta_dir.mkdir()

    chunk_output = ChunkingOutput(
        chunks_directory=str(tmp_path / "chunks"),
        chunks_by_file={
            "doc_a.txt": [
                ChunkItem(chunk_id="doc_a_c001", text="ทดสอบระบบ metadata", token_count=15)
            ]
        }
    )

    enricher = MetadataEnricher()
    enricher.chunks_dir = tmp_path / "chunks"
    enricher.metadata_dir = meta_dir

    result = enricher.execute(chunk_output)

    assert isinstance(result, MetadataOutput)
    assert len(result.enriched_chunks) == 1
    assert result.enriched_chunks[0].chunk_id == "doc_a_c001"
    assert (meta_dir / "doc_a_metadata.json").exists()
