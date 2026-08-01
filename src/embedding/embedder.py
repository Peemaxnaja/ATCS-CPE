from typing import Any
from src.utils.base_step import PipelineStep

class Embedder(PipelineStep):
    """
    Step 6: Embedding
    รับผิดชอบในการแปลง Text เป็น Vector
    """
    def execute(self, input_data: Any) -> Any:
        # TODO:
        # 1. อ่านไฟล์ Chunks + Metadata
        # 2. โหลด Embedding Model ตาม Config
        # 3. ส่ง Text สร้างเป็น Vector
        # 4. บันทึกผลลัพธ์ลงใน data/embeddings/
        print("Executing Embedding Step...")
        return "embeddings_path"
