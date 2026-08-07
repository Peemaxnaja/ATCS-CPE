


# Evaluate answer quality, not retrieval — the whole RAGPipeline runs per item.
#
# (หัวไฟล์เดิมถูกก๊อปมาจาก eval_retrieval.py ทั้งบล็อก บรรยายการเทียบ
#  dense/bm25/hybrid ซึ่งไฟล์นี้ไม่ได้ทำเลย แก้ให้ตรงกับของจริงแล้ว)
#
# วัดสี่อย่างต่อคำถามหนึ่งข้อ
#
#     context_hit    ค้นเจอ chunk ที่ถูกไหม — แยกความผิดของ retriever
#                    ออกจากความผิดของคนเขียนคำตอบ
#     faithfulness   คำในคำตอบมาจากเอกสารกี่ % — ต่ำแปลว่าน่าจะแต่งเอง
#     correctness    คำตอบทับกับ reference answer กี่ %
#     relevance      คำตอบเกาะคำถามแค่ไหน
#
# ข้อควรระวังตอนอ่านผล
#   * ทั้งสี่ค่าเป็นการนับคำทับกัน ไม่ใช่การเข้าใจความหมาย
#   * ถ้า USE_LLM = False คำตอบคือการคัดลอก chunk อันดับ 1 มาแปะ
#     faithfulness จะได้ 1.0 อัตโนมัติ และไม่ได้วัดอะไรเลย


import json
import re

import config
from evaluation.eval_retrieval import load_golden_set
from src.hybrid_retriever import tokenize
from src.prompt_templates import format_context

# กี่ข้อ — การเรียก LLM ช้า จึงตั้งไว้น้อย
LIMIT = 20

# ใช้คำถามรูปแบบไหน
# เดิมใช้ natural ซึ่งเป็นรูปแบบที่ง่ายที่สุด (retrieval MRR 0.99) การวัดคุณภาพ
# คำตอบด้วยคำถามที่ระบบค้นเจอถูกเกือบทุกข้ออยู่แล้ว จึงไม่ได้บอกอะไร
# เปลี่ยนมาใช้ paraphrase ที่เขียนใหม่ด้วยคำคนละชุด เป็นเคสที่ใช้ตัดสินจริง
VARIANT = "paraphrase"


def word_overlap(text_a, text_b):
    """
    สัดส่วนคำใน text_a ที่ปรากฏใน text_b ด้วย (0.0 - 1.0)

    ถ้าคำตอบถูก "คัดลอก / เรียบเรียง" มาจากเอกสาร ค่าจะสูง
    ถ้าแต่งขึ้นเอง ค่าจะต่ำ
    """
    words_a = set(tokenize(text_a))
    if not words_a:
        return 0.0

    words_b = set(tokenize(text_b))
    return len(words_a & words_b) / len(words_a)


def is_refusal(answer):
    """คำตอบนี้คือการบอกว่า 'ไม่รู้' ใช่ไหม"""
    phrases = ["ไม่พบข้อมูล", "ไม่มีข้อมูล", "ไม่สามารถตอบ"]
    return any(phrase in answer for phrase in phrases)


def evaluate_one_item(rag, item):
    """ทดสอบคำถาม 1 ข้อ คืน dict ของคะแนน"""
    query = item["variants"].get(VARIANT, item["question"])
    result = rag.ask(query)

    answer = result["answer"].replace(config.DISCLAIMER, "").strip()
    context = format_context(result["retrieved"])

    found_ids = {chunk["chunk_id"] for chunk in result["retrieved"]}
    correct_ids = set(item["relevant_chunk_ids"])

    return {
        "id": item["id"],
        "query": query,
        "answer": answer,
        "refused": is_refusal(answer),
        "context_hit": bool(found_ids & correct_ids),   # ค้นเจอ chunk ที่ถูกไหม
        "has_citation": bool(re.search(r"\[\d+\]", result["answer"])),
        "faithfulness": round(word_overlap(answer, context), 4),
        "correctness": round(word_overlap(answer, item["reference_answer"]), 4),
        "relevance": round(word_overlap(query, answer), 4),
        "seconds": result["timings"]["รวม"],
    }


def summarize(rows):
    """เฉลี่ยคะแนนของทุกข้อ"""
    def mean(key):
        return round(sum(row[key] for row in rows) / len(rows), 4)

    return {
        "จำนวนข้อ": len(rows),
        "อัตราการตอบว่าไม่รู้": mean("refused"),
        "อัตราค้นเจอ chunk ที่ถูก": mean("context_hit"),
        "มีการอ้างอิง [n]": mean("has_citation"),
        "faithfulness": mean("faithfulness"),
        "correctness": mean("correctness"),
        "relevance": mean("relevance"),
        "เวลาเฉลี่ย (วินาที)": mean("seconds"),
    }


def main():
    print("=== วัดคุณภาพคำตอบ ===")

    from src.rag_pipeline import RAGPipeline

    # เอาเฉพาะข้อที่มี variant นี้จริง ไม่งั้นจะหล่นไปใช้คำถามต้นฉบับเงียบ ๆ
    items = [item for item in load_golden_set()["items"]
             if VARIANT in item["variants"]][:LIMIT]
    print(f"ใช้คำถามรูปแบบ {VARIANT} จำนวน {len(items)} ข้อ")

    # ปิด memory เพราะแต่ละข้อต้องเป็นอิสระ ไม่ให้ข้อก่อนหน้ามีผลกับข้อถัดไป
    original_memory = config.USE_MEMORY
    config.USE_MEMORY = False

    rag = RAGPipeline()
    rag.show_settings()

    if not config.USE_LLM:
        print("\n! USE_LLM = False — คำตอบเป็นการตัดข้อความมา ไม่ใช่การสร้างจริง")
        print("  ตั้ง USE_LLM = True ใน config.py เพื่อให้ตัวเลขมีความหมาย")

    rows = []
    for number, item in enumerate(items, start=1):
        print(f"  [{number}/{len(items)}] {item['id']}", end="\r", flush=True)
        rows.append(evaluate_one_item(rag, item))

    config.USE_MEMORY = original_memory     # คืนค่าเดิม

    summary = summarize(rows)

    print("\n\n=== สรุป ===")
    for name, value in summary.items():
        print(f"  {name:26s} {value}")

    print("\n=== คำตอบที่ยึดตามเอกสารน้อยที่สุด (น่าสงสัยว่าแต่งเอง) ===")
    for row in sorted(rows, key=lambda r: r["faithfulness"])[:3]:
        print(f"  {row['id']} ({row['faithfulness']:.3f}) {row['query'][:50]}")
        print(f"      {row['answer'][:100]}...")

    with open(config.EVAL_GENERATION_FILE, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": rows}, f, ensure_ascii=False, indent=2)
    print(f"\nบันทึกรายงานที่ {config.EVAL_GENERATION_FILE}")


if __name__ == "__main__":
    main()
