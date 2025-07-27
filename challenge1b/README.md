# Approach Explanation – PDF Document Relevance Extractor (Challenge 1b)

## Problem Overview

The task is to design an intelligent document processing system that extracts the most relevant sections and subsections from a set of PDF documents. The relevance is defined with respect to a **persona** and a **job-to-be-done**, provided via an input JSON.

## Methodology

### 1. **PDF Parsing with Heuristic Sectioning**
We use `PyMuPDF (fitz)` to parse PDF documents and detect section boundaries using font size, boldness, and short line heuristics. If a line is bold or larger than body text and short in length, it's considered a section heading.

### 2. **Text Embedding with SentenceTransformers**
The model `all-MiniLM-L6-v2` (from Sentence Transformers) is used to generate semantic embeddings. These embeddings are generated for:
- The **persona query** (user’s role and expertise)
- The **context query** (the job-to-be-done task)
- Each document **section** and **subsection (paragraph)**

### 3. **Smart Scoring**
We compute cosine similarity of each section and paragraph against the persona and task embeddings:
score = 0.8 * similarity(context, section) + 0.2 * similarity(persona, section)
Only sections above a certain relevance threshold are retained.

### 4. **Subsection Extraction**
Top-ranked sections are further split into smaller paragraphs (subsections). These are scored and ranked separately, with the top 5 returned for deep insight.

### 5. **Offline and Efficient**
The model is downloaded during Docker build, so the container runs without internet. The system is CPU-friendly and designed to process 3–10 documents under 60 seconds.

## Output Structure

- `extracted_sections`: Top 5 relevant sections with titles, ranks, and page numbers.
- `subsection_analysis`: Top 5 short refined text snippets from across all documents.

This architecture ensures relevance, clarity, and performance under tight constraints.

```
challenge1b/
├── README.md
├── Dockerfile
├── requirements.txt
├── main.py
├── input/
│   ├── input.json
│   └── pdfs/
│       └── sample1.pdf
│       └── sample2.pdf
│       └── ...
├── output/
│   └── output.json
├── execution_instructions.md
└── Methodology-explanation.md

```
# Docker Execution Instructions

## Prerequisites

- Docker installed and running

```
- Folder structure:
challenge1b/
├── Dockerfile
├── requirements.txt
├── main.py
├── input/
│   ├── input.json
│   └── pdfs/
│       └── sample1.pdf
│       └── sample2.pdf
│       └── ...
├── output/
│   └── output.json

```

## 1. Build Docker Image
docker build -t pdf-analyzer .

## 2. Run the Analyzer

docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-analyzer

## 3. View Output
Check the generated output:
cat output/output.json

# ✅ Validation Checklist

#### 📄 Output Format Requirements
- [x] `output/challenge1b_output.json` is generated
- [x] Output includes top-level `metadata`, `extracted_sections`, and `subsection_analysis` fields

**Metadata**
- [X] Contains list of input documents
- [x] Contains persona string
- [x] Contains job-to-be-done string

**Extracted Sections**
- [x] Each entry includes `document` (PDF filename)
- [x] Each entry includes `page_number` (integer)
- [x] Each entry includes `section_title` (string)
- [x] Each entry includes `importance_rank` (integer)

**Subsection Analysis**
- [x] Each entry includes `document` (PDF filename)
- [x] Each entry includes `refined_text` (≤200 words, semantically relevant)
- [x] Each entry includes `page_number` (integer)

- [x] Output conforms to schema defined in `sample_dataset/schema/output_schema.json`

---

#### 🚦 Runtime & Resource Constraints
- [x] ✅ Runs on **CPU only**
- [x] ✅ Total **model size ≤ 1GB**
- [x] ✅ Processing time ≤ 60 seconds for 3–5 PDF documents
- [x] ✅ Processing completes within 10 seconds for a single 50-page PDF
- [x] ✅ Executes with **no internet access**
- [x] ✅ Memory usage remains within **16GB limit**
- [x] ✅ Fully compatible with **linux/amd64** (x86_64) architecture
