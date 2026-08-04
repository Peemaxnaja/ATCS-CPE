from typing import Any
from src.utils.base_step import PipelineStep

class QAEngine(PipelineStep):
    """
    Step 8: Retrieval + LLM
    รับผิดชอบในการรับคำถาม ค้นหาข้อมูล และส่งให้ LLM ตอบ
    """
    def execute(self, input_data: Any) -> Any:
        # TODO:
        # 1. รับคำถามจากผู้ใช้งาน
        # 2. นำคำถามไปทำ Embedding
        # 3. ค้นหาใน Vector Database (Similarity Search)
        # 4. ดึง Top K
        # 5. สร้าง Prompt ส่งให้ LLM
        # 6. คืนค่าคำตอบพร้อมอ้างอิง
        print("Executing Retrieval + LLM Step...")
        return "Answer + Citation"
