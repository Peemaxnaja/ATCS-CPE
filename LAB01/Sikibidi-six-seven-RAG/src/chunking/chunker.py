import json
import logging
from pathlib import Path
from typing import Any, Optional

import tiktoken
import yaml

from src.chunking.schemas import ChunkItem, ChunkingOutput
from src.utils.base_step import PipelineStep

logger = logging.getLogger(__name__)

class Chunker(PipelineStep):
    """
    Step 4: Chunking
    ทำหน้าที่ตัดแบ่งข้อความที่มีขนาดยาว (Standard Text) ให้เป็นชิ้นย่อย (Chunks)
    โดยยังคงเนื้อหาและบริบทที่ครบถ้วนสำหรับ Embedding Model
    """

    def __init__(self, config_path: str = "config/config.yaml") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.tokenizer_name = self.config.get("chunking", {}).get("tokenizer", "cl100k_base")
        self.tokenizer = self._init_tokenizer(self.tokenizer_name)

    def _load_config(self) -> dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning("Failed to load config file %s: %s. Using defaults.", self.config_path, e)
        return {}

    def _init_tokenizer(self, tokenizer_name: str) -> Any:
        try:
            return tiktoken.get_encoding(tokenizer_name)
        except Exception:
            try:
                return tiktoken.encoding_for_model(tokenizer_name)
            except Exception as e:
                logger.warning("Could not initialize tiktoken tokenizer '%s': %s. Falling back to cl100k_base.", tokenizer_name, e)
                return tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """คำนวณจำนวน Token จริงของข้อความ"""
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def chunk_text(
        self,
        text: str,
        filename_stem: str,
        chunk_size: int = 512,
        chunk_overlap: int = 64
    ) -> list[ChunkItem]:
        """
        หั่นข้อความเป็น Chunks ตาม Sliding Window (คิดหน่วยเป็น Token)
        """
        if not text.strip():
            return []

        tokens = self.tokenizer.encode(text)
        total_tokens = len(tokens)

        if total_tokens <= chunk_size:
            chunk_text = self.tokenizer.decode(tokens)
            return [
                ChunkItem(
                    chunk_id=f"{filename_stem}_c001",
                    text=chunk_text,
                    token_count=total_tokens
                )
            ]

        chunks: list[ChunkItem] = []
        step = max(1, chunk_size - chunk_overlap)
        chunk_index = 1

        for i in range(0, total_tokens, step):
            chunk_tokens = tokens[i : i + chunk_size]
            if not chunk_tokens:
                break

            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunk_item = ChunkItem(
                chunk_id=f"{filename_stem}_c{chunk_index:03d}",
                text=chunk_text,
                token_count=len(chunk_tokens)
            )
            chunks.append(chunk_item)
            chunk_index += 1

            if i + chunk_size >= total_tokens:
                break

        return chunks

    def execute(self, input_data: Any = None) -> ChunkingOutput:
        """
        อ่านไฟล์จาก data/normalized/ ตัดแบ่งเป็น Chunks และบันทึกเป็น JSON ลงใน data/chunks/
        """
        logger.info("Executing Chunking Step...")

        norm_dir_cfg = self.config.get("pipeline", {}).get("normalized_data_dir", "data/normalized")
        chunks_dir_cfg = self.config.get("pipeline", {}).get("chunks_data_dir", "data/chunks")

        input_dir = Path(norm_dir_cfg)
        file_list: list[Path] = []

        if hasattr(input_data, "normalized_file_list") and input_data.normalized_file_list:
            file_list = [Path(p) for p in input_data.normalized_file_list if Path(p).exists()]
        elif hasattr(input_data, "normalized_files_directory") and input_data.normalized_files_directory:
            input_dir = Path(input_data.normalized_files_directory)

        if not file_list:
            if input_dir.exists():
                file_list = list(input_dir.glob("*.txt"))
            else:
                logger.warning("Normalized input directory %s does not exist.", input_dir)

        output_dir = Path(chunks_dir_cfg)
        output_dir.mkdir(parents=True, exist_ok=True)

        chunk_size = self.config.get("chunking", {}).get("chunk_size", 512)
        chunk_overlap = self.config.get("chunking", {}).get("chunk_overlap", 64)

        chunks_by_file: dict[str, list[ChunkItem]] = {}

        if not file_list:
            logger.info("No normalized files found to chunk. Returning empty ChunkingOutput.")
            return ChunkingOutput(
                chunks_directory=str(output_dir),
                chunks_by_file={}
            )

        for file_path in file_list:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    text_content = f.read()

                stem = file_path.stem
                file_chunks = self.chunk_text(
                    text=text_content,
                    filename_stem=stem,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )

                chunks_by_file[file_path.name] = file_chunks

                # Write JSON output for each source file
                out_json_path = output_dir / f"{stem}_chunks.json"
                json_data = [chunk.model_dump() for chunk in file_chunks]

                with open(out_json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)

                logger.info(
                    "Successfully chunked '%s': created %d chunks -> %s",
                    file_path.name,
                    len(file_chunks),
                    out_json_path
                )

            except Exception as e:
                logger.error("Error chunking file %s: %s", file_path, e)

        output_contract = ChunkingOutput(
            chunks_directory=str(output_dir),
            chunks_by_file=chunks_by_file
        )

        logger.info("Chunking Step completed. Total files chunked: %d", len(chunks_by_file))
        return output_contract
