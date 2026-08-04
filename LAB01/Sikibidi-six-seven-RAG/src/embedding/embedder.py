import json
import logging
import math
from pathlib import Path
from typing import Any, Optional

import yaml

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from src.embedding.schemas import EmbeddedChunkItem, EmbeddingOutput
from src.metadata.schemas import EnrichedChunkItem, MetadataOutput
from src.utils.base_step import PipelineStep

logger = logging.getLogger(__name__)


class Embedder(PipelineStep):
    """
    Step 6: Embedding
    รับผิดชอบการแปลง Text Chunks และ Metadata ให้เป็น Vector Embeddings
    เพื่อนำเข้าสู่ Vector Database (Step 7)
    """

    def __init__(
        self,
        config_path: str = "config/config.yaml",
        model_name: Optional[str] = None,
        use_mock: bool = False
    ) -> None:
        self.config_path = Path(config_path)
        self.config = self._load_config()

        emb_cfg = self.config.get("embedding", {})
        meta_cfg = self.config.get("metadata", {})

        self.metadata_dir = Path(emb_cfg.get("metadata_directory", meta_cfg.get("metadata_directory", "data/metadata")))
        self.embeddings_dir = Path(emb_cfg.get("embeddings_directory", "data/embeddings"))
        
        self.model_name = model_name or emb_cfg.get("model_name", "BAAI/bge-m3")
        self.batch_size = int(emb_cfg.get("batch_size", 16))
        self.device = emb_cfg.get("device", "cpu")
        self.expected_dimension = emb_cfg.get("dimension")
        self.use_mock = use_mock

        self._model = None
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning("Failed to load config file %s: %s. Using defaults.", self.config_path, e)
        return {}

    def _get_model(self) -> Any:
        """Lazy load embedding model"""
        if self._model is not None:
            return self._model

        if self.use_mock or not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.info("Using mock vector generator for embedding execution.")
            self._model = "mock"
            return self._model

        try:
            logger.info("Loading SentenceTransformer model '%s' on %s...", self.model_name, self.device)
            self._model = SentenceTransformer(self.model_name, device=self.device)
            return self._model
        except Exception as e:
            logger.warning("Failed to load model '%s': %s. Falling back to mock generator.", self.model_name, e)
            self._model = "mock"
            return self._model

    def generate_mock_embedding(self, text: str, dimension: int = 384) -> list[float]:
        """สร้าง deterministic mock embedding vector จากข้อความสำหรับ testing/offline fallback"""
        target_dim = self.expected_dimension or dimension
        hash_val = sum(ord(c) for c in text)
        vector = []
        for i in range(target_dim):
            val = math.sin(hash_val + i)
            vector.append(round(val, 6))
        return vector

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        แปลงข้อความรายการหลายตัวเป็น Vector Embeddings โดยการประมวลผลเป็น Batch
        """
        if not texts:
            return []

        model = self._get_model()
        all_embeddings: list[list[float]] = []

        if model == "mock":
            dim = self.expected_dimension or 384
            for text in texts:
                all_embeddings.append(self.generate_mock_embedding(text, dimension=dim))
            return all_embeddings

        # Real SentenceTransformer encoding in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            encoded = model.encode(batch, show_progress_bar=False, convert_to_numpy=True)
            for vec in encoded:
                vec_list = [float(x) for x in vec]
                self.verify_dimension(vec_list)
                all_embeddings.append(vec_list)

        return all_embeddings

    def verify_dimension(self, vector: list[float]) -> bool:
        """ตรวจสอบความถูกต้องของมิติ (Dimension) ของ Vector"""
        if self.expected_dimension is not None:
            if len(vector) != self.expected_dimension:
                raise ValueError(
                    f"Vector dimension mismatch! Expected {self.expected_dimension}, got {len(vector)}"
                )
        return True

    def _extract_chunk_items(self, input_data: Any) -> list[dict[str, Any]]:
        """สกัดข้อมูล chunks ออกมาจาก input_data รูปแบบต่างๆ"""
        raw_items: list[dict[str, Any]] = []

        if isinstance(input_data, MetadataOutput):
            for enriched in input_data.enriched_chunks:
                raw_items.append({
                    "chunk_id": enriched.chunk_id,
                    "text": enriched.text,
                    "metadata": {
                        "source": enriched.source,
                        "filename": enriched.filename,
                        "page": enriched.page,
                        "language": enriched.language,
                        "author": enriched.author,
                        "created_at": enriched.created_at
                    }
                })
        elif isinstance(input_data, list):
            for item in input_data:
                if isinstance(item, EnrichedChunkItem):
                    raw_items.append({
                        "chunk_id": item.chunk_id,
                        "text": item.text,
                        "metadata": {
                            "source": item.source,
                            "filename": item.filename,
                            "page": item.page,
                            "language": item.language,
                            "author": item.author,
                            "created_at": item.created_at
                        }
                    })
                elif isinstance(item, dict):
                    meta = item.get("metadata", item)
                    raw_items.append({
                        "chunk_id": item.get("chunk_id", "unknown"),
                        "text": item.get("text", ""),
                        "metadata": meta
                    })
        elif isinstance(input_data, (str, Path)):
            input_path = Path(input_data)
            if input_path.is_file() and input_path.suffix == ".json":
                with open(input_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for chunk in data:
                            raw_items.append({
                                "chunk_id": chunk.get("chunk_id", ""),
                                "text": chunk.get("text", ""),
                                "metadata": chunk
                            })
        else:
            # Fallback: อ่านไฟล์ metadata JSON ทั้งหมดจาก data/metadata/
            if self.metadata_dir.exists():
                meta_files = list(self.metadata_dir.glob("*_metadata.json"))
                for meta_file in meta_files:
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            chunks = json.load(f)
                            if isinstance(chunks, list):
                                for chunk in chunks:
                                    raw_items.append({
                                        "chunk_id": chunk.get("chunk_id", ""),
                                        "text": chunk.get("text", ""),
                                        "metadata": chunk
                                    })
                    except Exception as e:
                        logger.error("Error reading metadata file %s: %s", meta_file, e)

        return raw_items

    def execute(self, input_data: Any = None) -> EmbeddingOutput:
        """
        หลักการทำงานหลักของ Step 6:
        1. อ่านข้อมูล Chunks & Metadata จาก Input Contract หรือ disk
        2. คำนวณ Vector Embeddings เป็นกลุ่ม (Batch)
        3. สร้าง Pydantic `EmbeddedChunkItem`
        4. บันทึกผลลัพธ์ลงโฟลเดอร์ `data/embeddings/`
        5. คืนค่า Pydantic `EmbeddingOutput` Contract
        """
        logger.info("Executing Embedding Step...")

        items = self._extract_chunk_items(input_data)
        if not items:
            logger.warning("No metadata chunks found to embed.")
            return EmbeddingOutput(
                embeddings_directory=str(self.embeddings_dir),
                embedded_chunks=[]
            )

        texts = [it["text"] for it in items]
        logger.info("Generating embeddings for %d chunk(s)...", len(texts))
        embeddings = self.embed_texts(texts)

        embedded_chunks: list[EmbeddedChunkItem] = []
        chunks_by_filename: dict[str, list[dict[str, Any]]] = {}

        for it, emb in zip(items, embeddings):
            chunk_item = EmbeddedChunkItem(
                chunk_id=it["chunk_id"],
                text=it["text"],
                metadata=it["metadata"],
                embedding=emb
            )
            embedded_chunks.append(chunk_item)

            filename = it["metadata"].get("filename", "default_doc")
            stem = Path(filename).stem
            if stem not in chunks_by_filename:
                chunks_by_filename[stem] = []
            chunks_by_filename[stem].append(chunk_item.model_dump())

        # Save embeddings files to disk
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # Save per-file JSON
        for stem, chunk_list in chunks_by_filename.items():
            out_file = self.embeddings_dir / f"{stem}_embeddings.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(chunk_list, f, ensure_ascii=False, indent=2)
            logger.info("Saved embeddings to %s", out_file)

        # Save consolidated embeddings file
        consolidated_file = self.embeddings_dir / "embeddings_all.json"
        with open(consolidated_file, "w", encoding="utf-8") as f:
            json.dump([item.model_dump() for item in embedded_chunks], f, ensure_ascii=False, indent=2)

        output = EmbeddingOutput(
            embeddings_directory=str(self.embeddings_dir),
            embedded_chunks=embedded_chunks
        )

        logger.info("Embedding Step completed successfully. Processed %d chunks.", len(embedded_chunks))
        return output
