# LAB04: RAG System Development I — ระบบถาม-ตอบความรู้ยุทโธปกรณ์และกิจการทหาร

รายวิชา ATCS-CPE
สิรวิชญ์ ศิริสลุง 116730462023-6

## งานที่ทำ

ต่อยอดจาก LAB02 ที่ทำ retrieval แบบ dense อย่างเดียว มาเป็นระบบ RAG เต็มรูป โดยเพิ่มของ Stage 2 เข้าไป คือ BM25 keyword search, การรวมอันดับด้วย RRF, cross-encoder reranking, query transformation, การให้ LLM เขียนคำตอบพร้อมอ้างอิง, ความจำบทสนทนา และที่สำคัญที่สุดคือ **ชุดวัดผล** ที่ทำให้ตอบได้ว่าแต่ละเทคนิคช่วยจริงหรือไม่ ด้วย Hit@k, Recall@k, Precision@k, MRR และ nDCG

ทุกฟีเจอร์เปิด-ปิดได้จาก `config.py` ตัวเดียว จุดประสงค์คือปิดทีละตัวแล้ววัดว่าคะแนนเปลี่ยนไปเท่าไร

knowledge base เป็นชุดถาม-ตอบความรู้ทางทหารที่ผมทำขึ้นเอง 182 คู่ อยู่ที่ `data/military_qa.txt`

ขอบเขตของข้อมูลคือ **ความรู้เชิงสารานุกรม** เท่านั้น — การจำแนกประเภท หลักการทำงาน ประวัติ และคำศัพท์ ไม่มีข้อมูลเชิงปฏิบัติการ วิธีสร้างหรือดัดแปลงอาวุธ ตัวเลขสมรรถนะทั้งหมดเป็นค่าโดยประมาณจากแหล่งข้อมูลสาธารณะ ระบบขึ้น disclaimer นี้ท้ายคำตอบทุกครั้ง

### สิ่งที่แก้จากโครงร่างต้นฉบับ

skeleton ที่อาจารย์ให้มาผูกกับโดเมนสุขภาพทางเพศไว้หลายจุด ผมเปลี่ยนทั้งหมดมาเป็นโดเมนทหาร ได้แก่ `SYSTEM_PROMPT`, `REWRITE_PROMPT`, `MULTI_QUERY_PROMPT`, `HYDE_PROMPT`, ตาราง `SLANG_MAP` ใน `query_transform.py`, ตาราง `TO_SLANG` ใน `build_golden_set.py` และคำถามตัวอย่างใน `lab07`

นอกจากเปลี่ยนโดเมนแล้ว มีสามจุดที่เป็นบั๊กจริงและต้องแก้

**หนึ่ง — โหมดไม่ใช้ LLM ตอบว่า "ไม่พบข้อมูล" ทุกครั้ง**

`NoLLM.chat()` ตัดข้อความบริบทออกจาก prompt ด้วยการ split ที่สตริง `"reference data :"` และ `"Q of user"` แต่ `USER_PROMPT` ในไฟล์เดียวกันเขียนหัวข้อไว้เป็นภาษาไทยว่า `"ข้อมูลอ้างอิง:"` และ `"คำถามของผู้ใช้:"` ทั้งสองสตริงจึงไม่มีทางเจอ ฟังก์ชันเลยคืน `NO_CONTEXT_MESSAGE` เสมอ ทั้งที่ retriever ค้นเจอเอกสารมาแล้ว

ผมย้ายหัวข้อทั้งสองออกมาเป็นค่าคงที่ `CONTEXT_HEADER` / `QUESTION_HEADER` ใน `prompt_templates.py` แล้วให้ `generator.py` import ไปใช้ ต่อไปแก้ prompt แล้วโหมดนี้จะไม่หลุดอีก เพราะไม่มีใครเดาสตริงเอง

จุดนี้สำคัญกับงานนี้เป็นพิเศษ เพราะเครื่องที่ผมรันไม่มี LLM ให้ใช้ ทั้งใบงานจึงต้องรันด้วย `USE_LLM = False` ถ้าไม่แก้ ผลวัดคำตอบจะออกมาว่าระบบปฏิเสธ 100%

**สอง — golden set สร้าง variant "partial" ให้ภาษาไทยแทบไม่ได้เลย**

