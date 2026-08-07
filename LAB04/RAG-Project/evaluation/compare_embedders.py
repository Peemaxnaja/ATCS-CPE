# Compare embedding models on the same corpus, chunks and golden set.
#
# Why
#   LAB02 and the first pass of this lab both used
#   paraphrase-multilingual-MiniLM-L12-v2, and both showed the same symptom:
#   a handful of chunks act as hub vectors that come back for unrelated
#   queries. MiniLM is a general similarity model — it was never trained for
#   retrieval. multilingual-e5-small is the same 384 dimensions but trained
#   with a query/passage objective, so it is the fair thing to compare against.
#
# What is held fixed
#   Chunks, chunk order, BM25 index and golden set are shared. Only the FAISS
#   index changes, so any difference is the embedder's doing.
#
# The e5 family requires "query: " and "passage: " prefixes. Without them the
# model still returns vectors, they are just worse — a silent failure, which is
# why the prefixes live in config next to the model name.
#
# Run: python -m evaluation.compare_embedders

import json
import os
import time

import numpy as np

import config
from evaluation.eval_retrieval import VARIANTS, run_one_setting
from evaluation.metrics import average, print_table

REPORT_FILE = os.path.join(config.OUTPUT_DIR, "compare_embedders.json")

EMBEDDERS = [
    {
        "name": "MiniLM",
        "model": "paraphrase-multilingual-MiniLM-L12-v2",
        "query_prefix": "",
        "passage_prefix": "",
        "index": os.path.join(config.VECTOR_DB_DIR, "document.index"),
    },
    {
        "name": "e5-small",
        "model": "intfloat/multilingual-e5-small",
        "query_prefix": "query: ",
        "passage_prefix": "passage: ",
        "index": os.path.join(config.VECTOR_DB_DIR, "document_e5.index"),
    },
]


def apply(embedder):
    """ชี้ config ไปที่โมเดลและ index ของตัวที่กำลังทดสอบ"""
    config.EMBEDDING_MODEL_NAME = embedder["model"]
    config.EMBEDDING_QUERY_PREFIX = embedder["query_prefix"]
    config.EMBEDDING_PASSAGE_PREFIX = embedder["passage_prefix"]
    config.FAISS_INDEX_FILE = embedder["index"]


def build_if_missing(embedder):
    """สร้าง FAISS index ของโมเดลนี้ ถ้ายังไม่มี

    ใช้ chunk ชุดเดิมจาก chunk_store เสมอ ไม่ตัดใหม่ ลำดับจึงตรงกันเป๊ะ
    และ BM25 กับ golden set ก็ยังเป็นชุดเดียวกันทั้งสองฝั่ง
    """
    if os.path.exists(embedder["index"]):
        print(f"  ใช้ index เดิมที่ {os.path.basename(embedder['index'])}")
        return

    from src.embedding_model import EmbeddingModel
    from src.vector_store import VectorStore, load_chunk_store

    print(f"  ยังไม่มี index — สร้างใหม่ด้วย {embedder['model']}")
    chunks = load_chunk_store(config.CHUNK_STORE_FILE)
    embeddings = EmbeddingModel().encode([chunk["text"] for chunk in chunks])

    VectorStore().build(np.asarray(embeddings)).save(embedder["index"])


def evaluate(embedder, items, top_k):
    """วัด dense อย่างเดียว และวัดแบบผสม ด้วยโค้ดชุดเดียวกับ eval_retrieval"""
    from src.hybrid_retriever import HybridRetriever

    config.USE_HYBRID = True
    retriever = HybridRetriever()
    bm25_index = retriever.bm25
    retriever.reranker = None

    report = {}
    for name, use_bm25, use_dense in [("dense", False, True), ("hybrid", True, True)]:
        retriever.bm25 = bm25_index if use_bm25 else None
        start_time = time.time()

        scores_by_variant, _ = run_one_setting(
            retriever, items, top_k, use_bm25, use_dense, normalize=True
        )
        all_scores = [s for scores in scores_by_variant.values() for s in scores]

        report[name] = {
            "overall": average(all_scores),
            "by_variant": {v: average(s) for v, s in scores_by_variant.items() if s},
            "ms_per_query": round((time.time() - start_time) * 1000 / len(all_scores), 1),
        }
    return report


def main():
    print("=== เทียบโมเดล embedding ===")
    print("chunk, BM25 และ golden set ใช้ชุดเดียวกันทั้งหมด ต่างกันแค่ตัว embedder\n")

    with open(config.GOLDEN_SET_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)["items"]
    top_k = max(config.EVAL_K_VALUES)

    results = {}
    for embedder in EMBEDDERS:
        print(f"[{embedder['name']}] {embedder['model']}")
        apply(embedder)
        build_if_missing(embedder)
        results[embedder["name"]] = evaluate(embedder, items, top_k)
        print()

    columns = ["hit@1", f"hit@{top_k}", "mrr", "ndcg@3"]

    for mode in ("dense", "hybrid"):
        print(f"=== {mode} — ภาพรวมทุกรูปแบบคำถาม ===")
        print_table({n: r[mode]["overall"] for n, r in results.items()}, columns)
        print()

    for variant in VARIANTS:
        rows = {}
        for name, report in results.items():
            for mode in ("dense", "hybrid"):
                scores = report[mode]["by_variant"].get(variant)
                if scores:
                    rows[f"{name}/{mode}"] = scores
        if rows:
            print(f"=== รูปแบบ: {variant} ===")
            print_table(rows, columns)
            print()

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump({"n_items": len(items), "embedders": EMBEDDERS, "results": results},
                  f, ensure_ascii=False, indent=2)
    print(f"บันทึกรายงานที่ {REPORT_FILE}")


if __name__ == "__main__":
    main()
