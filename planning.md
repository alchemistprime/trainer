Framework: Agnos
model: anthropic
ingest (readers):
    https://docs.agno.com/concepts/knowledge/readers
chunking:
embedder: voyageai
vector: weaviate

custom retriever: 
    https://docs.agno.com/examples/concepts/knowledge/custom_retriever/custom-retriever



### The RAG Pipeline: A Simplified View

Building a RAG (Retrieval-Augmented Generation) system is a two-phase process: **Indexing** and **Querying**.

#### Phase 1: Indexing (Building the Knowledge Base)

1.  **Load Data**: Get your documents from various sources (PDFs, websites, etc.).
2.  **Chunk & Embed**: Break the documents into smaller chunks and convert each chunk into a numerical vector (embedding) that captures its meaning.
3.  **Store Vectors**: Save these vectors in a **vector database** (like Qdrant or Pgvector) for quick searching.

#### Phase 2: Querying (Answering a Question)

1.  **Embed Query**: A user's question is also converted into a vector.
2.  **Retrieve Context**: The system uses this vector to search the database and find the most relevant chunks from your knowledge base.
3.  **Augment & Generate**: The retrieved chunks are added to the original question to create a complete prompt. This prompt is then sent to an LLM, which uses the provided context to generate an accurate and grounded answer.