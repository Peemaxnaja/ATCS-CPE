# Step 6: Embedding Module Documentation

เอกสารอธิบายการทำงานของโมดูล **Embedding (Step 6)** ในระบบ LLM Data Pipeline ตามมาตรฐานการพัฒนาของทีม (`teams/teams/Person_4_Embedding/instructions/development_guidelines.md`)

---

## 1. รายละเอียดของงานที่ทำ (What was done)

ใน Step 6 (Embedding Module) พัฒนาขึ้นโดย **Person 4** ได้ทำการพัฒนาโค้ดและส่วนประกอบต่างๆ เพื่อแปลงข้อความ (Text Chunks) และ Metadata จาก Step 5 ให้กลายเป็น Vector Embeddings สำหรับเตรียมนำเข้าฐานข้อมูล Vector Database ดังนี้:

- **ออกแบบ Pydantic Data Contracts (`src/embedding/schemas.py`)**:
  - `EmbeddedChunkItem`: โมเดลเก็บข้อมูล Chunk พร้อม Vector Embeddings ประกอบด้วย `chunk_id`, `text`, `metadata` (dict) และ `embedding` (`list[float]`)
  - `EmbeddingOutput`: โมเดลสำหรับส่งต่อผลลัพธ์ไปยัง Step ถัดไป (Step 7 Vector DB) ประกอบด้วย `embeddings_directory` และ `embedded_chunks` (list ของ `EmbeddedChunkItem`)
- **พัฒนาคลาสหลัก `Embedder` (`src/embedding/embedder.py`)**:
  - สืบทอดอินเทอร์เฟซกลาง `PipelineStep` จาก `src/utils/base_step.py`
  - โหลดโมเดลผ่าน `SentenceTransformer` (เช่น `BAAI/bge-m3` หรือ `sentence-transformers/all-MiniLM-L6-v2`) ตามที่กำหนดใน `config/config.yaml`
  - รองรับการประมวลผลข้อความแบบกลุ่ม (**Batch Processing**) เพื่อเร่งความเร็วและจัดการหน่วยความจำ
  - ตรวจสอบมิติ Vector (**Dimension Verification**) ผ่านเมธอด `verify_dimension`
  - มีระบบ **Deterministic Mock Vector Generator** สำหรับการรันในสภาพแวดล้อมทดสอบความเร็วสูงหรือแบบออฟไลน์
  - รองรับทั้งการรับ Object Contract (`MetadataOutput`) จาก Step 5 และการอ่านไฟล์ JSON จาก `data/metadata/`
  - ส่งออกผลลัพธ์เป็นไฟล์ JSON ในโฟลเดอร์ `data/embeddings/{filename_stem}_embeddings.json` และไฟล์รวม `data/embeddings/embeddings_all.json`
- **การเพิ่มการตั้งค่าใน Configuration (`config/config.yaml`)**:
  - เพิ่มการตั้งค่า `embedding:` ระบุ `metadata_directory`, `embeddings_directory`, `model_name`, `batch_size`, `device`, และ `dimension`
- **การเชื่อมต่อกับ Pipeline Runner (`run_pipeline.py`)**:
  - เชื่อมต่อคำสั่ง `py run_pipeline.py embedding` และส่งต่อข้อมูลไปยัง `DBLoader` ใน `run_all()`
- **การเพิ่ม Unit Tests (`tests/test_embedding.py`)**:
  - ทดสอบ Pydantic Data Contracts (`test_embedded_chunk_item_schema`, `test_embedding_output_schema`)
  - ทดสอบระบบ Batch Processing (`test_batch_processing`)
  - ทดสอบการตรวจสอบ Vector Dimension (`test_dimension_verification`)
  - ทดสอบการทำงาน End-to-End ผ่าน Object Contract (`test_embedder_execute_with_metadata_output_contract`)
  - ทดสอบการทำงานผ่านไฟล์ Metadata JSON บน Disk (`test_embedder_execute_with_files`)

---

## 2. วิธีการรันโค้ด (How to run)

### การรันผ่าน Pipeline Runner (`run_pipeline.py`)
สามารถรันเฉพาะ Step 6: Embedding ผ่านคำสั่ง CLI:
```bash
py run_pipeline.py embedding
```

### การรันทั้ง Pipeline (Step 1 ถึง Step 7)
```bash
py run_pipeline.py all
```

### การรันใน Python Code
```python
from src.embedding.embedder import Embedder

embedder = Embedder(config_path="config/config.yaml")
result = embedder.execute()

print(f"Embeddings directory: {result.embeddings_directory}")
print(f"Total embedded chunks: {len(result.embedded_chunks)}")
```

### การรัน Unit Tests สำหรับ Embedding Module
```bash
py -m pytest tests/test_embedding.py -v
```

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### 3.1 ไฟล์ผลลัพธ์ใน `data/embeddings/`
ระบบจะสร้างไฟล์ JSON นามสกุล `{filename_stem}_embeddings.json` และ `embeddings_all.json` เช่น `data/embeddings/sample_embeddings.json`:

```json
[
  {
    "chunk_id": "sample_c001",
    "text": "HEADER: Document Title - LLM Data Pipeline\nThis is a sample text document for testing...",
    "metadata": {
      "source": "data/raw/sample.docx",
      "filename": "sample.docx",
      "page": 1,
      "language": "en",
      "author": "Pipeline System",
      "created_at": "2026-08-01T09:08:29.426218+00:00"
    },
    "embedding": [
      -0.994453,
      -0.448796,
      0.509482,
      0.999344
    ]
  }
]
```

### 3.2 Object ส่งต่อ (`EmbeddingOutput`)
ฟังก์ชัน `execute()` จะส่งคืน Pydantic Object ตาม Data Contract:
```python
EmbeddingOutput(
    embeddings_directory="data/embeddings",
    embedded_chunks=[
        EmbeddedChunkItem(
            chunk_id="sample_c001",
            text="...",
            metadata={...},
            embedding=[-0.994453, -0.448796, 0.509482, ...]
        )
    ]
)
```

---

## 4. Dependencies (Required Libraries)

แพ็กเกจที่ต้องใช้งานใน Step นี้ได้รับการระบุในไฟล์ `requirements.txt` ที่ Root ของโปรเจกต์เรียบร้อยแล้ว:

| Library | Version Requirement | Purpose |
| :--- | :--- | :--- |
| `pydantic` | `>=2.0.0` | ควบคุม Data Schema Contract (`EmbeddedChunkItem`, `EmbeddingOutput`) |
| `pyyaml` | `>=6.0` | อ่านค่าคอนฟิก `metadata_directory`, `embeddings_directory`, `model_name`, `batch_size`, `device`, `dimension` จาก `config/config.yaml` |
| `pytest` | `>=7.0.0` | สำหรับทดสอบ Unit Tests ของโมดูล |
| `sentence-transformers` | `>=3.0.0` | สำหรับโหลด Embedding Model (เช่น `BAAI/bge-m3` หรือ `all-MiniLM-L6-v2`) มาประมวลผล Text เป็น Vector |
| `torch` | `>=2.0.0` | สำหรับคำนวณและประมวลผล Tensor/Vector Array บน CPU/GPU |
| `numpy` | `>=1.24.0` | สำหรับจัดการและแปลง Vector Array |