`make_variants()` ตัดคำด้วย `re.split(r"[\s()/]+", ...)` ซึ่งอาศัยช่องว่าง คำถามภาษาไทยล้วนจึงถูกนับเป็นก้อนเดียว ไม่ผ่านเงื่อนไข `len(words) >= 2` ผลคือจาก 60 ข้อ สร้าง partial ได้แค่ 20 ข้อ เฉพาะข้อที่บังเอิญมีชื่อรุ่นภาษาอังกฤษคั่นอยู่อย่าง `AK-47` หรือ `S-400`

ผมเปลี่ยนมาตัดคำไทยด้วย pythainlp (engine `newmm`) แบบเดียวกับที่ BM25 ใช้อยู่แล้ว แยกออกมาเป็นฟังก์ชัน `content_words()` และเพิ่มคำเชื่อมไทยเข้า `STOPWORDS` เพราะพอตัดคำจริงแล้ว คำอย่าง "กับ" "จาก" "โดย" โผล่ขึ้นมาเต็มไปหมด ตอนนี้สร้าง partial ได้ครบ 60 จาก 60 ข้อ

**สาม — `SHOW_SOURCES` เปิดไว้แต่โค้ดที่แสดงผลถูก comment ทิ้ง**

ใน `main.py` บล็อกที่พิมพ์รายการแหล่งอ้างอิงถูก comment ไว้ทั้งก้อน ตั้งค่ายังไงก็ไม่แสดง ผมเปิดกลับมาและแปลข้อความเป็นไทย เพราะใบงานนี้ต้องตรวจสอบย้อนกลับได้ว่าเลข `[1]` ในคำตอบมาจากคู่ Q&A ไหน บรรทัดที่เท่าไรของไฟล์ต้นฉบับ

ค่าเริ่มต้นอื่นที่เปลี่ยน — `USE_LLM = False` (ให้ clone มาแล้วรันได้เลยโดยไม่ต้องมี Ollama) และ `SOURCE_FILE` ชี้ไป `military_qa.txt`

## ชุดข้อมูล

รูปแบบเดียวกับ LAB02 คือ `[หมวด]` / `Q:` / `A:` คั่นแต่ละคู่ด้วยบรรทัดว่าง เขียนใหม่ทั้งหมด 182 คู่ กระจาย 12 หมวดให้ใกล้เคียงกัน หมวดละ 15-16 ข้อ เพื่อไม่ให้หมวดใหญ่กินพื้นที่ตอนสุ่ม golden set

| หมวด | จำนวน Q&A |
| :--- | :---: |
| อาวุธปืนเล็ก | 15 |
| ปืนใหญ่และอาวุธสนับสนุน | 15 |
| รถถังและยานเกราะ | 15 |
| อากาศยานรบ | 15 |
| เฮลิคอปเตอร์ทางทหาร | 15 |
| เรือรบและเรือดำน้ำ | 15 |
| ขีปนาวุธและการป้องกันภัยทางอากาศ | 15 |
| อากาศยานไร้คนขับและสงครามอิเล็กทรอนิกส์ | 15 |
| กองทัพไทย | 15 |
| หลักนิยมและคำศัพท์ทางทหาร | 15 |
| สงครามไซเบอร์และปฏิบัติการอวกาศ | 16 |
| อาวุธนิวเคลียร์และการควบคุมอาวุธ | 16 |
| **รวม** | **182** |

คำตอบยาวเฉลี่ย 281 ตัวอักษร ยาวสุด 363 ที่ `CHUNK_SIZE = 400` จึงมีแค่ 2 ข้อที่ถูกตัดเป็น 2 ชิ้น รวมได้ 184 chunks — ต่างจาก LAB02 ที่ 313 คู่แตกเป็น 419 chunks เพราะคราวนี้ผมคุมความยาวคำตอบไว้ตั้งแต่ตอนเขียน dataset

## สถาปัตยกรรม

