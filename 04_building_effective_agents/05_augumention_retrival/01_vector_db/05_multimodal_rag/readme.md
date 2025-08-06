# Step 5: [Multimodal RAG](https://milvus.io/docs/multimodal_rag_with_milvus.md) - Beyond Text to Images, Audio, and Mixed Content

## Learning Objectives
By the end of this module, you will be able to:
- Understand multimodal embedding models and their capabilities
- Implement image-to-text and text-to-image search
- Handle audio content with speech-to-text integration
- Build unified search across multiple content types
- Design retrieval systems for mixed-media documents

## Theoretical Foundation

### Why Multimodal RAG Matters

**Modern Information is Multimodal:**
- **Technical documentation**: Text with diagrams, screenshots, flowcharts
- **Educational content**: Video lectures with slides and transcripts
- **Research papers**: Text with figures, tables, equations
- **Business reports**: Charts, graphs, infographics with analysis
- **Social media**: Posts with images, videos, audio clips

**Traditional RAG Limitations:**
- **Text-only**: Ignores visual information completely
- **Context loss**: Alt-text doesn't capture visual details
- **Incomplete understanding**: Misses relationships between text and visuals
- **Poor user experience**: Can't answer questions about visual content

### Multimodal Embedding Models

### 1. CLIP (Contrastive Language-Image Pre-training)
**What it does**: Creates unified embedding space for text and images
**Capabilities:**
- **Image → Text**: Find text descriptions matching an image
- **Text → Image**: Find images matching text descriptions
- **Cross-modal**: Compare similarity between text and images directly

**Model Options:**
- **OpenAI CLIP**: Original, good general performance
- **OpenCLIP**: Open-source variants with different sizes
- **CLIP-ViT-B/32**: Balanced speed/accuracy (most common)
- **CLIP-ViT-L/14**: Higher accuracy, slower

### 2. ALIGN (A Large-scale ImaGe and Noisy-text embedding)
**Advantages**: Trained on larger, noisier dataset
**Better for**: Real-world, diverse image content

### 3. Vision-Language Models
**LLaVA**: Large Language and Vision Assistant
**BLIP-2**: Bootstrapped Vision-Language Pre-training
**GPT-4V**: Commercial multimodal model (via API)

### Multimodal Search Architecture

### Core Components

**1. Content Processing Pipeline**
```python
def process_multimodal_document(file_path: str) -> List[ModalChunk]:
    """Extract and process different content types"""
    
    # Detect content types
    text_content = extract_text(file_path)
    images = extract_images(file_path)
    audio_clips = extract_audio(file_path)
    
    # Create unified chunks
    chunks = []
    for image in images:
        chunks.append(ImageChunk(
            content=image,
            embedding=clip_model.encode_image(image),
            metadata=extract_image_metadata(image)
        ))
    
    for text_segment in chunk_text(text_content):
        chunks.append(TextChunk(
            content=text_segment,
            embedding=text_model.encode(text_segment),
            metadata=extract_text_metadata(text_segment)
        ))
    
    return chunks
```

**2. Unified Search Interface**
```python
def multimodal_search(query: Union[str, Image], k: int = 10) -> List[ModalChunk]:
    """Search across all content types"""
    
    if isinstance(query, str):
        query_embedding = text_model.encode(query)
    else:  # Image query
        query_embedding = clip_model.encode_image(query)
    
    # Search all content types
    results = search_multimodal_index(query_embedding, k)
    return results
```

## Image Content Processing

### Image Extraction and Analysis

**1. Document Image Extraction**
```python
def extract_images_from_pdf(pdf_path: str) -> List[ImageData]:
    """Extract images from PDF documents"""
    import fitz  # PyMuPDF
    
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            # Extract image data
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            images.append(ImageData(
                data=image_bytes,
                page=page_num,
                position=img_index,
                format=base_image["ext"]
            ))
    
    return images
```

