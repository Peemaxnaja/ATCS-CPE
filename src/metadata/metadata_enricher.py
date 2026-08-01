from typing import Any
from src.utils.base_step import PipelineStep

class MetadataEnricher(PipelineStep):
    """
    Step 5: Metadata
    รับผิดชอบในการแทรกข้อมูลบริบทเข้าไปในแต่ละ Chunk
    """
    def execute(self, input_data: Any) -> Any:
        # TODO:
        # 1. อ่านไฟล์ Chunks JSON
        # 2. ดึงข้อมูลบริบทจากไฟล์ต้นฉบับมาแปลงเป็น Metadata (source, filename, etc.)
        # 3. แทรก Metadata เหล่านี้เข้าไป
        # 4. บันทึกกลับเป็น JSON ลงใน data/metadata/
        print("Executing Metadata Step...")
        return "chunks_with_metadata_path"
