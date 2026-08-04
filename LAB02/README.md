# LAB02 — RAG Retrieval System (Thai Firearms Law & Safety QA)

**รายวิชา:** ATCS-CPE
**ชื่อ-นามสกุล:** สิรวิชญ์ ศิริสลุง
**รหัสนักศึกษา:** 116730462023-6

---

## 1. รายละเอียดใบงาน (Overview)

สร้างระบบ **RAG (Retrieval-Augmented Generation)** แบบ from scratch ด้วย Python โดยไม่ใช้เฟรมเวิร์กสำเร็จรูป (ไม่มี LangChain / LlamaIndex) เพื่อทำความเข้าใจกลไกภายในของ Retrieval Pipeline ตั้งแต่การอ่านเอกสาร → Chunking → Embedding → Vector Database → Semantic Search

**Knowledge Base ที่เลือกใช้:** ชุดข้อมูลถาม-ตอบเกี่ยวกับ **กฎหมายอาวุธปืนไทย ความปลอดภัย และการใช้งาน** ที่จัดทำขึ้นเอง (`data/gun_q_a.txt`)

> ⚠️ **ข้อจำกัดการใช้งาน:** ข้อมูลในชุดนี้จัดทำเพื่อการศึกษาเท่านั้น ไม่ใช่ความเห็นทางกฎหมายรายกรณี หากมีข้อพิพาทให้ปรึกษาทนายความหรือนายทะเบียนท้องที่ ระบบจะแสดง disclaimer นี้ทุกครั้งที่ตอบคำถาม

### สิ่งที่ปรับปรุงจากโครงร่างต้นฉบับ

โครงร่างโปรเจกต์ (skeleton) มาจาก repository ประกอบการเรียนของอาจารย์ผู้สอน ซึ่งออกแบบไว้สำหรับอ่าน **PDF** ในใบงานนี้ได้ดัดแปลงและพัฒนาต่อดังนี้

| หัวข้อ | โครงร่างต้นฉบับ | สิ่งที่พัฒนาในใบงานนี้ |
| :--- | :--- | :--- |
| แหล่งข้อมูล | PDF (`main_document1.pdf`) | ไฟล์ `.txt` รูปแบบ Q&A ที่จัดทำเอง 313 คู่ |
| Document Loader | สกัดข้อความจาก PDF + เลขหน้า | เขียน parser สำหรับรูปแบบ `[หมวด] / Q: / A:` และใช้ `line_no` แทนเลขหน้าเพื่ออ้างอิงกลับไปยังต้นฉบับ |
| Metadata | page number | `category`, `question`, `answer`, `line_no`, `qa_id`, `part_idx` |
| Embedding Model | ค่าเริ่มต้น | `paraphrase-multilingual-MiniLM-L12-v2` เพื่อรองรับภาษาไทย |
| การรองรับภาษาไทยบน Windows | — | เพิ่ม `sys.stdout.reconfigure(encoding="utf-8")` ใน `config.py` แก้ปัญหา `UnicodeEncodeError` บน console |
| Interactive CLI | — | `main.py` แบบวนรับคำถามจากผู้ใช้ พร้อมแสดง similarity score และ disclaimer |

### จุดเด่นของ Dataset: ออกแบบให้รองรับหลายระดับภาษา

ปัญหาสำคัญของระบบ Retrieval ภาษาไทยคือ ผู้ใช้จริงมักไม่ได้ถามด้วยภาษาทางการ ชุดข้อมูลนี้จึงเก็บ **ข้อเท็จจริงเดียวกันในสามระดับภาษา** เพื่อให้ retriever จับคู่คำถามได้ไม่ว่าผู้ใช้จะพิมพ์มาแบบไหน

```
[หมวด: กฎหมายอาวุธปืนและทะเบียน]                    → ทางการ  "การแจ้งอาวุธปืนสูญหายต้องดำเนินการอย่างไร"
[หมวด: กฎหมายอาวุธปืนและทะเบียน | ภาษา: กันเอง]     → กันเอง   "ปืนหายทำไงดี"
[หมวด: กฎหมายอาวุธปืนและทะเบียน | ภาษา: แสลง]      → แสลง     "ปืนหายทำไงวะ"
```

**6 หมวดเนื้อหา × 3 ระดับภาษา = 18 หมวดย่อย**

