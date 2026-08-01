import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from src.metadata.schemas import EnrichedChunkItem, MetadataOutput
from src.utils.base_step import PipelineStep

logger = logging.getLogger(__name__)

class MetadataEnricher(PipelineStep):
    """
    Step 5: Metadata Enrichment
    ทำหน้าที่สกัดและเพิ่มข้อมูลบริบท (Metadata) ให้กับ Text Chunks เช่น แหล่งที่มา
    ชื่อไฟล์ หน้า ภาษา ผู้เขียน และเวลาสร้าง เพื่อใช้ในการอ้างอิง (Citation)
    """

    def __init__(self, config_path: str = "config/config.yaml") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_config()

        meta_cfg = self.config.get("metadata", {})
        pipeline_cfg = self.config.get("pipeline", {})

        self.chunks_dir = Path(meta_cfg.get("chunks_directory", pipeline_cfg.get("chunks_data_dir", "data/chunks")))
        self.metadata_dir = Path(meta_cfg.get("metadata_directory", pipeline_cfg.get("metadata_data_dir", "data/metadata")))
        self.raw_dir = Path(pipeline_cfg.get("raw_data_dir", "data/raw"))
        self.default_language = meta_cfg.get("default_language", "th")
        self.default_author = meta_cfg.get("default_author", "Pipeline System")

    def _load_config(self) -> dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning("Failed to load config file %s: %s. Using defaults.", self.config_path, e)
        return {}

    def detect_language(self, text: str) -> str:
        """ตรวจจับภาษาเบื้องต้นจากชุดอักขระ (Thai vs English)"""
        if not text:
            return self.default_language
        
        # Check for Thai Unicode characters
        if re.search(r"[\u0e00-\u0e7f]", text):
            return "th"
        # Check for English alphabets
        elif re.search(r"[a-zA-Z]", text):
            return "en"
        return self.default_language

    def extract_page_number(self, chunk_id: str, text: str) -> Optional[int]:
        """ลองสกัดหมายเลขหน้าจาก text หรือ chunk_id (ถ้ามี)"""
        page_match = re.search(r"(?:page|หน้า)\s*[:=]?\s*(\d+)", text, re.IGNORECASE)
        if page_match:
            try:
                return int(page_match.group(1))
            except ValueError:
                pass
        
        chunk_num_match = re.search(r"_c(\d+)$", chunk_id)
        if chunk_num_match:
            try:
                # Approximate page based on chunk index
                return int(chunk_num_match.group(1))
            except ValueError:
                pass
        return None

    def get_source_file_info(self, stem_name: str) -> tuple[str, str, Optional[str]]:
        """
        ค้นหาข้อมูลไฟล์ต้นฉบับใน data/raw/ เพื่อรับ source path, filename และ file timestamp
        """
        matched_raw_file: Optional[Path] = None
        if self.raw_dir.exists():
            for raw_file in self.raw_dir.glob("*"):
                if raw_file.stem.lower() == stem_name.lower():
                    matched_raw_file = raw_file
                    break

        if matched_raw_file and matched_raw_file.exists():
            filename = matched_raw_file.name
            source_path = str(matched_raw_file).replace("\\", "/")
            stat = matched_raw_file.stat()
            created_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        else:
            filename = f"{stem_name}.txt"
            source_path = f"data/raw/{filename}"
            created_at = datetime.now(timezone.utc).isoformat()

        return source_path, filename, created_at

    def enrich_chunk(
        self,
        chunk_id: str,
        text: str,
        stem_name: str,
        page: Optional[int] = None,
        author: Optional[str] = None
    ) -> EnrichedChunkItem:
        """สร้าง EnrichedChunkItem และ Validate ตาม Pydantic Data Contract"""
        source_path, filename, file_created_at = self.get_source_file_info(stem_name)
        lang = self.detect_language(text)
        extracted_page = page if page is not None else self.extract_page_number(chunk_id, text)
        chunk_author = author if author else self.default_author

        return EnrichedChunkItem(
            chunk_id=chunk_id,
            text=text,
            source=source_path,
            filename=filename,
            page=extracted_page,
            language=lang,
            author=chunk_author,
            created_at=file_created_at
        )

    def execute(self, input_data: Any = None) -> MetadataOutput:
        """
        อ่าน Chunks จาก input_data หรือ data/chunks/
        แทรก Metadata และบันทึกผลลัพธ์ลงใน data/metadata/
        """
        logger.info("Executing Metadata Enrichment Step...")

        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        all_enriched_chunks: list[EnrichedChunkItem] = []
        enriched_by_file: dict[str, list[EnrichedChunkItem]] = {}

        # 1. Processing chunks from input_data if provided
        if hasattr(input_data, "chunks_by_file") and input_data.chunks_by_file:
            for file_name, chunk_items in input_data.chunks_by_file.items():
                stem = Path(file_name).stem
                if stem.endswith("_chunks"):
                    stem = stem[:-7]
                file_enriched: list[EnrichedChunkItem] = []
                for item in chunk_items:
                    c_id = getattr(item, "chunk_id", str(item.get("chunk_id", ""))) if isinstance(item, dict) else item.chunk_id
                    c_text = getattr(item, "text", str(item.get("text", ""))) if isinstance(item, dict) else item.text
                    enriched = self.enrich_chunk(chunk_id=c_id, text=c_text, stem_name=stem)
                    file_enriched.append(enriched)
                    all_enriched_chunks.append(enriched)
                enriched_by_file[stem] = file_enriched

        # 2. If no chunks from memory or to supplement disk output, read from data/chunks/
        if self.chunks_dir.exists():
            chunk_files = list(self.chunks_dir.glob("*.json"))
            for c_file in chunk_files:
                stem = c_file.stem
                if stem.endswith("_chunks"):
                    stem = stem[:-7]

                if stem in enriched_by_file:
                    continue

                try:
                    with open(c_file, "r", encoding="utf-8") as f:
                        raw_chunks = json.load(f)

                    if isinstance(raw_chunks, list):
                        file_enriched = []
                        for item in raw_chunks:
                            c_id = item.get("chunk_id", f"{stem}_c000")
                            c_text = item.get("text", "")
                            enriched = self.enrich_chunk(chunk_id=c_id, text=c_text, stem_name=stem)
                            file_enriched.append(enriched)
                            all_enriched_chunks.append(enriched)
                        enriched_by_file[stem] = file_enriched
                except Exception as e:
                    logger.error("Failed to read or parse chunk file %s: %s", c_file, e)

        # 3. Save enriched metadata JSON files to data/metadata/
        for stem, enriched_items in enriched_by_file.items():
            out_json_path = self.metadata_dir / f"{stem}_metadata.json"
            try:
                json_data = [item.model_dump() for item in enriched_items]
                with open(out_json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                logger.info("Saved metadata file: %s (%d enriched items)", out_json_path, len(enriched_items))
            except Exception as e:
                logger.error("Failed to write metadata file %s: %s", out_json_path, e)

        output_contract = MetadataOutput(
            metadata_directory=str(self.metadata_dir).replace("\\", "/"),
            enriched_chunks=all_enriched_chunks
        )

        logger.info(
            "Metadata Enrichment Step finished. Total chunks enriched: %d across %d files.",
            len(all_enriched_chunks),
            len(enriched_by_file)
        )
        return output_contract
