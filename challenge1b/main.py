import json
import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
import datetime
import re

# --- Configuration ---
MODEL_NAME = 'all-MiniLM-L6-v2'
RELEVANCE_THRESHOLD = 0.25
MAX_RESULTS = 5

def clean_text(text):
    """Cleans text by removing list markers and extra whitespace."""
    text = text.replace('•', '').replace('\u2022', '').replace('\u00A0', ' ').replace('\uf0b7','').replace('\u00b0F','°F').replace('\u00b0C','°C').replace('\n',' ')
    text = re.sub(r'^\s*[-*]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

def is_heading(span, body_font_size):
    """Heuristic to check if a text span is a heading."""
    size = round(span["size"])
    is_bold = "bold" in span["font"].lower()
    if size > body_font_size or (is_bold and size >= body_font_size):
        return True
    return False

def parse_pdf_into_sections(doc_path, doc_name):
    """Parses a PDF document into sections based on headings."""
    try:
        doc = fitz.open(doc_path)
    except Exception as e:
        print(f"Error opening {doc_path}: {e}")
        return []

    sections = []
    current_heading = "Introduction"
    current_text = ""
    last_page_num = 1
    font_sizes = {}

    for page in doc:
        for block in page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span['text'].strip():
                            size = round(span["size"])
                            font_sizes[size] = font_sizes.get(size, 0) + len(span["text"])

    body_font_size = max(font_sizes, key=font_sizes.get) if font_sizes else 10

    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)["blocks"]
        for block in blocks:
            if block["type"] == 0 and "lines" in block:
                line_text = "".join(span["text"] for line in block["lines"] for span in line["spans"]).strip()
                if not line_text:
                    continue
                first_span = block["lines"][0]["spans"][0]
                if is_heading(first_span, body_font_size) and len(line_text.split()) < 12:
                    if current_text.strip():
                        sections.append({
                            "document": doc_name,
                            "section_title": current_heading,
                            "content": current_text.strip(),
                            "page_number": last_page_num
                        })
                    current_heading = line_text
                    current_text = ""
                    last_page_num = page_num
                else:
                    for line in block["lines"]:
                        current_text += "".join(span["text"] for span in line["spans"]) + " "
                    current_text += "\n"

    if current_text.strip():
        sections.append({
            "document": doc_name,
            "section_title": current_heading,
            "content": current_text.strip(),
            "page_number": last_page_num
        })
    return sections

def analyze_documents(input_data):
    """Core analysis function using SentenceTransformers."""
    print("Loading AI model...")
    model = SentenceTransformer(MODEL_NAME)
    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]

    print(f"Using Persona Query: '{persona}'")
    print(f"Using Context Query: '{job}'")

    context_embedding = model.encode(job, convert_to_tensor=True)
    persona_embedding = model.encode(persona, convert_to_tensor=True)

    all_sections = []
    doc_list = input_data["documents"]

    print("Parsing documents...")
    for doc_info in doc_list:
        doc_filename = os.path.basename(doc_info["filename"])
        doc_path = doc_info["filename"]
        if os.path.exists(doc_path):
            all_sections.extend(parse_pdf_into_sections(doc_path, doc_filename))
        else:
            print(f"Warning: Document not found at '{doc_path}'")

    if not all_sections:
        return None

    print("Scoring all sections...")
    for section in all_sections:
        score_text = f"{section['section_title']}\n{section['content'][:500]}"
        text_embedding = model.encode(score_text, convert_to_tensor=True)
        context_score = util.cos_sim(context_embedding, text_embedding)[0][0].item()
        persona_score = util.cos_sim(persona_embedding, text_embedding)[0][0].item()
        section['score'] = (0.8 * context_score) + (0.2 * persona_score)

    ranked_sections = sorted(all_sections, key=lambda s: s['score'], reverse=True)
    relevant_sections = [s for s in ranked_sections if s['score'] >= RELEVANCE_THRESHOLD]
    final_sections = relevant_sections[:MAX_RESULTS]

    extracted_sections_output = []
    for i, section in enumerate(final_sections):
        extracted_sections_output.append({
            "document": section["document"],
            "section_title": section["section_title"],
            "importance_rank": i + 1,
            "page_number": section["page_number"]
        })

    print(f"Deriving top {len(final_sections)} subsections...")
    subsection_pool = []
    for section in final_sections:
        paragraphs = [p.strip() for p in section['content'].split('\n\n') if len(p.strip().split()) > 15]
        for para in paragraphs:
            subsection_pool.append({
                'text': para,
                'document': section['document'],
                'page_number': section['page_number']
            })

    subsection_analysis_output = []
    if subsection_pool:
        for snippet in subsection_pool:
            text_embedding = model.encode(snippet['text'], convert_to_tensor=True)
            context_score = util.cos_sim(context_embedding, text_embedding)[0][0].item()
            persona_score = util.cos_sim(persona_embedding, text_embedding)[0][0].item()
            snippet['score'] = (0.8 * context_score) + (0.2 * persona_score)

        final_snippets = sorted(subsection_pool, key=lambda s: s['score'], reverse=True)[:MAX_RESULTS]
        for snippet in final_snippets:
            subsection_analysis_output.append({
                "document": snippet['document'],
                "refined_text": clean_text(snippet['text']),
                "page_number": snippet['page_number']
            })

    final_output = {
        "metadata": {
            "input_pdfs": [os.path.basename(d["filename"]) for d in doc_list],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        },
        "extracted_sections": extracted_sections_output,
        "subsection_analysis": subsection_analysis_output
    }

    return final_output

def main():
    input_file_path = 'input/input.json'
    output_file_path = 'output/output.json'
    pdf_folder = 'input/pdfs'

    if not os.path.exists(input_file_path):
        print(f"Error: Input file not found at '{input_file_path}'")
        return

    with open(input_file_path, 'r') as f:
        input_data = json.load(f)

    # Adjust PDF paths
    for doc in input_data.get("documents", []):
        doc["filename"] = os.path.join(pdf_folder, os.path.basename(doc["filename"]))

    result = analyze_documents(input_data)

    if result:
        with open(output_file_path, 'w') as f:
            json.dump(result, f, indent=4)
        print(f"\n✅ Analysis complete. Output saved to '{output_file_path}'")
    else:
        print("⚠️ No relevant sections found.")

if __name__ == '__main__':
    main()
