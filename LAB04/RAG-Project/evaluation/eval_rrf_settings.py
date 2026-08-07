# ลองปรับค่า RRF ดูว่าคะแนนขยับไหม
#
# ที่ต้องลองเพราะ RRF ให้คะแนนตามอันดับอย่างเดียว ผู้เข้ารอบอันดับท้าย ๆ ของฝั่ง
# ที่ค้นไม่เจออะไรเลย ก็ยังได้โหวตเท่ากับอันดับท้าย ๆ ของฝั่งที่ค้นเจอ
#
# ดูเฉพาะ variant paraphrase เพราะอีกสี่แบบสร้างจากคำถามต้นฉบับ คะแนนเกาะ 1.0
# อยู่แล้ว ปรับอะไรก็ไม่ขยับ
#
# Run: python -m evaluation.eval_rrf_settings

import json

import config
from evaluation.eval_retrieval import run_one_setting
from evaluation.metrics import average, print_table

VARIANT = "paraphrase"

# (ชื่อ, น้ำหนัก BM25, floor ของ dense)
SETTINGS = [
    ("ค่าเดิม", 1.0, 0.0),
    ("เชื่อ BM25 น้อยลง", 0.5, 0.0),
    ("เชื่อ BM25 มากขึ้น", 2.0, 0.0),
    ("ตัดตัวคะแนนต่ำทิ้ง", 1.0, 0.8),
]


def main():
    print(f"=== ลองค่า RRF บน variant {VARIANT} ===")

    with open(config.GOLDEN_SET_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)["items"]

    config.USE_HYBRID = True
    from src.hybrid_retriever import HybridRetriever

    retriever = HybridRetriever()
    top_k = max(config.EVAL_K_VALUES)

    results = {}
    for name, bm25_weight, dense_floor in SETTINGS:
        config.RRF_BM25_WEIGHT = bm25_weight
        config.RRF_DENSE_FLOOR = dense_floor

        scores_by_variant, _ = run_one_setting(
            retriever, items, top_k, use_bm25=True, use_dense=True, normalize=True
        )
        results[name] = average(scores_by_variant[VARIANT])

    # คืนค่าเดิม เผื่อมีใครเรียกไฟล์นี้แล้วใช้ config ต่อ
    config.RRF_BM25_WEIGHT = 1.0
    config.RRF_DENSE_FLOOR = 0.0

    print()
    print_table(results, ["hit@1", f"hit@{top_k}", "mrr", "ndcg@3"])

    baseline = results["ค่าเดิม"]["mrr"]
    best_name = max(results, key=lambda n: results[n]["mrr"])
    best = results[best_name]["mrr"]
    print(f"\nดีที่สุด: {best_name} — MRR {best:.4f} "
          f"เทียบค่าเดิม {baseline:.4f} ({(best - baseline) / baseline * 100:+.1f}%)")
    print("คำถามทดสอบมี 55 ข้อ ส่วนต่างระดับนี้จึงยังบอกไม่ได้ว่าดีขึ้นจริง")


if __name__ == "__main__":
    main()
