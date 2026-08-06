# LAB01: LLM Data Pipeline สำหรับระบบ RAG

รายวิชา ATCS-CPE
สิรวิชญ์ ศิริสลุง 116730462023-6

## งานที่ทำ

ใบงานนี้ทำกันเป็นกลุ่ม สร้าง data pipeline 8 ขั้นสำหรับเตรียมข้อมูลป้อนระบบ RAG แล้วแบ่งกันรับผิดชอบคนละขั้น ผมได้ขั้นที่ 5 คือ Metadata Enrichment

| ขั้น | Step | หน้าที่ |
| :---: | :--- | :--- |
| 1 | Collection | รวบรวมข้อมูลจากหลายแหล่งมาไว้ที่เดียว |
| 2 | Cleaning | ลบแท็ก HTML, header/footer, ข้อความซ้ำ |
| 3 | Normalization | จัดรูปแบบข้อความ ช่องว่าง Unicode |
| 4 | Chunking | หั่นข้อความเป็น chunk |
| 5 | Metadata Enrichment | แปะข้อมูลบริบทให้แต่ละ chunk (ขั้นที่ผมทำ) |
| 6 | Embedding | แปลงข้อความเป็นเวกเตอร์ |
| 7 | Vector Database | เก็บเวกเตอร์เพื่อค้นคืน |
| 8 | LLM / Retrieval | ดึงข้อมูลไปประกอบคำตอบ |

### ขั้นที่ 5: Metadata Enrichment

chunk ที่ออกจากขั้นที่ 4 เป็นก้อนข้อความเปล่า ไม่มีอะไรบอกว่ามาจากไฟล์ไหน หน้าไหน ภาษาอะไร พอเอาไปใช้จริงระบบจะอ้างอิงกลับไปต้นฉบับไม่ได้ ตอบคำถามผู้ใช้ได้แต่บอกไม่ได้ว่าเอามาจากไหน โมดูลนี้เลยทำหน้าที่แปะข้อมูลพวกนั้นกลับเข้าไปให้ทุก chunk ก่อนส่งต่อไปขั้น embedding

ไฟล์ที่เขียนในส่วนนี้

- `src/metadata/schemas.py` กำหนด data contract ด้วย Pydantic (`EnrichedChunkItem`, `MetadataOutput`)
- `src/metadata/metadata_enricher.py` คลาส `MetadataEnricher` สืบทอดจาก `PipelineStep`
- `config/config.yaml` เพิ่มส่วน `metadata:`
- `run_pipeline.py` ต่อโมดูลเข้ากับ pipeline runner
- `tests/test_metadata.py` unit test

รายละเอียดเต็มอยู่ที่ [`docs/metadata_enrichment.md`](Sikibidi-six-seven-RAG/docs/metadata_enrichment.md) และคู่มือการใช้โมดูลอยู่ที่ [`src/metadata/README.md`](Sikibidi-six-seven-RAG/src/metadata/README.md)

## โครงสร้างไฟล์

```
LAB01/
├── README.md
└── Sikibidi-six-seven-RAG/        โปรเจกต์กลุ่ม นำเข้าด้วย git subtree
    ├── config/config.yaml         ค่าคอนฟิกของทุก step
    ├── data/
    │   ├── raw/                   ไฟล์ต้นฉบับ (Chap-01..12.pdf, sample.*)
    │   └── clean/ normalized/ chunks/ metadata/ embeddings/
    ├── docs/
    │   ├── metadata_enrichment.md
    │   └── person_1_collection_cleaning.md
    ├── src/
    │   ├── collection/ cleaning/ normalization/ chunking/
    │   ├── metadata/              ขั้นที่ 5
    │   ├── embedding/ vectordb/ retrieval/
    │   └── utils/base_step.py
    ├── tests/
    ├── requirements.txt
    └── run_pipeline.py
```

## วิธีรัน

ติดตั้ง dependencies ก่อน

```bash
cd LAB01/Sikibidi-six-seven-RAG
py -m pip install -r requirements.txt
```

รันเฉพาะขั้นที่ 5, รันทั้ง pipeline, และรัน test ตามลำดับ

```bash
py run_pipeline.py metadata
py run_pipeline.py all
py -m pytest tests/test_metadata.py -v
```

## ที่มาของโค้ดและข้อมูล

โฟลเดอร์ `Sikibidi-six-seven-RAG/` เป็นผลงานร่วมของกลุ่ม ผมนำเข้ามาด้วย `git subtree` แทนการก๊อปไฟล์ เพื่อให้ commit history ของต้นทางติดมาด้วย ตรวจสอบย้อนกลับได้ว่าใครเขียนส่วนไหน

| รายการ | แหล่งที่มา |
| :--- | :--- |
| source code โปรเจกต์กลุ่ม | https://github.com/PROxTAE/Sikibidi-six-seven-RAG |
| dataset `data/raw/Chap-01..12.pdf` | เอกสารประกอบการเรียนของรายวิชา |
| `pydantic` | https://github.com/pydantic/pydantic |
| `pyyaml` | https://github.com/yaml/pyyaml |
| `pytest` | https://github.com/pytest-dev/pytest |

ไม่มีการใช้ข้อมูลที่ละเมิดลิขสิทธิ์ ข้อมูลส่วนบุคคลที่ไม่ได้รับอนุญาต หรือข้อมูลผิดกฎหมาย

ถ้าต้องดึงงานที่กลุ่มอัปเดตเข้ามาเพิ่ม

```bash
git remote add rag https://github.com/PROxTAE/Sikibidi-six-seven-RAG.git   # ครั้งแรกครั้งเดียว
git subtree pull --prefix=LAB01/Sikibidi-six-seven-RAG rag main
```

## การส่งงาน

รายวิชานี้ให้ใช้ repository เดียวตลอดเทอม เก็บทุกใบงานและ final project ไว้ที่เดียว ของผมคือ https://github.com/Peemaxnaja/ATCS-CPE โดยแยกแต่ละใบงานไว้ในโฟลเดอร์ `LAB01` ถึง `LAB10` และมี `Final-Project/` ต่างหาก แต่ละโฟลเดอร์ต้องมี source code, dataset (ถ้ามี), รายงาน `.pdf` (ถ้ามี) และ `README.md` อธิบายใบงาน

ตอนส่งให้ commit และ push ก่อนกำหนด แล้วส่งลิงก์โฟลเดอร์ให้อาจารย์

```bash
git add LAB01/
git commit -m "LAB01: <สิ่งที่ทำ>"
git push origin main
```

ลิงก์ของใบงานนี้: https://github.com/Peemaxnaja/ATCS-CPE/tree/main/LAB01

อาจารย์ใช้ commit history และเวลาที่ push ประกอบการตรวจด้วย ผมจึงทยอย commit ระหว่างทำ ไม่รวบไว้ push ทีเดียวตอนใกล้ส่ง

เรื่องแหล่งข้อมูล รายวิชาเปิดให้เลือก dataset, source code หรือโมเดลจากที่ไหนก็ได้ ตราบใดที่ไม่ละเมิดกฎหมาย ลิขสิทธิ์ หรือเงื่อนไขของเจ้าของข้อมูล แต่ถ้าเอาของคนอื่นมาใช้ต้องอ้างอิงแหล่งที่มาหรือแนบ URL ไว้ใน README ทุกครั้ง การเอาผลงานคนอื่นมาใช้โดยไม่อ้างอิงถือว่าผิดหลัก academic integrity และมีผลต่อคะแนน
