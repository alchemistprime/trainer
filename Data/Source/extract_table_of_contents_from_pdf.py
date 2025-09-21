import os
import glob
import json
import re
import sys
import PyPDF2

def extract_toc_from_text(pdf_path, max_pages=2):
    """
    Extracts a table of contents from a PDF and outputs a toc.json-style hierarchy.
    """
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            pages_to_scan = range(min(max_pages, len(reader.pages)))

            # Patterns to identify section and subsection headers
            # Using findall to capture all matches on a line
            section_re = re.compile(r"^(Part \d+[:]?\s*|)(.*)$", re.IGNORECASE)
            subsection_re = re.compile(r"^\s*(\d+[.]\s*|)(.*)$")

            toc = []
            current_section = None

            for page_num in pages_to_scan:
                page = reader.pages[page_num]
                text = page.extract_text() or ""
                
                # Split text into lines, handling different newline characters
                lines = text.replace('\r', '').split('\n')
                
                for line in lines:
                    line_clean = line.strip()
                    if not line_clean:
                        continue

                    # Attempt to match as a section
                    m_section = section_re.match(line_clean)
                    if m_section:
                        # Check for a specific section title to avoid false positives
                        title = m_section.group(2).strip()
                        if len(title) > 2: # Heuristic to ignore single-letter titles
                            current_section = {"topic": title, "subsections": []}
                            toc.append(current_section)
                            
                    # Attempt to match as a subsection and ensure we have a current section
                    m_subsection = subsection_re.match(line_clean)
                    if m_subsection and current_section:
                        # Heuristic to distinguish subsections from other text
                        if m_subsection.group(1).strip() or " " in m_subsection.group(2):
                           current_section["subsections"].append({"topic": m_subsection.group(2).strip()})

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    return toc

def main():
    pdf_dir = "Data/Source"
    pdf_paths = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    output_dir = "Data/TOC"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get number of pages to scan from command line, default to 2
    try:
        num_pages_to_scan = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    except (ValueError, IndexError):
        num_pages_to_scan = 2

    for pdf_path in pdf_paths:
        print(f"Processing: {pdf_path}")
        toc = extract_toc_from_text(pdf_path, max_pages=num_pages_to_scan)
        doc_title = os.path.splitext(os.path.basename(pdf_path))[0].replace(" ", "_")
        toc_json = {"doc_title": doc_title, "toc": toc}
        json_path = os.path.join(output_dir, f"{doc_title}_toc.json")
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(toc_json, f, indent=2)
        print(f"TOC saved to {json_path}")

if __name__ == "__main__":
    main()
