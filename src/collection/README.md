# 📦 Step 1: Collection Module (`src/collection/`)

เอกสารประกอบการใช้งานและการทำงานของโมดูล **Collection** ซึ่งเป็นขั้นตอนแรกของ **LLM Data Pipeline**

---

## 1. รายละเอียดของงานที่ทำ (What was done)

โมดูล `Collector` (`src/collection/collector.py`) มีหน้าที่รวบรวมไฟล์เอกสารดิบจากแหล่งข้อมูลต้นทางเพื่อเตรียมส่งต่อเข้าสู่กระบวนการ Cleaning โดยมีความสามารถดังนี้:

- **การรองรับไฟล์หลากรูปแบบ:** สามารถค้นหาและโหลดไฟล์นามสกุล `.pdf`, `.docx`, `.html`, `.txt`, และ `.md` จากโฟลเดอร์ต้นทางที่กำหนด (เช่น `data/sample/`)
- **การตรวจสอบความสมบูรณ์ของไฟล์ (Integrity Check):** 
  - ตรวจสอบว่าไฟล์มีอยู่จริง
  - ตรวจสอบขนาดไฟล์ต้องไม่เท่ากับ 0 bytes (ไม่เป็นไฟล์ว่าง)
  - ทดสอบเปิดอ่านไฟล์เบื้องต้นเพื่อให้แน่ใจว่าไฟล์ไม่เสียหายระหว่างการคัดลอก
- **การคัดลอกลง Raw Directory:** นำไฟล์ที่ผ่านการตรวจสอบไปจัดเก็บไว้ใน `data/raw/`
- **การใช้อินเทอร์เฟซมาตรฐาน:** สืบทอดจาก `PipelineStep` (`src.utils.base_step.PipelineStep`) และใช้เมธอด `execute(input_data)`
- **Data Contract (Pydantic v2):** ส่งคืนผลลัพธ์ผ่านคลาส `CollectionOutput` ซึ่งประกอบด้วย path ไดเรกทอรีปลายทาง และรายชื่อไฟล์ absolute path ทั้งหมด
- **Logging Standard:** ใช้ Python `logging` โมดูลในการบันทึก Log การทำงาน พร้อมระดับ Log Level และ Timestamp แทนการใช้ `print()`

---

## 2. วิธีการรันโค้ด (How to run)

### 2.1 รันผ่าน Pipeline Runner หลัก (`run_pipeline.py`)

```bash
python run_pipeline.py collection
```

### 2.2 รันผ่านการเรียกใช้โมดูล Python โดยตรง

```python
from src.collection.collector import Collector

# 1. สร้าง Instance ของ Collector (อ่าน config จาก config/config.yaml โดยอัตโนมัติ)
collector = Collector(config_path="config/config.yaml")

# 2. สั่งประมวลผล (สามารถระบุ custom source path ผ่าน input_data ได้)
output = collector.execute()

# 3. ตรวจสอบผลลัพธ์
print("Raw Files Directory:", output.raw_files_directory)
print("Collected Files Count:", len(output.file_list))
```

### 2.3 รัน Unit Tests

```bash
python -m pytest tests/test_collection.py
```

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### 3.1 ไฟล์และไดเรกทอรีที่เกิดขึ้น

ไฟล์เอกสารดิบที่ผ่าน integrity check จะถูกคัดลอกไปที่ `data/raw/`:

```text
data/raw/
├── sample.docx
├── sample.html
├── sample.md
├── sample.pdf
└── sample.txt
```

### 3.2 รูปแบบวัตถุข้อมูลส่งคืน (Return Data Structure)

คืนค่าเป็น Pydantic Object `CollectionOutput`:

```python
CollectionOutput(
    raw_files_directory="H:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/data/raw",
    file_list=[
        "H:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/data/raw/sample.docx",
        "H:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/data/raw/sample.html",
        "H:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/data/raw/sample.md",
        "H:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/data/raw/sample.pdf",
        "H:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/data/raw/sample.txt"
    ]
)
```

---

## 4. Dependencies (Required Libraries)

โมดูล Collection มีการใช้งานไลบรารีดังต่อไปนี้ (ระบุไว้ใน `requirements.txt` ที่ Root ของโปรเจกต์):

- `pydantic>=2.0.0` : สำหรับ Data Contract validation (`CollectionOutput`)
- `pyyaml>=6.0` : สำหรับอ่านไฟล์การตั้งค่า `config/config.yaml`
- `pytest>=7.0.0` : สำหรับรัน Unit Tests ใน `tests/test_collection.py`
