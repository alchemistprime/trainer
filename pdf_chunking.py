import streamlit as st
import PyPDF2
import re
import json

# --- TOC Extraction ---
def extract_toc_from_text(pdf_path, toc_page_nums=None, max_pages=5):
    """Extracts a table of contents from a PDF using a combination of structured and heuristic patterns."""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        pages_to_scan = toc_page_nums if toc_page_nums else range(min(max_pages, len(reader.pages)))

        # Regex for patterns like "Part 1: Title ........ 5"
        section_re = re.compile(r"^\s*Part\s*\d+[:\.]?\s*(.+?)\s*[.\s]{2,}\s*(\d+)\s*$", re.IGNORECASE)
        # Regex for patterns like "1.1 Title ........ 5"
        numbered_re = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(.+?)\s*[.\s]{2,}\s*(\d+)\s*$")
        # Regex for generic titles followed by a page number, e.g., "Some Title ........ 5"
        generic_re_with_page = re.compile(r"^\s*([A-Z].*?)\s*[.\s]{2,}\s*(\d+)\s*$")
        # Regex for generic titles on a line by themselves, e.g., "Conclusion"
        generic_re_no_page = re.compile(r"^\s*([A-Z][^.]{3,})\s*$")

        toc = []
        current_section = None

        for page_num in pages_to_scan:
            page = reader.pages[page_num]
            text = page.extract_text() or ""
            for line in text.splitlines():
                line_clean = line.strip()

                # Skip empty lines or lines that are likely just page numbers
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
                    # Avoid matching full sentences by checking for ending punctuation.
                    if not title_candidate.endswith(('.', '?', '!')):
                        title = title_candidate
                        is_section = title.isupper() or not current_section
                        is_subsection = not is_section

                if title:
                    # Clean up trailing dots or weird characters from the title
                    title = re.sub(r'\s*\.+\s*$', '', title).strip()

                    if is_section:
                        if not toc or toc[-1]['title'] != title:
                            current_section = {"title": title, "subsections": []}
                            toc.append(current_section)
                    elif is_subsection and current_section:
                        if not current_section['subsections'] or current_section['subsections'][-1]['title'] != title:
                            current_section["subsections"].append({"title": title})
    return toc

# --- PDF Text Loading ---
def load_pdf_lines(pdf_path):
    """Loads all lines from a PDF and returns them with page and line number info."""
    all_lines = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            for line_num, line in enumerate(text.splitlines()):
                all_lines.append({
                    "text": line.strip(),
                    "page": page_num + 1,
                    "line_in_page": line_num + 1
                })
    return all_lines



def get_raw_text_from_toc_pages(pdf_path, toc_page_nums=None, max_pages=5):
    """Extracts raw text from the first few pages of a PDF for debugging."""
    raw_text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        pages_to_scan = toc_page_nums if toc_page_nums else range(min(max_pages, len(reader.pages)))
        for page_num in pages_to_scan:
            page = reader.pages[page_num]
            text = page.extract_text() or ""
            raw_text += f"--- Page {page_num + 1} ---\n{text}\n\n"
    return raw_text

