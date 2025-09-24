from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

# Example: Metadata filter for a specific section_topic
filters = MetadataFilters(
    filters=[
        MetadataFilter(key="section_topic", operator=FilterOperator.EQ, value="A Powerful, Proven System You Can Trust"),
    ]
)

# Use filters in your query engine
query_engine = index.as_query_engine(filters=filters, llm=llm)
response = query_engine.query("What are the main points in this section?")
print(response)
