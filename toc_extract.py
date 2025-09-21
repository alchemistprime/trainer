import os
import glob
import json
import re
import PyPDF2

def extract_toc_from_text(pdf_path, toc_page_nums=None, max_pages=1):
    """Extracts a table of contents from a PDF using a combination of structured and heuristic patterns."""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        pages_to_scan = toc_page_nums if toc_page_nums else range(min(max_pages, len(reader.pages)))

        section_re = re.compile(r"^\s*Part\s*\d+[:\.]?\s*(.+?)\s*[.\s]{2,}\s*(\d+)\s*$", re.IGNORECASE)
        numbered_re = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(.+?)\s*[.\s]{2,}\s*(\d+)\s*$")
        generic_re_with_page = re.compile(r"^\s*([A-Z].*?)\s*[.\s]{2,}\s*(\d+)\s*$")
        generic_re_no_page = re.compile(r"^\s*([A-Z][^.]{3,})\s*$")

        toc = []
        current_section = None

        for page_num in pages_to_scan:
            page = reader.pages[page_num]
            text = page.extract_text() or ""
            for line in text.splitlines():
                line_clean = line.strip()
                if not line_clean or line_clean.isdigit():
                    continue

                m_section = section_re.match(line_clean)
                m_numbered = numbered_re.match(line_clean)
                m_generic_with_page = generic_re_with_page.match(line_clean)
                m_generic_no_page = generic_re_no_page.match(line_clean)

                title = None
                is_section = False
                is_subsection = False

                if m_section:
                    title = m_section.group(1).strip()
                    is_section = True
                elif m_numbered:
                    numbering = m_numbered.group(1)
                    title = m_numbered.group(2).strip()
                    is_section = '.' not in numbering
                    is_subsection = not is_section
                elif m_generic_with_page:
                    title = m_generic_with_page.group(1).strip()
                    is_section = title.isupper() or not current_section
                    is_subsection = not is_section
                elif m_generic_no_page:
                    title_candidate = m_generic_no_page.group(1).strip()
                    if not title_candidate.endswith(('.', '?', '!')):
                        title = title_candidate
                        is_section = title.isupper() or not current_section
                        is_subsection = not is_section

                if title:
                    title = re.sub(r'\s*\.+\s*$', '', title).strip()
                    if is_section:
                        if not toc or toc[-1]['title'] != title:
                            current_section = {"title": title, "subsections": []}
                            toc.append(current_section)
                    elif is_subsection and current_section:
                        if not current_section['subsections'] or current_section['subsections'][-1]['title'] != title:
                            current_section["subsections"].append({"title": title})
    return toc

def main():
    pdf_dir = "Data/Source"
    pdf_paths = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    output_dir = "Data/TOC"
    os.makedirs(output_dir, exist_ok=True)

    for pdf_path in pdf_paths:
        print(f"Processing: {pdf_path}")
        toc = extract_toc_from_text(pdf_path)
        doc_title = os.path.splitext(os.path.basename(pdf_path))[0]
        toc_json = {"doc_title": doc_title, "toc": toc}
        json_path = os.path.join(output_dir, f"{doc_title}_toc.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(toc_json, f, indent=2)
        print(f"TOC saved to {json_path}")

if __name__ == "__main__":
    main()