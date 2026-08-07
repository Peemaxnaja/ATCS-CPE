




# Central configuration for the entire project.
# Change settings here to experiment without modifying the source code.

import os
import sys

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

# 1. ลองปิดทีละตัวแล้วรัน evaluation ดูว่าคะแนนเปลี่ยนไปแค่ไหน

USE_HYBRID = True            # ค้นด้วย BM25 ควบคู่กับ dense (ปิด = dense อย่างเดียว)
USE_RERANK = False            # จัดอันดับใหม่ด้วย cross-encoder — แม่นขึ้นแต่ช้ามาก
USE_QUERY_TRANSFORM = False      # แปลงคำถามก่อนค้น — เสีย LLM เพิ่ม 1 ครั้งต่อคำถาม
USE_MEMORY = True              # จำบทสนทนา เพื่อตอบคำถามต่อเนื่องได้
USE_LLM = False             # False = แสดงข้อความที่ค้นได้ดิบ ๆ ไม่เรียก LLM เลย
                            # ตั้งเป็น True เมื่อมี Ollama/OpenAI/Gemini พร้อมใช้ (ดูข้อ 5)
SHOW_SOURCES = True          # True = แสดงรายการแหล่งอ้างอิงท้ายคำตอบ
SHOW_DEBUG = False          # True = แสดงคะแนนและเวลาของแต่ละขั้น


# 2. ที่อยู่ไฟล์
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")


# clack python build_index.py
SOURCE_FILE = os.path.join(DATA_DIR, "military_qa.txt")
GOLDEN_SET_FILE = os.path.join(DATA_DIR, "golden_set.json")

# ผลลัพธ์ระหว่างทางจาก build_index.py
EXTRACTED_TEXT_FILE = os.path.join(OUTPUT_DIR, "extracted_text.json")
CHUNKS_FILE = os.path.join(OUTPUT_DIR, "chunks.json")
EMBEDDINGS_FILE = os.path.join(OUTPUT_DIR, "embeddings.npy")
RETRIEVAL_RESULTS_FILE = os.path.join(OUTPUT_DIR, "retrieval_results.json")
EVAL_RETRIEVAL_FILE = os.path.join(OUTPUT_DIR, "eval_retrieval.json")
EVAL_GENERATION_FILE = os.path.join(OUTPUT_DIR, "eval_generation.json")

# ฐานข้อมูลที่ระบบใช้ค้นจริง
FAISS_INDEX_FILE = os.path.join(VECTOR_DB_DIR, "document.index")
CHUNK_STORE_FILE = os.path.join(VECTOR_DB_DIR, "chunk_store.json")
BM25_INDEX_FILE = os.path.join(VECTOR_DB_DIR, "bm25_index.pkl")
INDEX_META_FILE = os.path.join(VECTOR_DB_DIR, "index_meta.json")

# 3. การเตรียมข้อมูล  (แก้แล้วต้องรัน build_index.py ใหม่)
CHUNK_SIZE = 400        # ตัวอักษรต่อ chunk (คำตอบส่วนใหญ่สั้นกว่านี้อยู่แล้ว)
CHUNK_OVERLAP = 50      # ให้ chunk ที่ติดกันเหลื่อมกัน กันใจความขาดตอน

# ตัวโมเดลจริงถูกดาวน์โหลดไปเก็บที่ C:\Users\----\.cache\huggingface
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# บางโมเดลบังคับให้เติมคำนำหน้าคนละแบบระหว่างฝั่งคำถามกับฝั่งเอกสาร
# ตระกูล e5 เป็นตัวอย่าง ถ้าไม่เติมคะแนนจะตกอย่างเห็นได้ชัด
# MiniLM ไม่ต้องเติมอะไร จึงเว้นว่างไว้
EMBEDDING_QUERY_PREFIX = ""
EMBEDDING_PASSAGE_PREFIX = ""

# 4. การค้นหา
TOP_K = 3               # ส่งกี่ chunk ให้ LLM เขียนคำตอบ
CANDIDATE_K = 20        # ดึง TOP_K
RRF_K = 60              # ค่าคงที่ของสูตร RRF

