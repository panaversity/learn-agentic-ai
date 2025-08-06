# Step 2: Basic Retrieval - K-Similarity Search

## Learning Objectives
By the end of this module, you will be able to:
- Perform semantic search using vector similarity
- Understand different distance metrics and their use cases
- Implement k-nearest neighbor (k-NN) search
- Optimize search parameters for quality and speed
- Build a simple question-answering system

## Theoretical Foundation

### Vector Similarity Search

**Core Concept**: Find documents with embeddings most similar to a query embedding.

**The Process:**
1. **Query Embedding**: Convert user question to vector using same model
2. **Similarity Calculation**: Compare query vector to all stored vectors
3. **Ranking**: Sort by similarity score (distance)
4. **Retrieval**: Return top-k most similar documents

### Distance Metrics

**1. Cosine Similarity** (Recommended)
- **What it measures**: Angle between vectors (direction similarity)
- **Range**: -1 to 1 (1 = identical, 0 = perpendicular, -1 = opposite)
- **Best for**: Text embeddings (most common choice)
- **Why**: Ignores magnitude, focuses on semantic direction

**2. Euclidean Distance (L2)**
- **What it measures**: Straight-line distance in vector space
- **Range**: 0 to ∞ (0 = identical, larger = more different)
- **Best for**: When magnitude matters
- **Limitation**: Sensitive to vector length

**3. Manhattan Distance (L1)**
- **What it measures**: Sum of absolute differences
- **Use case**: Specific applications, less common for embeddings

### K-Nearest Neighbors (k-NN)

**Parameter Tuning:**
- **k=1**: Only the most similar document (might be too narrow)
- **k=5**: Good balance for most applications
- **k=10+**: More context but potential noise

**Quality vs. Quantity Trade-off:**
- **Lower k**: Higher precision, might miss relevant info
- **Higher k**: Higher recall, might include irrelevant content

### Search Quality Factors

**1. Query Quality**
- **Specific queries**: "How to implement OAuth in Node.js?"
- **General queries**: "Programming help" (harder to match)

**2. Document Granularity**
- **Full documents**: Rich context but might be too broad
- **Paragraphs/sections**: More precise matching

**3. Embedding Model Alignment**
- **Same model**: Query and documents use identical embedding model
- **Domain relevance**: Model trained on relevant domain data

## Search Optimization

### Milvus Index Types

**1. FLAT** (Exact Search)
- **Accuracy**: 100% (brute force)
- **Speed**: Slow for large collections
- **Memory**: High
- **Best for**: Small datasets, highest accuracy needed

**2. IVF_FLAT** (Inverted File)
- **Accuracy**: 95-99% (approximate)
- **Speed**: Fast
- **Memory**: Medium
- **Best for**: General purpose, good balance

**3. HNSW** (Hierarchical Navigable Small World)
- **Accuracy**: 95-99%
- **Speed**: Very fast
- **Memory**: High
- **Best for**: Real-time applications, large datasets

### Search Parameters

**IVF Parameters:**
- **nlist**: Number of clusters (√collection_size is good starting point)
- **nprobe**: How many clusters to search (higher = more accurate, slower)

**HNSW Parameters:**
- **M**: Max connections per node (12-48 typical)
- **efConstruction**: Search depth during index building

## What We'll Build

### Simple Search Interface
```python
def search_documents(query: str, k: int = 5) -> List[Document]:
    """
    Search for documents similar to the query
    
    Args:
        query: User's question or search term
        k: Number of results to return
        
    Returns:
        List of most similar documents with scores
    """
```

### Features to Implement
1. **Query Processing**: Clean and prepare user input
2. **Embedding Generation**: Convert query to vector
3. **Similarity Search**: Find k most similar documents
4. **Result Formatting**: Present results with similarity scores
5. **Performance Monitoring**: Track search latency

### Search Quality Assessment

**Manual Evaluation:**
- Test with known good queries
- Check if expected documents appear in top results
- Verify similarity scores make intuitive sense

**Metrics to Track:**
- **Search latency**: How fast are results returned?
- **Similarity scores**: Are top results significantly more similar?
- **Result diversity**: Are we getting varied, relevant content?

## Common Challenges & Solutions

### 1. Query-Document Mismatch
**Problem**: Query style differs from document style
**Solution**: Query expansion, rephrasing, better prompting

### 2. Poor Similarity Scores
**Problem**: Low scores even for relevant content
**Solution**: Check embedding model, document quality, preprocessing

### 3. Slow Search Performance
**Problem**: High latency for search results
**Solution**: Optimize index type, adjust parameters, consider caching

### 4. Irrelevant Results
**Problem**: Top results don't match query intent
**Solution**: Improve document quality, consider metadata filtering

## Success Criteria
- Build working search interface
- Achieve sub-second search response times
- Understand similarity score patterns
- Identify when search works well vs. poorly
- Optimize search parameters for your use case

---

**Next Step**: In Step 3, we'll learn advanced ingestion strategies including document chunking to improve search precision and handle larger documents.