| # | หมวดเนื้อหา | จำนวน Q&A |
| :---: | :--- | :---: |
| 1 | การขออนุญาตและการครอบครอง | 52 |
| 2 | กฎหมายอาวุธปืนและทะเบียน | 54 |
| 3 | ความปลอดภัยและการเก็บรักษา | 57 |
| 4 | การป้องกันตัวและขอบเขตทางกฎหมาย | 52 |
| 5 | ชนิดและกลไกของอาวุธปืน | 50 |
| 6 | การดูแลรักษาและกีฬายิงปืน | 48 |
| | **รวม** | **313** |

---

## 2. สถาปัตยกรรมระบบ (Architecture)

```
data/gun_q_a.txt
       │
       ▼  Lab 1 — document_loader.py
outputs/extracted_text.json        313 Q&A records + line_no
       │
       ▼  Lab 2 — text_splitter.py         (CHUNK_SIZE=400, OVERLAP=50)
outputs/chunks.json                419 chunks
       │
       ▼  Lab 3 — embedding_model.py       (paraphrase-multilingual-MiniLM-L12-v2)
outputs/embeddings.npy             (419, 384) float32, L2-normalized
       │
       ▼  Lab 4 — vector_store.py          (FAISS IndexFlatIP)
vector_db/document.index  +  vector_db/chunk_store.json
       │
       │        user query ──► Lab 5 — encode_query() ──► (384,) vector
       │                                                        │
       ▼                                                        ▼
       └────────────────► Lab 6 — FAISS similarity search (top-k) ──► Lab 7 / main.py
```

**หมายเหตุเชิงเทคนิค:** เวกเตอร์ถูก normalize ตั้งแต่ขั้น embedding ดังนั้นการใช้ FAISS `IndexFlatIP` (Inner Product) จึงให้ผลเทียบเท่า **Cosine Similarity** — คะแนนยิ่งสูงยิ่งใกล้เคียง

---

## 3. โครงสร้างไฟล์ใน LAB02

```
LAB02/
├── README.md                       <- ไฟล์นี้
└── RAG-Project/
    ├── config.py                   <- ค่าคอนฟิกกลาง (paths, chunk size, model, top-k)
    ├── main.py                     <- โปรแกรมหลัก ถาม-ตอบแบบ interactive
    ├── requirements.txt
    │
    ├── data/
    │   └── gun_q_a.txt             <- Knowledge Base 313 Q&A (จัดทำเอง)
    │
    ├── labs/                       <- สคริปต์ทีละขั้นตอน
    │   ├── lab01_extract_text.py       สกัด Q&A จากไฟล์ต้นฉบับ
    │   ├── lab02_chunking.py           แบ่งข้อความเป็น chunks
    │   ├── lab03_create_embeddings.py  สร้าง embeddings
    │   ├── lab04_create_vector_db.py   สร้าง FAISS index
    │   ├── lab05_query_embedding.py    ทดลอง embed คำถาม
    │   ├── lab06_similarity_search.py  ทดลอง similarity search
    │   └── lab07_complete_retrieval.py รวมทุกขั้นเป็น pipeline เดียว
    │
    ├── src/                        <- โมดูลหลักที่ใช้ซ้ำได้
    │   ├── document_loader.py          parser รูปแบบ [หมวด]/Q:/A:
    │   ├── text_splitter.py            chunking พร้อม overlap
    │   ├── embedding_model.py          wrapper ของ sentence-transformers
    │   ├── vector_store.py             wrapper ของ FAISS
    │   └── retriever.py                รวม embed query + search
    │
    ├── outputs/                    <- ผลลัพธ์ระหว่างทาง (แนบมาเพื่อตรวจสอบ)
    │   ├── extracted_text.json
    │   ├── chunks.json
    │   ├── embeddings.npy
    │   └── retrieval_results.json
    │
    └── vector_db/                  <- ฐานข้อมูลเวกเตอร์ที่สร้างไว้แล้ว
        ├── document.index
        └── chunk_store.json
```

---

## 4. วิธีการรันโค้ด (How to Run)

### 4.1 ติดตั้ง Dependencies

```bash
cd LAB02/RAG-Project
py -m pip install -r requirements.txt
```

| Library | Purpose |
| :--- | :--- |
| `sentence-transformers` | โหลดโมเดล multilingual สำหรับสร้าง embeddings |
| `faiss-cpu` | Vector index และ similarity search |
| `numpy` | จัดการ array ของเวกเตอร์ |
| `tqdm` | progress bar ระหว่างสร้าง embeddings |

### 4.2 รันทีละขั้นตอน (Lab 1 → Lab 7)

