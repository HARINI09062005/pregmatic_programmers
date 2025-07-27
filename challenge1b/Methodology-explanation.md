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