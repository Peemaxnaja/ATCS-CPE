from typing import Any
from src.utils.base_step import PipelineStep

class Collector(PipelineStep):
    """
    Step 1: Collection
    รับผิดชอบในการโหลดข้อมูลจากไฟล์หลายประเภท
    """
    def execute(self, input_data: Any) -> Any:
        # TODO: 
        # 1. โหลดค่า Config เช่น Path ต้นทางของเอกสาร
        # 2. วนลูปอ่านไฟล์จากต้นทาง (รองรับ .pdf, .docx, .html, .txt, .md)
        # 3. บันทึกเป็น Raw Documents ลงในโฟลเดอร์ data/raw/
        print("Executing Collection Step...")
        return "raw_documents_path"
