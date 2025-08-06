# Step 2: pgvector Hybrid Search - Combining SQL with Vector Similarity

## Learning Objectives
By the end of this module, you will be able to:
- Install and configure pgvector extension in PostgreSQL
- Combine traditional SQL queries with vector similarity search
- Build hybrid search systems that leverage both structured and semantic data
- Implement real-world search applications using pgvector and embeddings

## Theoretical Foundation

### What is Hybrid Search?

**Traditional SQL Search:**
- Exact matches and pattern matching
- Structured queries on known fields
- Fast for precise lookups
- Limited by rigid matching criteria

**Vector Similarity Search:**
- Semantic understanding of content
- Finds conceptually related items
- Handles natural language queries
- May miss specific details

**Hybrid Search - Best of Both Worlds:**
- Combines SQL filtering with semantic similarity
- Precise filtering + conceptual understanding
- Better relevance and recall
- Handles complex real-world queries

### Understanding pgvector

**What is pgvector:**
- PostgreSQL extension for vector operations
- Native vector storage and indexing
- High-performance similarity search
- Integrates seamlessly with SQL

**Vector Operations:**
- **Cosine Similarity**: Measures angle between vectors
- **Euclidean Distance**: Measures straight-line distance
- **Inner Product**: Measures alignment of vectors
- **HNSW Indexing**: Hierarchical Navigable Small World for fast search

**Storage Types:**
```sql
-- Different vector types and sizes
vector(1536)    -- OpenAI ada-002 embeddings
vector(768)     -- Sentence transformers
vector(384)     -- Compact models
vector(3072)    -- OpenAI text-embedding-3-large
```

### Architecture Patterns

**1. Metadata + Content Hybrid**
```sql
-- Traditional approach: separate tables
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    created_at TIMESTAMP,
    category VARCHAR(50),
    author_id INTEGER
);

CREATE TABLE document_embeddings (
    document_id INTEGER REFERENCES documents(id),
    content_embedding vector(1536),
    title_embedding vector(1536)
);
```

**2. Unified Table Approach**
```sql
-- Modern approach: everything in one table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    created_at TIMESTAMP,
    category VARCHAR(50),
    author_id INTEGER,
    content_embedding vector(1536),
    title_embedding vector(1536)
);
```

**3. Multi-Modal Search**
```sql
-- Support for different content types
CREATE TABLE content_items (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(20), -- 'text', 'image', 'audio'
    title TEXT,
    description TEXT,
    file_path TEXT,
    metadata JSONB,
    text_embedding vector(1536),
    image_embedding vector(512),  -- Different size for image embeddings
    created_at TIMESTAMP
);
```

## Setting Up pgvector

### 1. Install pgvector Extension

**For Neon (Serverless PostgreSQL):**
```sql
-- pgvector is pre-installed in Neon
-- Just enable it in your database
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**For Local PostgreSQL:**
```bash
# Install pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

# Or using package manager (Ubuntu/Debian)
sudo apt install postgresql-14-pgvector

# Or using Homebrew (macOS)
brew install pgvector
```

**For Docker:**
```bash
# Use pre-built image with pgvector
docker run -d \
  --name postgres-vector \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  pgvector/pgvector:pg15
```

### 2. Create Hybrid Search Schema

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create products table with hybrid search capabilities
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10,2),
    brand VARCHAR(100),
    tags TEXT[],
    rating DECIMAL(2,1),
    in_stock BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Vector embeddings for semantic search
    name_embedding vector(1536),
    description_embedding vector(1536)
);

-- Create customers table with preference vectors
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    signup_date DATE,
    
    -- Customer preference vector learned from behavior
    preference_vector vector(1536)
);

-- Create purchase history with rating embeddings
CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    product_id INTEGER REFERENCES products(id),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    
    -- Embedding of the review text
    review_embedding vector(1536)
);

-- Create search queries log for analytics
CREATE TABLE search_queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT,
    query_embedding vector(1536),
    customer_id INTEGER REFERENCES customers(id),
    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results_count INTEGER,
    clicked_products INTEGER[]
);
```

### 3. Create Vector Indexes

```sql
-- Create HNSW indexes for fast vector similarity search
CREATE INDEX ON products USING hnsw (name_embedding vector_cosine_ops);
CREATE INDEX ON products USING hnsw (description_embedding vector_cosine_ops);
CREATE INDEX ON customers USING hnsw (preference_vector vector_cosine_ops);
CREATE INDEX ON purchases USING hnsw (review_embedding vector_cosine_ops);
CREATE INDEX ON search_queries USING hnsw (query_embedding vector_cosine_ops);

-- Create traditional indexes for hybrid queries
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_rating ON products(rating);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_purchases_date ON purchases(purchase_date);
```