```bash
py labs/lab01_extract_text.py        # -> outputs/extracted_text.json
py labs/lab02_chunking.py            # -> outputs/chunks.json
py labs/lab03_create_embeddings.py   # -> outputs/embeddings.npy
py labs/lab04_create_vector_db.py    # -> vector_db/document.index, chunk_store.json
py labs/lab05_query_embedding.py     # ทดลอง embed คำถาม
py labs/lab06_similarity_search.py   # ทดลองค้นหา top-k
py labs/lab07_complete_retrieval.py  # -> outputs/retrieval_results.json
```

### 4.3 รันระบบถาม-ตอบ

ต้องรัน **Lab 1 ถึง Lab 4** ให้ครบก่อน เพื่อสร้าง vector database (หรือใช้ไฟล์ใน `vector_db/` ที่แนบมาแล้วได้เลย)

```bash
py main.py
```

```
--- RAG System for Firearms Law & Safety QA ---
--- Enter ('exit', 'quit', or 'q' to quit) ---

ถามเรื่องปืน กฎหมาย หรือความปลอดภัยได้เลย: _
```

---

## 5. ผลการทดลอง (Results)

### 5.1 สถิติของ Pipeline

| รายการ | ค่า |
| :--- | :--- |
| Q&A pairs ที่สกัดได้ | 313 |
| Chunks หลังแบ่ง | 419 |
| ขนาด Embedding | `(419, 384)` `float32` |
| Index type | FAISS `IndexFlatIP` (≡ cosine similarity) |
| Top-K ที่ใช้ | 3 |

### 5.2 ตัวอย่างผลการค้นคืน

ทดสอบด้วยคำถาม 5 ข้อใน `lab07_complete_retrieval.py` ครอบคลุมหลายหมวดและหลายระดับภาษา ผลลัพธ์เต็มอยู่ที่ [`outputs/retrieval_results.json`](RAG-Project/outputs/retrieval_results.json)

| # | Query (ภาษาพูด) | Top-1 Match | Category ที่ match | Score | ผล |
| :---: | :--- | :--- | :--- | :---: | :---: |
| 1 | `ปืนหายต้องทำยังไง` | "ปืนหายทำไงวะ" | ทะเบียน \| **แสลง** | 0.75 | ✅ |
| 2 | `ป.3 กับ ป.4 ต่างกันยังไง` | "ใบ ป.4 คืออะไร ต่างจาก ป.3 อย่างไร" | ทะเบียน (ทางการ) | 0.58 | ✅ |
| 3 | `พกปืนติดตัวได้ไหม` | "ปืนตกพื้นแล้วลั่นเองได้หรือไม่" | ความปลอดภัย | 0.78 | ❌ |
| 4 | `เก็บปืนที่บ้านยังไงให้ปลอดภัย` | "ควรเก็บปืนไว้ที่บ้านอย่างไร" | ความปลอดภัย | 0.78 | ✅ |
| 5 | `โจรเข้าบ้านยิงได้ป่ะ` | "กระสุนทะลุผนังบ้านได้หรือไม่" | ความปลอดภัย | 0.74 | ❌ |

### 5.3 วิเคราะห์ผล (Analysis)

**สิ่งที่ทำงานได้ดี — การออกแบบ dataset หลายระดับภาษาได้ผลจริง**

คำถามข้อ 1 `ปืนหายต้องทำยังไง` เขียนด้วยภาษากลาง ๆ แต่ระบบดึงอันดับ 1 มาจากหมวด **แสลง** ("ปืนหายทำไงวะ" 0.75) และอันดับ 2 จากหมวด **กันเอง** ("ปืนหายทำไงดี") ได้ถูกต้อง ยืนยันว่าการเก็บข้อเท็จจริงเดียวกันในหลายระดับภาษาช่วยให้ retriever จับคู่ความหมายได้ แม้รูปประโยคต่างกันมาก

ข้อ 2 น่าสนใจตรงที่ score ต่ำที่สุด (0.58) แต่กลับ match **ถูกที่สุด** — เพราะคำถามเป็นเชิงเปรียบเทียบที่มีเนื้อหาเฉพาะเจาะจง (`ป.3` / `ป.4`) โมเดลจึงจับได้แม่นแม้ค่าความคล้ายไม่สูง

**ข้อจำกัดที่พบ — score สูงไม่ได้แปลว่า match ถูก**

ข้อ 3 และ 5 ให้ผลผิด ทั้งที่ score สูงกว่าข้อที่ถูกต้องเสียอีก ดูรายละเอียด top-3 จะเห็นปัญหาชัดขึ้น

