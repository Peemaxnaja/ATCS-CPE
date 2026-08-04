<div align="center">

# `ATCS-CPE`

### Advanced Topics in Computer Engineering — Coursework Portfolio

*A single repository holding every lab and the final project for the course.*

<br/>

![Course](https://img.shields.io/badge/course-ATCS--CPE-0A0A0A?style=for-the-badge)
![Labs](https://img.shields.io/badge/labs-1%20%2F%2010-1F6FEB?style=for-the-badge)
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
| 02 | `LAB02` | — | — | ⏳ |
| 03 | `LAB03` | — | — | ⏳ |
| 04 | `LAB04` | — | — | ⏳ |
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
├── LAB02/ … LAB10/                 ⏳ one folder per lab
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
