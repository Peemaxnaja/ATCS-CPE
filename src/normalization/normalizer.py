from typing import Any
from src.utils.base_step import PipelineStep

class Normalizer(PipelineStep):
    """
    Step 3: Normalization
    รับผิดชอบในการปรับตัวอักษรและช่องว่างให้เป็นมาตรฐาน
    """
    def execute(self, input_data: Any) -> Any:
        # TODO:
        # 1. อ่านไฟล์ Clean Text
        # 2. แปลง Encoding ให้เป็นมาตรฐาน (UTF-8)
        # 3. ทำ Unicode Normalization
        # 4. บันทึก Standard Text ลงใน data/normalized/
        print("Executing Normalization Step...")
        return "normalized_text_path"