```
data/military_qa.txt
       │
       ▼  document_loader.py                182 Q&A + category + line_no
outputs/extracted_text.json
       │
       ▼  text_splitter.py                  CHUNK_SIZE=400, OVERLAP=50
outputs/chunks.json                         184 chunks
       │
       ├──► embedding_model.py              paraphrase-multilingual-MiniLM-L12-v2
       │    outputs/embeddings.npy          (184, 384) float32, L2-normalized
       │         │
       │         ▼  vector_store.py         FAISS IndexFlatIP
       │    vector_db/document.index
       │
       └──► hybrid_retriever.build_bm25()   tokenize ไทยด้วย pythainlp newmm
            vector_db/bm25_index.pkl        คำถามถูกใส่ซ้ำ 2 ครั้งใน corpus

─────────────────────────── ตอบคำถาม ───────────────────────────

query
  │
  ▼  query_transform.py     normalize_query() แทนคำพูด → ศัพท์ทางทหาร
  │                         (ถ้าเปิด USE_QUERY_TRANSFORM จะเรียก LLM
  │                          ทำ rewrite / multi_query / hyde เพิ่ม)
  ├──────────────┬──────────────┐
  ▼              ▼              │  ค้นทุกคำถามที่แปลงได้ ทุกวิธี
dense search   BM25 search      │  CANDIDATE_K = 20
  │              │              │
  └──────┬───────┘              │
         ▼  reciprocal_rank_fusion()   score = Σ 1/(RRF_K + rank)
         │
         ▼  rerankers.py        cross-encoder จัดอันดับใหม่ (ถ้าเปิด USE_RERANK)
         │
         ▼  prompt_templates.format_context()   บล็อก [1] [2] [3]
         │
         ▼  generator.py        LLM เขียนคำตอบ + อ้างอิง [n]
         │                      ถ้า USE_LLM = False → คืนบล็อก [1] ตรง ๆ
         ▼
      คำตอบ + แหล่งอ้างอิง + disclaimer
         │
         ▼  memory.py           เก็บ MEMORY_MAX_TURNS = 6 รอบล่าสุด
```

เวกเตอร์ถูก normalize มาตั้งแต่ขั้น embedding การใช้ `IndexFlatIP` จึงเท่ากับ cosine similarity เหมือน LAB02

จุดที่ต่างจาก LAB02 อย่างมีนัยคือ **RRF ไม่ได้เอาคะแนนดิบมาบวกกัน แต่บวกจากอันดับ** (`1/(60 + rank)`) เพราะคะแนน cosine กับคะแนน BM25 อยู่คนละสเกล เทียบกันตรง ๆ ไม่ได้ ผลข้างเคียงคือคะแนนที่แสดงในโหมด hybrid จะอยู่ราว 0.03 ไม่ใช่ 0.7-0.8 แบบ dense ล้วน

## โครงสร้างไฟล์

```
LAB04/
├── README.md
└── RAG-Project/
    ├── config.py                      สวิตช์ทุกฟีเจอร์ + path + พารามิเตอร์
    ├── build_index.py                 สร้าง index ทั้งหมดในคำสั่งเดียว
    ├── main.py                        โปรแกรมถาม-ตอบแบบ interactive
    ├── requirements.txt
    │
    ├── data/
    │   ├── military_qa.txt            knowledge base 182 Q&A, 12 หมวด
    │   └── golden_set.json            ชุดวัดผล 60 ข้อ x 4 รูปแบบคำถาม
    │
    ├── labs/                          สคริปต์ทีละขั้น (Stage 1 เหมือน LAB02)
    │   ├── lab01_extract_text.py          สกัด Q&A จากไฟล์ต้นฉบับ
    │   ├── lab02_chunking.py              แบ่ง chunk
    │   ├── lab03_create_embeddings.py     สร้าง embeddings
    │   ├── lab04_create_vector_db.py      สร้าง FAISS index
    │   ├── lab05_query_embedding.py       ทดลอง embed คำถาม
    │   ├── lab06_similarity_search.py     ทดลอง similarity search
    │   └── lab07_complete_retrieval.py    รวมเป็น pipeline เดียว
    │
    ├── src/
    │   ├── document_loader.py             parser รูปแบบ [หมวด]/Q:/A:
    │   ├── text_splitter.py               chunking พร้อม overlap
    │   ├── embedding_model.py             wrapper ของ sentence-transformers
    │   ├── vector_store.py                wrapper ของ FAISS
    │   ├── index_meta.py                  เตือนเมื่อ index เก่ากว่า dataset
    │   ├── retriever.py                   dense อย่างเดียว (baseline)
    │   ├── hybrid_retriever.py            BM25 + dense + RRF
    │   ├── rerankers.py                   cross-encoder reranking
    │   ├── query_transform.py             normalize / rewrite / multi-query / HyDE
    │   ├── prompt_templates.py            prompt ทุกตัวรวมไว้ที่เดียว
    │   ├── generator.py                   เรียก LLM + โหมดไม่ใช้ LLM
    │   ├── memory.py                      ความจำบทสนทนา
    │   └── rag_pipeline.py                ประกอบทุกขั้นเป็น pipeline เดียว
    │
    ├── evaluation/
    │   ├── metrics.py                     Hit@k, Recall@k, Precision@k, MRR, nDCG
    │   ├── build_golden_set.py            สร้างชุดวัดผลจาก chunk store
    │   ├── eval_retrieval.py              เทียบ dense / bm25 / hybrid
    │   └── eval_generation.py             วัดคุณภาพคำตอบ
    │
    ├── outputs/                       ผลลัพธ์ระหว่างทาง แนบมาให้ตรวจ
    │   ├── extracted_text.json
    │   ├── chunks.json
    │   ├── embeddings.npy
    │   ├── retrieval_results.json
    │   ├── eval_retrieval.json
    │   └── eval_generation.json
    │
    └── vector_db/                     ฐานข้อมูลที่ build ไว้แล้ว
        ├── document.index                 FAISS
        ├── bm25_index.pkl                 BM25
        ├── chunk_store.json               chunk เรียงตรงกับลำดับใน FAISS
        └── index_meta.json                ลายนิ้วมือ dataset ที่ใช้ build
```

