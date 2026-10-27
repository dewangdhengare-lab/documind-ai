# DocuMind AI — Intelligent Document Intelligence Platform

DocuMind AI is a full-stack document intelligence application powered by Retrieval-Augmented Generation (RAG), local vector search, and high-performance LLM synthesis.

Users can upload documents in **PDF**, **DOCX**, **TXT**, and **CSV** formats (up to 50MB) and execute six core AI operations with citations and grounded reasoning:

1. **AI Document Chat** — Conversational RAG with page and source snippet citations, multi-turn dialogue, and automated CSV statistical computation.
2. **Document Summarization** — Multi-depth summarization (Short, Executive, Detailed, Section-wise, Key Points, Facts & Figures) with Markdown export.
3. **Information Extraction** — Predefined and custom structured extraction templates with data table display and downloadable CSV and JSON exports.
4. **Document Comparison** — Multi-document cross-comparison detecting common themes, nuances, and contradictions.
5. **Interactive Quiz Generator** — Grounded assessment creation (Multiple Choice, True/False, Short Answer) with live scoring, detailed answer keys, and source explanations.
6. **Report Generator** — Full-fledged research and corporate report synthesis with in-app editing and export to **PDF** and **DOCX**.

---

## Architecture Overview

```
d:\Gen_AI_Project\
├── backend/
│   ├── config.py                 # Application configuration & path management
│   ├── database.py               # SQLite setup with WAL mode and foreign keys
│   ├── models.py                 # SQLAlchemy relational schemas
│   ├── schemas.py                # Pydantic v2 schemas and request models
│   ├── main.py                   # FastAPI application entry point with lifespan
│   ├── services/
│   │   ├── pdf_parser.py         # pypdf text extraction with page metadata
│   │   ├── docx_parser.py        # python-docx parser with heading hierarchy
│   │   ├── txt_parser.py         # Text chunking and section extraction
│   │   ├── csv_service.py        # Pandas analysis, profiling, and query execution
│   │   ├── chunking_service.py   # Overlapping semantic text chunker
│   │   ├── embedding_service.py  # Local sentence-transformers (all-MiniLM-L6-v2)
│   │   ├── vector_store.py       # Persistent ChromaDB storage
│   │   ├── retrieval_service.py  # Cosine-similarity top-k semantic retrieval
│   │   ├── llm_service.py        # Groq API provider service
│   │   ├── chat_service.py       # RAG chat logic with citation building
│   │   ├── summarization_service.py # Summarization engine
│   │   ├── extraction_service.py # Structured JSON/table extraction
│   │   ├── comparison_service.py # Multi-document comparison engine
│   │   ├── quiz_service.py       # Assessment generation and scoring
│   │   ├── report_service.py     # Report synthesis and markdown editing
│   │   └── export_service.py     # ReportLab PDF and python-docx exports
│   ├── routers/                  # Modular FastAPI routers
│   ├── uploads/                  # Secure file upload storage
│   └── tests/
│       └── test_backend.py       # Automated test suite
├── frontend/
│   ├── src/
│   │   ├── api/client.ts         # Centralized Axios client for all features
│   │   ├── components/           # Sidebar, Layout, FileUpload, Selector, etc.
│   │   ├── pages/                # 8 complete application workspaces
│   │   ├── hooks/useDocuments.ts # Real-time polling document hook
│   │   └── types/index.ts        # TypeScript interfaces
├── test_files/                   # Real test documents (PDF, DOCX, TXT, CSV)
└── README.md
```

---

## Prerequisites

- **Python**: 3.10+ (Tested on Python 3.13)
- **Node.js**: 18+ and npm
- **Groq API Key**: Get a free API key at [console.groq.com](https://console.groq.com/)

---

## Quick Start Guide

### 1. Configure Backend Environment

Copy `.env.example` to `backend/.env`:
```powershell
cp backend/.env.example backend/.env
```

Open `backend/.env` and insert your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
```

> **Note**: Embedding runs locally via `sentence-transformers` (`all-MiniLM-L6-v2`) and requires no external API key.

### 2. Start the Backend API Server

In a PowerShell terminal:
```powershell
cd d:\Gen_AI_Project\backend
uvicorn main:app --host 127.0.0.1 --port 8008 --reload
```

The backend starts at `http://127.0.0.1:8008`. You can inspect the Swagger documentation at `http://127.0.0.1:8008/docs`.

### 3. Start the Frontend Development Server

In a second PowerShell terminal:
```powershell
cd d:\Gen_AI_Project\frontend
npm run dev
```

The frontend will run at `http://localhost:5173`. Open your browser and navigate to `http://localhost:5173`.

---

## Automated Tests

### Backend Test Suite
Run the test suite verifying document parsing, vector indexing, retrieval, and PDF/DOCX exports:
```powershell
cd d:\Gen_AI_Project\backend
python -m pytest tests/test_backend.py -v
```

### Frontend Type-Check & Production Build
```powershell
cd d:\Gen_AI_Project\frontend
npm run build
```

---

## Testing the 6 Core Features

We have provided five pre-generated test documents in `d:\Gen_AI_Project\test_files\`:
- `research_paper.pdf` (5-page healthcare AI study with methodology, tables, results)
- `project_plan.docx` (Project Phoenix technical implementation plan)
- `sample_report.txt` (Q3 business report)
- `annual_review.txt` (Annual strategic performance review)
- `sales_data.csv` (20 rows of regional product sales metrics)

### Workflow Walkthrough:

1. **Document Library (`/documents`)**:
   - Drag and drop or browse to upload `research_paper.pdf`, `project_plan.docx`, `annual_review.txt`, and `sales_data.csv`.
   - The status progresses from `Uploading` &rarr; `Processing` &rarr; `Ready`.

2. **AI Document Chat (`/chat`)**:
   - Select `research_paper.pdf`.
   - Ask: *"What are the primary findings regarding diagnostic imaging accuracy?"*
   - Verify that the answer cites `research_paper.pdf` and expands to show the exact grounding snippet.
   - Select `sales_data.csv`.
   - Ask: *"What is the total revenue and which category has the highest sales?"*
   - Verify that DocuMind uses pandas calculations to compute exact figures.

3. **Document Summarization (`/summarize`)**:
   - Choose `project_plan.docx`.
   - Pick **Executive Summary** or **Facts & Figures**.
   - Click **Generate Summary** and review the structured markdown output.
   - Click **Export (.md)** or copy to clipboard.

4. **Information Extraction (`/extract`)**:
   - Select `project_plan.docx` and choose template **Project Information** or **Risks & Mitigations**.
   - Click **Extract Structured Data**.
   - Inspect the interactive table and click **Export CSV** or **Export JSON**.

5. **Document Comparison (`/compare`)**:
   - Select both `sample_report.txt` and `annual_review.txt`.
   - Click **Compare Selected Documents**.
   - Review the comparison table, similarities, differences, and highlighted contradictions.

6. **Quiz Generator (`/quiz`)**:
   - Select `research_paper.pdf`.
   - Set question count to 5, choose Multiple Choice & True/False, and click **Generate Interactive Quiz**.
   - Complete the quiz, submit your answers, and review your final score and source-grounded explanations.

7. **Report Generator (`/reports`)**:
   - Select `project_plan.docx` and `research_paper.pdf`.
   - Configure title, purpose, audience, and sections.
   - Click **Generate Report**.
   - Review the output, toggle **Edit Text** to customize sections, and click **PDF** or **DOCX** to download the rendered file.