## Generating and Storing Embeddings

### 1. Embedding Generation Service

```python
import asyncio
import asyncpg
import openai
from typing import List, Dict, Any, Optional
import numpy as np

class EmbeddingService:
    def __init__(self, openai_api_key: str, database_url: str):
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
        self.database_url = database_url
        self.connection_pool = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        self.connection_pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=10
        )
    
    async def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Generate embedding for given text"""
        
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * 1536
        
        try:
            response = await self.openai_client.embeddings.create(
                input=text.strip(),
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 1536
    
    async def generate_batch_embeddings(self, texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        
        # Filter out empty texts
        filtered_texts = [text.strip() if text else "" for text in texts]
        
        try:
            response = await self.openai_client.embeddings.create(
                input=filtered_texts,
                model=model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            return [[0.0] * 1536] * len(texts)
    
    async def store_product_embeddings(self, products_data: List[Dict[str, Any]]):
        """Store product data with generated embeddings"""
        
        # Generate embeddings for all products
        names = [product['name'] for product in products_data]
        descriptions = [product['description'] for product in products_data]
        
        name_embeddings = await self.generate_batch_embeddings(names)
        description_embeddings = await self.generate_batch_embeddings(descriptions)
        
        # Store in database
        async with self.connection_pool.acquire() as connection:
            for i, product in enumerate(products_data):
                await connection.execute("""
                    INSERT INTO products (
                        name, description, category, price, brand, tags, rating, in_stock,
                        name_embedding, description_embedding
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                    product['name'],
                    product['description'],
                    product['category'],
                    product['price'],
                    product['brand'],
                    product['tags'],
                    product['rating'],
                    product['in_stock'],
                    name_embeddings[i],
                    description_embeddings[i]
                )
    
    async def update_customer_preferences(self, customer_id: int):
        """Update customer preference vector based on purchase history"""
        
        async with self.connection_pool.acquire() as connection:
            # Get customer's purchase history with product embeddings
            purchases = await connection.fetch("""
                SELECT p.description_embedding, pu.rating
                FROM purchases pu
                JOIN products p ON pu.product_id = p.id
                WHERE pu.customer_id = $1 AND pu.rating >= 4
            """, customer_id)
            
            if not purchases:
                return
            
            # Calculate weighted average of liked products
            weighted_embeddings = []
            total_weight = 0
            
            for purchase in purchases:
                embedding = purchase['description_embedding']
                weight = purchase['rating'] / 5.0  # Normalize rating to 0-1
                
                if not weighted_embeddings:
                    weighted_embeddings = [x * weight for x in embedding]
                else:
                    for j, val in enumerate(embedding):
                        weighted_embeddings[j] += val * weight
                
                total_weight += weight
            
            # Normalize by total weight
            if total_weight > 0:
                preference_vector = [x / total_weight for x in weighted_embeddings]
                
                # Store preference vector
                await connection.execute("""
                    UPDATE customers 
                    SET preference_vector = $1 
                    WHERE id = $2
                """, preference_vector, customer_id)

# Sample data for testing
sample_products = [
    {
        "name": "iPhone 15 Pro",
        "description": "Latest iPhone with advanced camera system, titanium design, and A17 Pro chip",
        "category": "smartphones",
        "price": 999.99,
        "brand": "Apple",
        "tags": ["smartphone", "camera", "premium"],
        "rating": 4.8,
        "in_stock": True
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "description": "Premium Android smartphone with S Pen, excellent display, and versatile camera system",
        "category": "smartphones", 
        "price": 1199.99,
        "brand": "Samsung",
        "tags": ["smartphone", "android", "stylus"],
        "rating": 4.7,
        "in_stock": True
    },
    {
        "name": "MacBook Air M3",
        "description": "Lightweight laptop with M3 chip, all-day battery life, and stunning Retina display",
        "category": "laptops",
        "price": 1099.99,
        "brand": "Apple",
        "tags": ["laptop", "ultrabook", "M3"],
        "rating": 4.9,
        "in_stock": True
    },
    {
        "name": "Dell XPS 13",
        "description": "Premium Windows ultrabook with Intel processors, compact design, and excellent build quality",
        "category": "laptops",
        "price": 899.99,
        "brand": "Dell",
        "tags": ["laptop", "windows", "ultrabook"],
        "rating": 4.6,
        "in_stock": True
    },
    {
        "name": "Sony WH-1000XM5",
        "description": "Industry-leading noise canceling headphones with exceptional sound quality",
        "category": "audio",
        "price": 399.99,
        "brand": "Sony",
        "tags": ["headphones", "noise-canceling", "wireless"],
        "rating": 4.8,
        "in_stock": True
    }
]

# Initialize and populate database
async def setup_sample_data():
    embedding_service = EmbeddingService(
        openai_api_key="your-openai-api-key",
        database_url="your-neon-database-url"
    )
    
    await embedding_service.initialize()
    await embedding_service.store_product_embeddings(sample_products)
    print("Sample data with embeddings stored successfully!")
```

