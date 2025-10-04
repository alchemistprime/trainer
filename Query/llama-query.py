import os
from dotenv import load_dotenv
import phoenix as px
#from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from phoenix.otel import register

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.core.query_engine import CitationQueryEngine

from phoenix.otel import register
tracer_provider = register(
    endpoint="http://localhost:6006/v1/traces",  # or your remote Phoenix instance
    project_name="trainer_rag",
    protocol="http/protobuf",
    auto_instrument=True 
)



# Load environment variables
load_dotenv()

# Load API keys from environment variables
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable not set.")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

# Set up storage backends for RAG pipeline
# MongoDB handles metadata for filtering/queries
# LanceDB handles vector-based retrieval
docstore = MongoDocumentStore.from_uri(
    uri="mongodb://localhost:27017/",
    db_name="Trainer",
    namespace="trainer_alpha"
)

vector_store = LanceDBVectorStore(
    uri="./Data/lancedb_store", 
    table_name="trainer_data"
)

# Configure embedding model and LLM
# Embeddings convert text into vectors for similarity search
# The LLM synthesizes answers from retrieved chunks
embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",
    input_type="search_document",
    embedding_type="float"
)

llm = Anthropic(
    api_key=ANTHROPIC_API_KEY,
    model="claude-3-opus-20240229"
)

# Load existing vector index from storage
# This connects to the pre-built index from the ingest script
storage_context = StorageContext.from_defaults(
    docstore=docstore,
    vector_store=vector_store
)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context,
    embed_model=embed_model
)

# Create query engine with citation support
# CitationQueryEngine provides responses with source references
citation_query_engine = CitationQueryEngine.from_args(index, llm=llm)

# Execute query - Phoenix automatically traces the entire RAG flow
query_text = "List the five steps in the Sales Process"
response = citation_query_engine.query(query_text)

# Display results with citations
print("Response with citations:")
print(response)
print("\nCitations:")

for i, node in enumerate(response.source_nodes, 1):
    meta = node.node.metadata
    text = node.node.get_content()
    
    print(f"[{i}] {meta.get('doc_title', '')} | {meta.get('section_topic', '')} | {meta.get('subsection_topic', '')}")
    print(f"Text chunk: {text}\n")


