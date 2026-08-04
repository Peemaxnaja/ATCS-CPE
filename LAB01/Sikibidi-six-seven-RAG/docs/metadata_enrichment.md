# Step 5: Metadata Enrichment Documentation

เอกสารอธิบายรายละเอียดการพัฒนาและคู่มือการใช้งานสำหรับ **Step 5: Metadata Enrichment** (พัฒนาโดย **Person 3**)

---

## 1. รายละเอียดของงานที่ทำ (What Was Done)

ในขั้นตอน Step 5 นี้ ระบบทำหน้าที่สกัดและผนวกข้อมูลบริบท (Metadata Enrichment) เข้าไปใน Text Chunks แต่ละชิ้นที่ได้จาก Step 4 (Chunking) เพื่อเตรียมข้อมูลสำหรับการทำ Embedding, Vector Database และการระบุแหล่งอ้างอิง (Citation) ในระบบ RAG

### สิ่งที่ได้พัฒนาเพิ่ม/ปรับปรุง:
- **`src/metadata/schemas.py`**: กำหนด Pydantic Schemas V2 (`EnrichedChunkItem` และ `MetadataOutput`) เป็น Data Contract กลางของ Step 5
- **`src/metadata/metadata_enricher.py`**: พัฒนาคลาส `MetadataEnricher` (สืบทอดจาก `PipelineStep`) ทำหน้าที่:
  - อ่านข้อมูล Chunks จากหน่วยความจำ (`ChunkingOutput`) หรือสแกนไฟล์ JSON ใน `data/chunks/`
  - ค้นหาข้อมูลไฟล์ต้นฉบับใน `data/raw/` เพื่อดึง `filename`, `source` path และ timestamp (`created_at`)
  - ตรวจจับภาษาอัตโนมัติ (`language`: `"th"` / `"en"`)
  - สกัดหมายเลขหน้า (`page`) และผู้เขียน (`author`)
  - บันทึกไฟล์ JSON ในรูปแบบ `{filename_stem}_metadata.json` ลงโฟลเดอร์ `data/metadata/`
- **`config/config.yaml`**: เพิ่มส่วน `metadata:` สำหรับตั้งค่า directory paths, ภาษาเริ่มต้น (`default_language`) และผู้สร้างเอกสาร (`default_author`)
- **`run_pipeline.py`**: เชื่อมต่อ `MetadataEnricher` เข้ากับระบบ Pipeline Runner หลัก
- **`tests/test_metadata.py`**: สร้าง Unit Tests ครอบคลุมการตรวจจับภาษา, การแปลง Schema, การสกัดหมายเลขหน้า, และการรัน End-to-End Test

---

## 2. วิธีการรันโค้ด (How to Run)

### การรันเฉพาะ Step 5 (Metadata Enrichment):
```bash
py run_pipeline.py metadata
```

### การรันทั้ง Pipeline (Step 1 - 7):
```bash
py run_pipeline.py all
```

### การรัน Unit Tests สำหรับ Step 5:
```bash
py -m pytest tests/test_metadata.py
```

### การรัน Unit Tests ทั้งหมดในระบบ:
```bash
py -m pytest
```

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### โครงสร้างไฟล์ผลลัพธ์
ระบบจะสร้างไฟล์ JSON ใน `data/metadata/` เช่น:
- `data/metadata/sample_metadata.json`
- `data/metadata/Chap-01_metadata.json`

### ตัวอย่างโครงสร้างข้อมูล (JSON Schema):
```json
[
  {
    "chunk_id": "sample_c001",
    "text": "Header and document contents...",
    "source": "data/raw/sample.docx",
    "filename": "sample.docx",
    "page": 1,
    "language": "en",
    "author": "Pipeline System",
    "created_at": "2026-08-01T08:51:26.141515+00:00"
  }
]
```

### Pydantic Data Contract (`MetadataOutput`):
```python
class EnrichedChunkItem(BaseModel):
    chunk_id: str
    text: str
    source: str
    filename: str
    page: Optional[int] = None
    language: str = "th"
    author: Optional[str] = None
    created_at: Optional[str] = None

class MetadataOutput(BaseModel):
    metadata_directory: str
    enriched_chunks: list[EnrichedChunkItem]
```

---

## 4. Dependencies (Required Libraries)

โมดูลนี้ใช้ไลบรารีมาตรฐานและ dependencies ที่ระบุไว้ใน `requirements.txt` แล้ว:
- `pydantic>=2.0.0` (สำหรับ Schema & Data Contract Validation)
- `pyyaml>=6.0` (สำหรับการอ่านไฟล์ตั้งค่า `config/config.yaml`)
- `pytest>=7.0.0` (สำหรับรัน Unit Tests)
