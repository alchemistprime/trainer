import os
from dotenv import load_dotenv
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.core.query_engine import CitationQueryEngine
import weaviate

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable not set.")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set.")


# 1. Set up MongoDB docstore and Weaviate vector store (same as ingest)
# The script needs to access the pre-stored index. MongoDB handles
# metadata for filtering/queries, while Weaviate handles vector-based retrieval.
docstore = MongoDocumentStore.from_uri(
    uri="mongodb://localhost:27017/",
    db_name="Trainer",           # Replace with your database name
    namespace="trainer_alpha"  # Acts as the collection name/namespace
)
weaviate_client = weaviate.connect_to_local()
vector_store = WeaviateVectorStore(
    weaviate_client=weaviate_client,
    index_name="LlamaIndex"
)

# 2. Set up embedding and LLM
# Embeddings convert text into vectors for similarity search.
# The LLM synthesizes answers from retrieved chunks.
embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",  # or "embed-multilingual-v3.0"
    input_type="search_document",
    embedding_type="float"
)
llm = Anthropic(
    api_key=ANTHROPIC_API_KEY,
    model="claude-3-opus-20240229"
)

# 3. Load storage context and index
# This connects the script to the pre-built index,
# allowing queries against stored embeddings and metadata.
storage_context = StorageContext.from_defaults(
    docstore=docstore,
    vector_store=vector_store
)
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context,
    embed_model=embed_model
)

# 4. Query with CitationQueryEngine
# ensures responses include references to source documents,
# improving transparency and reducing hallucinations.
citation_query_engine = CitationQueryEngine.from_args(index, llm=llm)
response = citation_query_engine.query("List the five steps in the Sales Process")

# 5. Print response and all citation data
print("Response with citations:")
print(response)
print("\nCitations:")
for i, node in enumerate(response.source_nodes, 1):
    meta = node.node.metadata
    text = node.node.get_content()
    print(f"[(i)] {meta.get('doc_title', '')} | {meta.get('section_topic', '')} | {meta.get('subsection_topic', '')}")
    print(f"Text chunk: {text}\n")