**2. Image Description Generation**
```python
def generate_image_description(image: Image) -> str:
    """Generate text description of image content"""
    
    # Option 1: Use vision-language model
    description = vision_model.describe_image(image)
    
    # Option 2: Use object detection + scene description
    objects = object_detector.detect(image)
    scene = scene_classifier.classify(image)
    description = f"Scene: {scene}. Objects: {', '.join(objects)}"
    
    return description
```

**3. OCR for Text in Images**
```python
def extract_text_from_image(image: Image) -> str:
    """Extract text content from images using OCR"""
    import pytesseract
    
    # Preprocess image for better OCR
    processed_image = preprocess_for_ocr(image)
    
    # Extract text
    text = pytesseract.image_to_string(processed_image)
    
    # Clean and validate extracted text
    cleaned_text = clean_ocr_text(text)
    
    return cleaned_text
```

### Image Search Strategies

**1. Visual Similarity Search**
```python
def visual_similarity_search(query_image: Image, k: int = 10) -> List[ImageChunk]:
    """Find visually similar images"""
    query_embedding = clip_model.encode_image(query_image)
    
    # Search in image-only index
    similar_images = image_index.search(query_embedding, k)
    return similar_images
```

**2. Cross-Modal Search (Text → Image)**
```python
def text_to_image_search(text_query: str, k: int = 10) -> List[ImageChunk]:
    """Find images matching text description"""
    # Use CLIP to encode text query
    text_embedding = clip_model.encode_text(text_query)
    
    # Search in image index using text embedding
    matching_images = image_index.search(text_embedding, k)
    return matching_images
```

**3. Image → Text Search**
```python
def image_to_text_search(query_image: Image, k: int = 10) -> List[TextChunk]:
    """Find text content related to an image"""
    image_embedding = clip_model.encode_image(query_image)
    
    # Search in text index using image embedding
    related_text = text_index.search(image_embedding, k)
    return related_text
```

## Audio Content Processing

### Speech-to-Text Integration

**1. Audio Extraction**
```python
def extract_audio_from_video(video_path: str) -> str:
    """Extract audio track from video files"""
    import moviepy.editor as mp
    
    video = mp.VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path)
    
    return audio_path
```

**2. Speech Recognition**
```python
def transcribe_audio(audio_path: str) -> TranscriptionResult:
    """Convert speech to text with timestamps"""
    
    # Option 1: OpenAI Whisper (free, local)
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    
    # Option 2: Google Speech-to-Text API
    # result = google_speech_to_text(audio_path)
    
    return TranscriptionResult(
        text=result["text"],
        segments=result["segments"],  # Time-stamped segments
        language=result["language"]
    )
```

**3. Audio Chunking with Timestamps**
```python
def create_audio_chunks(transcription: TranscriptionResult) -> List[AudioChunk]:
    """Create searchable chunks from transcribed audio"""
    chunks = []
    
    for segment in transcription.segments:
        chunk = AudioChunk(
            text=segment["text"],
            start_time=segment["start"],
            end_time=segment["end"],
            embedding=text_model.encode(segment["text"]),
            metadata={
                "language": transcription.language,
                "confidence": segment.get("confidence", 1.0)
            }
        )
        chunks.append(chunk)
    
    return chunks
```

## Unified Multimodal Search

### Cross-Modal Ranking

**1. Modal Scoring Strategy**
```python
def multimodal_search_with_ranking(
    query: str, 
    k: int = 10,
    modal_weights: Dict[str, float] = None
) -> List[ModalChunk]:
    """Search across modalities with weighted scoring"""
    
    if modal_weights is None:
        modal_weights = {"text": 0.5, "image": 0.3, "audio": 0.2}
    
    # Search each modality
    text_results = text_search(query, k)
    image_results = text_to_image_search(query, k)
    audio_results = audio_search(query, k)
    
    # Apply modal weights
    for result in text_results:
        result.score *= modal_weights["text"]
    for result in image_results:
        result.score *= modal_weights["image"]
    for result in audio_results:
        result.score *= modal_weights["audio"]
    
    # Merge and rank
    all_results = text_results + image_results + audio_results
    all_results.sort(key=lambda x: x.score, reverse=True)
    
    return all_results[:k]
```

