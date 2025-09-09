# Analysis Engine - NLTK & LLM Integration

## Purpose
Core text analysis engine combining NLTK natural language processing with OpenAI LLM capabilities for comprehensive query-response analysis.

## Core Components

### `nltk_processor.py` - Main NLTK Analysis Engine
Comprehensive text analysis using NLTK and spaCy libraries.

**Key Methods:**
- `sentiment_analysis(text)` - Multi-model sentiment scoring (VADER, TextBlob, custom)
- `entity_extraction(text)` - Named entity recognition with spaCy integration
- `topic_modeling(texts, num_topics=5)` - LDA topic modeling with coherence
- `keyword_extraction(text, method='tfidf')` - Multiple keyword extraction methods
- `readability_analysis(text)` - Flesch-Kincaid, Gunning-Fog, ARI metrics
- `text_similarity(text1, text2)` - Cosine, Jaccard, semantic similarity
- `question_classification(question)` - Intent and complexity classification

### `llm_processor.py` - OpenAI Integration
Advanced analysis using large language models for business insights.

**Key Methods:**
- `analyze_conversation_quality(query, context, response)` - Response quality assessment
- `extract_business_insights(questions_batch)` - Business intelligence extraction
- `generate_executive_summary(dataset_analysis)` - High-level summaries
- `assess_response_completeness(query, response)` - Response adequacy scoring

### `sentiment_analyzer.py` - Specialized Sentiment Analysis
Multi-approach sentiment analysis with confidence scoring.

**Features:**
- VADER lexicon-based approach
- TextBlob pattern-based analysis
- Custom trained models for domain-specific sentiment
- Confidence scoring and ensemble methods
- Emotion detection beyond positive/negative/neutral

### `topic_modeler.py` - Topic Modeling Engine
LDA-based topic discovery and evolution tracking.

**Features:**
- Latent Dirichlet Allocation (LDA) implementation
- Topic coherence scoring for model optimization
- Topic evolution tracking over time
- Interactive topic exploration support
- Custom preprocessing pipelines

### `entity_extractor.py` - Named Entity Recognition
Entity extraction and relationship mapping using spaCy.

**Features:**
- Person, organization, location extraction
- Custom entity types for business domains
- Entity relationship network construction
- Co-occurrence analysis
- Entity disambiguation and linking

### `text_classifier.py` - Question & Response Classification
Classification of query types and response categories.

**Features:**
- Question intent classification (support, billing, feature)
- Complexity scoring based on linguistic features
- Urgency level assessment
- Response type categorization
- Quality indicators and scoring

## Analysis Pipeline Flow

```
1. Text Preprocessing
   ├── Tokenization and normalization
   ├── Stop word removal
   ├── Lemmatization
   └── Cleaning and validation

2. Core NLTK Analysis
   ├── Sentiment analysis (multi-model)
   ├── Named entity recognition
   ├── Part-of-speech tagging
   ├── Dependency parsing
   └── Keyword extraction

3. Advanced Analysis
   ├── Topic modeling (LDA)
   ├── Text similarity computation
   ├── Readability scoring
   └── Classification tasks

4. LLM Enhancement
   ├── Conversation quality assessment
   ├── Business insights generation
   ├── Response completeness scoring
   └── Executive summary creation

5. Results Integration
   ├── Database storage
   ├── Cache optimization
   ├── Real-time updates
   └── Export preparation
```

## Configuration

### NLTK Models Required
```python
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
```

### spaCy Models Required
```bash
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
```

### OpenAI Configuration
```python
OPENAI_API_KEY = "sk-proj-your-key-here"
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 4000
OPENAI_TEMPERATURE = 0.3
```

## Performance Optimizations

### Batch Processing
- Process multiple texts simultaneously
- Configurable batch sizes based on memory
- Progress tracking for long-running operations
- Parallel processing for CPU-intensive tasks

### Model Caching
- Cache loaded NLTK models in memory
- Persistent storage for topic models
- LLM response caching to reduce API calls
- Intelligent cache invalidation

### Resource Management
- Memory optimization for large datasets
- CPU utilization monitoring
- Background job queuing with Celery
- Resource limits and throttling

## Integration Points

### Database Integration
- SQLAlchemy models for analysis results
- Bulk insert operations for efficiency
- Indexing for fast retrieval
- Result versioning and tracking

### WebSocket Updates
- Real-time progress reporting
- Status updates during processing
- Error notification and recovery
- Completion notifications with results

### API Endpoints
- RESTful endpoints for analysis requests
- Batch processing support
- Job status tracking
- Result retrieval and export

### Background Jobs
- Celery task integration
- Job queue management
- Progress tracking and reporting
- Error handling and retry logic

## Usage Examples

### Basic Sentiment Analysis
```python
from analysis.nltk_processor import NLTKProcessor

processor = NLTKProcessor()
result = processor.sentiment_analysis("This product is amazing!")
# Returns: {'compound_score': 0.6, 'label': 'positive', ...}
```

### Topic Modeling
```python
texts = ["Query 1", "Query 2", "Query 3"]
topics = processor.topic_modeling(texts, num_topics=3)
# Returns: {'topics': [...], 'coherence_score': 0.85, ...}
```

### LLM Analysis
```python
from analysis.llm_processor import LLMProcessor

llm = LLMProcessor()
quality = llm.analyze_conversation_quality(query, context, response)
# Returns: {'response_relevance': 0.9, 'overall_quality': 0.85, ...}
```

*Last Updated: Initial project structure creation*
