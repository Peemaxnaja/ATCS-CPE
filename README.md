<div align="center">

# `ATCS-CPE`

### Advanced Topics in Computer Engineering — Coursework Portfolio

*A single repository holding every lab and the final project for the course.*

<br/>

![Course](https://img.shields.io/badge/course-ATCS--CPE-0A0A0A?style=for-the-badge)
![Labs](https://img.shields.io/badge/labs-3%20%2F%2010-1F6FEB?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-in%20progress-F0B429?style=for-the-badge)

</div>

---

## 👤 Author

| | |
| :--- | :--- |
| **Name** | สิรวิชญ์ ศิริสลุง |
| **Student ID** | `116730462023-6` |
| **GitHub** | [@Peemaxnaja](https://github.com/Peemaxnaja) |
| **Repository** | [Peemaxnaja/ATCS-CPE](https://github.com/Peemaxnaja/ATCS-CPE) |

---

## 📚 Lab Index

| # | Lab | Topic | Stack | Status |
| :---: | :--- | :--- | :--- | :---: |
| 01 | **[LAB01](LAB01/)** | LLM Data Pipeline for RAG — 8-stage ingestion pipeline. Owned **Step 5: Metadata Enrichment**. | `Python` `Pydantic` `pytest` | ✅ |
| 02 | **[LAB02](LAB02/)** | RAG Retrieval System built from scratch — Thai firearms law & safety QA over a self-authored 313-pair knowledge base. | `Python` `FAISS` `sentence-transformers` | ✅ |
| 03 | `LAB03` | — | — | ⏳ |
| 04 | **[LAB04](LAB04/)** | RAG System Development I — hybrid BM25 + dense retrieval with RRF, reranking, query transforms and a metrics harness, over a self-authored 182-pair Thai military knowledge base. | `Python` `FAISS` `rank-bm25` `pythainlp` | ✅ |
| 05 | `LAB05` | — | — | ⏳ |
| 06 | `LAB06` | — | — | ⏳ |
| 07 | `LAB07` | — | — | ⏳ |
| 08 | `LAB08` | — | — | ⏳ |
| 09 | `LAB09` | — | — | ⏳ |
| 10 | `LAB10` | — | — | ⏳ |
| ★ | `Final-Project` | — | — | ⏳ |

<sub>✅ submitted · 🚧 in progress · ⏳ not started</sub>

---

## 🗂 Repository Layout

```
ATCS-CPE/
│
├── LAB01/                          ✅ LLM Data Pipeline for RAG
│   ├── README.md                   → write-up, citations, submission guide
│   └── Sikibidi-six-seven-RAG/     → group project (git subtree, full history)
│       ├── config/  data/  docs/
│       ├── src/     tests/
│       ├── requirements.txt
│       └── run_pipeline.py
│
├── LAB02/                          ✅ RAG Retrieval System from scratch
│   ├── README.md                   → architecture, results analysis, citations
│   └── RAG-Project/
│       ├── data/gun_q_a.txt        → 313-pair Thai QA knowledge base
│       ├── labs/                   → lab01–lab07 step scripts
│       ├── src/                    → loader, splitter, embedder, FAISS store, retriever
│       ├── outputs/                → extracted text, chunks, embeddings, results
│       ├── vector_db/              → prebuilt FAISS index + chunk store
│       ├── config.py
│       └── main.py
│
├── LAB04/                          ✅ RAG System Development I
│   ├── README.md                   → architecture, evaluation analysis, citations
│   └── RAG-Project/
│       ├── data/military_qa.txt    → 182-pair Thai military knowledge base
│       ├── data/golden_set.json    → 60 questions x 4 query variants
│       ├── labs/                   → lab01–lab07 step scripts
│       ├── src/                    → + hybrid retriever, reranker, query transform,
│       │                             prompts, generator, memory, pipeline
│       ├── evaluation/             → Hit@k, Recall@k, Precision@k, MRR, nDCG
│       ├── outputs/                → pipeline artifacts + evaluation reports
│       ├── vector_db/              → prebuilt FAISS + BM25 indexes
│       ├── config.py               → one switch per feature
│       ├── build_index.py
│       └── main.py
│
├── LAB03/ LAB05/ … LAB10/          ⏳ one folder per lab
│   ├── <code>.ipynb | .py
│   ├── dataset.csv                 (if any)
│   ├── report.pdf                  (if any)
│   └── README.md
│
├── Final-Project/                  ⏳
│   ├── source_code/
│   ├── dataset/
│   ├── report.pdf
│   └── README.md
│
└── README.md                       ← you are here
```

Every lab is self-contained: its code, data, report, and a `README.md` explaining what was built, how to run it, and where the data came from.

---

## 🚀 Getting Started

```bash
git clone https://github.com/Peemaxnaja/ATCS-CPE.git
cd ATCS-CPE/LAB01/Sikibidi-six-seven-RAG

py -m pip install -r requirements.txt
py run_pipeline.py all
```

Each lab folder documents its own setup — see the lab's `README.md` for exact commands.

---

## 📐 Submission Convention

The course runs on a **one-repo-per-student** model. Every lab lands in this repository under its own `LABxx/` folder, committed and pushed **before the deadline** — grading takes commit history and push timestamps into account, so work is committed incrementally rather than dumped in a single commit.

Any external dataset, source code, or model is **cited with a URL** in the lab's `README.md`. Nothing here uses copyrighted, personal, or unlawfully obtained data.

> 📖 Full guidelines, including the required folder structure and the citation policy → **[LAB01/README.md § วิธีการส่งงานของรายวิชา](LAB01/README.md#5-วิธีการส่งงานของรายวิชา-submission-guidelines)**

---

<div align="center">
<sub>Built for ATCS-CPE · All work committed incrementally, sources cited.</sub>
</div>
