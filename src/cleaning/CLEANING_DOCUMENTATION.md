# 🧹 Step 2: Cleaning Module (`src/cleaning/`)

เอกสารอธิบายการทำงาน การรัน และผลลัพธ์ของโมดูล **Cleaning** ตามมาตรฐาน [development_guidelines.md](file:///h:/Sikibidi-six-seven-RAG/Sikibidi-six-seven-RAG/teams/Person_1_Collection_Cleaning/instructions/development_guidelines.md#L37-L44)

---

## 1. รายละเอียดของงานที่ทำ (What was done)

โมดูล `Cleaner` (`src/cleaning/cleaner.py`) รับผิดชอบสกัดข้อความ (Text Extraction) จากเอกสารหลากรูปแบบใน `data/raw/` และทำความสะอาดข้อมูลเพื่อกำจัด Noise ออกก่อนส่งต่อให้ Step 3 Normalization:

1. **Multi-format Parsers Implementation:**
   - **PDF (`.pdf`):** ใช้ `pypdf` สกัดข้อความภาษาไทยและอังกฤษแบบรายหน้ากระดาษ
   - **Word (`.docx`):** ใช้ `python-docx` สกัดเนื้อหาจากย่อหน้า (Paragraphs) และตาราง (Tables)
   - **HTML (`.html`):** ใช้ `BeautifulSoup` ถอดข้อความและกรององค์ประกอบส่วนเกิน (`<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, `<form>`)
   - **Markdown (`.md`):** ใช้ Regular Expressions ถอด formatting artifacts เช่น รูปภาพ `![alt](url)`, ลิงก์ `[text](url)`, โค้ดบล็อก `` ``` ``, หัวข้อ `#`, และตัวหนา/ตัวเอียง
   - **Text (`.txt`):** อ่านไฟล์ข้อความธรรมดาด้วย UTF-8
2. **Noise Reduction Algorithm (`clean_text` method):**
   - ลบรูปแบบหมายเลขหน้ากระดาษ เช่น `Page X of Y` หรือ `Page X`
   - ตัดช่องว่างเกินขอบ (Trim whitespace) ด้านหน้าและด้านหลังของทุกบรรทัด
   - ยุบบรรทัดว่างเปล่าที่ติดกันเกิน 2 บรรทัด (3+ newlines -> 2 newlines)
   - กรองไฟล์ที่มีข้อความสั้นเกินไปออกด้วยเกณฑ์ `min_text_length`
3. **Data Contract Compliance:**
   - สร้างคลาส `CleaningOutput` ด้วย `pydantic` (v2) เพื่อส่งต่อรายชื่อไฟล์ที่ผ่านการคลีนเรียบร้อยแล้ว
4. **Standardized Logging & Error Handling:**
   - ใช้ Python `logging` module พร้อมแสดง Timestamp และ Log Level (INFO/WARNING/ERROR)
   - ข้ามไฟล์ที่ไม่รองรับหรือไฟล์ที่เสียหายอย่างปลอดภัยโดยไม่ทำให้ระบบล่ม

---

## 2. วิธีการรันโค้ด (How to run)

### 2.1 รันผ่าน Pipeline Runner หลัก (`run_pipeline.py`)

```bash
python run_pipeline.py cleaning
```

### 2.2 รันผ่านสคริปต์ Python

```python
from src.collection.collector import Collector
from src.cleaning.cleaner import Cleaner

# Step 1: Collect raw files
collector = Collector(config_path="config/config.yaml")
collection_output = collector.execute()

# Step 2: Clean raw files
cleaner = Cleaner(config_path="config/config.yaml")
cleaning_output = cleaner.execute(collection_output)

print("Clean files directory:", cleaning_output.clean_files_directory)
print("Total cleaned files:", len(cleaning_output.cleaned_file_list))
```

### 2.3 รัน Unit Tests

```bash
python -m pytest tests/test_cleaning.py
```

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### 3.1 ไฟล์และไดเรกทอรีที่เกิดขึ้น

ข้อความ Plain Text ที่ผ่านการล้างแล้วจะถูกบันทึกลงในไดเรกทอรี `data/clean/` เป็นไฟล์นามสกุล `.txt` (UTF-8):

```text
data/clean/
├── sample.txt
└── [filename].txt
```

### 3.2 รูปแบบวัตถุข้อมูลส่งคืน (Return Value Object)

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

ได้เพิ่มแพ็กเกจไลบรารีทั้งหมดลงใน `requirements.txt` ที่ Root ของโปรเจกต์:

- `pydantic>=2.0.0` (สำหรับ Pydantic v2 Data Contract Validation)
- `pyyaml>=6.0` (สำหรับอ่านค่า Configuration)
- `beautifulsoup4>=4.10.0` (สำหรับสกัดข้อความจาก HTML)
- `pypdf>=3.0.0` (สำหรับถอดข้อความจากไฟล์ PDF)
- `python-docx>=1.0.0` (สำหรับถอดข้อความจากไฟล์ Word `.docx`)
- `pytest>=7.0.0` (สำหรับ Unit Test Framework)