## วิธีรัน

```bash
cd LAB04/RAG-Project
py -m pip install -r requirements.txt
```

ที่เพิ่มจาก LAB02 คือ `rank-bm25` สำหรับ keyword search, `pythainlp` สำหรับตัดคำไทยก่อนเข้า BM25 และ `openai` ที่ใช้เป็น client กลางคุยกับ Ollama / OpenAI / Gemini

สร้าง index ทั้งหมด (FAISS + BM25 + metadata) ในคำสั่งเดียว

```bash
py build_index.py
```

หรือจะรันทีละขั้นตามใบงาน Stage 1 ก็ได้

```bash
py labs/lab01_extract_text.py        # -> outputs/extracted_text.json
py labs/lab02_chunking.py            # -> outputs/chunks.json
py labs/lab03_create_embeddings.py   # -> outputs/embeddings.npy
py labs/lab04_create_vector_db.py    # -> vector_db/
py labs/lab05_query_embedding.py     # ทดลอง embed คำถาม
py labs/lab06_similarity_search.py   # ทดลองค้น top-k
py labs/lab07_complete_retrieval.py  # -> outputs/retrieval_results.json
```

ถาม-ตอบ

```bash
py main.py
```

วัดผล

```bash
py -m evaluation.build_golden_set    # -> data/golden_set.json
py -m evaluation.eval_retrieval      # -> outputs/eval_retrieval.json
py -m evaluation.eval_generation     # -> outputs/eval_generation.json
```

ไฟล์ใน `vector_db/` แนบมาให้แล้ว ถ้าไม่อยาก build เองข้ามไป `py main.py` ได้เลย

ถ้าจะใช้ LLM เขียนคำตอบจริง ต้องตั้ง `USE_LLM = True` ใน `config.py` แล้วเตรียม provider ให้พร้อม — `ollama serve` แล้ว `ollama pull llama3.1:8b` หรือเปลี่ยน `LLM_PROVIDER` เป็น `openai` / `gemini` แล้วตั้ง environment variable `OPENAI_API_KEY` / `GOOGLE_API_KEY`

## ผลการทดลอง

### ชุดวัดผล

`build_golden_set.py` สุ่ม 60 ข้อจาก 184 chunks แบบกระจายหมวดละ 5 ข้อ แล้วแปลงคำถามต้นฉบับเป็น 4 รูปแบบ เพื่อดูว่าระบบทนคำถามที่ไม่ตรงตัวได้แค่ไหน

