# Step 1: Indexing - Embeddings Generation & Document Ingestion

## Learning Objectives
By the end of this module, you will be able to:
- Understand what embeddings are and how they capture semantic meaning
- Generate embeddings using Google's text-embedding-001 model
- Store vectors efficiently in Milvus vector database
- Build a complete indexing pipeline for full documents
- Handle metadata and optimize batch processing

## Theoretical Foundation

### What Are Embeddings?

**Embeddings** are numerical representations of data (text, images, audio) in a high-dimensional vector space. Think of them as "coordinates" that capture the semantic meaning of content.

**Key Concepts:**
- **Semantic Similarity**: Similar content has similar embeddings (close in vector space)
- **Dimensionality**: Google's text-embedding-001 produces 768-dimensional vectors
- **Distance Metrics**: Cosine similarity, Euclidean distance measure closeness

**Example:**
```
"The cat sat on the mat" → [0.1, -0.3, 0.8, ..., 0.2] (768 numbers)
"A feline rested on the rug" → [0.11, -0.29, 0.81, ..., 0.19] (very similar!)
```

### Why Google Embeddings?

**Advantages:**
- ✅ **Free tier**: Generous limits for learning
- ✅ **High quality**: State-of-the-art semantic understanding
- ✅ **Multilingual**: Supports 100+ languages
- ✅ **Optimized**: Fast inference and good performance

**Specifications:**
- **Model**: `text-embedding-001`
- **Dimensions**: 768
- **Max input**: 20,000 characters
- **Rate limits**: 1,500 requests/minute (free tier)

### Vector Database: Milvus

**Why Milvus for Learning:**
- ✅ **Open source**: No vendor lock-in
- ✅ **Docker easy**: Simple local setup
- ✅ **Production ready**: Scales to billions of vectors
- ✅ **Rich features**: Multiple index types, hybrid search
- ✅ **Free**: No cloud costs for learning

**Core Concepts:**
- **Collections**: Like tables in traditional databases
- **Partitions**: Logical divisions within collections
- **Indexes**: Optimized structures for fast similarity search
- **Schemas**: Define field types and constraints

### The Indexing Pipeline

**Complete Workflow:**
1. **Document Preparation**: Load and clean raw documents
2. **Embedding Generation**: Convert text to vectors using Google API
3. **Metadata Extraction**: Title, source, timestamp, etc.
4. **Vector Storage**: Insert into Milvus collection
5. **Index Building**: Create optimized search structures

**Design Principles:**
- **Batch Processing**: Process multiple documents efficiently
- **Error Handling**: Graceful failures and retries
- **Monitoring**: Track progress and performance
- **Scalability**: Handle growing document collections

## What We'll Build

### Simple Indexing System
- Load documents from various sources (text files, PDFs)
- Generate embeddings for complete documents (no chunking yet)
- Store in Milvus with meaningful metadata
- Monitor processing progress and costs

### Key Components
1. **Document Loader**: Handle different file formats
2. **Embedding Client**: Google API integration with rate limiting
3. **Vector Store**: Milvus collection management
4. **Pipeline Orchestrator**: Coordinate the entire process

## Prerequisites
- Basic Python knowledge
- Understanding of APIs and JSON
- Familiarity with databases (helpful but not required)

## Success Criteria
- Successfully generate embeddings for 100+ documents
- Store vectors in Milvus with proper metadata
- Understand embedding quality and limitations
- Build reusable indexing pipeline

---

**Next Step**: Once we have documents indexed, we'll learn how to retrieve relevant information using similarity search in Step 2.
