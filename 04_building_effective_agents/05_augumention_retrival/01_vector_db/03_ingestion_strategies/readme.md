# Step 3: Advanced Ingestion Strategies - Document Chunking & Preprocessing

## Learning Objectives
By the end of this module, you will be able to:
- Implement intelligent document chunking strategies
- Handle different document formats (PDF, Word, Markdown, etc.)
- Optimize chunk size and overlap for better retrieval
- Preserve document structure and metadata
- Handle edge cases and error scenarios

## Theoretical Foundation

### Why Document Chunking Matters

**The Problem with Whole Documents:**
- **Context Length Limits**: LLMs have token limits (4K-32K typically)
- **Diluted Relevance**: Important info mixed with irrelevant content
- **Poor Matching**: Specific questions match broad documents poorly
- **Memory Inefficiency**: Large embeddings consume more storage

**The Chunking Solution:**
- **Focused Content**: Each chunk covers specific topic/concept
- **Better Matching**: Queries match relevant chunks precisely
- **Manageable Size**: Chunks fit within LLM context windows
- **Improved Accuracy**: More targeted semantic search

### Chunking Strategies

### 1. Fixed-Size Chunking
**Approach**: Split text every N characters/tokens
- **Pros**: Simple, predictable chunk sizes
- **Cons**: Breaks sentences/paragraphs mid-thought
- **Best for**: Uniform content, quick prototyping

```python
def fixed_chunk(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Split text into fixed-size chunks with overlap"""
```

### 2. Semantic Chunking (Recommended)
**Approach**: Split at natural boundaries (sentences, paragraphs)
- **Pros**: Preserves meaning, coherent chunks
- **Cons**: Variable chunk sizes
- **Best for**: Most text content, especially prose

**Natural Boundaries:**
- **Paragraph breaks**: `\n\n` or HTML `<p>` tags
- **Sentence endings**: Period + space + capital letter
- **Section headers**: Markdown `#` or numbered sections

### 3. Recursive Chunking
**Approach**: Try different separators in order of preference
- **Strategy**: Paragraphs → Sentences → Words → Characters
- **Advantage**: Maintains structure while respecting size limits

### 4. Document-Aware Chunking
**Approach**: Use document structure (headings, sections)
- **Best for**: Structured documents (technical docs, manuals)
- **Preserves**: Hierarchical information, context

## Chunk Optimization

### Size Considerations

**Chunk Size Guidelines:**
- **Small chunks (100-300 tokens)**: Very specific matching, might lack context
- **Medium chunks (300-800 tokens)**: Good balance for most use cases
- **Large chunks (800-1500 tokens)**: Rich context, might be too broad

**Testing Strategy:**
1. Start with 500-token chunks
2. Test with typical queries
3. Adjust based on result quality

### Overlap Strategy

**Why Overlap Matters:**
- **Continuity**: Prevents losing info at chunk boundaries
- **Context**: Ensures complete thoughts are captured
- **Redundancy**: Multiple chances to find relevant content

**Overlap Guidelines:**
- **10-20% overlap**: Good starting point
- **50-100 tokens**: Typical overlap size
- **Sentence-based**: Overlap complete sentences when possible

### Metadata Preservation

**Essential Metadata:**
- **Source document**: Original file name/path
- **Page/section numbers**: For citation and reference
- **Timestamps**: When document was created/modified
- **Document type**: PDF, web page, email, etc.
- **Author/source**: Attribution information

**Structural Metadata:**
- **Heading hierarchy**: H1, H2, H3 context
- **Section titles**: Current section/chapter
- **Table/figure captions**: Associated visual content
- **List context**: Whether chunk is part of a list

## Document Format Handling

### Text Documents
**Formats**: .txt, .md, .rtf
- **Advantages**: Clean text, easy parsing
- **Challenges**: Minimal structure information
- **Strategy**: Focus on paragraph/sentence boundaries

### PDF Documents
**Challenges**: 
- Complex layouts (columns, headers, footers)
- Mixed content (text, images, tables)
- OCR quality for scanned PDFs