| รูปแบบ | คืออะไร | จำนวนที่สร้างได้ | ตัวอย่าง |
| :--- | :--- | :---: | :--- |
| `verbatim` | คำถามต้นฉบับ ใช้ดูเพดานบนของระบบ | 60 | ปืนซุ่มยิงกับปืนต่อต้านยุทโธปกรณ์ต่างกันอย่างไร |
| `slang` | แทนศัพท์ทางทหารด้วยภาษาพูด | 10 | รถถัง → แทงค์, ขีปนาวุธ → มิสไซล์ |
| `partial` | ตัดเหลือแต่คำเนื้อหา แบบที่คนพิมพ์ค้นจริง | 60 | ปืน ซุ่ม ยิง ปืน |
| `natural` | เติมคำนำ/คำลงท้ายแบบภาษาพูด | 60 | อยากรู้ว่าปืนแบบ bullpup คืออะไร ยังไงครับ |

`slang` สร้างได้แค่ 10 ข้อ เพราะเงื่อนไขคือคำถามต้องมีคำในตาราง `TO_SLANG` อยู่จริง ซึ่งมีแค่ 10 ข้อจาก 60

### คะแนนการค้นหา

ทดสอบทุกข้อทุกรูปแบบ รวม 190 query ผลเต็มอยู่ใน [`outputs/eval_retrieval.json`](RAG-Project/outputs/eval_retrieval.json)

**ภาพรวม**

| วิธีค้น | Hit@1 | Hit@10 | MRR | nDCG@3 | ms/query |
| :--- | :---: | :---: | :---: | :---: | :---: |
| dense_only | 0.9053 | 0.9737 | 0.9336 | 0.9351 | 8.9 |
| **bm25_only** | **0.9947** | **1.0000** | **0.9965** | **0.9974** | **3.0** |
| hybrid (RRF) | 0.9684 | 1.0000 | 0.9765 | 0.9744 | 9.3 |

**แยกตามรูปแบบคำถาม (MRR)**

| วิธีค้น | verbatim | slang | partial | natural |
| :--- | :---: | :---: | :---: | :---: |
| dense_only | 0.9917 | 0.9000 | 0.8229 | 0.9917 |
| bm25_only | 1.0000 | 1.0000 | 0.9889 | 1.0000 |
| hybrid (RRF) | 1.0000 | 0.9333 | 0.9368 | 1.0000 |

### ผลออกมาไม่ตรงกับที่คาด

สมมติฐานที่ใบงานตั้งไว้คือ hybrid ควรชนะทุกวิธี แต่ผลจริงคือ **BM25 ล้วนชนะขาด** ทั้งแม่นกว่าและเร็วกว่า dense สามเท่า ส่วน hybrid อยู่ตรงกลาง คือถูกฉุดลงมาจาก BM25

ก่อนจะสรุปว่า BM25 ดีกว่า ต้องบอกก่อนว่าตัวเลขชุดนี้ **สูงเกินจริง** เพราะ golden set สร้างจากคำถามใน dataset เอง

- `verbatim` คือคำถามต้นฉบับเป๊ะ ๆ → BM25 จับคำได้ 100% เป็นธรรมดา
- `natural` แค่เติม "อยากรู้ว่า" ข้างหน้าและ "ครับ" ข้างหลัง เนื้อคำถามยังเหมือนเดิมทุกตัวอักษร → คะแนนเลยเท่ากับ verbatim เป๊ะ
- `partial` คือคำที่ตัดมาจากคำถามเดิม ก็ยังเป็นคำเดิมอยู่ดี

แปลว่าสามในสี่รูปแบบวัด "การจับคำตรงตัว" มากกว่าวัดความเข้าใจความหมาย งานนี้จึงเข้าทาง BM25 เต็ม ๆ ตั้งแต่ต้น ตัวเลข 0.99 ไม่ได้แปลว่าระบบเก่ง แต่แปลว่าข้อสอบรั่ว ถ้าจะวัดของจริงต้องมีคำถามที่ **เขียนใหม่ด้วยคำคนละชุด** ซึ่งชุดนี้ยังไม่มี

ที่ยังพอมีความหมายคือช่องว่างระหว่างรูปแบบของ dense เอง — verbatim/natural ได้ 0.9917 แต่ partial ตกลงมาที่ 0.8229 ทั้งที่เป็นคำถามเดียวกัน

### ทำไม dense ถึงพังตอนเจอ partial

ในรูปแบบ `partial` dense เลือกอันดับ 1 ผิด 15 ข้อจาก 60 ลองดูของจริง

