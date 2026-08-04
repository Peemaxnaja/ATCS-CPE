import json
from pathlib import Path
import pytest

from src.embedding.embedder import Embedder
from src.embedding.schemas import EmbeddedChunkItem, EmbeddingOutput
from src.metadata.schemas import EnrichedChunkItem, MetadataOutput


def test_embedded_chunk_item_schema():
    chunk = EmbeddedChunkItem(
        chunk_id="doc_a_c001",
        text="สวัสดีครับ LLM Data Pipeline",
        metadata={"source": "data/raw/doc_a.txt", "language": "th"},
        embedding=[0.1, 0.2, 0.3, 0.4]
    )
    assert chunk.chunk_id == "doc_a_c001"
    assert len(chunk.embedding) == 4
    assert chunk.metadata["language"] == "th"


def test_embedding_output_schema():
    chunk = EmbeddedChunkItem(
        chunk_id="doc_a_c001",
        text="Sample text",
        metadata={"filename": "doc_a.txt"},
        embedding=[0.5, 0.6]
    )
    out = EmbeddingOutput(
        embeddings_directory="data/embeddings",
        embedded_chunks=[chunk]
    )
    assert out.embeddings_directory == "data/embeddings"
    assert len(out.embedded_chunks) == 1
    assert out.embedded_chunks[0].chunk_id == "doc_a_c001"


def test_batch_processing():
    embedder = Embedder(use_mock=True)
    embedder.batch_size = 2
    embedder.expected_dimension = 128
    
    texts = ["Text 1", "Text 2", "Text 3", "Text 4", "Text 5"]
    embeddings = embedder.embed_texts(texts)

    assert len(embeddings) == 5
    for vec in embeddings:
        assert len(vec) == 128


def test_dimension_verification():
    embedder = Embedder(use_mock=True)
    embedder.expected_dimension = 4
    
    valid_vector = [0.1, 0.2, 0.3, 0.4]
    assert embedder.verify_dimension(valid_vector) is True

    invalid_vector = [0.1, 0.2, 0.3]
    with pytest.raises(ValueError, match="Vector dimension mismatch"):
        embedder.verify_dimension(invalid_vector)


def test_embedder_execute_with_metadata_output_contract(tmp_path):
    emb_dir = tmp_path / "embeddings"
    meta_dir = tmp_path / "metadata"
    emb_dir.mkdir()
    meta_dir.mkdir()

    input_contract = MetadataOutput(
        metadata_directory=str(meta_dir),
        enriched_chunks=[
            EnrichedChunkItem(
                chunk_id="sample_c001",
                text="เนื้อหาสำหรับการทำ Embedding 1",
                source="data/raw/sample.txt",
                filename="sample.txt",
                page=1,
                language="th",
                author="Tester",
                created_at="2026-08-01T00:00:00Z"
            ),
            EnrichedChunkItem(
                chunk_id="sample_c002",
                text="Embedding module test chunk 2",
                source="data/raw/sample.txt",
                filename="sample.txt",
                page=1,
                language="en",
                author="Tester",
                created_at="2026-08-01T00:00:00Z"
            )
        ]
    )

    embedder = Embedder(use_mock=True)
    embedder.embeddings_dir = emb_dir
    embedder.metadata_dir = meta_dir
    embedder.expected_dimension = 64

    result = embedder.execute(input_contract)

    assert isinstance(result, EmbeddingOutput)
    assert len(result.embedded_chunks) == 2
    assert result.embedded_chunks[0].chunk_id == "sample_c001"
    assert len(result.embedded_chunks[0].embedding) == 64

    out_file = emb_dir / "sample_embeddings.json"
    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        assert len(saved_data) == 2
        assert saved_data[0]["chunk_id"] == "sample_c001"
        assert "embedding" in saved_data[0]


def test_embedder_execute_with_files(tmp_path):
    emb_dir = tmp_path / "embeddings"
    meta_dir = tmp_path / "metadata"
    emb_dir.mkdir()
    meta_dir.mkdir()

    meta_file = meta_dir / "doc_test_metadata.json"
    mock_metadata_json = [
        {
            "chunk_id": "doc_test_c001",
            "text": "ข้อความจากไฟล์ metadata",
            "filename": "doc_test.txt",
            "source": "data/raw/doc_test.txt",
            "language": "th"
        }
    ]
    meta_file.write_text(json.dumps(mock_metadata_json, ensure_ascii=False), encoding="utf-8")

    embedder = Embedder(use_mock=True)
    embedder.embeddings_dir = emb_dir
    embedder.metadata_dir = meta_dir

    result = embedder.execute()

    assert isinstance(result, EmbeddingOutput)
    assert len(result.embedded_chunks) == 1
    assert result.embedded_chunks[0].chunk_id == "doc_test_c001"
    assert (emb_dir / "doc_test_embeddings.json").exists()
