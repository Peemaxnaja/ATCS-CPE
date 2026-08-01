import logging
import re
import unicodedata
from pathlib import Path
from typing import Any, Optional

import yaml
from pythainlp.util import normalize as thai_normalize_func

from src.normalization.schemas import NormalizationOutput
from src.utils.base_step import PipelineStep

logger = logging.getLogger(__name__)

class Normalizer(PipelineStep):
    """
    Step 3: Normalization
    ปรับและจัดแต่งตัวอักษร รวมถึงโครงสร้างเครื่องหมายและช่องว่างในข้อความให้เป็นมาตรฐานเดียวกัน
    """

    def __init__(self, config_path: str = "config/config.yaml") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning("Failed to load config file %s: %s. Using default settings.", self.config_path, e)
        return {}

    def normalize_text(self, text: str) -> str:
        """
        กระบวนการทำ Normalization:
        1. Unicode Normalization (NFKC)
        2. Thai Text Sanitization (ลบสระลอย สระซ้อน วรรณยุกต์ซ้อน)
        3. Whitespace Normalization
        """
        if not text:
            return ""

        # 1. Unicode Normalization (NFKC)
        unicode_form = self.config.get("normalization", {}).get("unicode_form", "NFKC")
        text = unicodedata.normalize(unicode_form, text)

        # 2. Thai Text Sanitization (PyThaiNLP)
        if self.config.get("normalization", {}).get("thai_normalize", True):
            text = thai_normalize_func(text)

        # 3. Clean spaces & line endings
        # ลบ spaces/tabs ซ้ำซ้อนในแต่ละบรรทัด
        lines = text.splitlines()
        cleaned_lines = []
        for line in lines:
            # แทนที่ spaces ซ้ำซ้อน ด้วยช่องว่างเดียว
            cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
            cleaned_lines.append(cleaned_line)

        # รวมบรรทัดเข้าด้วยกัน โดยไม่สะสมบรรทัดว่างเกิน 2 บรรทัดติดต่อกัน
        result = "\n".join(cleaned_lines)
        result = re.sub(r"\n{3,}", "\n\n", result).strip()

        return result

    def execute(self, input_data: Any = None) -> NormalizationOutput:
        """
        อ่านไฟล์จาก data/clean/ ทำการ normalize แล้วบันทึกลงใน data/normalized/
        """
        logger.info("Executing Normalization Step...")

        clean_dir_cfg = self.config.get("pipeline", {}).get("clean_data_dir", "data/clean")
        norm_dir_cfg = self.config.get("pipeline", {}).get("normalized_data_dir", "data/normalized")

        input_dir = Path(clean_dir_cfg)
        if hasattr(input_data, "clean_files_directory"):
            input_dir = Path(input_data.clean_files_directory)
        elif isinstance(input_data, str) and input_data and Path(input_data).exists():
            input_dir = Path(input_data)

        output_dir = Path(norm_dir_cfg)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not input_dir.exists():
            logger.warning("Input directory %s does not exist. Creating directory.", input_dir)
            input_dir.mkdir(parents=True, exist_ok=True)

        input_files = list(input_dir.glob("*.txt"))
        normalized_files: list[str] = []

        if not input_files:
            logger.info("No .txt files found in %s. Normalization step completed with empty list.", input_dir)
            return NormalizationOutput(
                normalized_files_directory=str(output_dir),
                normalized_file_list=[]
            )

        encoding = self.config.get("normalization", {}).get("encoding", "utf-8")

        for file_path in input_files:
            try:
                with open(file_path, "r", encoding=encoding, errors="replace") as f:
                    content = f.read()

                normalized_content = self.normalize_text(content)

                out_file_path = output_dir / file_path.name
                with open(out_file_path, "w", encoding="utf-8") as f:
                    f.write(normalized_content)

                normalized_files.append(str(out_file_path))
                logger.info("Successfully normalized: %s -> %s", file_path.name, out_file_path)

            except Exception as e:
                logger.error("Error processing file %s: %s", file_path, e)

        output_contract = NormalizationOutput(
            normalized_files_directory=str(output_dir),
            normalized_file_list=normalized_files
        )

        logger.info("Normalization Step completed. Processed %d files.", len(normalized_files))
        return output_contract