**2. Context-Aware Reranking**
```python
def rerank_multimodal_results(
    query: str, 
    results: List[ModalChunk]
) -> List[ModalChunk]:
    """Rerank considering cross-modal context"""
    
    enhanced_results = []
    for result in results:
        # Find related content in other modalities
        related_content = find_related_content(result)
        
        # Calculate enhanced relevance score
        base_score = result.score
        context_score = calculate_context_relevance(query, related_content)
        diversity_score = calculate_modal_diversity(result, enhanced_results)
        
        enhanced_score = (
            0.6 * base_score + 
            0.3 * context_score + 
            0.1 * diversity_score
        )
        
        result.enhanced_score = enhanced_score
        enhanced_results.append(result)
    
    enhanced_results.sort(key=lambda x: x.enhanced_score, reverse=True)
    return enhanced_results
```

### Modal Fusion Techniques

**1. Early Fusion (Feature Level)**
```python
def early_fusion_embedding(
    text: str, 
    image: Image, 
    audio_transcript: str
) -> np.ndarray:
    """Combine features before similarity calculation"""
    
    text_emb = text_model.encode(text)
    image_emb = clip_model.encode_image(image)
    audio_emb = text_model.encode(audio_transcript)
    
    # Concatenate or weighted average
    fused_embedding = np.concatenate([text_emb, image_emb, audio_emb])
    # OR: fused_embedding = 0.5*text_emb + 0.3*image_emb + 0.2*audio_emb
    
    return fused_embedding
```

**2. Late Fusion (Score Level)**
```python
def late_fusion_search(query: str, k: int = 10) -> List[ModalChunk]:
    """Combine scores from different modal searches"""
    
    # Get results from each modality
    modal_results = {
        "text": text_search(query, k),
        "image": text_to_image_search(query, k),
        "audio": audio_search(query, k)
    }
    
    # Normalize scores within each modality
    for modality, results in modal_results.items():
        scores = [r.score for r in results]
        normalized_scores = normalize_scores(scores)
        for result, norm_score in zip(results, normalized_scores):
            result.normalized_score = norm_score
    
    # Combine results
    return combine_modal_results(modal_results)
```

## Specialized Use Cases

### Technical Documentation

**Challenge**: Diagrams and code screenshots with explanatory text
**Solution**: 
- Extract code from screenshots using OCR
- Link diagrams to related text sections
- Search across visual flowcharts and textual explanations

```python
def process_technical_doc(doc_path: str) -> List[TechChunk]:
    """Process technical documentation with special handling"""
    
    chunks = []
    
    # Extract and process diagrams
    diagrams = extract_diagrams(doc_path)
    for diagram in diagrams:
        # OCR any text in diagram
        diagram_text = extract_text_from_image(diagram)
        
        # Generate description
        description = describe_technical_diagram(diagram)
        
        # Find related text sections
        related_text = find_adjacent_text(diagram, doc_path)
        
        chunks.append(TechChunk(
            type="diagram",
            visual_content=diagram,
            text_content=diagram_text + " " + description,
            related_context=related_text,
            embedding=generate_multimodal_embedding(diagram, description)
        ))
    
    return chunks
```

### Educational Content

**Challenge**: Video lectures with slides and transcripts
**Solution**:
- Sync slides with transcript timestamps
- Enable search by visual content or spoken words
- Link related slides and transcript segments

```python
def process_educational_video(video_path: str) -> List[EduChunk]:
    """Process educational video with slide sync"""
    
    # Extract components
    slides = extract_slides_from_video(video_path)
    transcript = transcribe_video(video_path)
    
    # Sync slides with transcript
    synced_chunks = []
    for slide in slides:
        # Find transcript segments that correspond to this slide
        relevant_segments = find_transcript_segments(
            slide.timestamp_start,
            slide.timestamp_end,
            transcript
        )
        
        # Combine slide and transcript
        combined_text = " ".join([seg.text for seg in relevant_segments])
        
        synced_chunks.append(EduChunk(
            slide_image=slide.image,
            transcript_text=combined_text,
            timestamp_start=slide.timestamp_start,
            timestamp_end=slide.timestamp_end,
            embedding=generate_multimodal_embedding(slide.image, combined_text)
        ))
    
    return synced_chunks
```

