"""
LLM Analysis Processor using OpenAI API
Provides advanced conversation analysis, business insights, and executive summaries
"""

import json
import hashlib
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import openai
from openai import OpenAI

from ..core.config import get_settings
from ..core.logging import get_logger, log_performance
from ..models.analytics import LLMAnalysisCache
from ..core.database import get_db, DatabaseTransaction

settings = get_settings()
logger = get_logger(__name__)

class LLMProcessor:
    """
    OpenAI-powered analysis processor for advanced text insights
    """
    
    def __init__(self):
        """Initialize LLM processor with OpenAI client"""
        self.client = None
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        
        if settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"❌ OpenAI client initialization failed: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not provided - LLM features will be disabled")
    
    def is_available(self) -> bool:
        """Check if LLM processing is available"""
        return self.client is not None
    
    @log_performance(logger, "conversation_quality_analysis")
    def analyze_conversation_quality(
        self, 
        query: str, 
        context: str, 
        response: str
    ) -> Dict[str, Union[float, List[str]]]:
        """
        Comprehensive conversation quality analysis
        
        Args:
            query: User query/question
            context: Additional context provided
            response: AI/agent response
            
        Returns:
            Dictionary with quality metrics and improvement suggestions
        """
        if not self.is_available():
            return self._fallback_quality_analysis(query, context, response)
        
        try:
            prompt = self._build_quality_analysis_prompt(query, context, response)
            
            # Check cache first
            cached_result = self._get_cached_result(prompt, 'conversation_quality')
            if cached_result:
                logger.info("Using cached conversation quality analysis")
                return cached_result
            
            response_data = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert conversation quality analyst. Analyze the conversation and provide structured feedback."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse the response
            analysis_text = response_data.choices[0].message.content
            result = self._parse_quality_analysis(analysis_text)
            
            # Cache the result
            self._cache_result(prompt, result, 'conversation_quality')
            
            return result
            
        except Exception as e:
            logger.error(f"LLM conversation analysis failed: {e}")
            return self._fallback_quality_analysis(query, context, response)
    
    def _build_quality_analysis_prompt(self, query: str, context: str, response: str) -> str:
        """Build prompt for conversation quality analysis"""
        return f"""
Analyze this conversation for quality metrics:

QUERY: {query[:500]}...

CONTEXT: {context[:300] if context else 'No context provided'}...

RESPONSE: {response[:800]}...

Please analyze and provide scores (0.0 to 1.0) for:
1. Response Relevance: How well does the response address the query?
2. Query Clarity: How clear and well-formed is the original query?
3. Context Utilization: How well is the provided context used?
4. Response Completeness: How complete and thorough is the response?
5. Overall Quality: Overall conversation quality score

Also provide 3-5 specific improvement suggestions.

Format your response as JSON:
{{
    "response_relevance": 0.85,
    "query_clarity": 0.90,
    "context_utilization": 0.75,
    "response_completeness": 0.80,
    "overall_quality": 0.82,
    "improvement_suggestions": [
        "Suggestion 1",
        "Suggestion 2",
        "Suggestion 3"
    ]
}}
"""
    
    @log_performance(logger, "business_insights_extraction") 
    def extract_business_insights(self, questions_batch: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Extract business intelligence from question patterns
        
        Args:
            questions_batch: List of question dictionaries with 'question' and 'response' keys
            
        Returns:
            Dictionary with business insights and recommendations
        """
        if not self.is_available():
            return self._fallback_business_insights(questions_batch)
        
        try:
            # Prepare data for analysis
            questions_text = "\n".join([
                f"Q: {q.get('question', '')[:200]}... A: {q.get('response', '')[:200]}..."
                for q in questions_batch[:20]  # Limit to first 20 for token limits
            ])
            
            prompt = f"""
Analyze these customer service conversations and extract business insights:

{questions_text}

Please identify:
1. Common Pain Points: What are customers struggling with most?
2. Emerging Trends: What new patterns or issues are appearing?
3. Satisfaction Indicators: What suggests customer satisfaction/dissatisfaction?
4. Action Recommendations: What should the business do to improve?
5. Priority Areas: What areas need immediate attention?

Format as JSON:
{{
    "common_pain_points": ["Point 1", "Point 2", "Point 3"],
    "emerging_trends": ["Trend 1", "Trend 2", "Trend 3"],
    "satisfaction_indicators": ["Indicator 1", "Indicator 2"],
    "action_recommendations": ["Action 1", "Action 2", "Action 3"],
    "priority_areas": [
        {{"area": "Area 1", "urgency": "high", "impact": "Customer retention"}},
        {{"area": "Area 2", "urgency": "medium", "impact": "Operational efficiency"}}
    ]
}}
"""
            
            # Check cache
            cached_result = self._get_cached_result(prompt, 'business_insights')
            if cached_result:
                return cached_result
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a business intelligence analyst specializing in customer service insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            analysis_text = response.choices[0].message.content
            result = self._parse_business_insights(analysis_text)
            
            # Cache the result
            self._cache_result(prompt, result, 'business_insights')
            
            return result
            
        except Exception as e:
            logger.error(f"Business insights extraction failed: {e}")
            return self._fallback_business_insights(questions_batch)
    
    @log_performance(logger, "executive_summary_generation")
    def generate_executive_summary(self, dataset_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate high-level executive summary
        
        Args:
            dataset_analysis: Complete analysis results from the dataset
            
        Returns:
            Executive summary with key findings and recommendations
        """
        if not self.is_available():
            return self._fallback_executive_summary(dataset_analysis)
        
        try:
            # Extract key metrics for summary
            total_questions = dataset_analysis.get('total_questions', 0)
            sentiment_avg = dataset_analysis.get('sentiment_avg', 0)
            top_topics = dataset_analysis.get('top_topics', [])[:5]
            top_keywords = dataset_analysis.get('top_keywords', [])[:10]
            
            prompt = f"""
Create an executive summary for this text analysis dataset:

DATASET OVERVIEW:
- Total Questions Analyzed: {total_questions}
- Average Sentiment Score: {sentiment_avg:.2f}
- Top Topics: {', '.join([t.get('topic', '') for t in top_topics])}
- Key Terms: {', '.join([k.get('keyword', '') for k in top_keywords])}

DETAILED ANALYSIS DATA:
{json.dumps(dataset_analysis, indent=2)[:2000]}...

Please provide an executive summary including:
1. Key Findings (3-5 bullet points)
2. Sentiment Overview (brief summary)
3. Top Themes (main topics/categories)
4. Recommendations (3-4 actionable items)
5. Metrics Summary (key numbers)

Format as JSON:
{{
    "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
    "sentiment_overview": "Brief sentiment summary",
    "top_themes": ["Theme 1", "Theme 2", "Theme 3"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "metrics_summary": {{
        "total_analyzed": {total_questions},
        "sentiment_score": {sentiment_avg},
        "primary_concerns": 3,
        "satisfaction_level": "Medium"
    }}
}}
"""
            
            # Check cache
            cached_result = self._get_cached_result(prompt, 'executive_summary')
            if cached_result:
                return cached_result
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an executive analyst creating summaries for business stakeholders."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=1500
            )
            
            summary_text = response.choices[0].message.content
            result = self._parse_executive_summary(summary_text)
            
            # Cache the result
            self._cache_result(prompt, result, 'executive_summary', expires_hours=24)
            
            return result
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return self._fallback_executive_summary(dataset_analysis)
    
    # Helper methods for caching
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        return hashlib.sha256(prompt.encode()).hexdigest()
    
    def _get_cached_result(self, prompt: str, result_type: str) -> Optional[Dict]:
        """Get cached LLM result if available and valid"""
        try:
            cache_key = self._get_cache_key(prompt)
            
            with DatabaseTransaction() as db:
                cached = db.query(LLMAnalysisCache).filter_by(
                    query_hash=cache_key,
                    result_type=result_type
                ).first()
                
                if cached and cached.is_cache_valid():
                    cached.increment_hit_count()
                    db.commit()
                    logger.info(f"Cache hit for {result_type}")
                    return cached.result_data
                    
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
        
        return None
    
    def _cache_result(
        self, 
        prompt: str, 
        result: Dict, 
        result_type: str, 
        expires_hours: int = 12
    ):
        """Cache LLM result for future use"""
        try:
            cache_key = self._get_cache_key(prompt)
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
            
            with DatabaseTransaction() as db:
                cache_entry = LLMAnalysisCache(
                    query_hash=cache_key,
                    query_text=prompt[:1000],  # Truncate for storage
                    result_type=result_type,
                    result_data=result,
                    model_used=self.model,
                    expires_at=expires_at
                )
                db.add(cache_entry)
                db.commit()
                logger.info(f"Cached {result_type} result")
                
        except Exception as e:
            logger.error(f"Result caching failed: {e}")
    
    # Parsing methods
    def _parse_quality_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse quality analysis response from LLM"""
        try:
            # Try to extract JSON from the response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._fallback_quality_parsing(analysis_text)
                
        except Exception as e:
            logger.error(f"Quality analysis parsing failed: {e}")
            return self._fallback_quality_parsing(analysis_text)
    
    def _parse_business_insights(self, analysis_text: str) -> Dict[str, List[str]]:
        """Parse business insights from LLM response"""
        try:
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._fallback_business_parsing(analysis_text)
                
        except Exception as e:
            logger.error(f"Business insights parsing failed: {e}")
            return self._fallback_business_parsing(analysis_text)
    
    def _parse_executive_summary(self, summary_text: str) -> Dict[str, Any]:
        """Parse executive summary from LLM response"""
        try:
            json_start = summary_text.find('{')
            json_end = summary_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = summary_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._fallback_summary_parsing(summary_text)
                
        except Exception as e:
            logger.error(f"Executive summary parsing failed: {e}")
            return self._fallback_summary_parsing(summary_text)
    
    # Fallback methods when LLM is not available
    def _fallback_quality_analysis(self, query: str, context: str, response: str) -> Dict[str, Any]:
        """Fallback quality analysis using simple heuristics"""
        try:
            # Simple heuristic-based analysis
            query_length = len(query.split())
            response_length = len(response.split())
            context_length = len(context.split()) if context else 0
            
            # Basic scoring
            query_clarity = min(1.0, max(0.3, (query_length - 3) / 20))  # 3-23 words optimal
            response_completeness = min(1.0, max(0.2, response_length / 50))  # Longer responses generally better
            context_utilization = 0.8 if context_length > 0 else 0.3
            
            # Word overlap for relevance
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            overlap = len(query_words.intersection(response_words))
            response_relevance = min(1.0, overlap / max(1, len(query_words) * 0.3))
            
            overall_quality = (query_clarity + response_completeness + context_utilization + response_relevance) / 4
            
            return {
                'response_relevance': response_relevance,
                'query_clarity': query_clarity,
                'context_utilization': context_utilization,
                'response_completeness': response_completeness,
                'overall_quality': overall_quality,
                'improvement_suggestions': [
                    'Consider using LLM analysis for more detailed insights',
                    'Provide more specific context for better analysis',
                    'Ensure responses directly address query points'
                ],
                'analysis_method': 'heuristic_fallback'
            }
            
        except Exception as e:
            logger.error(f"Fallback quality analysis failed: {e}")
            return {
                'response_relevance': 0.5,
                'query_clarity': 0.5,
                'context_utilization': 0.5,
                'response_completeness': 0.5,
                'overall_quality': 0.5,
                'improvement_suggestions': ['Analysis failed - check input data'],
                'error': str(e)
            }
    
    def _fallback_business_insights(self, questions_batch: List[Dict]) -> Dict[str, List[str]]:
        """Fallback business insights using simple analysis"""
        try:
            # Extract common keywords and patterns
            all_questions = [q.get('question', '') for q in questions_batch]
            all_text = ' '.join(all_questions).lower()
            
            # Common pain point indicators
            pain_indicators = ['problem', 'issue', 'error', 'broken', 'not working', 'frustrated', 'difficult']
            pain_points = [indicator for indicator in pain_indicators if indicator in all_text]
            
            # Trend indicators (frequency-based)
            words = all_text.split()
            word_freq = {}
            for word in words:
                if len(word) > 4:  # Filter short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            emerging_trends = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]]
            
            return {
                'common_pain_points': pain_points or ['Data analysis in progress'],
                'emerging_trends': emerging_trends or ['Trend analysis pending'],
                'satisfaction_indicators': ['Response quality metrics needed'],
                'action_recommendations': [
                    'Implement comprehensive text analysis',
                    'Monitor sentiment trends regularly',
                    'Address common pain points identified'
                ],
                'priority_areas': [
                    {'area': 'Data collection', 'urgency': 'high', 'impact': 'Foundation for insights'},
                    {'area': 'Analysis automation', 'urgency': 'medium', 'impact': 'Operational efficiency'}
                ],
                'analysis_method': 'heuristic_fallback'
            }
            
        except Exception as e:
            logger.error(f"Fallback business insights failed: {e}")
            return {
                'common_pain_points': ['Analysis unavailable'],
                'emerging_trends': ['Trend analysis unavailable'],
                'satisfaction_indicators': ['Satisfaction analysis unavailable'],
                'action_recommendations': ['Enable LLM integration for insights'],
                'priority_areas': [],
                'error': str(e)
            }
    
    def _fallback_executive_summary(self, dataset_analysis: Dict) -> Dict[str, Any]:
        """Fallback executive summary using dataset statistics"""
        try:
            total_questions = dataset_analysis.get('total_questions', 0)
            sentiment_avg = dataset_analysis.get('sentiment_avg', 0)
            
            # Generate simple summary
            sentiment_label = 'Positive' if sentiment_avg > 0.1 else 'Negative' if sentiment_avg < -0.1 else 'Neutral'
            
            return {
                'key_findings': [
                    f'Analyzed {total_questions} customer interactions',
                    f'Overall sentiment is {sentiment_label.lower()} ({sentiment_avg:.2f})',
                    'Detailed analysis requires LLM integration'
                ],
                'sentiment_overview': f'Average sentiment score of {sentiment_avg:.2f} indicates {sentiment_label.lower()} customer feedback',
                'top_themes': ['Theme analysis pending LLM integration'],
                'recommendations': [
                    'Enable OpenAI integration for detailed insights',
                    'Monitor sentiment trends over time',
                    'Implement automated analysis workflows'
                ],
                'metrics_summary': {
                    'total_analyzed': total_questions,
                    'sentiment_score': sentiment_avg,
                    'analysis_completeness': 'Basic',
                    'insight_level': 'Statistical only'
                },
                'analysis_method': 'statistical_fallback'
            }
            
        except Exception as e:
            logger.error(f"Fallback executive summary failed: {e}")
            return {
                'key_findings': ['Summary generation failed'],
                'sentiment_overview': 'Analysis unavailable',
                'top_themes': [],
                'recommendations': ['Check system configuration'],
                'metrics_summary': {},
                'error': str(e)
            }
    
    # Simple fallback parsers
    def _fallback_quality_parsing(self, text: str) -> Dict[str, Any]:
        """Simple fallback parsing for quality analysis"""
        return {
            'response_relevance': 0.7,
            'query_clarity': 0.7,
            'context_utilization': 0.7,
            'response_completeness': 0.7,
            'overall_quality': 0.7,
            'improvement_suggestions': ['Enable proper LLM integration for detailed analysis'],
            'analysis_method': 'fallback_parsing'
        }
    
    def _fallback_business_parsing(self, text: str) -> Dict[str, List[str]]:
        """Simple fallback parsing for business insights"""
        return {
            'common_pain_points': ['Analysis requires LLM integration'],
            'emerging_trends': ['Trend detection pending'],
            'satisfaction_indicators': ['Sentiment analysis available'],
            'action_recommendations': ['Configure OpenAI API for insights'],
            'priority_areas': [],
            'analysis_method': 'fallback_parsing'
        }
    
    def _fallback_summary_parsing(self, text: str) -> Dict[str, Any]:
        """Simple fallback parsing for executive summary"""
        return {
            'key_findings': ['Summary requires LLM integration'],
            'sentiment_overview': 'Basic sentiment analysis available',
            'top_themes': ['Theme analysis pending'],
            'recommendations': ['Enable OpenAI integration'],
            'metrics_summary': {},
            'analysis_method': 'fallback_parsing'
        }

# Global processor instance
_llm_processor = None

def get_llm_processor() -> LLMProcessor:
    """Get global LLM processor instance (singleton)"""
    global _llm_processor
    if _llm_processor is None:
        _llm_processor = LLMProcessor()
    return _llm_processor
