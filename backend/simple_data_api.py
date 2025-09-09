#!/usr/bin/env python3
"""
Simple endpoint to serve your actual legal data
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import csv
import io
import re
from collections import Counter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your dataset file path
YOUR_DATASET_FILE = "uploads/06a8437a-27e8-412f-a530-6cb04f7b6dc9_Brett Scrhieber questions.csv"

@app.get("/")
def root():
    return {
        "message": "Real Legal Data API",
        "dataset": "Brett Scrhieber questions",
        "endpoints": [
            "GET /questions - View actual questions", 
            "GET /wordcloud - Real word cloud from legal data"
        ]
    }

@app.get("/questions")
def get_real_questions(limit: int = 10):
    """Get actual questions from your legal dataset"""
    try:
        with open(YOUR_DATASET_FILE, 'rb') as f:
            content = f.read()
        
        csv_text = content.decode('latin-1')
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader, [])
        rows = list(csv_reader)
        
        # Extract first few questions and responses
        questions = []
        for i, row in enumerate(rows[:limit], 1):
            if len(row) >= 3:
                questions.append({
                    'number': i,
                    'timestamp': row[0],
                    'question': row[1],  # Original Question
                    'response': row[2][:300] + '...' if len(row[2]) > 300 else row[2]  # Human Loop Response (truncated)
                })
        
        return {
            'status': 'success',
            'total_questions': len(rows),
            'showing': len(questions),
            'questions': questions
        }
        
    except Exception as e:
        return {'error': str(e)}

@app.get("/wordcloud")
def get_real_wordcloud(mode: str = "all", columns: str = "all"):
    """Generate word cloud from your actual legal data with column filtering"""
    try:
        with open(YOUR_DATASET_FILE, 'rb') as f:
            content = f.read()
        
        csv_text = content.decode('latin-1')
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader, [])
        rows = list(csv_reader)
        
        # Column mapping for your legal dataset
        column_map = {
            'timestamp': 0,
            'questions': 1,      # Original Question
            'responses': 2,      # Human Loop Response  
            'project_ids': 3,    # Project Ids
            'user_ids': 4        # User Id
        }
        
        # Parse columns parameter
        if columns == "all":
            selected_columns = [1, 2]  # Questions + Responses
        elif columns == "questions":
            selected_columns = [1]     # Just questions
        elif columns == "responses":
            selected_columns = [2]     # Just responses
        else:
            # Parse comma-separated column names
            column_names = [c.strip().lower() for c in columns.split(',')]
            selected_columns = []
            for col_name in column_names:
                if col_name in column_map:
                    selected_columns.append(column_map[col_name])
                elif col_name in ['question', 'original_question']:
                    selected_columns.append(1)
                elif col_name in ['response', 'human_loop_response']:
                    selected_columns.append(2)
        
        # Extract text from selected columns only
        all_text_parts = []
        for row in rows:
            for col_idx in selected_columns:
                if len(row) > col_idx and row[col_idx].strip():
                    all_text_parts.append(row[col_idx])
        
        all_text = ' '.join(all_text_parts).lower()
        print(f"📊 Analyzing {len(selected_columns)} columns, {len(all_text_parts)} text segments")
        
        # Extract legal terms
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text)
        
        # Filter out common words and technical/system noise
        legal_stop_words = {
            # Common stop words
            'that', 'this', 'with', 'from', 'they', 'have', 'will', 'your', 'their', 
            'would', 'could', 'should', 'been', 'were', 'than', 'them', 'what', 'when', 
            'where', 'there', 'these', 'those', 'which', 'while', 'upon', 'said', 'also',
            'more', 'only', 'such', 'some', 'like', 'into', 'over', 'here', 'make', 'made',
            'take', 'come', 'back', 'time', 'well', 'then', 'know', 'just', 'work', 'first',
            'after', 'right', 'other', 'many', 'each', 'most', 'both', 'based', 'see',
            'information', 'about', 'case', 'please',
            
            # Technical/system words to always exclude (user request)
            'details', 'page', 'https', 'filevineapp', 'docwebviewer', 'docviewer', 'view', 
            'source', 'embedding', 'singletonschreiber', 'retrieved', 'matching', 'appeared',
            
            # URL components and technical artifacts
            'www', 'com', 'http', 'html', 'link', 'url', 'href', 'src', 'alt', 'title',
            'img', 'div', 'span', 'class', 'style', 'id'
        }
        
        legal_words = [w for w in words if w not in legal_stop_words and len(w) >= 4]
        
        # Get word frequencies
        word_counts = Counter(legal_words).most_common(20)
        
        # Format for frontend
        formatted_words = []
        max_count = word_counts[0][1] if word_counts else 1
        
        for word, count in word_counts:
            # Legal term sentiment
            positive_legal = ['defense', 'legal', 'professional', 'expert', 'qualified', 'evidence', 'court', 'counsel', 'attorney', 'judge', 'justice', 'trial']
            negative_legal = ['damages', 'punitive', 'violation', 'negligence', 'liability', 'fault', 'breach']
            
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
                'size': min(1.0, count / max_count),
            })
        
        return {
            'words': formatted_words,
            'insights': {
                'total_words': len(formatted_words),
                'mode': mode,
                'dataset_name': 'Brett Scrhieber Legal Questions',
                'source': 'real_legal_data',
                'sentiment_distribution': {
                    'positive': len([w for w in formatted_words if w['sentiment'] == 'positive']),
                    'negative': len([w for w in formatted_words if w['sentiment'] == 'negative']),
                    'neutral': len([w for w in formatted_words if w['sentiment'] == 'neutral'])
                }
            },
            'metadata': {
                'dataset_id': 'real-legal-data',
                'analysis_mode': mode,
                'columns_analyzed': columns,
                'selected_columns': selected_columns,
                'column_names': [headers[i] for i in selected_columns if i < len(headers)],
                'generated_at': '2025-09-09T14:50:00Z',
                'source': 'uploaded_legal_dataset',
                'total_questions': len(rows),
                'text_segments_analyzed': len(all_text_parts),
                'total_words': len(legal_words)
            }
        }
        
    except Exception as e:
        return {'error': f'Failed to analyze legal data: {str(e)}'}

@app.get("/columns")
def get_dataset_columns():
    """Get available columns from the legal dataset"""
    try:
        with open(YOUR_DATASET_FILE, 'rb') as f:
            content = f.read()
        
        csv_text = content.decode('latin-1')
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader, [])
        rows = list(csv_reader)
        
        # Sample data from each column to help user understand content
        column_info = []
        for i, header in enumerate(headers):
            sample_values = []
            for row in rows[:3]:  # Get 3 sample values
                if len(row) > i and row[i].strip():
                    sample_text = row[i][:100] + '...' if len(row[i]) > 100 else row[i]
                    sample_values.append(sample_text)
            
            # Determine if this column contains useful text content
            if i == 1:  # Original Question
                column_type = 'questions'
                description = 'User questions and legal queries'
            elif i == 2:  # Human Loop Response
                column_type = 'responses'
                description = 'Legal responses and guidance'
            elif i == 0:  # Timestamp
                column_type = 'metadata'
                description = 'Timestamp information'
            else:
                column_type = 'metadata'
                description = 'Additional metadata'
            
            column_info.append({
                'index': i,
                'name': header,
                'type': column_type,
                'description': description,
                'sample_values': sample_values,
                'recommended_for_wordcloud': column_type in ['questions', 'responses'],
                'total_non_empty': sum(1 for row in rows if len(row) > i and row[i].strip())
            })
        
        return {
            'status': 'success',
            'dataset_info': {
                'name': 'Brett Scrhieber Legal Questions',
                'total_rows': len(rows),
                'total_columns': len(headers)
            },
            'columns': column_info,
            'presets': {
                'questions_only': [1],
                'responses_only': [2], 
                'questions_and_responses': [1, 2],
                'all_text': [1, 2, 3, 4],
                'metadata_only': [0, 3, 4]
            }
        }
        
    except Exception as e:
        return {'error': f'Failed to get columns: {str(e)}'}

if __name__ == "__main__":
    import uvicorn
    print("🏛️  Starting Real Legal Data API on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