## Performance and Storage Considerations

### Embedding Storage

**Storage Requirements:**
- **Text embeddings**: 768 dimensions × 4 bytes = 3KB per chunk
- **Image embeddings**: 512 dimensions × 4 bytes = 2KB per image
- **Original content**: Variable (images can be large)

**Optimization Strategies:**
```python
def optimize_multimodal_storage(chunks: List[ModalChunk]):
    """Optimize storage for multimodal content"""
    
    for chunk in chunks:
        if chunk.type == "image":
            # Compress images
            chunk.content = compress_image(chunk.content, quality=85)
            
            # Store thumbnails for preview
            chunk.thumbnail = create_thumbnail(chunk.content, size=(150, 150))
            
            # Optionally store original separately
            chunk.original_path = store_original_image(chunk.content)
        
        # Quantize embeddings if needed
        chunk.embedding = quantize_embedding(chunk.embedding, precision=16)
```

### Search Performance

**Multimodal Index Strategy:**
```python
class MultimodalIndex:
    def __init__(self):
        # Separate indices for different modalities
        self.text_index = MilvusIndex("text_collection")
        self.image_index = MilvusIndex("image_collection")
        self.audio_index = MilvusIndex("audio_collection")
        
        # Unified index for cross-modal search
        self.unified_index = MilvusIndex("unified_collection")
    
    def search(self, query_embedding: np.ndarray, modalities: List[str]) -> List[ModalChunk]:
        """Search across specified modalities"""
        results = []
        
        for modality in modalities:
            if modality == "text":
                results.extend(self.text_index.search(query_embedding))
            elif modality == "image":
                results.extend(self.image_index.search(query_embedding))
            elif modality == "audio":
                results.extend(self.audio_index.search(query_embedding))
        
        return self.merge_and_deduplicate(results)
```

## What We'll Build

### Multimodal RAG System
```python
class MultimodalRAG:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.multimodal_index = MultimodalIndex()
        self.clip_model = CLIPModel()
    
    def ingest_document(self, file_path: str):
        """Process and index multimodal document"""
        # Detect content types
        content_types = detect_content_types(file_path)
        
        # Process each type
        all_chunks = []
        if "text" in content_types:
            all_chunks.extend(self.text_processor.process(file_path))
        if "images" in content_types:
            all_chunks.extend(self.image_processor.process(file_path))
        if "audio" in content_types:
            all_chunks.extend(self.audio_processor.process(file_path))
        
        # Index all chunks
        self.multimodal_index.add_chunks(all_chunks)
    
    def search(self, query: Union[str, Image], k: int = 10) -> List[ModalChunk]:
        """Unified search across all modalities"""
        # Process query
        if isinstance(query, str):
            query_embedding = self.clip_model.encode_text(query)
        else:
            query_embedding = self.clip_model.encode_image(query)
        
        # Search and rank
        results = self.multimodal_index.search(query_embedding, k=k*2)
        ranked_results = self.rerank_multimodal(query, results)
        
        return ranked_results[:k]
```

### Features to Implement
1. **Image extraction and processing**: From PDFs, documents, presentations
2. **Cross-modal search**: Text queries finding images and vice versa
3. **Audio transcription**: Speech-to-text with timestamp sync
4. **Unified search interface**: Single query across all content types
5. **Context-aware ranking**: Consider relationships between modalities

## Success Criteria
- Successfully extract and index images from documents
- Implement working text-to-image and image-to-text search
- Handle audio content with speech recognition
- Build unified search that works across all modalities
- Demonstrate improved search quality for multimodal content

---

**Next Step**: In Step 6, we'll explore advanced RAG architectures including hierarchical search, graph-based retrieval, and specialized patterns for different use cases.
