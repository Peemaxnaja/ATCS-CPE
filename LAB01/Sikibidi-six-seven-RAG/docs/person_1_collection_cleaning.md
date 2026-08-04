# 📄 เอกสารสรุปการดำเนินงาน Person 1: Collection & Cleaning Modules

**ผู้รับผิดชอบ:** Person 1  
**โมดูล:** `src/collection/` และ `src/cleaning/`  
**Branch:** `feature/collection-cleaning`  

---

## 📌 1. รายละเอียดของงานที่ทำ (What was done)

การพัฒนาในส่วนของ Person 1 ครอบคลุม **Step 1: Collection** และ **Step 2: Cleaning** สำหรับระบบ LLM Data Pipeline โดยมีรายละเอียดดังนี้:

### 1.1 Step 1: Collection (`src/collection/collector.py`)
- **การโหลดข้อมูลอเนกประสงค์:** พัฒนาคลาส `Collector` เพื่อรวบรวมไฟล์เอกสารต้นฉบับนามสกุล `.pdf`, `.docx`, `.html`, `.txt`, `.md` จากไดเรกทอรีต้นทาง (เช่น `data/sample/`) เข้าสู่ `data/raw/`
- **การตรวจสอบความสมบูรณ์ของไฟล์ (Integrity Check):** ตรวจสอบว่าไฟล์มีอยู่จริง อ่านได้ และมีขนาดมากกว่า 0 bytes ก่อนที่จะทำการคัดลอกลง `data/raw/`
- **การใช้งาน Data Contract:** ใช้ `pydantic` (v2) ในการกำหนด Data Contract ด้วยคลาส `CollectionOutput` ซึ่งระบุไดเรกทอรี raw files และรายการไฟล์ absolute paths ทั้งหมด
- **มาตรฐาน Logging:** ใช้ Python standard `logging` โมดูลแทนการใช้ `print()` เพื่อระบุระดับความสำคัญ Log (INFO, WARNING, ERROR) พร้อม Timestamp

### 1.2 Step 2: Cleaning (`src/cleaning/cleaner.py`)
- **การถอดข้อความแบบรองรับหลายรูปแบบ (Multi-format Parser):**
  - **PDF (`.pdf`):** ถอดข้อความด้วย `pypdf` ทีละหน้ากระดาษ
  - **Word (`.docx`):** ถอดข้อความจาก Paragraphs และ Tables ด้วย `python-docx`
  - **HTML (`.html`):** ถอดข้อความและกรององค์ประกอบขยะด้วย `BeautifulSoup` (กำจัด `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, `<form>`)
  - **Markdown (`.md`):** ถอดสัญลักษณ์จัดรูปแบบ เช่น รูปภาพ `![alt](url)`, ลิงก์ `[text](url)`, โค้ดบล็อก ` ``` `, หัวข้อ `#`, และตัวหนา/ตัวเอียง
  - **Text (`.txt`):** อ่านข้อความด้วยการเข้ารหัส UTF-8
- **การล้าง Noise (Noise Cleaning):**
  - ลบรูปแบบหมายเลขหน้ากระดาษ เช่น `Page X of Y` หรือ `Page X`
  - ลบบรรทัดว่างเปล่าซ้ำซ้อน (ยุบบรรทัดว่าง 3 บรรทัดขึ้นไปให้เหลือ 2 บรรทัด)
  - ตัดช่องว่างเกินขอบ (Trim whitespace) ด้านหน้าและด้านหลังของแต่ละบรรทัด
  - กรองไฟล์ที่มีข้อความสั้นเกินไปออกด้วย `min_text_length`
- **การบันทึกผลลัพธ์:** บันทึกข้อความ Plain Text ที่สะอาดแล้วลงใน `data/clean/` เป็นไฟล์นามสกุล `.txt` (UTF-8)
- **การใช้งาน Data Contract:** ส่งคืนผลลัพธ์เป็น `CleaningOutput` Pydantic object

### 1.3 การตั้งค่า และ Unit Tests
- **ไฟล์ Config:** สร้าง `config/config.yaml` สำหรับกำหนด path และตัวเลือกของ Collection/Cleaning
- **Data Samples:** สร้างไฟล์ตัวอย่าง 5 นามสกุลใน `data/sample/` (`sample.pdf`, `sample.docx`, `sample.html`, `sample.txt`, `sample.md`)
- **Unit Tests:** เขียน Unit Test ครอบคลุมใน `tests/test_collection.py` และ `tests/test_cleaning.py`

---

## 🚀 2. วิธีการรันโค้ด (How to run)

### 2.1 การรันผ่าน `run_pipeline.py`

1. **รันเฉพาะ Step 1 (Collection):**
   ```bash
   python run_pipeline.py collection
   ```

2. **รันเฉพาะ Step 2 (Cleaning):**
   ```bash
   python run_pipeline.py cleaning
   ```

3. **รัน Pipeline ทั้งหมด (Sequential Execution):**
   ```bash
   python run_pipeline.py all
   ```

### 2.2 การรันสคริปต์ Python โดยตรง

```python
from src.collection.collector import Collector
from src.cleaning.cleaner import Cleaner

# Executing Step 1: Collection
collector = Collector(config_path="config/config.yaml")
collection_output = collector.execute()

print(f"Collected {len(collection_output.file_list)} files.")

# Executing Step 2: Cleaning
cleaner = Cleaner(config_path="config/config.yaml")
cleaning_output = cleaner.execute(collection_output)

print(f"Cleaned {len(cleaning_output.cleaned_file_list)} files.")
```

### 2.3 การรัน Unit Tests

```bash
python -m pytest tests/test_collection.py tests/test_cleaning.py
```

---

## 📦 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### 3.1 โครงสร้างไฟล์ไดเรกทอรีหลังรัน

```text
data/
├── sample/                 # ไฟล์ตัวอย่างต้นทาง (.pdf, .docx, .html, .txt, .md)
├── raw/                    # คัดลอกไฟล์ดิบที่ผ่าน Integrity Check แล้ว
└── clean/                  # Plain text ที่ล้าง noise ออกเรียบร้อยแล้ว
```

### 3.2 รูปแบบ Data Contracts (Output Objects)

- **`CollectionOutput`**: `raw_files_directory: str`, `file_list: list[str]`
- **`CleaningOutput`**: `clean_files_directory: str`, `cleaned_file_list: list[str]`

---

## 🛠️ 4. Dependencies (Required Libraries)

ได้เพิ่มไลบรารีที่จำเป็นใน `requirements.txt` ที่ Root ของโปรเจกต์ดังนี้:

- `pydantic>=2.0.0`
- `pyyaml>=6.0`
- `pytest>=7.0.0`
- `beautifulsoup4>=4.10.0`
- `pypdf>=3.0.0`
- `python-docx>=1.0.0`
