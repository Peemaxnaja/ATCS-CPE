import os
import shutil
from pathlib import Path

import pytest
from src.normalization.normalizer import Normalizer
from src.normalization.schemas import NormalizationOutput

def test_normalization_text():
    normalizer = Normalizer()
    
    # Test Thai vowel normalization (เเ -> แ), multiple spaces collapsing, and line ending normalization
    raw_thai_text = "การทำ  Normalization    ภาษาไทย  เเละ  ปรับปรุงข้อความ  \n\n\nบรรทัดใหม่  "
    normalized = normalizer.normalize_text(raw_thai_text)
    
    # Check that multiple spaces were collapsed and Thai vowels normalized
    assert "  " not in normalized
    assert "และ" in normalized
    assert "การทำ Normalization ภาษาไทย และ ปรับปรุงข้อความ" in normalized

def test_normalization_execute_with_files(tmp_path):
    clean_dir = tmp_path / "clean"
    norm_dir = tmp_path / "normalized"
    clean_dir.mkdir()
    norm_dir.mkdir()

    # Create sample cleaned text file
    sample_file = clean_dir / "sample_doc.txt"
    sample_content = "สวัสดีครับ   นี่คือ   ข้อความ  ทดสอบ  \n\n\nสระซ้อน  เเละ  ลองทำ"
    sample_file.write_text(sample_content, encoding="utf-8")

    normalizer = Normalizer()
    normalizer.config["pipeline"] = {
        "clean_data_dir": str(clean_dir),
        "normalized_data_dir": str(norm_dir),
    }

    result = normalizer.execute()

    assert isinstance(result, NormalizationOutput)
    assert len(result.normalized_file_list) == 1
    
    out_file = Path(result.normalized_file_list[0])
    assert out_file.exists()
    
    processed_content = out_file.read_text(encoding="utf-8")
    assert "สวัสดีครับ นี่คือ ข้อความ ทดสอบ" in processed_content
    assert "และ" in processed_content
    assert "ลองทำ" in processed_content
