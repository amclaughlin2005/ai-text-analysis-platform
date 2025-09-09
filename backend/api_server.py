#!/usr/bin/env python3
"""
Simple API Server for AI Text Analysis Platform
Direct implementation without complex imports
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn
import csv
import io
import uuid
import os
import json

# Create app
app = FastAPI(
    title="AI Text Analysis API",
    description="Backend API for text analysis platform",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class WordCloudRequest(BaseModel):
    dataset_id: str = "demo"
    mode: str = "all" 
    filters: Dict[str, Any] = {}

# Root endpoints
@app.get("/")
def root():
    return {
        "message": "AI-Powered Text Analysis Platform API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "GET /health - Health check",
            "GET /docs - API documentation", 
            "POST /api/wordcloud/generate - Generate word cloud",
            "GET /api/wordcloud/modes - Get analysis modes",
            "GET /api/datasets - List datasets",
            "POST /api/datasets/upload - Upload CSV dataset",
            "GET /api/datasets/{id} - Get dataset details",
            "DELETE /api/datasets/{id} - Delete dataset"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "api_server"
    }

@app.get("/api/test-frontend-connection")
def test_frontend_connection():
    """Test endpoint specifically for frontend debugging"""
    return {
        "status": "success",
        "message": "Frontend can connect to backend!",
        "timestamp": datetime.now().isoformat(),
        "server_info": {
            "host": "localhost",
            "port": 8001,
            "cors_enabled": True,
            "upload_enabled": True
        }
    }

# Word cloud endpoints  
@app.post("/api/wordcloud/generate")
def generate_wordcloud(request: WordCloudRequest):
    """Generate word cloud data from uploaded datasets or mock data"""
    
    # Check if this is for a real uploaded dataset
    if request.dataset_id in datasets_storage:
        return generate_real_wordcloud(request.dataset_id, request.mode)
    
    # Otherwise use mock data
    return generate_mock_wordcloud(request.mode)

def generate_real_wordcloud(dataset_id: str, mode: str):
    """Generate word cloud from actual uploaded dataset"""
    try:
        dataset = datasets_storage[dataset_id]
        file_path = dataset['file_path']
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        # Read the CSV file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Decode with the known encoding
        csv_text = content.decode(dataset.get('csv_encoding', 'latin-1'))
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader, [])
        rows = list(csv_reader)
        
        # Find question and response columns
        header_lower = [h.lower().strip() for h in headers]
        question_col_idx = None
        response_col_idx = None
        
        for i, header in enumerate(header_lower):
            if 'question' in header:
                question_col_idx = i
            if 'response' in header:
                response_col_idx = i
        
        # Extract text based on mode
        if mode == 'all':
            # Use both questions and responses
            all_text = []
            for row in rows:
                if len(row) > max(question_col_idx or 0, response_col_idx or 0):
                    if question_col_idx is not None:
                        all_text.append(row[question_col_idx])
                    if response_col_idx is not None:
                        all_text.append(row[response_col_idx])
        elif mode == 'verbs':
            # Focus on action words from responses
            all_text = []
            for row in rows:
                if response_col_idx is not None and len(row) > response_col_idx:
                    all_text.append(row[response_col_idx])
        else:
            # Use questions for other modes
            all_text = []
            for row in rows:
                if question_col_idx is not None and len(row) > question_col_idx:
                    all_text.append(row[question_col_idx])
        
        # Simple word extraction and frequency analysis
        import re
        from collections import Counter
        
        combined_text = ' '.join(all_text).lower()
        
        # Extract meaningful words (4+ characters)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', combined_text)
        
        # Remove common stop words
        stop_words = {'that', 'this', 'with', 'from', 'they', 'have', 'will', 'your', 'their', 'would', 'could', 'should', 'been', 'were', 'than', 'them', 'what', 'when', 'where', 'there', 'these', 'those', 'which', 'while', 'upon', 'said', 'also', 'more', 'only', 'such', 'some', 'like', 'into', 'over', 'here', 'make', 'made', 'take', 'come', 'back', 'time', 'well', 'then', 'know', 'just', 'good', 'work', 'first', 'after', 'right', 'other', 'many', 'each', 'most', 'both'}
        
        filtered_words = [w for w in words if w not in stop_words and len(w) >= 4]
        
        # Get word frequencies
        word_counts = Counter(filtered_words).most_common(20)
        
        # Format for frontend
        formatted_words = []
        max_count = word_counts[0][1] if word_counts else 1
        
        for i, (word, count) in enumerate(word_counts):
            # Simple sentiment analysis for legal terms
            positive_legal = ['defense', 'legal', 'professional', 'expert', 'qualified', 'evidence', 'court', 'counsel', 'attorney', 'judge', 'justice']
            negative_legal = ['damages', 'punitive', 'violation', 'negligence', 'liability', 'fault', 'breach', 'misconduct', 'fraud']
            
            if word in positive_legal:
                sentiment = 'positive'
            elif word in negative_legal:
                sentiment = 'negative' 
            else:
                sentiment = 'neutral'
            
            formatted_words.append({
                'word': word,
                'frequency': count,
                'sentiment': sentiment,
                'size': count / max_count,  # Normalize to 0-1
            })
        
        return {
            'words': formatted_words,
            'insights': {
                'total_words': len(formatted_words),
                'mode': mode,
                'dataset_name': dataset['name'],
                'source': 'real_data',
                'sentiment_distribution': {
                    'positive': len([w for w in formatted_words if w['sentiment'] == 'positive']),
                    'negative': len([w for w in formatted_words if w['sentiment'] == 'negative']),
                    'neutral': len([w for w in formatted_words if w['sentiment'] == 'neutral'])
                }
            },
            'metadata': {
                'dataset_id': dataset_id,
                'analysis_mode': mode,
                'generated_at': datetime.now().isoformat(),
                'source': 'uploaded_dataset',
                'total_questions': len(rows),
                'text_analyzed': len(all_text)
            }
        }
        
    except Exception as e:
        print(f"❌ Real word cloud generation failed: {e}")
        # Fallback to mock data
        return generate_mock_wordcloud(mode)

def generate_mock_wordcloud(mode: str):
    """Generate mock word cloud data (fallback)"""
    
    # Mock word data by mode
    word_data = {
        'all': [
            {'word': 'customer', 'frequency': 85, 'sentiment': 'neutral', 'size': 1.0},
            {'word': 'support', 'frequency': 72, 'sentiment': 'positive', 'size': 0.85}, 
            {'word': 'service', 'frequency': 68, 'sentiment': 'positive', 'size': 0.8},
            {'word': 'help', 'frequency': 65, 'sentiment': 'positive', 'size': 0.76},
            {'word': 'issue', 'frequency': 58, 'sentiment': 'negative', 'size': 0.68},
            {'word': 'problem', 'frequency': 45, 'sentiment': 'negative', 'size': 0.53},
            {'word': 'solution', 'frequency': 42, 'sentiment': 'positive', 'size': 0.49},
            {'word': 'team', 'frequency': 38, 'sentiment': 'neutral', 'size': 0.45},
            {'word': 'quality', 'frequency': 35, 'sentiment': 'positive', 'size': 0.41},
            {'word': 'experience', 'frequency': 32, 'sentiment': 'neutral', 'size': 0.38}
        ],
        'verbs': [
            {'word': 'help', 'frequency': 65, 'sentiment': 'positive', 'size': 1.0},
            {'word': 'solve', 'frequency': 45, 'sentiment': 'positive', 'size': 0.69},
            {'word': 'support', 'frequency': 42, 'sentiment': 'positive', 'size': 0.65},
            {'word': 'fix', 'frequency': 38, 'sentiment': 'positive', 'size': 0.58},
            {'word': 'assist', 'frequency': 35, 'sentiment': 'positive', 'size': 0.54},
            {'word': 'resolve', 'frequency': 32, 'sentiment': 'positive', 'size': 0.49},
            {'word': 'provide', 'frequency': 28, 'sentiment': 'neutral', 'size': 0.43},
            {'word': 'understand', 'frequency': 25, 'sentiment': 'neutral', 'size': 0.38},
            {'word': 'explain', 'frequency': 22, 'sentiment': 'neutral', 'size': 0.34},
            {'word': 'improve', 'frequency': 20, 'sentiment': 'positive', 'size': 0.31}
        ],
        'emotions': [
            {'word': 'happy', 'frequency': 45, 'sentiment': 'positive', 'size': 1.0},
            {'word': 'frustrated', 'frequency': 42, 'sentiment': 'negative', 'size': 0.93},
            {'word': 'satisfied', 'frequency': 38, 'sentiment': 'positive', 'size': 0.84},
            {'word': 'confused', 'frequency': 35, 'sentiment': 'negative', 'size': 0.78},
            {'word': 'pleased', 'frequency': 32, 'sentiment': 'positive', 'size': 0.71},
            {'word': 'disappointed', 'frequency': 28, 'sentiment': 'negative', 'size': 0.62},
            {'word': 'grateful', 'frequency': 25, 'sentiment': 'positive', 'size': 0.56},
            {'word': 'worried', 'frequency': 22, 'sentiment': 'negative', 'size': 0.49},
            {'word': 'excited', 'frequency': 20, 'sentiment': 'positive', 'size': 0.44},
            {'word': 'calm', 'frequency': 18, 'sentiment': 'neutral', 'size': 0.4}
        ],
        'themes': [
            {'word': 'billing', 'frequency': 55, 'sentiment': 'negative', 'size': 1.0},
            {'word': 'technical', 'frequency': 48, 'sentiment': 'neutral', 'size': 0.87},
            {'word': 'account', 'frequency': 42, 'sentiment': 'neutral', 'size': 0.76},
            {'word': 'feature', 'frequency': 38, 'sentiment': 'positive', 'size': 0.69},
            {'word': 'security', 'frequency': 35, 'sentiment': 'neutral', 'size': 0.64},
            {'word': 'performance', 'frequency': 32, 'sentiment': 'negative', 'size': 0.58},
            {'word': 'training', 'frequency': 28, 'sentiment': 'neutral', 'size': 0.51},
            {'word': 'integration', 'frequency': 25, 'sentiment': 'neutral', 'size': 0.45},
            {'word': 'mobile', 'frequency': 22, 'sentiment': 'neutral', 'size': 0.4},
            {'word': 'documentation', 'frequency': 20, 'sentiment': 'negative', 'size': 0.36}
        ],
        'entities': [
            {'word': 'John Smith', 'frequency': 25, 'sentiment': 'neutral', 'size': 1.0},
            {'word': 'Microsoft', 'frequency': 22, 'sentiment': 'neutral', 'size': 0.88},
            {'word': 'Chicago', 'frequency': 20, 'sentiment': 'neutral', 'size': 0.8},
            {'word': 'Sales Team', 'frequency': 18, 'sentiment': 'positive', 'size': 0.72},
            {'word': 'Product X', 'frequency': 15, 'sentiment': 'neutral', 'size': 0.6},
            {'word': 'Support Dept', 'frequency': 12, 'sentiment': 'positive', 'size': 0.48},
            {'word': 'System Alpha', 'frequency': 10, 'sentiment': 'neutral', 'size': 0.4},
            {'word': 'Manager', 'frequency': 8, 'sentiment': 'neutral', 'size': 0.32},
            {'word': 'Customer ID', 'frequency': 5, 'sentiment': 'neutral', 'size': 0.2}
        ],
        'topics': [
            {'word': 'payment processing', 'frequency': 35, 'sentiment': 'negative', 'size': 1.0},
            {'word': 'user interface', 'frequency': 32, 'sentiment': 'neutral', 'size': 0.91},
            {'word': 'data migration', 'frequency': 28, 'sentiment': 'negative', 'size': 0.8},
            {'word': 'system performance', 'frequency': 25, 'sentiment': 'negative', 'size': 0.71},
            {'word': 'security features', 'frequency': 22, 'sentiment': 'positive', 'size': 0.63},
            {'word': 'mobile application', 'frequency': 20, 'sentiment': 'neutral', 'size': 0.57},
            {'word': 'customer support', 'frequency': 18, 'sentiment': 'positive', 'size': 0.51},
            {'word': 'integration tools', 'frequency': 15, 'sentiment': 'neutral', 'size': 0.43}
        ]
    }
    
    words = word_data.get(mode, word_data['all'])
    
    return {
        'words': words,
        'insights': {
            'total_words': len(words),
            'mode': mode,
            'sentiment_distribution': {
                'positive': len([w for w in words if w['sentiment'] == 'positive']),
                'negative': len([w for w in words if w['sentiment'] == 'negative']),
                'neutral': len([w for w in words if w['sentiment'] == 'neutral'])
            }
        },
        'metadata': {
            'dataset_id': 'mock-data',
            'analysis_mode': mode,
            'generated_at': datetime.now().isoformat(),
            'source': 'mock_data'
        }
    }

@app.get("/api/wordcloud/modes")
def get_wordcloud_modes():
    """Get available analysis modes"""
    return {
        'modes': ['all', 'verbs', 'themes', 'emotions', 'entities', 'topics'],
        'descriptions': {
            'all': 'All significant words',
            'verbs': 'Action words and verbs',
            'themes': 'Thematic categories', 
            'emotions': 'Emotional language',
            'entities': 'Named entities',
            'topics': 'Topic modeling results'
        }
    }

# In-memory storage for demo (replace with database later)
datasets_storage = {}
upload_directory = "uploads"

# Create uploads directory if it doesn't exist
os.makedirs(upload_directory, exist_ok=True)

# Dataset endpoints
@app.get("/api/datasets")
def get_datasets():
    """Get list of datasets"""
    try:
        # Demo datasets + uploaded ones
        demo_datasets = [
            {
                'id': 'demo-dataset-1',
                'name': 'Customer Support Demo',
                'description': 'Sample customer support conversations',
                'original_filename': 'support_demo.csv',
                'file_size': 1024000,
                'status': 'completed',
                'progress_percentage': 100,
                'status_message': 'Analysis completed',
                'total_questions': 150,
                'processed_questions': 150,
                'valid_questions': 145,
                'invalid_questions': 5,
                'sentiment_avg': 0.65,
                'sentiment_distribution': {'positive': 0.6, 'negative': 0.15, 'neutral': 0.25},
                'organizations_count': 8,
                'created_at': '2024-01-15T10:00:00Z',
                'updated_at': '2024-01-15T12:00:00Z',
                'processing_started_at': '2024-01-15T10:05:00Z',
                'processing_completed_at': '2024-01-15T12:00:00Z',
                'is_public': False
            }
        ]
        
        # Add uploaded datasets
        all_datasets = list(datasets_storage.values()) + demo_datasets
        
        return {
            'status': 'success',
            'data': {
                'datasets': all_datasets
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch datasets: {str(e)}")

@app.post("/api/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    """Upload and process CSV dataset"""
    try:
        print(f"📤 Upload request: {file.filename}, name: {name}")
        
        # Validate file
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Dataset name is required")
        
        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Read and validate CSV content
        content = await file.read()
        
        # Try multiple encodings to handle different CSV sources
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        csv_text = None
        used_encoding = None
        
        for encoding in encodings_to_try:
            try:
                csv_text = content.decode(encoding)
                used_encoding = encoding
                print(f"📝 Successfully decoded with encoding: {encoding}")
                break
            except UnicodeDecodeError as e:
                print(f"⚠️ Failed to decode with {encoding}: {e}")
                continue
        
        if csv_text is None:
            raise HTTPException(
                status_code=400, 
                detail="Could not decode CSV file. Please ensure it's saved as UTF-8, Latin-1, or Windows-1252 encoding."
            )
        
        # Parse CSV
        try:
            csv_reader = csv.reader(io.StringIO(csv_text))
            headers = next(csv_reader, [])
            rows = list(csv_reader)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse CSV file: {str(e)}. Please check the file format."
            )
        
        print(f"📊 CSV Analysis: {len(headers)} columns, {len(rows)} rows")
        print(f"📋 Headers: {headers}")
        
        # Validate required columns with flexible matching
        header_lower = [h.lower().strip() for h in headers]
        print(f"🔍 Looking for required columns in: {header_lower}")
        
        # Flexible column matching
        question_column = None
        response_column = None
        
        # Find question column
        question_patterns = ['question', 'original question', 'user question', 'query', 'user query']
        for pattern in question_patterns:
            if pattern in header_lower:
                question_column = pattern
                break
        
        # Find response column  
        response_patterns = ['response', 'human loop response', 'ai response', 'agent response', 'answer', 'reply']
        for pattern in response_patterns:
            if pattern in header_lower:
                response_column = pattern
                break
        
        missing_columns = []
        if not question_column:
            missing_columns.append('question (or similar: original question, query)')
        if not response_column:
            missing_columns.append('response (or similar: human loop response, answer)')
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}. Found columns: {', '.join(headers)}"
            )
        
        print(f"✅ Found question column: '{question_column}', response column: '{response_column}'")
        
        # Save file
        file_path = os.path.join(upload_directory, f"{dataset_id}_{file.filename}")
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Create dataset record
        dataset = {
            'id': dataset_id,
            'user_id': 'demo-user',
            'name': name.strip(),
            'description': description.strip() if description else None,
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': len(content),
            'status': 'completed',  # Skip processing for demo
            'progress_percentage': 100,
            'status_message': 'Upload completed - ready for analysis',
            'total_questions': len(rows),
            'processed_questions': len(rows),
            'valid_questions': len(rows),
            'invalid_questions': 0,
            'sentiment_avg': 0.45,  # Mock analysis results
            'sentiment_distribution': {'positive': 0.5, 'negative': 0.2, 'neutral': 0.3},
            'top_topics': [{'topic': 'customer service', 'score': 0.8}],
            'top_entities': [{'entity': 'Support Team', 'count': 15}],
            'top_keywords': [{'keyword': 'help', 'score': 0.9}],
            'avg_question_length': 75.0,
            'avg_response_length': 120.0,
            'avg_complexity_score': 0.4,
            'data_quality_score': 0.85,
            'organizations_count': 0,
            'organization_names': [],
            'is_public': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'processing_started_at': datetime.now().isoformat(),
            'processing_completed_at': datetime.now().isoformat(),
            'csv_headers': headers,
            'csv_encoding': used_encoding,
            'password_protected': password is not None
        }
        
        # Store in memory
        datasets_storage[dataset_id] = dataset
        
        print(f"✅ Dataset created: {name} ({len(rows)} questions)")
        
        return {
            'status': 'success',
            'data': dataset,
            'message': f'Dataset "{name}" uploaded successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/datasets/{dataset_id}")
def get_dataset(dataset_id: str):
    """Get dataset details"""
    if dataset_id not in datasets_storage:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {
        'status': 'success',
        'data': datasets_storage[dataset_id]
    }

@app.delete("/api/datasets/{dataset_id}")
def delete_dataset(dataset_id: str):
    """Delete dataset"""
    if dataset_id not in datasets_storage:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = datasets_storage[dataset_id]
    
    # Delete file if exists
    if 'file_path' in dataset and os.path.exists(dataset['file_path']):
        os.remove(dataset['file_path'])
        print(f"🗑️ Deleted file: {dataset['file_path']}")
    
    # Remove from storage
    del datasets_storage[dataset_id]
    
    print(f"✅ Dataset deleted: {dataset['name']}")
    
    return {
        'status': 'success',
        'message': f'Dataset "{dataset["name"]}" deleted successfully'
    }

@app.get("/api/datasets/{dataset_id}/analyze")
def analyze_real_dataset(dataset_id: str):
    """Analyze actual content from uploaded CSV"""
    try:
        if dataset_id not in datasets_storage:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = datasets_storage[dataset_id]
        file_path = dataset['file_path']
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        # Read and parse the actual CSV content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Use the same encoding detection as upload
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        csv_text = None
        
        for encoding in encodings_to_try:
            try:
                csv_text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if not csv_text:
            raise HTTPException(status_code=500, detail="Could not decode CSV file")
        
        # Parse CSV
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader, [])
        rows = list(csv_reader)
        
        # Find question and response columns
        header_lower = [h.lower().strip() for h in headers]
        question_col_idx = None
        response_col_idx = None
        
        question_patterns = ['question', 'original question', 'user question', 'query']
        for i, header in enumerate(header_lower):
            if any(pattern in header for pattern in question_patterns):
                question_col_idx = i
                break
        
        response_patterns = ['response', 'human loop response', 'ai response', 'answer']
        for i, header in enumerate(header_lower):
            if any(pattern in header for pattern in response_patterns):
                response_col_idx = i
                break
        
        # Extract questions and responses
        questions = []
        responses = []
        
        for row in rows[:10]:  # Analyze first 10 for preview
            if len(row) > max(question_col_idx or 0, response_col_idx or 0):
                if question_col_idx is not None:
                    questions.append(row[question_col_idx])
                if response_col_idx is not None:
                    responses.append(row[response_col_idx])
        
        # Simple word frequency analysis
        all_text = ' '.join(questions + responses).lower()
        
        # Remove common words and extract meaningful terms
        import re
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text)
        
        # Count frequencies
        word_freq = {}
        for word in words:
            if word not in ['that', 'this', 'with', 'from', 'they', 'have', 'will', 'your', 'their', 'would', 'could', 'should']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
        
        return {
            'status': 'success',
            'dataset_info': {
                'name': dataset['name'],
                'total_questions': len(rows),
                'headers': headers,
                'question_column': headers[question_col_idx] if question_col_idx is not None else None,
                'response_column': headers[response_col_idx] if response_col_idx is not None else None
            },
            'sample_analysis': {
                'sample_questions': questions[:5],
                'sample_responses': [resp[:200] + '...' for resp in responses[:5]],
                'top_words': top_words,
                'total_words_analyzed': len(words),
                'unique_words': len(word_freq)
            },
            'note': 'This is a basic analysis preview. Full NLTK analysis will provide sentiment, entities, and topics.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/datasets/{dataset_id}/questions")
def get_dataset_questions(dataset_id: str, page: int = 1, limit: int = 20):
    """Get actual questions and answers from uploaded dataset"""
    try:
        if dataset_id not in datasets_storage:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = datasets_storage[dataset_id]
        file_path = dataset['file_path']
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        # Read the CSV file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Decode with the known encoding
        csv_text = content.decode(dataset.get('csv_encoding', 'latin-1'))
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader, [])
        rows = list(csv_reader)
        
        # Find column indices
        header_lower = [h.lower().strip() for h in headers]
        question_col_idx = None
        response_col_idx = None
        timestamp_col_idx = None
        project_col_idx = None
        user_col_idx = None
        
        for i, header in enumerate(header_lower):
            if 'question' in header:
                question_col_idx = i
            elif 'response' in header:
                response_col_idx = i
            elif 'timestamp' in header:
                timestamp_col_idx = i
            elif 'project' in header:
                project_col_idx = i
            elif 'user' in header:
                user_col_idx = i
        
        # Paginate results
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_rows = rows[start_idx:end_idx]
        
        # Format questions
        questions = []
        for i, row in enumerate(paginated_rows, start=start_idx + 1):
            if len(row) > max(question_col_idx or 0, response_col_idx or 0):
                question_data = {
                    'row_number': i,
                    'question': row[question_col_idx] if question_col_idx is not None else '',
                    'response': row[response_col_idx] if response_col_idx is not None else '',
                    'timestamp': row[timestamp_col_idx] if timestamp_col_idx is not None and len(row) > timestamp_col_idx else '',
                    'project_id': row[project_col_idx] if project_col_idx is not None and len(row) > project_col_idx else '',
                    'user_id': row[user_col_idx] if user_col_idx is not None and len(row) > user_col_idx else ''
                }
                questions.append(question_data)
        
        total_questions = len(rows)
        total_pages = (total_questions + limit - 1) // limit
        
        return {
            'status': 'success',
            'data': {
                'questions': questions,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total_questions': total_questions,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                },
                'dataset_info': {
                    'id': dataset_id,
                    'name': dataset['name'],
                    'headers': headers,
                    'columns_found': {
                        'question': headers[question_col_idx] if question_col_idx is not None else None,
                        'response': headers[response_col_idx] if response_col_idx is not None else None
                    }
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get questions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get questions: {str(e)}")

# Start server
if __name__ == "__main__":
    print("🚀 Starting API Server with Dataset Upload on port 8001...")
    print("📁 Upload directory:", upload_directory)
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