## Implementing Hybrid Search

### 1. Basic Hybrid Search Class

```python
import asyncio
import asyncpg
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

class HybridSearchEngine:
    def __init__(self, database_url: str, embedding_service: EmbeddingService):
        self.database_url = database_url
        self.embedding_service = embedding_service
        self.connection_pool = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.connection_pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=10
        )
    
    async def hybrid_product_search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        min_rating: Optional[float] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining SQL filtering with vector similarity
        """
        
        # Generate embedding for search query
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Build SQL conditions for structured filtering
        conditions = ["in_stock = true"]
        params = [query_embedding]
        param_count = 1
        
        if category:
            param_count += 1
            conditions.append(f"category = ${param_count}")
            params.append(category)
        
        if min_price is not None:
            param_count += 1
            conditions.append(f"price >= ${param_count}")
            params.append(min_price)
        
        if max_price is not None:
            param_count += 1
            conditions.append(f"price <= ${param_count}")
            params.append(max_price)
        
        if brand:
            param_count += 1
            conditions.append(f"brand ILIKE ${param_count}")
            params.append(f"%{brand}%")
        
        if min_rating is not None:
            param_count += 1
            conditions.append(f"rating >= ${param_count}")
            params.append(min_rating)
        
        # Combine SQL filtering with vector similarity
        where_clause = " AND ".join(conditions)
        
        sql = f"""
            SELECT 
                id, name, description, category, price, brand, rating,
                -- Calculate similarity scores
                1 - (name_embedding <=> $1) as name_similarity,
                1 - (description_embedding <=> $1) as description_similarity,
                -- Combined similarity (weighted average)
                (1 - (name_embedding <=> $1)) * 0.3 + 
                (1 - (description_embedding <=> $1)) * 0.7 as combined_similarity
            FROM products
            WHERE {where_clause}
                AND (
                    (1 - (name_embedding <=> $1)) > {similarity_threshold} OR
                    (1 - (description_embedding <=> $1)) > {similarity_threshold}
                )
            ORDER BY combined_similarity DESC
            LIMIT {limit}
        """
        
        async with self.connection_pool.acquire() as connection:
            rows = await connection.fetch(sql, *params)
            
            return [dict(row) for row in rows]
    
    async def personalized_search(
        self,
        customer_id: int,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform personalized search using customer preference vector
        """
        
        # Get customer preference vector
        async with self.connection_pool.acquire() as connection:
            customer = await connection.fetchrow(
                "SELECT preference_vector FROM customers WHERE id = $1",
                customer_id
            )
            
            if not customer or not customer['preference_vector']:
                # Fall back to regular hybrid search
                return await self.hybrid_product_search(query, limit=limit)
            
            preference_vector = customer['preference_vector']
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Combine query embedding with user preferences (weighted)
            combined_embedding = []
            for i in range(len(query_embedding)):
                combined_val = query_embedding[i] * 0.7 + preference_vector[i] * 0.3
                combined_embedding.append(combined_val)
            
            # Search using combined embedding
            rows = await connection.fetch("""
                SELECT 
                    id, name, description, category, price, brand, rating,
                    1 - (description_embedding <=> $1) as similarity_score
                FROM products
                WHERE in_stock = true
                    AND (1 - (description_embedding <=> $1)) > 0.6
                ORDER BY similarity_score DESC
                LIMIT $2
            """, combined_embedding, limit)
            
            return [dict(row) for row in rows]
    
    async def find_similar_products(
        self,
        product_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find products similar to a given product
        """
        
        async with self.connection_pool.acquire() as connection:
            # Get the target product's embedding
            target_product = await connection.fetchrow(
                "SELECT description_embedding, category FROM products WHERE id = $1",
                product_id
            )
            
            if not target_product:
                return []
            
            target_embedding = target_product['description_embedding']
            target_category = target_product['category']
            
            # Find similar products (prefer same category)
            rows = await connection.fetch("""
                SELECT 
                    id, name, description, category, price, brand, rating,
                    1 - (description_embedding <=> $1) as similarity_score,
                    CASE WHEN category = $2 THEN 1.1 ELSE 1.0 END as category_boost
                FROM products
                WHERE id != $3 AND in_stock = true
                ORDER BY similarity_score * category_boost DESC
                LIMIT $4
            """, target_embedding, target_category, product_id, limit)
            
            return [dict(row) for row in rows]
    
    async def search_by_natural_language(
        self,
        query: str,
        customer_id: Optional[int] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Advanced natural language search with intent recognition
        """
        
        # Extract intent and parameters from natural language
        intent_analysis = await self._analyze_search_intent(query)
        
        # Choose search strategy based on intent
        if intent_analysis['type'] == 'product_search':
            results = await self.hybrid_product_search(
                query=intent_analysis['query'],
                category=intent_analysis.get('category'),
                min_price=intent_analysis.get('min_price'),
                max_price=intent_analysis.get('max_price'),
                brand=intent_analysis.get('brand'),
                min_rating=intent_analysis.get('min_rating'),
                limit=limit
            )
        elif intent_analysis['type'] == 'personalized' and customer_id:
            results = await self.personalized_search(
                customer_id=customer_id,
                query=intent_analysis['query'],
                limit=limit
            )
        else:
            # Default to hybrid search
            results = await self.hybrid_product_search(query, limit=limit)
        
        # Log search for analytics
        await self._log_search_query(query, customer_id, len(results))
        
        return {
            'query': query,
            'intent': intent_analysis,
            'results': results,
            'total_results': len(results)
        }
    
    async def _analyze_search_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze search query to extract intent and parameters
        """
        
        query_lower = query.lower()
        intent = {
            'type': 'product_search',
            'query': query,
            'category': None,
            'brand': None,
            'min_price': None,
            'max_price': None,
            'min_rating': None
        }
        
        # Category detection
        categories = {
            'smartphone': ['phone', 'smartphone', 'mobile', 'iphone', 'android'],
            'laptops': ['laptop', 'computer', 'macbook', 'ultrabook'],
            'audio': ['headphones', 'earphones', 'speaker', 'audio']
        }
        
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                intent['category'] = category
                break
        
        # Brand detection
        brands = ['apple', 'samsung', 'dell', 'sony', 'microsoft', 'google']
        for brand in brands:
            if brand in query_lower:
                intent['brand'] = brand
                break
        
        # Price range detection
        import re
        price_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        prices = re.findall(price_pattern, query_lower.replace(',', ''))
        
        if prices:
            if 'under' in query_lower or 'below' in query_lower or 'less than' in query_lower:
                intent['max_price'] = float(prices[0])
            elif 'over' in query_lower or 'above' in query_lower or 'more than' in query_lower:
                intent['min_price'] = float(prices[0])
            elif len(prices) == 2:
                intent['min_price'] = float(min(prices))
                intent['max_price'] = float(max(prices))
        
        # Rating detection
        if 'highly rated' in query_lower or 'best rated' in query_lower:
            intent['min_rating'] = 4.5
        elif 'good rating' in query_lower:
            intent['min_rating'] = 4.0
        
        # Personalization intent
        if any(word in query_lower for word in ['recommend', 'suggest', 'for me', 'my preferences']):
            intent['type'] = 'personalized'
        
        return intent
    
    async def _log_search_query(self, query: str, customer_id: Optional[int], results_count: int):
        """Log search query for analytics"""
        
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        async with self.connection_pool.acquire() as connection:
            await connection.execute("""
                INSERT INTO search_queries (query_text, query_embedding, customer_id, results_count)
                VALUES ($1, $2, $3, $4)
            """, query, query_embedding, customer_id, results_count)
```

## Success Criteria

By the end of this module, you should have:

1. **Working pgvector Setup**: PostgreSQL database with pgvector extension and sample data
2. **Hybrid Search Implementation**: Combining SQL filters with vector similarity search
3. **Advanced Search Features**: Personalization, faceted search, and reranking
4. **Real-world Applications**: E-commerce search and content discovery examples
5. **Performance Optimization**: Proper indexing and query monitoring

### Key Metrics to Track
- Search relevance (user click-through rates)
- Query performance (response times < 100ms for simple queries)
- Index efficiency (proper HNSW parameter tuning)
- User satisfaction (search result ratings)

---

**Next Step**: In Step 3, we'll integrate Google MCP Toolbox to add enterprise-grade features like multi-model support, advanced analytics, and production monitoring to our hybrid search system.
