For better ingesting, exported PDF to plain text
Open and edit in Word.
File save as PDF.

Attempted to convert PDF Table of Contents into json and used to Gemini to help write a script but it kept failing locally (extract_table_of_contents_from_pdf.py). Gemini said it was an environment differences so tired several attempts but each failed and ulimately had Gemini create the *toc.json files

Use the *toc.json files to chunck each section in the pdf source documents for embedding purposes and create metatada for filtering downstream.  Use this script (chunk_by_toc_json.py) which got about 90% there and did the rest manually rather than debugging the code.

llama-starter.py  initial run of RAG app. first draft.
