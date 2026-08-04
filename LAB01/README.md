# LAB01 — LLM Data Pipeline for RAG

**รายวิชา:** ATCS-CPE
**ชื่อ-นามสกุล:** สิรวิชญ์ ศิริสลุง
**รหัสนักศึกษา:** 116730462023-6

---

## 1. รายละเอียดใบงาน (Overview)

ใบงานนี้เป็นการพัฒนา **LLM Data Pipeline 8 ขั้นตอน** สำหรับระบบ RAG (Retrieval-Augmented Generation) โดยทำงานเป็นกลุ่ม แบ่งความรับผิดชอบตามขั้นตอนของ Pipeline

| ขั้นตอน | Task | คำอธิบาย |
| :---: | :--- | :--- |
| 1 | Collection | รวบรวมข้อมูลจากแหล่งต่าง ๆ มาไว้ที่เดียว |
| 2 | Cleaning | ลบแท็ก HTML, Header/Footer และข้อความซ้ำ |
| 3 | Normalization | ปรับรูปแบบข้อความ ช่องว่าง และ Unicode |
| 4 | Chunking | หั่นข้อความเป็น Chunks ขนาดเหมาะสม |
| **5** | **Metadata Enrichment** | **แปะข้อมูลบริบท (ชื่อไฟล์, ผู้เขียน, หน้า, ภาษา, วันที่) ให้แต่ละ Chunk — ส่วนที่ข้าพเจ้ารับผิดชอบ** |
| 6 | Embedding | แปลงข้อความเป็นเวกเตอร์ |
| 7 | Vector Database | จัดเก็บเวกเตอร์เพื่อการค้นคืน |
| 8 | LLM / Retrieval | ดึงข้อมูลมาประกอบคำตอบผ่าน LLM |

### ส่วนที่รับผิดชอบ: Step 5 — Metadata Enrichment

พัฒนาโมดูลสกัดและเพิ่ม Metadata ให้ Text Chunks ทุกชิ้นที่ได้จาก Step 4 เพื่อใช้ระบุแหล่งอ้างอิง (Citation) และประกอบการค้นหาในระบบ RAG ประกอบด้วย

- `src/metadata/schemas.py` — Pydantic Data Contract (`EnrichedChunkItem`, `MetadataOutput`)
- `src/metadata/metadata_enricher.py` — คลาส `MetadataEnricher` สืบทอดจาก `PipelineStep`
- `config/config.yaml` — เพิ่มส่วนตั้งค่า `metadata:`
- `run_pipeline.py` — เชื่อมต่อเข้ากับ Pipeline Runner
- `tests/test_metadata.py` — Unit Tests ของโมดูล

📄 เอกสารฉบับเต็ม: [`Sikibidi-six-seven-RAG/docs/metadata_enrichment.md`](Sikibidi-six-seven-RAG/docs/metadata_enrichment.md)
📄 คู่มือโมดูล: [`Sikibidi-six-seven-RAG/src/metadata/README.md`](Sikibidi-six-seven-RAG/src/metadata/README.md)

---

## 2. โครงสร้างไฟล์ใน LAB01

```
LAB01/
├── README.md                      <- ไฟล์นี้
└── Sikibidi-six-seven-RAG/        <- โปรเจกต์กลุ่ม (นำเข้าแบบ git subtree)
    ├── config/
    │   └── config.yaml            <- ค่าคอนฟิกของทุก Step
    ├── data/
    │   ├── raw/                   <- Dataset ต้นฉบับ (Chap-01..12.pdf, sample.*)
    │   ├── clean/ normalized/ chunks/ metadata/ embeddings/
    ├── docs/
    │   ├── metadata_enrichment.md
    │   └── person_1_collection_cleaning.md
    ├── src/
    │   ├── collection/ cleaning/ normalization/ chunking/
    │   ├── metadata/              <- Step 5 (ส่วนที่รับผิดชอบ)
    │   ├── embedding/ vectordb/ retrieval/
    │   └── utils/base_step.py
    ├── tests/
    ├── requirements.txt
    └── run_pipeline.py
```

---

## 3. วิธีการรันโค้ด (How to Run)

```bash
cd LAB01/Sikibidi-six-seven-RAG
py -m pip install -r requirements.txt
```

รันเฉพาะ Step 5:

```bash
py run_pipeline.py metadata
```

รันทั้ง Pipeline:

```bash
py run_pipeline.py all
```

รัน Unit Tests ของ Step 5:

```bash
py -m pytest tests/test_metadata.py -v
```

---

## 4. แหล่งที่มาและการอ้างอิง (Citation)

โค้ดในโฟลเดอร์ `Sikibidi-six-seven-RAG/` เป็นผลงานร่วมของกลุ่ม นำเข้ามาด้วย `git subtree` จาก Repository ต้นทาง โดยยังคง commit history เดิมไว้ครบถ้วนเพื่อให้ตรวจสอบที่มาได้

| รายการ | แหล่งที่มา |
| :--- | :--- |
| Source Code (โปรเจกต์กลุ่ม) | https://github.com/PROxTAE/Sikibidi-six-seven-RAG |
| Dataset (`data/raw/Chap-01..12.pdf`) | เอกสารประกอบการเรียนที่ใช้ในรายวิชา |
| `pydantic` | https://github.com/pydantic/pydantic |
| `pyyaml` | https://github.com/yaml/pyyaml |
| `pytest` | https://github.com/pytest-dev/pytest |

