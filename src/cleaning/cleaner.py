from typing import Any
from src.utils.base_step import PipelineStep

class Cleaner(PipelineStep):
    """
    Step 2: Cleaning
    รับผิดชอบในการทำความสะอาด Raw Documents
    """
    def execute(self, input_data: Any) -> Any:
        # TODO:
        # 1. อ่านไฟล์ Raw Documents
        # 2. สกัดข้อความ (Extract Text)
        # 3. กำจัด Noise: ลบ HTML Tags, Header, Footer, Navigation
        # 4. บันทึก Clean Text ลงใน data/clean/
        print("Executing Cleaning Step...")
        return "clean_text_path"
