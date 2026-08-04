import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
from pydantic import BaseModel, Field

from src.utils.base_step import PipelineStep

# Logging Configuration
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class CollectionOutput(BaseModel):
    """Data Contract output for Collection Step."""
    raw_files_directory: str = Field(..., description="Absolute path of the raw files directory")
    file_list: List[str] = Field(default_factory=list, description="List of absolute paths of collected files")


class Collector(PipelineStep):
    """
    Step 1: Collection Module
    Collects raw documents (.pdf, .docx, .html, .txt, .md) from source directories or configs
    and saves them securely to data/raw/.
    """

    DEFAULT_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".html", ".txt", ".md"}

    def __init__(self, config_path: Union[str, Path] = "config/config.yaml") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Loads configuration from YAML file or returns defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    if config and "collection" in config:
                        return config["collection"]
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}. Using defaults.")

        return {
            "source_directory": "data/sample",
            "raw_directory": "data/raw",
            "allowed_extensions": list(self.DEFAULT_ALLOWED_EXTENSIONS),
        }

    def _verify_file_integrity(self, file_path: Path) -> bool:
        """Verifies that the file exists, is non-empty, and is readable."""
        if not file_path.is_file():
            logger.warning(f"File integrity check failed: '{file_path}' is not a valid file.")
            return False
        
        try:
            if file_path.stat().st_size == 0:
                logger.warning(f"File integrity check failed: '{file_path}' is empty (0 bytes).")
                return False
            
            # Attempt to open file to ensure readability
            with open(file_path, "rb") as f:
                f.read(1024)
            return True
        except Exception as e:
            logger.error(f"File integrity check error for '{file_path}': {e}")
            return False

    def execute(self, input_data: Optional[Union[str, Path, Dict[str, Any]]] = None) -> CollectionOutput:
        """
        Executes the file collection process.
        
        :param input_data: Optional custom source directory path or dict config.
        :return: CollectionOutput containing raw files directory and collected file paths.
        """
        logger.info("Starting Collection Step...")

        # Determine source and target directories
        source_dir_str = self.config.get("source_directory", "data/sample")
        raw_dir_str = self.config.get("raw_directory", "data/raw")
        allowed_exts = set(self.config.get("allowed_extensions", self.DEFAULT_ALLOWED_EXTENSIONS))

        if isinstance(input_data, (str, Path)):
            source_dir_str = str(input_data)
        elif isinstance(input_data, dict) and "source_directory" in input_data:
            source_dir_str = input_data["source_directory"]

        source_path = Path(source_dir_str).resolve()
        raw_path = Path(raw_dir_str).resolve()

        # Ensure raw output directory exists
        raw_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Source directory: {source_path}")
        logger.info(f"Target raw directory: {raw_path}")

        collected_files: List[str] = []
        failed_files: List[str] = []

        if not source_path.exists():
            logger.warning(f"Source directory '{source_path}' does not exist.")
            return CollectionOutput(
                raw_files_directory=str(raw_path),
                file_list=[]
            )

        # Collect files matching allowed extensions
        files_to_process = [
            p for p in source_path.rglob("*")
            if p.is_file() and p.suffix.lower() in allowed_exts
        ]

        for src_file in files_to_process:
            if self._verify_file_integrity(src_file):
                dest_file = raw_path / src_file.name
                try:
                    shutil.copy2(src_file, dest_file)
                    collected_files.append(str(dest_file.resolve()))
                    logger.info(f"Successfully collected file: '{src_file.name}' -> '{dest_file.resolve()}'")
                except Exception as e:
                    logger.error(f"Failed to copy file '{src_file}': {e}")
                    failed_files.append(str(src_file))
            else:
                failed_files.append(str(src_file))

        logger.info(
            f"Collection finished. Total collected: {len(collected_files)}, "
            f"Failed/Skipped: {len(failed_files)}"
        )

        return CollectionOutput(
            raw_files_directory=str(raw_path),
            file_list=collected_files
        )