**Tools & Strategies:**
- **PyPDF2/pdfplumber**: Basic text extraction
- **Camelot/Tabula**: Table extraction
- **OCR integration**: For scanned documents
- **Layout analysis**: Preserve reading order

### Microsoft Office Documents
**Formats**: .docx, .pptx, .xlsx
- **Advantages**: Rich metadata, clear structure
- **Tools**: python-docx, openpyxl, python-pptx
- **Strategy**: Preserve formatting context

### Web Content
**Sources**: HTML, web scraping
- **Challenges**: Navigation elements, ads, boilerplate
- **Tools**: BeautifulSoup, newspaper3k, trafilatura
- **Strategy**: Extract main content, remove noise

### Code Documents
**Formats**: .py, .js, .java, etc.
- **Special considerations**: Preserve function boundaries
- **Metadata**: Function names, class names, comments
- **Chunking**: By function/class rather than arbitrary splits

## Advanced Preprocessing

### Text Cleaning

**Common Issues:**
- **Extra whitespace**: Multiple spaces, tabs, newlines
- **Special characters**: Non-printable characters, encoding issues
- **Formatting artifacts**: HTML tags, markdown syntax
- **OCR errors**: Character recognition mistakes

**Cleaning Pipeline:**
1. **Normalize encoding**: Ensure UTF-8
2. **Remove artifacts**: Clean HTML/markdown if needed
3. **Fix spacing**: Normalize whitespace
4. **Preserve structure**: Keep important formatting
5. **Validate text**: Check for garbage/corrupted content

### Language Detection
**Why it matters**: Different models for different languages
**Implementation**: langdetect, polyglot libraries
**Strategy**: Per-chunk detection for multilingual documents

### Content Filtering
**Quality filters:**
- **Minimum length**: Skip very short chunks
- **Maximum repetition**: Avoid redundant content
- **Language confidence**: Skip low-confidence detections
- **Content type**: Filter out navigation, legal text, etc.

## Error Handling & Edge Cases

### Common Issues

**1. Empty Documents**
- **Detection**: File exists but no extractable text
- **Handling**: Log warning, skip gracefully

**2. Corrupted Files**
- **Detection**: Parsing exceptions, encoding errors
- **Handling**: Fallback to raw text extraction or skip

**3. Very Large Documents**
- **Detection**: File size or chunk count thresholds
- **Handling**: Stream processing, batch insertion

**4. Mixed Languages**
- **Detection**: Multiple languages in same document
- **Handling**: Per-chunk language detection, appropriate models

### Monitoring & Quality Assurance

**Ingestion Metrics:**
- **Processing time**: Track performance bottlenecks
- **Success rate**: Percentage of successfully processed documents
- **Chunk distribution**: Average/median chunk sizes
- **Error frequency**: Common failure patterns

**Quality Checks:**
- **Sample chunk review**: Manual inspection of results
- **Duplicate detection**: Identify redundant content
- **Coverage analysis**: Ensure complete document processing

## What We'll Build

### Intelligent Document Processor
```python
class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def process_document(self, file_path: str) -> List[DocumentChunk]:
        """Process a document into optimized chunks"""
    
    def chunk_text(self, text: str, metadata: dict) -> List[DocumentChunk]:
        """Intelligently chunk text preserving meaning"""
```

### Features to Implement
1. **Multi-format support**: Handle various document types
2. **Adaptive chunking**: Choose strategy based on content
3. **Metadata preservation**: Maintain document context
4. **Quality validation**: Ensure clean, useful chunks
5. **Error recovery**: Handle problematic documents gracefully

## Success Criteria
- Process multiple document formats successfully
- Generate chunks that preserve semantic meaning
- Maintain useful metadata for each chunk
- Handle errors gracefully without crashing
- Achieve consistent chunk quality across document types

---

**Next Step**: In Step 4, we'll learn advanced retrieval strategies including hybrid search, query expansion, and re-ranking techniques to improve search quality.
