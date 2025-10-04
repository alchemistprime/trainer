# Q&A Dataset Generation Considerations

For creating a dataset to test recall and MRR (Mean Reciprocal Rank), here are the key considerations for Q&A pair generation:

## Question Design Considerations

**Question Complexity Levels:**
- Simple factual questions (direct lookup)
- Multi-hop reasoning questions (require connecting multiple chunks)
- Comparative questions ("What's the difference between...")
- Analytical questions ("Why does..." or "How does...")

**Question Types by Retrieval Difficulty:**
- **Easy:** Questions with exact keyword matches in source text
- **Medium:** Questions requiring synonyms/paraphrasing
- **Hard:** Questions needing inference or cross-document reasoning

## Answer Quality Considerations

**Ground Truth Answers:**
- Include exact source document IDs/chunks that contain the answer
- Rank multiple valid answer sources by relevance
- Include "no answer" cases for robustness testing

**Answer Granularity:**
- Short factual answers vs. comprehensive explanations
- Single-sentence vs. multi-paragraph responses
- Direct quotes vs. synthesized answers

## Dataset Balance & Coverage

**Content Coverage:**
- Ensure questions span all major topics in your sales training data
- Test edge cases and less common scenarios
- Include questions that require multiple document sections

**Difficulty Distribution:**
- 30% easy (high keyword overlap)
- 50% medium (moderate paraphrasing)
- 20% hard (inference/reasoning required)

## Generation Strategies

**Manual Creation:**
- Domain experts create questions while reviewing documents
- Ensures high quality but limited scale

**LLM-Assisted Generation:**
- Use Claude/GPT to generate questions from document chunks
- Verify and filter for quality
- Good for scale but requires validation

**Hybrid Approach:**
- LLM generates candidates, humans refine and validate
- Best balance of scale and quality

Would you like me to help you implement any specific generation strategy or create example Q&A pairs for your sales training data?