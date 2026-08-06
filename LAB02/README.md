# LAB02: RAG Retrieval System ถาม-ตอบกฎหมายอาวุธปืนและความปลอดภัย

รายวิชา ATCS-CPE
สิรวิชญ์ ศิริสลุง 116730462023-6

## งานที่ทำ

เขียนระบบ RAG (Retrieval-Augmented Generation) ด้วย Python ตั้งแต่ต้น ไม่ใช้ LangChain หรือ LlamaIndex เพื่อให้เห็นกลไกข้างในจริงๆ ว่าตั้งแต่อ่านเอกสารจนถึงค้นเจอคำตอบมันผ่านอะไรบ้าง ครอบคลุม chunking, embedding, vector database และ semantic search

knowledge base ที่ใช้เป็นชุดถาม-ตอบเรื่องกฎหมายอาวุธปืนไทย ความปลอดภัย และการใช้งาน ที่ผมทำขึ้นเอง อยู่ที่ `data/gun_q_a.txt`

ข้อมูลชุดนี้ทำเพื่อการศึกษา ไม่ใช่ความเห็นทางกฎหมายรายกรณี ถ้ามีข้อพิพาทจริงต้องไปปรึกษาทนายหรือนายทะเบียนท้องที่ ระบบจะขึ้น disclaimer นี้ทุกครั้งที่ตอบ

### สิ่งที่แก้จากโครงร่างต้นฉบับ

skeleton ที่อาจารย์ให้มาออกแบบไว้อ่าน PDF ผมเปลี่ยนมาใช้ไฟล์ `.txt` แบบ Q&A ที่ทำเอง 313 คู่ เลยต้องเขียน parser ใหม่ให้รองรับรูปแบบ `[หมวด] / Q: / A:` และใช้ `line_no` แทนเลขหน้าในการอ้างอิงกลับต้นฉบับ metadata ที่เก็บจึงไม่ใช่แค่เลขหน้าอย่างเดิม แต่มี `category`, `question`, `answer`, `line_no`, `qa_id`, `part_idx`

ที่ต้องเปลี่ยนอีกอย่างคือ embedding model เพราะค่าเริ่มต้นจับภาษาไทยไม่ได้ ผมสลับไปใช้ `paraphrase-multilingual-MiniLM-L12-v2` และระหว่างรันบน Windows เจอ `UnicodeEncodeError` ตอน print ภาษาไทยลง console เลยเพิ่ม `sys.stdout.reconfigure(encoding="utf-8")` ไว้ใน `config.py` ส่วน `main.py` เขียนเพิ่มเป็น CLI วนรับคำถาม แสดง similarity score กับ disclaimer ต่อท้าย

### เรื่องภาษาใน dataset

ปัญหาที่เจอตอนออกแบบชุดข้อมูลคือ คนที่ถามเรื่องปืนจริงๆ ไม่ได้พิมพ์เป็นภาษาราชการ แต่เอกสารกฎหมายที่เอามาเรียบเรียงเขียนเป็นภาษาราชการล้วน ถ้าเก็บแค่แบบเดียว retriever จะจับคู่ไม่เจอ ผมเลยเก็บข้อเท็จจริงเดียวกันหลายระดับภาษา

```
[หมวด: กฎหมายอาวุธปืนและทะเบียน]                    "การแจ้งอาวุธปืนสูญหายต้องดำเนินการอย่างไร"
[หมวด: กฎหมายอาวุธปืนและทะเบียน | ภาษา: กันเอง]     "ปืนหายทำไงดี"
[หมวด: กฎหมายอาวุธปืนและทะเบียน | ภาษา: แสลง]      "ปืนหายทำไงวะ"
```

แบ่งเป็น 6 หมวดเนื้อหา ไม่ได้เขียนครบทั้งสามระดับทุกข้อ ตอนนี้ได้ทางการ 127 ข้อ กันเอง 98 ข้อ แสลง 88 ข้อ

| หมวด | จำนวน Q&A |
| :--- | :---: |
| การขออนุญาตและการครอบครอง | 52 |
| กฎหมายอาวุธปืนและทะเบียน | 54 |
| ความปลอดภัยและการเก็บรักษา | 57 |
| การป้องกันตัวและขอบเขตทางกฎหมาย | 52 |
| ชนิดและกลไกของอาวุธปืน | 50 |
| การดูแลรักษาและกีฬายิงปืน | 48 |
| รวม | 313 |

