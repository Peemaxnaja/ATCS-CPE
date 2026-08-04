from abc import ABC, abstractmethod
from typing import Any

class PipelineStep(ABC):
    """โครงสร้างกลางสำหรับทุก Module ใน Pipeline"""
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """รับ Input ประมวลผล และคืนค่า Output"""
        pass
