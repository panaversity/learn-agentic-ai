# Step 4: Advanced Retrieval Strategies - Hybrid Search & Query Enhancement

[Watch Layering every technique in RAG, one query at a time](https://www.youtube.com/watch?v=w9u11ioHGA0)

## Learning Objectives
By the end of this module, you will be able to:
- Implement hybrid search combining vector and keyword search
- Use query expansion and rewriting techniques
- Apply re-ranking algorithms to improve result quality
- Build multi-stage retrieval pipelines
- Optimize retrieval for different query types

## Theoretical Foundation

### Limitations of Pure Vector Search

**Common Failure Cases:**
- **Exact terminology**: Searches for specific names, IDs, or technical terms
- **Negation queries**: "Show me documents NOT about X"
- **Boolean logic**: "Documents about A AND B but NOT C"
- **Rare entities**: Proper nouns, acronyms, specialized vocabulary
- **Numerical queries**: Specific dates, versions, quantities

**Why Vector Search Struggles:**
- **Semantic approximation**: Embeddings capture general meaning, not exact terms
- **Training limitations**: Embedding models may not know rare terms
- **Context compression**: 768 dimensions can't capture all nuances

### Hybrid Search Architecture

**The Best of Both Worlds:**
- **Vector search**: Captures semantic similarity and intent
- **Keyword search**: Finds exact matches and specific terms
- **Combined scoring**: Merge results intelligently

**Implementation Approaches:**

### 1. Parallel Search + Score Fusion
```python
def hybrid_search(query: str, k: int = 10):
    # Run both searches in parallel
    vector_results = vector_search(query, k)
    keyword_results = keyword_search(query, k)
    
    # Combine and re-rank
    combined_results = fuse_scores(vector_results, keyword_results)
    return combined_results[:k]
```

### 2. Sequential Search (Vector → Keyword)
```python
def sequential_search(query: str, k: int = 10):
    # First pass: Vector search for semantic candidates
    candidates = vector_search(query, k * 3)
    
    # Second pass: Keyword search within candidates
    final_results = keyword_search_subset(query, candidates, k)
    return final_results
```

### 3. Conditional Search Strategy
```python
def adaptive_search(query: str, k: int = 10):
    query_type = classify_query(query)
    
    if query_type == "exact_match":
        return keyword_search(query, k)
    elif query_type == "semantic":
        return vector_search(query, k)
    else:
        return hybrid_search(query, k)
```

## Score Fusion Techniques

### 1. Reciprocal Rank Fusion (RRF)
**Formula**: `score = 1 / (k + rank)`
- **Advantage**: Simple, effective, rank-based
- **Use case**: When scores from different systems aren't comparable

```python
def reciprocal_rank_fusion(results_list: List[List], k: int = 60):
    """Combine rankings using RRF"""
    combined_scores = {}
    for results in results_list:
        for rank, doc in enumerate(results):
            if doc.id not in combined_scores:
                combined_scores[doc.id] = 0
            combined_scores[doc.id] += 1 / (k + rank + 1)
    return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
```

### 2. Weighted Score Combination
**Formula**: `final_score = α × vector_score + β × keyword_score`
- **Advantage**: Preserves score magnitudes
- **Challenge**: Requires score normalization

### 3. Distribution-Based Fusion
**Approach**: Normalize scores to same distribution before combining
- **Method**: Convert to percentiles or z-scores
- **Advantage**: Handles different score ranges

## Query Enhancement Techniques

### Query Expansion

**1. Synonym Expansion**
```python
def expand_with_synonyms(query: str) -> str:
    """Add synonyms to broaden search"""
    # Original: "car repair"
    # Expanded: "car repair automobile fix maintenance"
```

**2. Related Term Addition**
```python
def expand_with_context(query: str, domain: str) -> str:
    """Add domain-specific related terms"""
    # Query: "login issues"
    # Domain: "web development"
    # Expanded: "login issues authentication authorization session"
```

**3. LLM-Based Expansion**
```python
def llm_query_expansion(query: str) -> List[str]:
    """Use LLM to generate related queries"""
    prompt = f"""
    Given this search query: "{query}"
    Generate 3 alternative ways to ask the same question:
    """
    # Returns multiple query variations
```

### Query Rewriting

**1. Intent Clarification**
```python
# Original: "How do I fix this?"
# Rewritten: "How do I fix authentication errors in web applications?"
```

**2. Specificity Enhancement**
```python
# Original: "Python error"
# Rewritten: "Python ImportError module not found troubleshooting"
```

**3. Context Addition**
```python
# With conversation history
# Original: "What about error handling?"
# Rewritten: "What about error handling in Python API development?"
```

## Re-ranking Algorithms

### 1. Cross-Encoder Re-ranking
**Approach**: Use a specialized model to score query-document pairs
```python
def cross_encoder_rerank(query: str, candidates: List[Document]) -> List[Document]:
    """Re-rank candidates using cross-encoder model"""
    scores = cross_encoder.predict([(query, doc.content) for doc in candidates])
    return sort_by_scores(candidates, scores)
```

**Advantages:**
- **Higher accuracy**: Considers query-document interaction
- **Better relevance**: Trained specifically for ranking tasks

**Disadvantages:**
- **Slower**: Must process each query-document pair
- **Resource intensive**: Typically used on smaller candidate sets

### 2. LLM-Based Re-ranking
**Approach**: Use LLM to assess relevance and re-order results
```python
def llm_rerank(query: str, candidates: List[Document]) -> List[Document]:
    prompt = f"""
    Query: {query}
    
    Rank these documents by relevance (most relevant first):
    {format_documents(candidates)}
    
    Return only the document IDs in order of relevance.
    """
```

### 3. Feature-Based Re-ranking
**Approach**: Use multiple signals to compute relevance scores
```python
def feature_based_rerank(query: str, candidates: List[Document]) -> List[Document]:
    features = []
    for doc in candidates:
        features.append({
            'semantic_score': doc.vector_score,
            'keyword_score': doc.keyword_score,
            'freshness': calculate_freshness(doc.timestamp),
            'authority': calculate_authority(doc.source),
            'query_overlap': calculate_overlap(query, doc.content)
        })
    
    scores = ranking_model.predict(features)
    return sort_by_scores(candidates, scores)
```

## Multi-Stage Retrieval Pipeline

### Stage 1: Candidate Generation (Fast, Broad)
```python
def generate_candidates(query: str, k: int = 100) -> List[Document]:
    """Fast first-pass retrieval for broad recall"""
    return vector_search(query, k, index_type="IVF_FLAT")
```

### Stage 2: Initial Filtering (Medium Speed, Focused)
```python
def filter_candidates(query: str, candidates: List[Document]) -> List[Document]:
    """Apply filters and keyword matching"""
    filtered = keyword_filter(query, candidates)
    return filtered[:50]  # Reduce to top candidates
```

### Stage 3: Precise Re-ranking (Slow, Accurate)
```python
def final_ranking(query: str, candidates: List[Document]) -> List[Document]:
    """Expensive but accurate final ranking"""
    return cross_encoder_rerank(query, candidates[:20])
```

### Complete Pipeline
```python
def advanced_retrieval(query: str, k: int = 10) -> List[Document]:
    # Stage 1: Fast candidate generation
    candidates = generate_candidates(query, k=100)
    
    # Stage 2: Filtering and hybrid search
    filtered = filter_candidates(query, candidates)
    
    # Stage 3: Precise re-ranking
    ranked = final_ranking(query, filtered)
    
    return ranked[:k]
```

## Query Classification

### Query Type Detection
```python
def classify_query(query: str) -> str:
    """Determine optimal retrieval strategy based on query type"""
    
    # Exact match queries
    if has_quotes(query) or has_specific_terms(query):
        return "exact_match"
    
    # Factual queries
    if starts_with_wh_words(query):
        return "factual"
    
    # Conceptual queries
    if has_abstract_terms(query):
        return "conceptual"
    
    # Procedural queries
    if has_how_to_pattern(query):
        return "procedural"
    
    return "general"
```

### Strategy Selection
```python
RETRIEVAL_STRATEGIES = {
    "exact_match": lambda q: keyword_search(q, boost_exact=True),
    "factual": lambda q: hybrid_search(q, vector_weight=0.7),
    "conceptual": lambda q: vector_search(q, expand_query=True),
    "procedural": lambda q: hybrid_search(q, keyword_weight=0.3)
}

def adaptive_retrieval(query: str) -> List[Document]:
    query_type = classify_query(query)
    strategy = RETRIEVAL_STRATEGIES[query_type]
    return strategy(query)
```

## Performance Optimization

### Caching Strategies
```python
# Query result caching
@lru_cache(maxsize=1000)
def cached_search(query: str, k: int) -> List[Document]:
    return expensive_search(query, k)

# Embedding caching
embedding_cache = {}
def get_cached_embedding(text: str) -> np.ndarray:
    if text not in embedding_cache:
        embedding_cache[text] = generate_embedding(text)
    return embedding_cache[text]
```

### Batch Processing
```python
def batch_rerank(queries: List[str], candidates_list: List[List[Document]]):
    """Process multiple queries in batch for efficiency"""
    all_pairs = []
    for query, candidates in zip(queries, candidates_list):
        pairs = [(query, doc.content) for doc in candidates]
        all_pairs.extend(pairs)
    
    # Single batch inference
    scores = cross_encoder.predict(all_pairs)
    
    # Redistribute scores back to original structure
    return redistribute_scores(scores, candidates_list)
```

## Evaluation & Testing

### Retrieval Metrics
```python
def evaluate_retrieval(test_queries: List[TestQuery]) -> Dict[str, float]:
    """Evaluate retrieval quality"""
    metrics = {
        'precision_at_5': 0,
        'recall_at_10': 0,
        'mrr': 0,  # Mean Reciprocal Rank
        'ndcg_at_10': 0  # Normalized Discounted Cumulative Gain
    }
    
    for query in test_queries:
        results = advanced_retrieval(query.text, k=10)
        metrics['precision_at_5'] += precision_at_k(results[:5], query.relevant_docs)
        metrics['recall_at_10'] += recall_at_k(results, query.relevant_docs)
        # ... calculate other metrics
    
    # Average across all queries
    return {k: v/len(test_queries) for k, v in metrics.items()}
```

### A/B Testing Framework
```python
def ab_test_retrieval(strategy_a, strategy_b, test_queries: List[str]):
    """Compare two retrieval strategies"""
    results_a = [strategy_a(q) for q in test_queries]
    results_b = [strategy_b(q) for q in test_queries]
    
    # Human evaluation or automated metrics
    return compare_results(results_a, results_b)
```

## What We'll Build

### Advanced Search Engine
```python
class AdvancedSearchEngine:
    def __init__(self):
        self.vector_searcher = VectorSearcher()
        self.keyword_searcher = KeywordSearcher()
        self.reranker = CrossEncoderReranker()
        self.query_expander = QueryExpander()
    
    def search(self, query: str, k: int = 10) -> List[Document]:
        """Multi-stage advanced retrieval"""
        # Query enhancement
        enhanced_query = self.query_expander.expand(query)
        
        # Hybrid candidate generation
        candidates = self.hybrid_search(enhanced_query, k=50)
        
        # Re-ranking
        ranked_results = self.reranker.rerank(query, candidates)
        
        return ranked_results[:k]
```

### Features to Implement
1. **Hybrid search**: Vector + keyword combination
2. **Query enhancement**: Expansion and rewriting
3. **Multi-stage pipeline**: Fast → accurate progression
4. **Adaptive strategies**: Query-type specific approaches
5. **Performance optimization**: Caching and batching

## Success Criteria
- Implement working hybrid search system
- Show improved results over pure vector search
- Handle different query types appropriately
- Achieve good performance with multi-stage pipeline
- Demonstrate measurable quality improvements

---

**Next Step**: In Step 5, we'll explore multimodal RAG systems that can handle images, audio, and other non-text content alongside traditional text documents.
