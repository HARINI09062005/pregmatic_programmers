# 📄 PDF Structural Outline Extractor  
**Adobe India Hackathon 2025 – Challenge 1a Submission**

---

## 🚀 Project Overview

This project provides a containerized, offline solution to extract a **structured outline** from PDF files. It detects **title, section headings (H1, H2, H3)** using visual style analysis (font size, boldness, and color), generating a clean JSON file for each PDF.

---

## 🧠 Key Features

- 📚 **Text Extraction** using `PyMuPDF`
- 🧬 **Dominant Style Detection** to avoid false positives on bold/italic words
- 🏷️ **Multi-Level Heading Detection** (H1, H2, H3)
- 🧾 **JSON Output** with document title and outline
- 🐳 Fully containerized with no internet dependency
- ⚙️ Optimized for CPU-only environments

---

## 🗂️ Directory Layout

```
.
├── process_pdf_to_outline.py       # Main PDF parser
├── Dockerfile                      # For containerization
├── input/                          # Folder with input PDFs (read-only)
├── output/                         # Folder where output JSONs are saved
└── README.md
```

---

## 💻 How It Works

1. Opens the PDF using PyMuPDF (`fitz`)
2. Analyzes each line’s **font size**, **boldness**, and **color**
3. Determines the most common style as "body text"
4. Detects **section titles** by finding deviations from the body style
5. Ranks heading levels (H1 > H2 > H3) using font size
6. Builds a **sorted outline** with hierarchy and page numbers
7. Outputs a JSON file for each PDF

---

## ✅ Output Format

The JSON for each PDF looks like this:

```json
{
  "title": "Sample Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "1. Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "1.1 Background",
      "page": 1
    }
  ]
}
```

---

## 🐳 Docker Usage

### 🔧 Build the Image
```bash
docker build -t pdf-outline-extractor .
```

### ▶️ Run the Container
```bash
docker run --rm \
-v $(pwd)/input:/app/input:ro \
-v $(pwd)/output:/app/output \
--network none pdf-outline-extractor
```

---

## ⚙️ Runtime Configuration

| Parameter      | Value              |
|----------------|--------------------|
| CPU            | 8 cores (amd64)     |
| RAM            | ≤ 16 GB            |
| Execution Time | ≤ 10 seconds per 50-page PDF |
| Model Size     | N/A (no ML models) |
| Internet       | ❌ Not used        |


## 📌 Validation Checklist

- [x] Processes all PDFs from `/app/input`
- [x] Outputs a `.json` per `.pdf` to `/app/output`
- [x] Output matches expected format
- [x] No external network access
- [x] Works on AMD64, CPU-only
- [x] Executes under 10 seconds per PDF

---

## 🧠 Implementation Notes

- Uses **dominant style detection** for robust heading classification
- Handles multi-span text lines with different styles
- Skips short captions, numbered bullets, and non-heading lines
- Designed to work even when section numbers are missing

---

## 👨‍💻 Author

Built with ❤️ by [Harini M / Yuvaraj S]  
For Adobe India Hackathon 2025 – Challenge 1a

---
