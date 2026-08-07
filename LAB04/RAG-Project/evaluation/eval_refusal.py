# วัดว่าระบบ "บอกว่าไม่รู้" เป็นไหม
#
# ปัญหา
#   FAISS คืน top-k ให้เสมอ ไม่ว่าคำถามจะเกี่ยวกับคลังความรู้หรือไม่ ระบบเดิม
#   จึงตอบทุกคำถาม ถามเรื่องส้มตำก็ได้ chunk เรื่องปีกเดลตากลับมา แล้วตอบไป
#   พร้อมอ้างอิง [1] และ disclaimer ต่อท้ายอย่างมั่นใจ
#
# วิธีวัด
#   ต้องดูสองด้านพร้อมกัน ไม่งั้นโกงได้ง่ายมาก
#
#     ปฏิเสธถูก      คำถามนอกคลังที่ระบบปฏิเสธ / คำถามนอกคลังทั้งหมด
#     เผลอปฏิเสธ     คำถามในคลังที่ระบบดันปฏิเสธ / คำถามในคลังทั้งหมด
#
#   ถ้าดูแค่ค่าแรก ตั้ง MIN_DENSE_SCORE สูง ๆ ก็ได้ 100% ทันที แต่ระบบจะปฏิเสธ
#   ทุกอย่างจนใช้งานไม่ได้ ค่าที่ดีคือค่าแรกสูงและค่าที่สองเป็นศูนย์
#
#   คำถามในคลังใช้ variant paraphrase เพราะเป็นชุดที่คะแนนต่ำที่สุด ถ้าเกณฑ์
#   ไม่เผลอปฏิเสธชุดนี้ ชุดอื่นก็ปลอดภัย
#
# Run: python -m evaluation.eval_refusal

import json
import os

import config

OUT_OF_SCOPE_FILE = os.path.join(config.DATA_DIR, "out_of_scope.json")
REPORT_FILE = os.path.join(config.OUTPUT_DIR, "eval_refusal.json")

VARIANT = "paraphrase"

# เกณฑ์ที่จะลอง — 0 คือปิดการตรวจ ซึ่งเป็นพฤติกรรมเดิมก่อนแก้
THRESHOLDS = [0.0, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60]


def load_questions():
    with open(config.GOLDEN_SET_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)["items"]
    in_scope = [i["variants"][VARIANT] for i in items if VARIANT in i["variants"]]

    with open(OUT_OF_SCOPE_FILE, "r", encoding="utf-8") as f:
        out_of_scope = json.load(f)["questions"]

    return in_scope, out_of_scope


def best_scores(retriever, questions):
    """คืนคะแนน dense ที่ดีที่สุดของแต่ละคำถาม — ค้นรอบเดียวแล้วเอาไปลองทุกเกณฑ์

    คิดคะแนนแบบเดียวกับ is_in_scope() ใน rag_pipeline.py เป๊ะ ๆ
    """
    from src.query_transform import normalize_query

    scores = []
    for question in questions:
        chunks = retriever.retrieve(normalize_query(question), top_k=config.TOP_K)
        found = [c["dense_score"] for c in chunks if c.get("dense_score") is not None]
        scores.append(max(found) if found else None)

    return scores


def main():
    print("=== วัดความสามารถในการบอกว่าไม่รู้ ===")

    in_scope, out_of_scope = load_questions()
    print(f"คำถามในคลัง ({VARIANT}): {len(in_scope)} ข้อ")
    print(f"คำถามนอกคลัง: {len(out_of_scope)} ข้อ\n")

    config.USE_HYBRID = True
    from src.hybrid_retriever import HybridRetriever

    retriever = HybridRetriever()
    in_scores = best_scores(retriever, in_scope)
    out_scores = best_scores(retriever, out_of_scope)

    print("=== การกระจายของคะแนน ===")
    print(f"  ในคลัง   ต่ำสุด {min(in_scores):.4f}   สูงสุด {max(in_scores):.4f}")
    print(f"  นอกคลัง  ต่ำสุด {min(out_scores):.4f}   สูงสุด {max(out_scores):.4f}")

    gap = min(in_scores) - max(out_scores)
    if gap > 0:
        print(f"  ช่องว่างระหว่างสองกลุ่ม {gap:.4f} — แยกได้ด้วยเส้นเดียว")
    else:
        print(f"  สองกลุ่มคาบเกี่ยวกัน {-gap:.4f} — ไม่มีเกณฑ์ไหนแยกได้หมด")

    print("\n=== ผลของแต่ละเกณฑ์ ===")
    header = f"{'MIN_DENSE_SCORE':>16}{'ปฏิเสธถูก':>14}{'เผลอปฏิเสธ':>14}"
    print(header)
    print("-" * 46)

    rows = []
    for threshold in THRESHOLDS:
        refused_ok = sum(1 for s in out_scores if s < threshold) / len(out_scores)
        refused_wrong = sum(1 for s in in_scores if s < threshold) / len(in_scores)
        rows.append({
            "threshold": threshold,
            "refused_out_of_scope": round(refused_ok, 4),
            "refused_in_scope": round(refused_wrong, 4),
        })
        mark = "  <- ค่าที่ใช้" if threshold == config.MIN_DENSE_SCORE else ""
        print(f"{threshold:16.2f}{refused_ok:13.1%}{refused_wrong:13.1%}{mark}")

    print("\n=== คำถามนอกคลังที่คะแนนสูงสุด (หลอกเกณฑ์ได้มากที่สุด) ===")
    for question, score in sorted(zip(out_of_scope, out_scores),
                                  key=lambda pair: pair[1], reverse=True)[:4]:
        verdict = "ปฏิเสธ" if score < config.MIN_DENSE_SCORE else "ยังตอบอยู่"
        print(f"  {score:.4f}  {verdict:10s} {question}")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "variant": VARIANT,
            "n_in_scope": len(in_scope),
            "n_out_of_scope": len(out_of_scope),
            "in_scope_min": round(min(in_scores), 4),
            "out_of_scope_max": round(max(out_scores), 4),
            "thresholds": rows,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nบันทึกรายงานที่ {REPORT_FILE}")


if __name__ == "__main__":
    main()
