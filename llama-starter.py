import glob
import os
from pathlib import Path
from dotenv import load_dotenv
import weaviate
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.storage.kvstore.mongodb import MongoDBKVStore
from llama_index.storage.docstore.mongodb import MongoDocumentStore

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable not set.")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

# 1. Load all PDFs from a directory
pdf_paths = glob.glob("Data/Source/*.pdf")
reader = PyMuPDFReader()
documents = []
for path in pdf_paths:
    documents.extend(reader.load(file_path=Path(path)))

# 2. Chunking strategy (customize as needed)
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
pipeline = IngestionPipeline(transformations=[splitter])
nodes = pipeline.run(documents=documents)

# 3. Set up Cohere embedding model
embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",  # or "embed-multilingual-v3.0"
    input_type="search_document",
    embedding_type="float"
)

# 4. Set up MongoDB document store (Docker default: localhost:27017)
#ongo_kvstore = MongoDBKVStore(uri="mongodb://localhost:27017", db_name="llamaindex_db")
mongo_store = MongoDocumentStore.from_uri(uri="mongodb://localhost:27017")
mongo_store.add_documents(nodes)

storage_context = StorageContext.from_defaults(docstore=mongo_store)

# 5. Set up Weaviate client and vector store
client = weaviate.connect_to_local()
vector_store = WeaviateVectorStore(weaviate_client=client, index_name="LlamaIndex")
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 6. Build and persist the index
index = VectorStoreIndex(nodes, embed_model=embed_model, storage_context=storage_context)
index.storage_context.persist(persist_dir="./storage")

# 7. Set up Anthropic LLM for querying (use a supported model)
llm = Anthropic(
    api_key=ANTHROPIC_API_KEY,
    model="claude-3-opus-20240229"
)

# 8. Query the index using Anthropic LLM
query_engine = index.as_query_engine(llm=llm)
response = query_engine.query("What is the main topic of these documents?")
print(response)

# 9. Close the Weaviate client connection
client.close()