> ⚠️ ไม่มีการใช้ข้อมูลที่ละเมิดลิขสิทธิ์ ข้อมูลส่วนบุคคลที่ไม่ได้รับอนุญาต หรือข้อมูลที่ผิดกฎหมาย

### การอัปเดต subtree จาก Repository ต้นทาง

```bash
# ครั้งแรกเท่านั้น: เพิ่ม remote
git remote add rag https://github.com/PROxTAE/Sikibidi-six-seven-RAG.git

# ดึงการเปลี่ยนแปลงล่าสุดจากต้นทางเข้ามาใน LAB01/
git subtree pull --prefix=LAB01/Sikibidi-six-seven-RAG rag main
```

---

## 5. วิธีการส่งงานของรายวิชา (Submission Guidelines)

ข้อกำหนดการส่งงานตามที่อาจารย์ผู้สอนกำหนด ใช้กับทุกใบงานตลอดรายวิชา

### 5.1 หลักการ

นักศึกษาทุกคนต้องสร้างบัญชี GitHub และใช้ **Repository เพียง 1 Repository ตลอดทั้งรายวิชา** เพื่อรวบรวมใบงาน (LAB) และโครงงาน (Final Project) ไว้ในที่เดียว

Repository ของข้าพเจ้า: **https://github.com/Peemaxnaja/ATCS-CPE**

### 5.2 โครงสร้างโฟลเดอร์ที่กำหนด

รายวิชานี้มี LAB ประมาณ 10 ใบงาน สามารถสร้างโฟลเดอร์ `LAB01` ถึง `LAB10` ไว้ล่วงหน้าได้ตั้งแต่เริ่มเรียน แต่ละใบงานต้องแยกเก็บในโฟลเดอร์ของตนเอง

```
ATCS-CPE/
│
├── LAB01/
│   ├── LAB1_code.ipynb
│   ├── dataset.csv
│   ├── report.pdf
│   └── README.md
│
├── LAB02/
│   ├── LAB2_code.ipynb
│   ├── dataset.csv
│   ├── report.pdf
│   └── README.md
│
├── LAB03/
│   ├── ...
│
├── ...
│
├── LAB10/
│   ├── ...
│
└── Final-Project/
    ├── source_code/
    ├── dataset/
    ├── report.pdf
    └── README.md
```

### 5.3 ไฟล์ที่ต้องมีในแต่ละโฟลเดอร์ LAB

| ไฟล์ | รายละเอียด |
| :--- | :--- |
| Source Code | `.ipynb` หรือ `.py` |
| Dataset | ถ้ามี |
| รายงานผลการทดลอง | `.pdf` (ถ้ามี) |
| `README.md` | อธิบายรายละเอียดของใบงาน |

### 5.4 ขั้นตอนการส่ง

1. ทำใบงานให้เสร็จภายในโฟลเดอร์ `LABxx/` ของตนเอง
2. **Commit และ Push** ขึ้น GitHub **ก่อนวันและเวลาที่กำหนดส่ง**
3. ส่ง **ลิงก์ Repository** หรือ **ลิงก์โฟลเดอร์ของ LAB** ที่กำหนด ผ่านระบบที่อาจารย์แจ้ง

```bash
git add LAB01/
git commit -m "LAB01: <อธิบายสิ่งที่ทำ>"
git push origin main
```

ลิงก์สำหรับส่ง LAB01: https://github.com/Peemaxnaja/ATCS-CPE/tree/main/LAB01

> 📌 อาจารย์จะใช้ **commit history** และ **เวลาที่ Push ขึ้น GitHub** เป็นข้อมูลประกอบการตรวจและประเมินผล

### 5.5 การเลือกใช้ Dataset และแหล่งข้อมูล

- เลือกใช้ Dataset, Source Code, โมเดล หรือแหล่งอ้างอิงจากที่ใดก็ได้อย่างอิสระ — เว็บไซต์ งานวิจัย หน่วยงานภาครัฐ หรือ Open Dataset จากทั่วโลก ตราบใดที่ไม่ละเมิดกฎหมาย ลิขสิทธิ์ หรือเงื่อนไขการใช้งานของเจ้าของข้อมูล
- หากนำ Dataset, Source Code, โมเดล หรือข้อมูลของผู้อื่นมาใช้ **ต้องอ้างอิงแหล่งที่มา (Citation) หรือแนบลิงก์ (URL)** ไปยังแหล่งข้อมูลต้นฉบับไว้ใน `README.md` หรือรายงานทุกครั้ง
- **ข้อควรระวัง:** ห้ามใช้ข้อมูลที่ละเมิดลิขสิทธิ์ ข้อมูลส่วนบุคคล (Personal Data) ที่ไม่ได้รับอนุญาต หรือข้อมูลที่ผิดกฎหมาย การนำผลงานของผู้อื่นมาใช้โดยไม่อ้างอิงแหล่งที่มาถือว่าขัดต่อหลักจริยธรรมทางวิชาการ (Academic Integrity) และอาจส่งผลต่อการประเมินผลรายวิชา

### 5.6 หมายเหตุ

ควร Commit งานอย่างสม่ำเสมอระหว่างการพัฒนา ไม่ควรรอ Commit เพียงครั้งเดียวก่อนถึงกำหนดส่ง เพื่อป้องกันข้อมูลสูญหาย และแสดงให้เห็นถึงลำดับขั้นตอนการพัฒนางานอย่างเป็นระบบ
