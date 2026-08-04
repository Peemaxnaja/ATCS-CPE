# Step 5: Metadata Enrichment Module Documentation

เอกสารอธิบายการทำงานของโมดูล **Metadata Enrichment (Step 5)** ในระบบ LLM Data Pipeline ตามมาตรฐานการพัฒนาของทีม (`teams/Person_3_Metadata/instructions/development_guidelines.md`)

---

## 1. รายละเอียดของงานที่ทำ (What was done)

ใน Step 5 (Metadata Enrichment Module) พัฒนาขึ้นโดย **Person 3** ได้ทำการพัฒนาโค้ดและส่วนประกอบต่างๆ เพื่อสกัดและเพิ่มข้อมูลบริบท (Metadata) ให้กับ Text Chunks ทุกชิ้นที่ได้จาก Step 4 (Chunking) เพื่อนำไปใช้ระบุแหล่งอ้างอิง (Citation) และประกอบการค้นหาในระบบ RAG ดังนี้:

- **ออกแบบ Pydantic Data Contracts (`src/metadata/schemas.py`)**:
  - `EnrichedChunkItem`: โมเดลเก็บข้อมูล Chunk พร้อม Metadata ประกอบด้วย `chunk_id`, `text`, `source`, `filename`, `page`, `language`, `author`, และ `created_at`
  - `MetadataOutput`: โมเดลสำหรับส่งต่อผลลัพธ์ไปยัง Step ถัดไป (Step 6 Embedding) ประกอบด้วย `metadata_directory` และ `enriched_chunks` (list ของ `EnrichedChunkItem`)
- **พัฒนาคลาสหลัก `MetadataEnricher` (`src/metadata/metadata_enricher.py`)**:
  - สืบทอดอินเทอร์เฟซกลาง `PipelineStep` จาก `src/utils/base_step.py`
  - รองรับทั้งการรับข้อมูลตรงจากหน่วยความจำ (`ChunkingOutput`) และการอ่านไฟล์ JSON ใน `data/chunks/`
  - ค้นหาข้อมูลไฟล์ดิบใน `data/raw/` เพื่อสกัด `filename`, `source` path และ timestamp การสร้างไฟล์ (`created_at`)
  - ตรวจจับภาษาอัตโนมัติ (`language`: `"th"` / `"en"`)
  - สกัดหมายเลขหน้า (`page`) และผู้เขียน (`author`)
  - ส่งออกผลลัพธ์เป็นไฟล์ JSON ในโฟลเดอร์ `data/metadata/{filename_stem}_metadata.json`
- **การเพิ่มการตั้งค่าใน Configuration (`config/config.yaml`)**:
  - เพิ่มการตั้งค่า `metadata:` ระบุ `chunks_directory`, `metadata_directory`, `default_language`, และ `default_author`
- **การเชื่อมต่อกับ Pipeline Runner (`run_pipeline.py`)**:
  - เพิ่มคำสั่ง `py run_pipeline.py metadata` และส่งต่อข้อมูลไปยัง `Embedder` ใน `run_all()`
- **การเพิ่ม Unit Tests (`tests/test_metadata.py`)**:
  - ทดสอบการตรวจจับภาษา (`test_detect_language`)
  - ทดสอบความถูกต้องของ Data Contract (`test_enrich_chunk_validation`)
  - ทดสอบการสกัดหมายเลขหน้า (`test_extract_page_number`)
  - ทดสอบการทำงาน End-to-End ผ่านการอ่าน/เขียนไฟล์ (`test_metadata_enricher_execute_with_files`)
  - ทดสอบการรับ Object Contract จาก Step 4 (`test_metadata_enricher_with_chunking_output_contract`)

---

## 2. วิธีการรันโค้ด (How to run)

### การรันผ่าน Pipeline Runner (`run_pipeline.py`)
สามารถรันเฉพาะ Step 5: Metadata Enrichment ผ่านคำสั่ง CLI:
```bash
py run_pipeline.py metadata
```

### การรันทั้ง Pipeline (Step 1 ถึง Step 7)
```bash
py run_pipeline.py all
```

### การรันใน Python Code
```python
from src.metadata.metadata_enricher import MetadataEnricher

enricher = MetadataEnricher(config_path="config/config.yaml")
result = enricher.execute()

print(f"Metadata directory: {result.metadata_directory}")
print(f"Total enriched chunks: {len(result.enriched_chunks)}")
```

### การรัน Unit Tests สำหรับ Metadata Module
```bash
py -m pytest tests/test_metadata.py -v
```

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### 3.1 ไฟล์ผลลัพธ์ใน `data/metadata/`
ระบบจะสร้างไฟล์ JSON นามสกุล `{filename_stem}_metadata.json` แยกตามไฟล์ต้นทาง เช่น `data/metadata/sample_metadata.json`:

```json
[
  {
    "chunk_id": "sample_c001",
    "text": "HEADER: Document Title - LLM Data Pipeline\nThis is a sample text document for testing...",
    "source": "data/raw/sample.docx",
    "filename": "sample.docx",
    "page": 1,
    "language": "en",
    "author": "Pipeline System",
    "created_at": "2026-08-01T08:51:26.141515+00:00"
  }
]
```

### 3.2 Object ส่งต่อ (`MetadataOutput`)
ฟังก์ชัน `execute()` จะส่งคืน Pydantic Object ตาม Data Contract:
```python
MetadataOutput(
    metadata_directory="data/metadata",
    enriched_chunks=[
        EnrichedChunkItem(
            chunk_id="sample_c001",
            text="...",
            source="data/raw/sample.docx",
            filename="sample.docx",
            page=1,
            language="en",
            author="Pipeline System",
            created_at="2026-08-01T08:51:26.141515+00:00"
        )
    ]
)
```

---

## 4. Dependencies (Required Libraries)

แพ็กเกจที่ต้องใช้งานใน Step นี้ได้รับการระบุในไฟล์ `requirements.txt` ที่ Root ของโปรเจกต์เรียบร้อยแล้ว:

| Library | Version Requirement | Purpose |
| :--- | :--- | :--- |
| `pydantic` | `>=2.0.0` | ควบคุม Data Schema Contract (`EnrichedChunkItem`, `MetadataOutput`) |
| `pyyaml` | `>=6.0` | อ่านค่าคอนฟิก `chunks_directory`, `metadata_directory`, `default_language`, `default_author` จาก `config/config.yaml` |
| `pytest` | `>=7.0.0` | สำหรับทดสอบ Unit Tests ของโมดูล |
