# 🧹 Step 2: Cleaning Module (`src/cleaning/`)

เอกสารประกอบการใช้งานและการทำงานของโมดูล **Cleaning** ซึ่งเป็นขั้นตอนที่สองของ **LLM Data Pipeline**

---

## 1. รายละเอียดของงานที่ทำ (What was done)

โมดูล `Cleaner` (`src/cleaning/cleaner.py`) รับผิดชอบการสกัดข้อความ (Text Extraction) จากไฟล์เอกสารดิบใน `data/raw/` และทำความสะอาดเพื่อกำจัด Noise โดยมีความสามารถดังนี้:

- **Multi-format Text Extraction:**
  - **PDF (`.pdf`):** ถอดข้อความรายหน้าด้วย `pypdf`
  - **Word (`.docx`):** ถอดข้อความจาก ย่อหน้า และ ตาราง ด้วย `python-docx`
  - **HTML (`.html`):** สกัดข้อความและตัด HTML Tags, Script, Style, Navigation, Header, Footer ออกด้วย `BeautifulSoup`
  - **Markdown (`.md`):** ถอดเครื่องหมายจัดรูปแบบ (Markdown formatting artifacts) เช่น รูปภาพ, ลิงก์, โค้ดบล็อก, หัวข้อ (#), และตัวหนา/ตัวเอียง ด้วย Regex
  - **Text (`.txt`):** อ่านข้อความตัวอักษรด้วย UTF-8
- **Noise Reduction & Normalization:**
  - ลบรูปแบบหมายเลขหน้ากระดาษ เช่น `Page X of Y`
  - ตัดช่องว่างขอบบรรทัด (Whitespace trimming)
  - ยุบบรรทัดว่างเปล่าที่ซ้ำซ้อน
  - กรองเอกสารที่มีข้อความสั้นเกินไปออกด้วย `min_text_length`
- **การใช้อินเทอร์เฟซมาตรฐาน:** สืบทอดจาก `PipelineStep` (`src.utils.base_step.PipelineStep`)
- **Data Contract (Pydantic v2):** ส่งคืนผลลัพธ์ผ่าน `CleaningOutput`
- **Logging Standard:** ใช้ Python `logging` โมดูลแทน `print()`

---

## 2. วิธีการรันโค้ด (How to run)

### 2.1 รันผ่าน Pipeline Runner หลัก (`run_pipeline.py`)

```bash
python run_pipeline.py cleaning
```

### 2.2 รันผ่านการเรียกใช้โมดูล Python โดยตรง

```python
from src.collection.collector import Collector
from src.cleaning.cleaner import Cleaner

# รัน Collection Step ก่อน หรือส่ง CollectionOutput เข้ามา
collector = Collector()
collection_output = collector.execute()

cleaner = Cleaner()
cleaning_output = cleaner.execute(collection_output)

print("Clean Directory:", cleaning_output.clean_files_directory)
print("Cleaned Files Count:", len(cleaning_output.cleaned_file_list))
```

### 2.3 รัน Unit Tests

```bash
python -m pytest tests/test_cleaning.py
```

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### 3.1 ไฟล์และไดเรกทอรีที่เกิดขึ้น

ไฟล์ Plain Text ที่สะอาดแล้วจะถูกบันทึกไปที่ `data/clean/`:

```text
data/clean/
├── sample.txt
└── ...
```

### 3.2 รูปแบบวัตถุข้อมูลส่งคืน (Return Data Structure)

คืนค่าเป็น Pydantic Object `CleaningOutput`:

```python
CleaningOutput(
    clean_files_directory="H:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/data/clean",
    cleaned_file_list=[
        "H:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/data/clean/sample.txt"
    ]
)
```

---

## 4. Dependencies (Required Libraries)

โมดูล Cleaning มีการใช้งานไลบรารีดังต่อไปนี้ (ระบุไว้ใน `requirements.txt` ที่ Root ของโปรเจกต์):

- `pydantic>=2.0.0` : สำหรับ Data Contract validation (`CleaningOutput`)
- `pyyaml>=6.0` : สำหรับอ่านไฟล์การตั้งค่า `config/config.yaml`
- `beautifulsoup4>=4.10.0` : สำหรับสกัดและกรองข้อความจาก HTML
- `pypdf>=3.0.0` : สำหรับถอดข้อความจากไฟล์ PDF
- `python-docx>=1.0.0` : สำหรับถอดข้อความจากไฟล์ Word (.docx)
- `pytest>=7.0.0` : สำหรับรัน Unit Tests ใน `tests/test_cleaning.py`