## สถาปัตยกรรม

```
data/gun_q_a.txt
       │
       ▼  Lab 1  document_loader.py
outputs/extracted_text.json        313 Q&A + line_no
       │
       ▼  Lab 2  text_splitter.py         CHUNK_SIZE=400, OVERLAP=50
outputs/chunks.json                419 chunks
       │
       ▼  Lab 3  embedding_model.py       paraphrase-multilingual-MiniLM-L12-v2
outputs/embeddings.npy             (419, 384) float32, L2-normalized
       │
       ▼  Lab 4  vector_store.py          FAISS IndexFlatIP
vector_db/document.index  +  vector_db/chunk_store.json
       │
       │        query ──► Lab 5  encode_query() ──► (384,) vector
       │                                                  │
       ▼                                                  ▼
       └──────────► Lab 6  FAISS similarity search ──► Lab 7 / main.py
```

เวกเตอร์ถูก normalize มาตั้งแต่ขั้น embedding แล้ว การใช้ `IndexFlatIP` (inner product) จึงให้ผลเท่ากับ cosine similarity คะแนนยิ่งสูงยิ่งใกล้

## โครงสร้างไฟล์

```
LAB02/
├── README.md
└── RAG-Project/
    ├── config.py                   paths, chunk size, model, top-k
    ├── main.py                     โปรแกรมถาม-ตอบแบบ interactive
    ├── requirements.txt
    │
    ├── data/gun_q_a.txt            knowledge base 313 Q&A
    │
    ├── labs/                       สคริปต์ทีละขั้น
    │   ├── lab01_extract_text.py       สกัด Q&A จากไฟล์ต้นฉบับ
    │   ├── lab02_chunking.py           แบ่ง chunk
    │   ├── lab03_create_embeddings.py  สร้าง embeddings
    │   ├── lab04_create_vector_db.py   สร้าง FAISS index
    │   ├── lab05_query_embedding.py    ทดลอง embed คำถาม
    │   ├── lab06_similarity_search.py  ทดลอง similarity search
    │   └── lab07_complete_retrieval.py รวมเป็น pipeline เดียว
    │
    ├── src/                        โมดูลที่ใช้ซ้ำ
    │   ├── document_loader.py          parser รูปแบบ [หมวด]/Q:/A:
    │   ├── text_splitter.py            chunking พร้อม overlap
    │   ├── embedding_model.py          wrapper ของ sentence-transformers
    │   ├── vector_store.py             wrapper ของ FAISS
    │   └── retriever.py                embed query + search
    │
    ├── outputs/                    ผลลัพธ์ระหว่างทาง แนบมาให้ตรวจ
    │   ├── extracted_text.json
    │   ├── chunks.json
    │   ├── embeddings.npy
    │   └── retrieval_results.json
    │
    └── vector_db/                  vector database ที่ build ไว้แล้ว
        ├── document.index
        └── chunk_store.json
```

## วิธีรัน

```bash
cd LAB02/RAG-Project
py -m pip install -r requirements.txt
```

ที่ต้องลงคือ `sentence-transformers` สำหรับโมเดล multilingual, `faiss-cpu` สำหรับ index และ similarity search, `numpy` และ `tqdm`

รันทีละขั้นตาม lab

```bash
py labs/lab01_extract_text.py        # -> outputs/extracted_text.json
py labs/lab02_chunking.py            # -> outputs/chunks.json
py labs/lab03_create_embeddings.py   # -> outputs/embeddings.npy
py labs/lab04_create_vector_db.py    # -> vector_db/
py labs/lab05_query_embedding.py     # ทดลอง embed คำถาม
py labs/lab06_similarity_search.py   # ทดลองค้น top-k
py labs/lab07_complete_retrieval.py  # -> outputs/retrieval_results.json
```

ตัวระบบถาม-ตอบต้องมี vector database ก่อน ถ้าจะสร้างเองต้องรัน lab 1 ถึง 4 ให้ครบ หรือใช้ไฟล์ใน `vector_db/` ที่แนบมาแล้วได้เลย

```bash
py main.py
```

