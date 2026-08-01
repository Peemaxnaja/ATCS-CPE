# Step 4: Chunking Module Documentation

เอกสารอธิบายการทำงานของโมดูล **Chunking (Step 4)** ในระบบ LLM Data Pipeline ตามมาตรฐานการพัฒนาของทีม (`teams/Person_2_Normalization_Chunking/instructions/development_guidelines.md`)

---

## 1. รายละเอียดของงานที่ทำ (What was done)

ใน Step 4 (Chunking Module) ได้ทำการพัฒนาโค้ดและส่วนประกอบต่างๆ เพื่อตัดแบ่งข้อความยาว (Standard Text) ออกเป็นชิ้นย่อย (Chunks) โดยรักษับริบทของข้อความสำหรับ Embedding Model ดังนี้:

- **ออกแบบ Pydantic Data Contracts (`src/chunking/schemas.py`)**:
  - `ChunkItem`: โมเดลเก็บข้อมูล Chunk ประกอบด้วย `chunk_id`, `text`, และ `token_count`
  - `ChunkingOutput`: โมเดลสำหรับส่งต่อผลลัพธ์ไปยัง Step ถัดไป ประกอบด้วย `chunks_directory` และ `chunks_by_file` (dict แมปชื่อไฟล์กับรายการ `ChunkItem`)
- **พัฒนาคลาสหลัก `Chunker` (`src/chunking/chunker.py`)**:
  - สืบทอดอินเทอร์เฟซกลาง `PipelineStep` จาก `src/utils/base_step.py`
  - โหลดและจัดการ Tokenizer ผ่านไลบรารี `tiktoken` (ค่าเริ่มต้น: `cl100k_base`)
  - อัลกอริทึม **Sliding Window Chunking**:
    - แปลงข้อความจากไฟล์ใน `data/normalized/` เป็น Token IDs
    - ตัดแบ่ง Token ทีละก้อนตามขนาด `chunk_size` (default: 512 tokens)
    - เลื่อน Slide window ถัดไปตามระยะ overlap `chunk_overlap` (default: 64 tokens)
    - ถอดรหัส Token IDs กลับเป็นข้อความ Plain Text
  - สร้างรหัส ID เฉพาะแบบระบุเอกสารต้นทาง (`chunk_id`) ในรูปแบบ `{filename_stem}_c{index:03d}` เช่น `sample_document_c001`
  - คำนวณจำนวน Token จริง (`token_count`) ของแต่ละ Chunk
  - ส่งออกผลลัพธ์เป็นไฟล์ JSON ในโฟลเดอร์ `data/chunks/{filename_stem}_chunks.json`
- **การเพิ่ม Unit Tests (`tests/test_chunking.py`)**:
  - ทดสอบการนับ Token (`test_chunker_count_tokens`)
  - ทดสอบการสร้าง Chunk เดี่ยวสำหรับข้อความสั้น (`test_chunker_single_chunk`)
  - ทดสอบ Sliding Window และการคุมขนาด Token สำหรับข้อความยาว (`test_chunker_sliding_window`)
  - ทดสอบการอ่าน/เขียนไฟล์และ Data Contract End-to-End (`test_chunker_execute_with_files`)

---

## 2. วิธีการรันโค้ด (How to run)

### การรันผ่าน Pipeline Runner (`run_pipeline.py`)
สามารถรันเฉพาะ Step 4: Chunking ผ่านคำสั่ง CLI:
```bash
python run_pipeline.py chunking
```

### การรันใน Python Code
```python
from src.chunking.chunker import Chunker

chunker = Chunker(config_path="config/config.yaml")
result = chunker.execute()

print(f"Chunks directory: {result.chunks_directory}")
print(f"Processed files: {list(result.chunks_by_file.keys())}")
```

### การรัน Unit Tests สำหรับ Chunking Module
```bash
python -m pytest tests/test_chunking.py -v
```

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### 3.1 ไฟล์ผลลัพธ์ใน `data/chunks/`
ระบบจะสร้างไฟล์ JSON นามสกุล `{filename_stem}_chunks.json` แยกตามไฟล์ต้นทาง เช่น `data/chunks/sample_document_chunks.json`:

```json
[
  {
    "chunk_id": "sample_document_c001",
    "text": "เนื้อหาข้อความใน chunk...",
    "token_count": 256
  },
  {
    "chunk_id": "sample_document_c002",
    "text": "เนื้อหาข้อความใน chunk ถัดไป...",
    "token_count": 248
  }
]
```

### 3.2 Object ส่งต่อ (`ChunkingOutput`)
ฟังก์ชัน `execute()` จะส่งคืน Pydantic Object ตาม Data Contract:
```python
ChunkingOutput(
    chunks_directory="data/chunks",
    chunks_by_file={
        "sample_document.txt": [
            ChunkItem(chunk_id="sample_document_c001", text="...", token_count=256),
            ChunkItem(chunk_id="sample_document_c002", text="...", token_count=248)
        ]
    }
)
```

---

## 4. Dependencies (Required Libraries)

แพ็กเกจที่ต้องใช้งานใน Step นี้ได้รับการระบุในไฟล์ `requirements.txt` ที่ Root ของโปรเจกต์เรียบร้อยแล้ว:

| Library | Version Requirement | Purpose |
| :--- | :--- | :--- |
| `tiktoken` | `>=0.7.0` | คำนวณจำนวน Token และตัดแบ่งข้อความแบบ Sliding Window (OpenAI Compatible Tokenizer) |
| `pydantic` | `>=2.0.0` | ควบคุม Data Schema Contract (`ChunkItem`, `ChunkingOutput`) |
| `pyyaml` | `>=6.0` | อ่านค่าคอนฟิก `chunk_size`, `chunk_overlap`, `tokenizer` จาก `config/config.yaml` |
| `pytest` | `>=8.0.0` | สำหรับทดสอบ Unit Tests ของโมดูล |