```
Query: "พกปืนติดตัวได้ไหม"
  1. 0.78  ปืนตกพื้นแล้วลั่นเองได้หรือไม่          ❌ คนละเรื่อง
  2. 0.78  เอาปืนไว้ในรถได้ป่ะ                     ~ ใกล้เคียง
  3. 0.78  เอาปืนไว้ในรถได้ไหม                     ~ ใกล้เคียง
  (คำตอบที่ควรได้คือเรื่องใบ ป.12 ใบอนุญาตพกพา — ไม่ติด top-3)

Query: "โจรเข้าบ้านยิงได้ป่ะ"
  1. 0.74  กระสุนทะลุผนังบ้านได้หรือไม่            ❌ คนละเรื่อง
  2. 0.69  ป้องกันเกินสมควรแก่เหตุคืออะไร          ~ เกี่ยวข้อง
  3. 0.67  โจรเข้าบ้านยิงได้เลยป่ะ                 ✅ ตรงที่สุด แต่อยู่อันดับ 3
```

สาเหตุที่วิเคราะห์ได้:

1. **โมเดลจับโครงสร้างประโยคมากกว่าความหมายเฉพาะ** — ข้อ 3 ทั้ง top-3 ได้ score เท่ากันหมด (0.78) แสดงว่าโมเดลแยกไม่ออกจริง ๆ สิ่งที่มันจับได้คือ pattern "ปืน + ... + ได้ไหม/ได้หรือไม่" ไม่ใช่เจตนาของคำถาม
2. **คำที่ปรากฏร่วมกันดึงคะแนนขึ้น** — ข้อ 5 คำว่า "บ้าน" ทำให้ "กระสุนทะลุผนัง**บ้าน**" ชนะ "**โจรเข้าบ้าน**ยิงได้เลยป่ะ" ที่แทบเป็นคำถามเดียวกัน
3. **`MiniLM-L12` เป็นโมเดลขนาดเล็ก (384 มิติ)** — แลกความเร็วกับความละเอียดในการแยกความหมายภาษาไทย
4. **`IndexFlatIP` ไม่มีการกรองด้วย metadata** — ค้นทั้ง 419 chunks เท่ากันหมด ไม่ได้ใช้ `category` ช่วยจำกัดขอบเขต

### 5.4 แนวทางพัฒนาต่อ (Future Work)

| แนวทาง | คาดว่าจะแก้ปัญหา |
| :--- | :--- |
| ใช้โมเดลที่ใหญ่ขึ้น เช่น `paraphrase-multilingual-mpnet-base-v2` (768 มิติ) | ความละเอียดในการแยกความหมายภาษาไทย |
| เพิ่ม **Reranker** (cross-encoder) จัดอันดับซ้ำจาก top-10 → top-3 | ข้อ 5 ที่คำตอบถูกอยู่อันดับ 3 |
| **Hybrid search** — ผสม BM25 (keyword) กับ vector search | คำเฉพาะอย่าง `ป.12`, `พกพา` ที่ semantic จับไม่ติด |
| **Metadata filtering** ด้วย `category` ก่อนค้น | ข้อ 3 ที่ข้ามหมวดไปหยิบคำตอบผิดหมวด |
| เพิ่มเกณฑ์ **score threshold** ตัดผลที่ไม่มั่นใจทิ้ง | ลดการตอบผิดแบบมั่นใจ |

---

## 6. แหล่งที่มาและการอ้างอิง (Citation)