```
--- RAG System for Firearms Law & Safety QA ---
--- Enter ('exit', 'quit', or 'q' to quit) ---

ถามเรื่องปืน กฎหมาย หรือความปลอดภัยได้เลย: _
```

## ผลการทดลอง

pipeline สกัด Q&A ได้ 313 คู่ แบ่งเป็น 419 chunks ได้ embedding ขนาด `(419, 384)` แบบ `float32` เก็บใน FAISS `IndexFlatIP` และตั้ง top-k ไว้ที่ 3

ผมทดสอบด้วยคำถาม 5 ข้อใน `lab07_complete_retrieval.py` เลือกให้กระจายทั้งหมวดและระดับภาษา ผลเต็มอยู่ใน [`outputs/retrieval_results.json`](RAG-Project/outputs/retrieval_results.json)

| คำถาม | ผลอันดับ 1 | หมวดที่ match | score | ตรงไหม |
| :--- | :--- | :--- | :---: | :---: |
| ปืนหายต้องทำยังไง | ปืนหายทำไงวะ | ทะเบียน (แสลง) | 0.75 | ตรง |
| ป.3 กับ ป.4 ต่างกันยังไง | ใบ ป.4 คืออะไร ต่างจาก ป.3 อย่างไร | ทะเบียน (ทางการ) | 0.58 | ตรง |
| พกปืนติดตัวได้ไหม | ปืนตกพื้นแล้วลั่นเองได้หรือไม่ | ความปลอดภัย | 0.78 | ไม่ตรง |
| เก็บปืนที่บ้านยังไงให้ปลอดภัย | ควรเก็บปืนไว้ที่บ้านอย่างไร | ความปลอดภัย | 0.78 | ตรง |
| โจรเข้าบ้านยิงได้ป่ะ | กระสุนทะลุผนังบ้านได้หรือไม่ | ความปลอดภัย | 0.74 | ไม่ตรง |

### สิ่งที่ได้ผล

ข้อแรกผมพิมพ์แบบกลางๆ ว่า "ปืนหายต้องทำยังไง" ซึ่งไม่ตรงกับประโยคไหนใน dataset เลย แต่ระบบดึงแสลง "ปืนหายทำไงวะ" (0.75) ขึ้นอันดับ 1 และกันเอง "ปืนหายทำไงดี" (0.72) อันดับ 2 ทั้งคู่ตอบถูก แรงที่ลงไปเขียนหลายระดับภาษาจึงคุ้ม เพราะ retriever ข้ามระดับภาษามาหยิบได้จริง

ข้อ 2 น่าสนใจกว่า score ต่ำสุดในชุด (0.58) แต่กลับตรงที่สุด เพราะคำถามมีคำเฉพาะอย่าง ป.3 ป.4 อยู่ โมเดลเลยล็อกเป้าถูกทั้งที่ความคล้ายโดยรวมไม่สูง สรุปได้ว่าเอา score ไปเทียบข้ามคำถามไม่ได้

### ที่พังคือข้อ 3 กับข้อ 5

สองข้อนี้ตอบผิด ทั้งที่ score สูงกว่าข้อที่ตอบถูกเสียอีก ดู top-3 เต็มๆ แล้วเห็นปัญหาชัด

```
"พกปืนติดตัวได้ไหม"
  0.7847  ปืนตกพื้นแล้วลั่นเองได้หรือไม่          คนละเรื่อง
  0.7833  เอาปืนไว้ในรถได้ป่ะ                     พอเกี่ยว
  0.7782  เอาปืนไว้ในรถได้ไหม                     พอเกี่ยว
  คำตอบที่ควรได้คือเรื่องใบ ป.12 ใบอนุญาตพกพา ซึ่งไม่ติด top-3

"โจรเข้าบ้านยิงได้ป่ะ"
  0.7409  กระสุนทะลุผนังบ้านได้หรือไม่            คนละเรื่อง
  0.6865  ป้องกันเกินสมควรแก่เหตุคืออะไร          เกี่ยวข้อง
  0.6701  โจรเข้าบ้านยิงได้เลยป่ะ                 แทบเป็นคำถามเดียวกัน แต่ได้แค่อันดับ 3
```

