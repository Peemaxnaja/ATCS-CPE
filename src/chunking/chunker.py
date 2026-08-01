from typing import Any
from src.utils.base_step import PipelineStep

class Chunker(PipelineStep):
    """
    Step 4: Chunking
    รับผิดชอบในการตัดข้อความออกเป็นส่วนย่อยๆ
    """
    def execute(self, input_data: Any) -> Any:
        # TODO:
        # 1. อ่านไฟล์ Standard Text
        # 2. ตัดข้อความออกเป็นส่วนย่อยๆ (Split by Token)
        # 3. กำหนด chunk_id ให้กับแต่ละ Chunk
        # 4. บันทึกผลลัพธ์เป็นไฟล์ JSON ลงใน data/chunks/
        print("Executing Chunking Step...")
        return "chunks_json_path"