# น้ำหนักของแต่ละฝั่งตอนรวมอันดับ — 1.0 เท่ากันคือเชื่อพอกัน
RRF_DENSE_WEIGHT = 1.0
RRF_BM25_WEIGHT = 1.0

# คะแนนความคล้าย (cosine) ต่ำสุดที่ยังถือว่าคำถามอยู่ในคลังความรู้
# ต่ำกว่านี้ระบบจะตอบ NO_CONTEXT_MESSAGE แทนที่จะเดาจากเอกสารที่ไม่เกี่ยวข้อง
# ตั้ง 0 = ปิดการตรวจ ตอบทุกคำถามเหมือนเดิม
#
# ที่มาของเลข 0.40 — วัดจริงด้วย evaluation/eval_refusal.py
#   คำถามในคลัง (paraphrase 55 ข้อ ซึ่งคะแนนต่ำที่สุด)  ต่ำสุด 0.4573
#   คำถามนอกคลัง (19 ข้อ)                                สูงสุด 0.6050
# สองกลุ่มคาบเกี่ยวกัน จึงไม่มีเกณฑ์ไหนแยกได้หมด ต้องเลือกจุดแลกเปลี่ยน
#
#   0.40  ปฏิเสธถูก 73.7%  เผลอปฏิเสธ 0.0%   <- เลือกอันนี้
#   0.45  ปฏิเสธถูก 78.9%  เผลอปฏิเสธ 0.0%
#   0.50  ปฏิเสธถูก 84.2%  เผลอปฏิเสธ 7.3%
#
# 0.45 ได้คะแนนดีกว่าบนชุดนี้ แต่ห่างจากคำถามในคลังที่คะแนนต่ำสุดแค่ 0.0073
# ซึ่งแปลว่ามันพอดีกับข้อมูลที่วัดเกินไป คำถามใหม่ข้อเดียวก็พังได้
# เลือก 0.40 เพื่อให้มีระยะเผื่อ ยอมแลกกับคำถามนอกคลังที่หลุดมา 1 ข้อ
MIN_DENSE_SCORE = 0.40

# ตัดผู้เข้ารอบที่คะแนนต่ำกว่ากี่เท่าของอันดับ 1 ทิ้งก่อนเข้า RRF (0 = ไม่ตัด)
# RRF นับแต่อันดับ ผู้เข้ารอบท้ายแถวที่คะแนนจริงเกือบศูนย์จึงมีสิทธิ์โหวตเท่ากัน
# ค่าที่ตั้งไว้มาจากการกวาดหาบน variant paraphrase (ดู README)
RRF_DENSE_FLOOR = 0.0
RRF_BM25_FLOOR = 0.0

RERANK_MODEL_NAME = "BAAI/bge-reranker-v2-m3"   # ใช้เมื่อ USE_RERANK = True

QUERY_TRANSFORM_MODE = "multi_query"   # rewrite | multi_query | hyde
MULTI_QUERY_COUNT = 3

# 5. LLM
LLM_PROVIDER = "ollama"
LLM_MODEL = ""          # เว้นว่าง = ใช้ค่า default 
LLM_TEMPERATURE = 0.2   # เหมือนค่าเทรดโฮล 
LLM_MAX_TOKENS = 800

LLM_PROVIDERS = {
    "ollama": ("http://localhost:11434/v1", "llama3.1:8b", None),
    "openai": ("https://api.openai.com/v1", "gpt-4o-mini", "OPENAI_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/",
               "gemini-1.5-flash", "GOOGLE_API_KEY"),
}


# 6. ข้อความและการวัดผล
MEMORY_MAX_TURNS = 6    # จำนวนรอบของการจำบทสนทนา
NO_CONTEXT_MESSAGE = "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้อง"
DISCLAIMER = ("หมายเหตุ: ข้อมูลนี้เป็นความรู้เชิงสารานุกรมเพื่อการศึกษาเท่านั้น "
              "ตัวเลขสมรรถนะเป็นค่าโดยประมาณจากแหล่งข้อมูลสาธารณะ")

EVAL_K_VALUES = [1, 3, 5, 10]
GOLDEN_SET_SIZE = 120   # 10 ข้อต่อหมวด จาก 12 หมวด — ขยายตามขนาด dataset ที่โตขึ้น


# create output directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