```
g0006  "ปืน ซุ่ม ยิง ปืน"          (จาก "ปืนซุ่มยิงกับปืนต่อต้านยุทโธปกรณ์ต่างกันอย่างไร")
       ควรได้ [6]
       dense  [25, 11, 21]   อันดับ 1 = อาวุธนำวิถีต่อสู้รถถังแบบ fire-and-forget คืออะไร
       bm25   [6, 26, 135]   ถูกตั้งแต่อันดับ 1

g0014  "เกราะ กัน กระสุน"          (จาก "เกราะกันกระสุนระดับต่าง ๆ ป้องกันอะไรได้บ้าง")
       ควรได้ [14]
       dense  [25, 14, 102]  อันดับ 1 = อาวุธนำวิถีต่อสู้รถถังแบบ fire-and-forget คืออะไร
       bm25   [14, 37, 34]

g0017  "ปืนใหญ่ อัตตา จร"          (จาก "ปืนใหญ่อัตตาจรต่างจากปืนใหญ่ลากจูงอย่างไร")
       ควรได้ [17]
       dense  [25, 26, 29]   อันดับ 1 = อาวุธนำวิถีต่อสู้รถถังแบบ fire-and-forget คืออะไร
       bm25   [17, 18, 15]
```

สามข้อนี้ dense ตอบผิดเป็น chunk เดียวกันหมดคือ `[25]` ทั้งที่คำถามคนละหมวดกันเลย (ปืนเล็ก / เกราะ / ปืนใหญ่) ปรากฏการณ์นี้เรียกว่า hub vector — เวกเตอร์ที่บังเอิญอยู่กลาง ๆ ของ embedding space แล้วกลายเป็นเพื่อนบ้านที่ใกล้ที่สุดของ query ที่โมเดลอ่านไม่ออก

สาเหตุที่โมเดลอ่านไม่ออกคือรูปแบบข้อความ `partial` เอาคำที่ตัดแล้วมาต่อกันด้วยช่องว่าง `"ปืนใหญ่ อัตตา จร"` ซึ่งไม่ใช่ประโยคภาษาไทยที่ `paraphrase-multilingual-MiniLM-L12-v2` เคยเห็นตอนเทรน พอ encode ออกมาเวกเตอร์เลยไม่มีทิศทางชัดเจน แล้วตกไปหา hub ส่วน BM25 ไม่สนใจเรื่องนี้เลย เพราะมันตัดคำใหม่แล้วนับคำตรง ๆ ช่องว่างจึงไม่มีผล

### RRF ทำให้แย่ลงได้ ถ้าสัญญาณฝั่งหนึ่งเสีย

จุดที่น่าสนใจกว่าคือ hybrid **แพ้ BM25 ล้วน** ในรูปแบบ partial (0.9368 vs 0.9889) และบางข้อ hybrid ทำผลเสียกว่าทั้งสองวิธีที่เอามารวมกัน

```
g0041  "รถ หุ้ม เกราะ"             (จาก "รถหุ้มเกราะแบบ MRAP ออกแบบมาเพื่ออะไร")
       ควรได้ [41]
       dense  [30, 89, 34]   ผิดทั้งสามอันดับ
       bm25   [41, 35, 50]   ถูกตั้งแต่อันดับ 1
       hybrid [35, 34, 36]   ผิดทั้งสามอันดับ — คำตอบที่ถูกหลุด top-3 ไปเลย
```

RRF ให้คะแนนจากอันดับ `1/(60 + rank)` โดยเชื่อทั้งสองฝั่งเท่ากัน ไม่มีกลไกดูว่าฝั่งไหนมั่นใจแค่ไหน พอ dense เดามั่วมาทั้งลิสต์ คะแนนขยะจากฝั่งนั้นก็ยังถูกบวกเข้าไปเต็ม ๆ และเนื่องจากผู้เข้ารอบจาก dense มี 20 ตัว ขณะที่ของถูกจาก BM25 มีตัวเดียว ผลรวมจึงถูกเสียงข้างมากที่ผิดกลบ

บทเรียนคือ hybrid ไม่ใช่ของที่เปิดแล้วดีขึ้นเสมอ มันดีขึ้นต่อเมื่อสองวิธีผิดคนละแบบ ถ้าวิธีหนึ่งผิดแบบสุ่มทั้งลิสต์ การเอามารวมคือการเจือจางของดี

