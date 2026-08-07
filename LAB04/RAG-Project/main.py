





#1. สร้าง index ก่อน: python build_index.py
#2. จากนั้นรัน: python main.py


import os

import config
from src import index_meta
from src.rag_pipeline import RAGPipeline

def print_answer(result):   # Display the answer and its source
    print()
    print(result["answer"])

    # เปิดกลับมาใช้ เพราะงานนี้ต้องตรวจสอบย้อนกลับได้ว่าคำตอบมาจากคู่ Q&A ไหน
    if config.SHOW_SOURCES and result["sources"]:
        print("\nแหล่งอ้างอิง:")
        for source in result["sources"]:
            print(f"  [{source['n']}] {source['question']}")
            print(f"      บรรทัดที่ {source['line_no']} · คะแนน {source['score']}")

    if config.SHOW_DEBUG:
        print(f"\n[Debug] Search queries: {result['queries_used']}")
        print(f"[Debug] Execution time (seconds): {result['timings']}")


def main():
    # Build the index if it doesn't exist
    if not os.path.exists(config.FAISS_INDEX_FILE):
        print("FAISS index not found.")
        print("Run: python build_index.py")
        return

    # if edit dataset and forget build 
    index_meta.warn_if_stale()

    print("--" * 30)
    print("ระบบถาม-ตอบความรู้ยุทโธปกรณ์และกิจการทหาร (RAG)")
    print("--" * 30)

    rag = RAGPipeline()
    #rag.show_settings()

    print("\nพิมพ์คำถามเกี่ยวกับยุทโธปกรณ์หรือกิจการทหารได้เลย (พิมพ์ exit เพื่อออก)")

    while True:
        question = input("\nQ: ").strip()

        if question in ("exit", "quit", "q"):
            print("จบการทำงาน")
            break

        if not question:
            continue

        result = rag.ask(question)
        print_answer(result)


if __name__ == "__main__":
    main()
