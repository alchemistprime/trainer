import os
from dotenv import load_dotenv
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    RetrievalEvaluator,
)
import weaviate

# Load env, setup index (same as query script)
load_dotenv()
# ... (copy setup from llama-query.py)

# Setup evaluators
llm = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), model="claude-3-opus-20240229")
faithfulness_evaluator = FaithfulnessEvaluator(llm=llm)
relevancy_evaluator = RelevancyEvaluator(llm=llm)
retrieval_evaluator = RetrievalEvaluator.from_metric_names(
    ["mrr", "hit_rate"], retriever=index.as_retriever()
)

# Sample evaluation dataset (expand this)
eval_queries = [
    {
        "query": "What are the five steps in the Sales Process?",
        "expected_answer": "Step 1: Greet, Step 2: Determine Wants and Needs, etc.",  # Ground truth
        "expected_sources": ["The_Sales_Process"]  # Expected doc_titles
    },
    # Add more...
]

# Run evaluations
for item in eval_queries:
    query = item["query"]
    expected_answer = item["expected_answer"]
    expected_sources = item["expected_sources"]
    
    # Get response
    citation_query_engine = CitationQueryEngine.from_args(index, llm=llm)
    response = citation_query_engine.query(query)
    
    # Evaluate response quality
    faithfulness_result = faithfulness_evaluator.evaluate_response(
        query=query, response=response.response, contexts=[node.node.get_content() for node in response.source_nodes]
    )
    relevancy_result = relevancy_evaluator.evaluate_response(
        query=query, response=response.response
    )
    
    # Evaluate retrieval
    retrieval_result = retrieval_evaluator.evaluate(
        query=query, expected_ids=None  # Or provide expected node IDs if known
    )
    
    # Custom citation check (simple example)
    citation_sources = [node.node.metadata.get("doc_title", "") for node in response.source_nodes]
    citation_accuracy = any(src in citation_sources for src in expected_sources)  # At least one match
    
    # Log results
    print(f"Query: {query}")
    print(f"Faithfulness: {faithfulness_result.score}")
    print(f"Relevancy: {relevancy_result.score}")
    print(f"Retrieval MRR: {retrieval_result.metric_vals_dict.get('mrr', 0)}")
    print(f"Citation Accuracy: {citation_accuracy}")
    print("---")