### คุณภาพคำตอบ — ยังวัดไม่ได้จริง

`eval_generation.py` รัน 20 ข้อ ด้วยคำถามรูปแบบ `natural` ผลอยู่ใน [`outputs/eval_generation.json`](RAG-Project/outputs/eval_generation.json)

| ตัวชี้วัด | ค่า |
| :--- | :---: |
| อัตราการตอบว่าไม่รู้ | 0.0 |
| อัตราค้นเจอ chunk ที่ถูก | 1.0 |
| มีการอ้างอิง `[n]` | 1.0 |
| faithfulness | 1.0 |
| correctness | 0.9804 |
| relevance | 0.4132 |
| เวลาเฉลี่ย | 0.043 วินาที |

**ตัวเลขชุดนี้อ่านตามตัวไม่ได้** เพราะเครื่องที่ผมรันไม่มี LLM (ไม่ได้ติดตั้ง Ollama และไม่มี API key) จึงต้องรันด้วย `USE_LLM = False` ซึ่งแปลว่า "คำตอบ" ที่ได้คือการคัดลอกข้อความ chunk อันดับ 1 มาแปะพร้อมต่อท้ายด้วย `[1]`

พอคำตอบคือตัวเอกสารเอง faithfulness ย่อมได้ 1.0 อัตโนมัติ (วัดว่าคำในคำตอบมาจากเอกสารกี่ %) correctness ได้ 0.98 เพราะ chunk ที่หยิบมามักเป็น chunk เดียวกับ reference answer และ has_citation ได้ 1.0 เพราะโค้ดเติม `[1]` ให้เองทุกครั้ง สามค่านี้จึงไม่ได้วัดความสามารถของระบบเลย

ค่าที่ยังพอมีความหมายมีสองตัว — **อัตราค้นเจอ chunk ที่ถูก 1.0** ยืนยันว่า retriever ทำงานได้จริงในระดับ context และ **relevance 0.4132** ที่ต่ำ เป็นผลที่คาดได้ เพราะคำตอบดิบ ๆ ไม่ได้เขียนล้อคำถามแบบที่ LLM จะทำ

ส่วนเวลา 0.043 วินาทีต่อข้อคือเวลาของ retrieval อย่างเดียว ถ้าต่อ LLM เข้าไปจริงจะขึ้นไปหลักวินาที

### สิ่งที่ยังไม่ได้ทดสอบ

| ฟีเจอร์ | สถานะ | เหตุผล |
| :--- | :--- | :--- |
| `USE_RERANK` cross-encoder | เขียนโค้ดครบ ยังไม่ได้รัน | ต้องโหลดโมเดล `BAAI/bge-reranker-v2-m3` ขนาดราว 2.2 GB ซึ่งยังไม่มีใน cache เครื่องนี้ |
| `USE_QUERY_TRANSFORM` (rewrite / multi-query / HyDE) | เขียนโค้ดครบ ยังไม่ได้รัน | ทั้งสามโหมดต้องเรียก LLM |
| `USE_LLM` การสร้างคำตอบจริง | เขียนโค้ดครบ ยังไม่ได้รัน | ไม่มี LLM ให้ใช้บนเครื่อง |
| `USE_MEMORY` | รันได้ แต่ประเมินไม่ได้ | ผลของความจำจะเห็นก็ต่อเมื่อ LLM เอา history ไปใช้เขียนคำตอบ |

ส่วนที่วัดได้จริงในใบงานนี้จึงจบที่ retrieval เท่านั้น ผมเลือกจะบอกตรง ๆ แทนที่จะรายงานตัวเลข faithfulness 1.0 เป็นผลสำเร็จ

### จะทำต่อยังไง

เรื่องที่ต้องแก้ก่อนอย่างอื่นคือ **golden set** ตราบใดที่คำถามทดสอบยังใช้คำชุดเดียวกับ dataset ตัวเลขจะอิ่มตัวที่ 0.99 และเปรียบเทียบอะไรไม่ได้เลย แผนคือเขียน paraphrase ด้วยมือสัก 30-40 ข้อ ใช้คำคนละชุดกับต้นฉบับ (เช่น ถาม "รถถังรุ่นไหนป้องกันทุ่นระเบิดได้ดี" แทนคำถามต้นฉบับที่มีคำว่า MRAP อยู่) แล้ววัดใหม่ ผมคาดว่าตอนนั้น dense จะกลับมานำ BM25 และ hybrid จะเริ่มมีเหตุผล