# --- Chunking Logic ---
def chunk_pdf_using_toc(all_lines, toc, doc_title, chunk_size, chunk_overlap):
    """Chunks the PDF lines based on the provided TOC structure."""
    chunks = []
    for section in toc:
        section_title = section["title"]
        for subsection in section["subsections"]:
            subsection_title = subsection["title"]
            
            # Find start and end line indices for the subsection
            start_idx, end_idx = -1, -1
            for i, line_info in enumerate(all_lines):
                if subsection_title.lower() in line_info["text"].lower():
                    start_idx = i
                    break
            
            if start_idx != -1:
                # End index is the start of the next section/subsection or end of doc
                for i in range(start_idx + 1, len(all_lines)):
                    line_text = all_lines[i]["text"].lower()
                    # Check for next subsection (e.g., "2. Another Topic") or next section
                    if any(sub["title"].lower() in line_text for sub in section["subsections"] if sub["title"] != subsection_title) or \
                       any(sec["title"].lower() in line_text for sec in toc if sec["title"] != section_title):
                        end_idx = i
                        break
                if end_idx == -1:
                    end_idx = len(all_lines)

                # Create chunks for the identified line range
                group_lines = all_lines[start_idx:end_idx]
                for i in range(0, len(group_lines), chunk_size - chunk_overlap):
                    chunk_lines = group_lines[i:i + chunk_size]
                    if not chunk_lines: continue
                    
                    chunk_text = "\n".join(l["text"] for l in chunk_lines)
                    chunk_meta = {
                        "doc_title": doc_title,
                        "section": section_title,
                        "subsection": subsection_title,
                        "page_start": chunk_lines[0]["page"],
                        "page_end": chunk_lines[-1]["page"],
                        "line_start": chunk_lines[0]["line_in_page"],
                        "line_end": chunk_lines[-1]["line_in_page"],
                    }
                    chunks.append({"text": chunk_text, "metadata": chunk_meta})
    return chunks

# --- Streamlit UI ---
st.title("PDF TOC Extraction and Chunking")

# Step 1: Upload PDF
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], key="pdf_upload")

if uploaded_file:
    # Save the uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.header("1. Extract Table of Contents (TOC)")

    # Debug view for raw TOC text
    if st.checkbox("Show raw text from TOC pages (for debugging)"):
        with st.spinner("Extracting raw text..."):
            raw_text = get_raw_text_from_toc_pages("temp.pdf")
            st.text_area("Raw Text from First 5 Pages", raw_text, height=300)

    if st.button("Extract TOC from PDF"):
        with st.spinner("Extracting TOC..."):
            toc_list = extract_toc_from_text("temp.pdf")
            doc_title = uploaded_file.name.replace('.pdf', '').replace('_', ' ')
            
            # Store for chunking
            st.session_state.toc = toc_list
            st.session_state.doc_title = doc_title

            # Store for display and download
            toc_with_title = {"doc_title": doc_title, "toc": toc_list}
            st.session_state.toc_json = toc_with_title
            st.success("TOC extracted successfully!")

    if 'toc_json' in st.session_state:
        st.json(st.session_state.toc_json)
        st.download_button(
            label="Download TOC JSON",
            data=json.dumps(st.session_state.toc_json, indent=2),
            file_name="toc.json",
            mime="application/json"
        )

    # Step 3: Upload reviewed TOC and Chunk
    st.subheader("Upload Reviewed TOC and Chunk PDF")
    uploaded_toc_file = st.file_uploader("Upload reviewed TOC JSON", type=["json"], key="toc_upload")

    if uploaded_toc_file:
        try:
            toc_content = json.loads(uploaded_toc_file.getvalue())
            doc_title = toc_content.get("doc_title", "Unknown")
            toc_list = toc_content.get("toc", [])
            
            st.success("Reviewed TOC loaded.")

            # Chunking parameters
            st.subheader("Chunking Parameters")
            chunk_size = st.slider("Chunk Size (lines)", 5, 50, 10)
            chunk_overlap = st.slider("Chunk Overlap (lines)", 0, 20, 2)

            if st.button("Chunk PDF using TOC"):
                with st.spinner("Loading PDF and chunking..."):
                    all_lines = load_pdf_lines("temp.pdf")
                    chunks = chunk_pdf_using_toc(all_lines, toc_list, doc_title, chunk_size, chunk_overlap)
                    st.session_state.chunks = chunks
                    st.success(f"PDF chunked into {len(chunks)} parts.")

        except Exception as e:
            st.error(f"Failed to process TOC file: {e}")

    # Display chunks
    if 'chunks' in st.session_state:
        st.subheader(f"Generated Chunks ({len(st.session_state.chunks)}) ")
        for i, chunk in enumerate(st.session_state.chunks):
            with st.expander(f"Chunk {i + 1}"):
                st.code(chunk["text"])
                st.json(chunk["metadata"])