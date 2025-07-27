# Docker Execution Instructions

## Prerequisites

- Docker installed and running
- Input filename must me input.json

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