เรื่อง RRF ที่ถูกสัญญาณเสียฉุด แก้ได้สองทาง ทางแรกคือถ่วงน้ำหนักแต่ละฝั่งแทนที่จะเชื่อเท่ากัน ทางที่สองคือตัดผู้เข้ารอบที่คะแนนต่ำกว่า threshold ทิ้งก่อนเข้า fusion จะได้ไม่มีขยะ 20 ตัวไปโหวต

hub vector ที่ chunk `[25]` เป็นอาการของโมเดล 384 มิติเหมือนที่เจอใน LAB02 ควรลอง `paraphrase-multilingual-mpnet-base-v2` (768 มิติ) หรือ `intfloat/multilingual-e5-small` ที่ออกแบบมาสำหรับ retrieval โดยเฉพาะ

สุดท้ายคือหา LLM มาต่อให้ได้ เพื่อปลดล็อกทั้งการวัดคุณภาพคำตอบ query transformation และ memory ซึ่งตอนนี้เขียนไว้แต่ยังพิสูจน์ไม่ได้ว่าช่วยจริงหรือไม่

## ที่มาของโค้ดและข้อมูล

| รายการ | แหล่งที่มา |
| :--- | :--- |
| โครงร่างโปรเจกต์ Stage 1-2 และแนวทางการวัดผล | [aproot-en/Advanced-Topic-in-Computer-Software-Course](https://github.com/aproot-en/Advanced-Topic-in-Computer-Software-Course) โฟลเดอร์ `DL-04-RAG System Development I` ของอาจารย์ Anuruk Prommakhot |
| `data/military_qa.txt` | ผมทำขึ้นเองสำหรับใบงานนี้ เรียบเรียงจากข้อมูลสาธารณะเชิงสารานุกรมด้านยุทโธปกรณ์ |
| embedding model | [`paraphrase-multilingual-MiniLM-L12-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) สัญญาอนุญาต Apache-2.0 |
| reranker model (เตรียมไว้ ยังไม่ได้รัน) | [`BAAI/bge-reranker-v2-m3`](https://huggingface.co/BAAI/bge-reranker-v2-m3) สัญญาอนุญาต Apache-2.0 |
| `sentence-transformers` | https://github.com/UKPLab/sentence-transformers |
| `faiss` | https://github.com/facebookresearch/faiss |
| `rank_bm25` | https://github.com/dorianbrown/rank_bm25 |
| `pythainlp` | https://github.com/PyThaiNLP/pythainlp |
| `openai` (client กลางสำหรับ Ollama / OpenAI / Gemini) | https://github.com/openai/openai-python |
| `numpy` | https://github.com/numpy/numpy |
| อัลกอริทึม Reciprocal Rank Fusion | Cormack, Clarke & Buettcher (2009), *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods*, SIGIR '09 |
| แนวคิด HyDE | Gao et al. (2022), *Precise Zero-Shot Dense Retrieval without Relevance Labels*, [arXiv:2212.10496](https://arxiv.org/abs/2212.10496) |

ไม่มีการใช้ข้อมูลที่ละเมิดลิขสิทธิ์ ข้อมูลส่วนบุคคลที่ไม่ได้รับอนุญาต หรือข้อมูลผิดกฎหมาย เนื้อหาใน dataset เป็นความรู้เชิงสารานุกรมจากแหล่งสาธารณะ เรียบเรียงเพื่อการศึกษา ไม่มีข้อมูลเชิงปฏิบัติการหรือวิธีสร้าง/ดัดแปลงอาวุธ

## การส่งงาน

รายละเอียดข้อกำหนดการส่งงานของรายวิชาอยู่ใน [README ของ LAB01](../LAB01/README.md) ใช้เหมือนกันทุกใบงาน

```bash
git add LAB04/
git commit -m "LAB04: <สิ่งที่ทำ>"
git push origin main
```

ลิงก์ของใบงานนี้: https://github.com/Peemaxnaja/ATCS-CPE/tree/main/LAB04
