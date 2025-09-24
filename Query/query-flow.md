# Key Concepts and Flow

### RAG Workflow: Query → Embed query → Search vectors in Weaviate → Retrieve chunks + metadata from MongoDB → LLM generates response with citations.

### Databases:
- Weaviate: Stores vector embeddings for fast similarity search.

- MongoDB: Stores metadata for filtering and context (e.g., which document/section a chunk came from). 

### Embeddings:  
- Text is converted to numerical vectors (via Cohere) so the system can find semantically similar content.
### LLM: 
- Anthropic's Claude generates human-like answers based on retrieved chunks.
### Citations: 
- Ensures responses are grounded in source data, listing doc titles, sections, and text snippets.





# Query Flow for llama-query.py

This document explains the step-by-step flow of the query script in `llama-query.py`.

## 1. Imports and Environment Setup

The script starts by importing necessary modules:

- `os` for environment variables
- `dotenv` to load .env file
- LlamaIndex components: StorageContext, VectorStoreIndex, WeaviateVectorStore, MongoDocumentStore, CohereEmbedding, Anthropic, CitationQueryEngine
- `weaviate` for connection

It loads environment variables from a `.env` file and validates that the required API keys (`COHERE_API_KEY` and `ANTHROPIC_API_KEY`) are set.

## 2. Setting up Storage Backends

- Initializes a MongoDB document store using the URI `mongodb://localhost:27017/`, database name "Trainer", and namespace "trainer_alpha" (which acts as the collection name).
- Connects to a local Weaviate instance and sets up a vector store with the index name "LlamaIndex".

## 3. Setting up Models

- Configures the Cohere embedding model with the API key, model name "embed-english-v3.0", input type "search_document", and embedding type "float".
- Initializes the Anthropic LLM with the API key and model "claude-3-opus-20240229".

## 4. Loading the Index

- Creates a `StorageContext` from the MongoDB docstore and Weaviate vector store.
- Loads a `VectorStoreIndex` from the vector store, incorporating the storage context and embedding model. This allows querying the pre-ingested data.

## 5. Querying with Citations

- Instantiates a `CitationQueryEngine` using the loaded index and the Anthropic LLM.
- Performs a query with the placeholder text "Your question here" (this should be replaced with an actual query).

## 6. Output and Citations

- Prints the query response, which includes citations.
- For each source node in the response, extracts and prints the metadata (doc_title, section_topic, subsection_topic) and the corresponding text chunk.

This flow enables retrieval-augmented generation (RAG) with traceable citations, pulling relevant chunks from the stored PDFs based on the query.