| รายการ | แหล่งที่มา / หมายเหตุ |
| :--- | :--- |
| โครงร่างโปรเจกต์ (skeleton) และแนวทางใบงาน Lab 01–07 | [aproot-en/Advanced-Topic-in-Computer-Software-Course](https://github.com/aproot-en/Advanced-Topic-in-Computer-Software-Course) — `DL-03-LLM Retrieval System` โดยอาจารย์ผู้สอน (Anuruk Prommakhot) |
| Dataset `data/gun_q_a.txt` | **จัดทำขึ้นเองสำหรับใบงานนี้** โดยเรียบเรียงจากข้อมูลสาธารณะเรื่องกฎหมายอาวุธปืนไทย |
| กฎหมายอ้างอิงในเนื้อหา | พระราชบัญญัติอาวุธปืน เครื่องกระสุนปืน วัตถุระเบิด ดอกไม้เพลิง และสิ่งเทียมอาวุธปืน พ.ศ. 2490 |
| Embedding model | [`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) — Apache-2.0 |
| `sentence-transformers` | https://github.com/UKPLab/sentence-transformers |
| `faiss` | https://github.com/facebookresearch/faiss |
| `numpy` | https://github.com/numpy/numpy |
| `tqdm` | https://github.com/tqdm/tqdm |

> ⚠️ ไม่มีการใช้ข้อมูลที่ละเมิดลิขสิทธิ์ ข้อมูลส่วนบุคคลที่ไม่ได้รับอนุญาต หรือข้อมูลที่ผิดกฎหมาย เนื้อหาในชุดข้อมูลเป็นการเรียบเรียงเพื่อการศึกษา ไม่ใช่คำแนะนำทางกฎหมาย

---

## 7. วิธีการส่งงานของรายวิชา (Submission Guidelines)

ข้อกำหนดการส่งงานตามที่อาจารย์ผู้สอนกำหนด ใช้กับทุกใบงานตลอดรายวิชา

### 7.1 หลักการ

นักศึกษาทุกคนต้องสร้างบัญชี GitHub และใช้ **Repository เพียง 1 Repository ตลอดทั้งรายวิชา** เพื่อรวบรวมใบงาน (LAB) และโครงงาน (Final Project) ไว้ในที่เดียว

Repository ของข้าพเจ้า: **https://github.com/Peemaxnaja/ATCS-CPE**

### 7.2 โครงสร้างโฟลเดอร์ที่กำหนด

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

### 7.3 ไฟล์ที่ต้องมีในแต่ละโฟลเดอร์ LAB

| ไฟล์ | รายละเอียด |
| :--- | :--- |
| Source Code | `.ipynb` หรือ `.py` |
| Dataset | ถ้ามี |
| รายงานผลการทดลอง | `.pdf` (ถ้ามี) |
| `README.md` | อธิบายรายละเอียดของใบงาน |

### 7.4 ขั้นตอนการส่ง

1. ทำใบงานให้เสร็จภายในโฟลเดอร์ `LABxx/` ของตนเอง
2. **Commit และ Push** ขึ้น GitHub **ก่อนวันและเวลาที่กำหนดส่ง**
3. ส่ง **ลิงก์ Repository** หรือ **ลิงก์โฟลเดอร์ของ LAB** ที่กำหนด ผ่านระบบที่อาจารย์แจ้ง

```bash
git add LAB02/
git commit -m "LAB02: <อธิบายสิ่งที่ทำ>"
git push origin main
```

ลิงก์สำหรับส่ง LAB02: https://github.com/Peemaxnaja/ATCS-CPE/tree/main/LAB02

> 📌 อาจารย์จะใช้ **commit history** และ **เวลาที่ Push ขึ้น GitHub** เป็นข้อมูลประกอบการตรวจและประเมินผล

### 7.5 การเลือกใช้ Dataset และแหล่งข้อมูล

- เลือกใช้ Dataset, Source Code, โมเดล หรือแหล่งอ้างอิงจากที่ใดก็ได้อย่างอิสระ — เว็บไซต์ งานวิจัย หน่วยงานภาครัฐ หรือ Open Dataset จากทั่วโลก ตราบใดที่ไม่ละเมิดกฎหมาย ลิขสิทธิ์ หรือเงื่อนไขการใช้งานของเจ้าของข้อมูล
- หากนำ Dataset, Source Code, โมเดล หรือข้อมูลของผู้อื่นมาใช้ **ต้องอ้างอิงแหล่งที่มา (Citation) หรือแนบลิงก์ (URL)** ไปยังแหล่งข้อมูลต้นฉบับไว้ใน `README.md` หรือรายงานทุกครั้ง
- **ข้อควรระวัง:** ห้ามใช้ข้อมูลที่ละเมิดลิขสิทธิ์ ข้อมูลส่วนบุคคล (Personal Data) ที่ไม่ได้รับอนุญาต หรือข้อมูลที่ผิดกฎหมาย การนำผลงานของผู้อื่นมาใช้โดยไม่อ้างอิงแหล่งที่มาถือว่าขัดต่อหลักจริยธรรมทางวิชาการ (Academic Integrity) และอาจส่งผลต่อการประเมินผลรายวิชา

### 7.6 หมายเหตุ

ควร Commit งานอย่างสม่ำเสมอระหว่างการพัฒนา ไม่ควรรอ Commit เพียงครั้งเดียวก่อนถึงกำหนดส่ง เพื่อป้องกันข้อมูลสูญหาย และแสดงให้เห็นถึงลำดับขั้นตอนการพัฒนางานอย่างเป็นระบบ