ข้อ 3 คะแนนทั้งสามอันดับห่างกันไม่ถึง 0.007 แปลว่าโมเดลแยกไม่ออกจริงๆ สิ่งที่มันจับได้คือรูปประโยค "ปืน + อะไรสักอย่าง + ได้ไหม" ไม่ใช่เจตนาของคำถาม ส่วนข้อ 5 ชัดกว่านั้น คำว่า "บ้าน" ที่โผล่ในทั้งสองประโยคดัน "กระสุนทะลุผนังบ้าน" ขึ้นเหนือ "โจรเข้าบ้านยิงได้เลยป่ะ" ที่แทบเป็นคำถามเดียวกันกับที่ผมพิมพ์

เท่าที่วิเคราะห์ได้ ส่วนหนึ่งมาจาก `MiniLM-L12` เป็นโมเดลเล็กแค่ 384 มิติ แลกความเร็วกับความละเอียดในการแยกความหมายภาษาไทย อีกส่วนมาจากการที่ `IndexFlatIP` ค้นทั้ง 419 chunks เท่ากันหมด ทั้งที่ผมอุตส่าห์เก็บ `category` ไว้ในทุก chunk แต่ยังไม่ได้เอามาใช้กรองอะไรเลย

### จะทำต่อยังไง

อย่างแรกคือลองโมเดลใหญ่ขึ้น เช่น `paraphrase-multilingual-mpnet-base-v2` ที่ 768 มิติ ดูว่าแยกความหมายภาษาไทยดีขึ้นแค่ไหน

ปัญหาข้อ 5 ที่คำตอบถูกอยู่อันดับ 3 แก้ด้วย reranker แบบ cross-encoder ได้ตรงๆ คือดึง top-10 มาก่อนแล้วให้ reranker จัดอันดับใหม่เหลือ top-3 ส่วนข้อ 3 ที่หลุดไปคนละหมวด น่าจะช่วยได้ด้วย metadata filtering ใช้ `category` จำกัดขอบเขตก่อนค้น

คำเฉพาะอย่าง ป.12 หรือ "พกพา" ที่ semantic search จับไม่ติด ต้องพึ่ง hybrid search ผสม BM25 เข้าไป และควรมี score threshold ตัดผลที่ไม่มั่นใจทิ้ง ดีกว่าตอบผิดแบบมั่นใจ

## ที่มาของโค้ดและข้อมูล

| รายการ | แหล่งที่มา |
| :--- | :--- |
| โครงร่างโปรเจกต์และแนวทาง lab 01-07 | [aproot-en/Advanced-Topic-in-Computer-Software-Course](https://github.com/aproot-en/Advanced-Topic-in-Computer-Software-Course) โฟลเดอร์ `DL-03-LLM Retrieval System` ของอาจารย์ Anuruk Prommakhot |
| `data/gun_q_a.txt` | ผมทำขึ้นเองสำหรับใบงานนี้ เรียบเรียงจากข้อมูลสาธารณะเรื่องกฎหมายอาวุธปืนไทย |
| กฎหมายที่อ้างถึงในเนื้อหา | พระราชบัญญัติอาวุธปืน เครื่องกระสุนปืน วัตถุระเบิด ดอกไม้เพลิง และสิ่งเทียมอาวุธปืน พ.ศ. 2490 |
| embedding model | [`paraphrase-multilingual-MiniLM-L12-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) สัญญาอนุญาต Apache-2.0 |
| `sentence-transformers` | https://github.com/UKPLab/sentence-transformers |
| `faiss` | https://github.com/facebookresearch/faiss |
| `numpy` | https://github.com/numpy/numpy |
| `tqdm` | https://github.com/tqdm/tqdm |

ไม่มีการใช้ข้อมูลที่ละเมิดลิขสิทธิ์ ข้อมูลส่วนบุคคลที่ไม่ได้รับอนุญาต หรือข้อมูลผิดกฎหมาย เนื้อหาใน dataset เรียบเรียงเพื่อการศึกษา ไม่ใช่คำแนะนำทางกฎหมาย

## การส่งงาน

รายละเอียดข้อกำหนดการส่งงานของรายวิชาอยู่ใน [README ของ LAB01](../LAB01/README.md) ใช้เหมือนกันทุกใบงาน

```bash
git add LAB02/
git commit -m "LAB02: <สิ่งที่ทำ>"
git push origin main
```

ลิงก์ของใบงานนี้: https://github.com/Peemaxnaja/ATCS-CPE/tree/main/LAB02
