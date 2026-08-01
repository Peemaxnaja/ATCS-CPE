# Step 3: Normalization Module Documentation

เอกสารอธิบายการทำงานของโมดูล **Normalization (Step 3)** ในระบบ LLM Data Pipeline ตามมาตรฐานการพัฒนาของทีม (`teams/Person_2_Normalization_Chunking/instructions/development_guidelines.md`)

---

## 1. รายละเอียดของงานที่ทำ (What was done)

ใน Step 3 (Normalization Module) ได้ทำการพัฒนาโค้ดและส่วนประกอบต่างๆ เพื่อปรับและจัดแต่งตัวอักษร รวมถึงโครงสร้างเครื่องหมายและช่องว่างในข้อความให้เป็นมาตรฐานเดียวกัน (Standard Text) ดังนี้:

- **ออกแบบ Pydantic Data Contract (`src/normalization/schemas.py`)**:
  - `NormalizationOutput`: โมเดลสำหรับส่งต่อผลลัพธ์ไปยัง Step ถัดไป ประกอบด้วย `normalized_files_directory` (เส้นทางโฟลเดอร์ผลลัพธ์) และ `normalized_file_list` (รายการเส้นทางไฟล์ที่ผ่านการ Normalization แล้ว)
- **พัฒนาคลาสหลัก `Normalizer` (`src/normalization/normalizer.py`)**:
  - สืบทอดอินเทอร์เฟซกลาง `PipelineStep` จาก `src/utils/base_step.py`
  - อ่านไฟล์ Plain Text จาก `data/clean/` หรือผ่าน `CleaningOutput` Pydantic model
  - บังคับการอ่านและเขียนไฟล์ด้วยการเข้ารหัส `UTF-8`
  - **Unicode Normalization (NFKC)**: แปลงมาตรฐานตัวอักษร อักขระพิเศษ ตัวเลข และสัญลักษณ์ด้วย `unicodedata.normalize('NFKC', text)`
  - **Thai Text Sanitization (PyThaiNLP)**: ใช้ `pythainlp.util.normalize(text)` ในการปรับแต่งภาษาไทย จัดการสระลอย สระเกิน สระซ้อน (เช่น แปลง `เเ` เป็น `แ`, ลบ zero-width spaces)
  - **Whitespace Normalization**: ทำการยุบช่องว่าง/แท็บที่ติดต่อกัน (`\s+`) ให้เหลือช่องว่างเดียว และจัดโครงสร้างเว้นบรรทัดใหม่ให้สม่ำเสมอ
  - บันทึกไฟล์ข้อความมาตรฐานลงใน `data/normalized/{filename}.txt`
- **การเพิ่ม Unit Tests (`tests/test_normalization.py`)**:
  - ทดสอบ Unicode NFKC, PyThaiNLP Thai vowel normalization และ Whitespace cleaning (`test_normalization_text`)
  - ทดสอบการอ่านไฟล์จาก directory การประมวลผล การสร้างไฟล์ output และ Pydantic schema validation (`test_normalization_execute_with_files`)

---

## 2. วิธีการรันโค้ด (How to run)

### การรันผ่าน Pipeline Runner (`run_pipeline.py`)
สามารถรันเฉพาะ Step 3: Normalization ผ่านคำสั่ง CLI:
```bash
python run_pipeline.py normalization
```

### การรันใน Python Code
```python
from src.normalization.normalizer import Normalizer

normalizer = Normalizer(config_path="config/config.yaml")
result = normalizer.execute()

print(f"Normalized directory: {result.normalized_files_directory}")
print(f"Processed files: {result.normalized_file_list}")
```

### การรัน Unit Tests สำหรับ Normalization Module
```bash
python -m pytest tests/test_normalization.py -v
```

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Output)

### 3.1 ไฟล์ผลลัพธ์ใน `data/normalized/`
ระบบจะสร้างไฟล์ข้อความมาตรฐาน (.txt) เข้ารหัส UTF-8 ลงในโฟลเดอร์ `data/normalized/` เช่น `data/normalized/sample_document.txt`

**ตัวอย่างเนื้อหาข้อความหลัง Normalization:**
- สระซ้อน/สระผิดรูปแบบถูกจัดระเบียบ (เช่น `เเละ` -> `และ`)
- ช่องว่างซ้ำซ้อนถูกยุบเหลือช่องเดียว (`สวัสดี   ครับ` -> `สวัสดี ครับ`)
- โครงสร้างบรรทัดเรียบร้อย ไม่มีเว้นบรรทัดว่างเกิน 2 บรรทัดติดกัน

### 3.2 Object ส่งต่อ (`NormalizationOutput`)
ฟังก์ชัน `execute()` จะส่งคืน Pydantic Object ตาม Data Contract:
```python
NormalizationOutput(
    normalized_files_directory="data/normalized",
    normalized_file_list=[
        "data/normalized/sample_document.txt"
    ]
)
```

---

## 4. Dependencies (Required Libraries)

แพ็กเกจที่ต้องใช้งานใน Step นี้ได้รับการระบุในไฟล์ `requirements.txt` ที่ Root ของโปรเจกต์แล้ว:

| Library | Version Requirement | Purpose |
| :--- | :--- | :--- |
| `pythainlp` | `>=5.0.0` | จัดการ Unicode & Thai Text Normalization (ลบสระซ้อน สระลอย วรรณยุกต์) |
| `unicodedata` | Python Standard Library | จัดการ Unicode NFKC normalization |
| `pydantic` | `>=2.0.0` | ควบคุม Data Schema Contract (`NormalizationOutput`) |
| `pyyaml` | `>=6.0` | อ่านค่าคอนฟิก `unicode_form`, `thai_normalize` จาก `config/config.yaml` |
| `pytest` | `>=8.0.0` | สำหรับทดสอบ Unit Tests ของโมดูล |
