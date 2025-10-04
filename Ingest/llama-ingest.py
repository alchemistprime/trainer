import json
import os
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.schema import TextNode
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.llms.anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable not set.")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

# Load your JSON data
with open("./Ingest/trainer_source_data_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Create TextNode objects with metadata
nodes = [
    TextNode(
        text=entry["text"],
        metadata={
            "doc_title": entry["doc_title"],
            "section_topic": entry["section_topic"],
            "subsection_topic": entry["subsection_topic"]
        }
    )
    for entry in data
]

# Set up MongoDB docstore using from_uri
docstore = MongoDocumentStore.from_uri(
    uri="mongodb://localhost:27017/",
    db_name="Trainer",           # Replace with your database name
    namespace="trainer_alpha"  # Acts as the collection name/namespace
)
docstore.add_documents(nodes)  # Store nodes in MongoDB

# Set up LanceDB vector store
vector_store = LanceDBVectorStore(uri="./Data/lancedb_store", table_name="trainer_data",
                                  mode="overwrite")

# Set up Cohere embedding model
embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",  # or "embed-multilingual-v3.0"
    input_type="search_document",
    embedding_type="float"
)

# Create storage context
storage_context = StorageContext.from_defaults(
    docstore=docstore,
    vector_store=vector_store
)

# Build the index from nodes
index = VectorStoreIndex(
    nodes=nodes,
    storage_context=storage_context,
    embed_model=embed_model
)

# Set up Anthropic LLM for querying (use a supported model)
#llm = Anthropic(
#    api_key=ANTHROPIC_API_KEY,
#    model="claude-3-opus-20240229"
#)
#
## Query engine
#query_engine = index.as_query_engine(llm=llm)
#response = query_engine.query("what is the first step in the Sales Process")
#print(response)