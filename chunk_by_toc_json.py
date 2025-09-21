import os
import json
import re
import pdfplumber

def load_toc_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_pdf_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def find_section_indices(text, section_titles):
    # Returns a dict mapping each title to its start index in the text
    indices = {}
    for title in section_titles:
        # Escape special regex characters in title
        pattern = re.escape(title)
        match = re.search(pattern, text)
        if match:
            indices[title] = match.start()
    return indices

def chunk_by_toc(pdf_text, toc_json):
    doc_title = toc_json["doc_title"]
    toc = toc_json["toc"]
    chunks = []

    # Gather all subsection titles in order
    all_subsections = []
    for section in toc:
        section_topic = section["topic"]
        for subsection in section["subsections"]:
            all_subsections.append({
                "section_topic": section_topic,
                "subsection_topic": subsection["topic"]
            })

    # Find indices for each subsection topic
    subsection_titles = [sub["subsection_topic"] for sub in all_subsections]
    indices = find_section_indices(pdf_text, subsection_titles)

    # Sort subsection topics by their index in the text
    sorted_subsections = sorted(
        [(title, idx) for title, idx in indices.items()],
        key=lambda x: x[1]
    )

    # Chunk text for each subsection
    for i, (title, start_idx) in enumerate(sorted_subsections):
        end_idx = sorted_subsections[i+1][1] if i+1 < len(sorted_subsections) else len(pdf_text)
        chunk_text = pdf_text[start_idx:end_idx].strip()
        # Find section topic for this subsection
        section_topic = next(
            (sub["section_topic"] for sub in all_subsections if sub["subsection_topic"] == title),
            None
        )
        chunk = {
            "doc_title": doc_title,
            "section_topic": section_topic,
            "subsection_topic": title,
            "text": chunk_text
        }
        chunks.append(chunk)
    return chunks

def clean_text(text):
    # Replace common unicode escapes with ASCII equivalents
    text = text.replace('\u2019', "'")
    text = text.replace('\u2014', '-')
    text = text.replace('\u2026', '...')
    # Replace newlines with space
    text = text.replace('\n', ' ')
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    # Paths
    toc_json_path = "Data/Source/understanding_the_buyer_toc.json"
    pdf_path = "Data/Source/Understanding The Buyer.pdf"
    output_path = "Data/Source/understanding_the_buyer_chunks.json"

    # Load TOC JSON
    toc_json = load_toc_json(toc_json_path)
    # Extract PDF text
    pdf_text = extract_pdf_text(pdf_path)
    # Chunk by TOC
    chunks = chunk_by_toc(pdf_text, toc_json)

    # Clean text in chunks
    for chunk in chunks:
        chunk['text'] = clean_text(chunk['text'])

    # Save chunks to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    print(f"Chunked data saved to {output_path}")

    # Print summary
    for chunk in chunks:
        print(f"\nSection: {chunk['section_topic']}")
        print(f"Subsection: {chunk['subsection_topic']}")
        print(f"Text preview: {chunk['text'][:200]}...")
        print("-" * 40)

if __name__ == "__main__":
    main()