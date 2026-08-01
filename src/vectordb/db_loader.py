from typing import Any
from src.utils.base_step import PipelineStep

class DBLoader(PipelineStep):
    """
    Step 7: Vector Database
    รับผิดชอบในการโหลดข้อมูลเข้า Database
    """
    def execute(self, input_data: Any) -> Any:
        # TODO:
        # 1. อ่าน Embeddings
        # 2. เชื่อมต่อไปยัง Vector Database
        # 3. Insert ข้อมูล Embeddings เข้าสู่ Database
        print("Executing Vector Database Loader Step...")
        return "database_collection_reference"
