"""
Schema Detection Service for JSON and CSV files
Automatically detects data structure and suggests field mappings
"""

import json
import csv
import io
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, date
from collections import Counter
from sqlalchemy.orm import Session

# Optional pandas import
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from ..models.data_schema import DataSchema, SchemaField, DataType, FieldRole
from ..models.dataset import Dataset

logger = logging.getLogger(__name__)

class SchemaDetectionService:
    """Service for detecting and analyzing data schemas"""
    
    # Common field name patterns for role detection
    FIELD_PATTERNS = {
        FieldRole.PRIMARY_TEXT: [
            r'.*question.*', r'.*query.*', r'.*title.*', r'.*subject.*', 
            r'.*content.*', r'.*text.*', r'.*message.*', r'.*description.*',
            r'.*comment.*', r'.*review.*', r'.*feedback.*'
        ],
        FieldRole.SECONDARY_TEXT: [
            r'.*response.*', r'.*answer.*', r'.*reply.*', r'.*solution.*',
            r'.*context.*', r'.*details.*', r'.*explanation.*', r'.*body.*'
        ],
        FieldRole.CATEGORY: [
            r'.*category.*', r'.*type.*', r'.*status.*', r'.*priority.*',
            r'.*department.*', r'.*tag.*', r'.*label.*', r'.*class.*',
            r'.*group.*', r'.*org.*', r'.*organization.*'
        ],
        FieldRole.IDENTIFIER: [
            r'.*id$', r'.*_id$', r'^id.*', r'.*uuid.*', r'.*key.*',
            r'.*reference.*', r'.*ticket.*', r'.*number.*'
        ],
        FieldRole.TIMESTAMP: [
            r'.*date.*', r'.*time.*', r'.*timestamp.*', r'.*created.*',
            r'.*updated.*', r'.*modified.*', r'.*when.*'
        ]
    }
    
    @staticmethod
    def detect_json_schema(
        file_content: bytes,
        filename: str,
        max_sample_records: int = 100
    ) -> Dict[str, Any]:
        """Detect schema from JSON file"""
        try:
            # Try to decode as UTF-8 first
            content_str = file_content.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    content_str = file_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode file with any supported encoding")
        
        # Parse JSON
        try:
            data = json.loads(content_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Array of objects
            records = data[:max_sample_records]
            total_records = len(data)
        elif isinstance(data, dict):
            # Single object or object with array property
            if len(data) == 1 and isinstance(list(data.values())[0], list):
                # {"items": [...]} structure
                key = list(data.keys())[0]
                records = data[key][:max_sample_records]
                total_records = len(data[key])
            else:
                # Single record
                records = [data]
                total_records = 1
        else:
            raise ValueError("JSON must be an object or array")
        
        if not records:
            raise ValueError("No data records found in JSON")
        
        # Detect schema from sample records
        schema_info = SchemaDetectionService._analyze_records(records, 'json')
        schema_info['total_records'] = total_records
        schema_info['sample_data'] = records[:10]  # Store first 10 for preview
        schema_info['detected_encoding'] = 'utf-8'  # JSON is always UTF-8
        
        return schema_info
    
    @staticmethod
    def detect_csv_schema(
        file_content: bytes,
        filename: str,
        max_sample_records: int = 100
    ) -> Dict[str, Any]:
        """Detect schema from CSV file"""
        # Detect encoding
        encoding = SchemaDetectionService._detect_encoding(file_content)
        content_str = file_content.decode(encoding)
        
        # Detect delimiter
        delimiter = SchemaDetectionService._detect_delimiter(content_str)
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(content_str), delimiter=delimiter)
        
        try:
            records = []
            for i, row in enumerate(csv_reader):
                if i >= max_sample_records:
                    break
                records.append(row)
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")
        
        if not records:
            raise ValueError("No data records found in CSV")
        
        # Count total records (rewind and count)
        total_records = sum(1 for _ in csv.DictReader(io.StringIO(content_str), delimiter=delimiter))
        
        # Detect schema from sample records
        schema_info = SchemaDetectionService._analyze_records(records, 'csv')
        schema_info['total_records'] = total_records
        schema_info['sample_data'] = records[:10]
        schema_info['detected_encoding'] = encoding
        schema_info['detected_delimiter'] = delimiter
        schema_info['has_headers'] = True  # We're using DictReader, so assume headers
        
        return schema_info
    
    @staticmethod
    def _detect_encoding(file_content: bytes) -> str:
        """Detect file encoding"""
        # Try common encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                file_content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Default fallback
    
    @staticmethod
    def _detect_delimiter(content: str) -> str:
        """Detect CSV delimiter"""
        sample = content[:1024]  # Use first 1KB for detection
        
        # Common delimiters
        delimiters = [',', ';', '\t', '|']
        
        # Count occurrences in first few lines
        lines = sample.split('\n')[:5]
        delimiter_scores = {}
        
        for delimiter in delimiters:
            scores = []
            for line in lines:
                if line.strip():
                    scores.append(line.count(delimiter))
            
            if scores:
                # Check consistency (good delimiter should have similar counts across lines)
                avg_score = sum(scores) / len(scores)
                variance = sum((x - avg_score) ** 2 for x in scores) / len(scores)
                delimiter_scores[delimiter] = avg_score - variance  # Favor consistency
        
        # Return delimiter with highest score
        if delimiter_scores:
            return max(delimiter_scores.items(), key=lambda x: x[1])[0]
        
        return ','  # Default fallback
    
    @staticmethod
    def _analyze_records(records: List[Dict], file_format: str) -> Dict[str, Any]:
        """Analyze sample records to detect field types and structure"""
        if not records:
            return {}
        
        # Get all field names from all records
        all_fields = set()
        for record in records:
            all_fields.update(SchemaDetectionService._flatten_dict(record).keys())
        
        # Analyze each field
        fields_analysis = {}
        for field_name in all_fields:
            field_analysis = SchemaDetectionService._analyze_field(field_name, records)
            fields_analysis[field_name] = field_analysis
        
        # Create schema structure
        schema = {
            'file_format': file_format,
            'fields': fields_analysis,
            'field_count': len(all_fields),
            'record_sample_size': len(records),
            'confidence_score': SchemaDetectionService._calculate_confidence(fields_analysis)
        }
        
        return schema
    
    @staticmethod
    def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary to dot notation"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(SchemaDetectionService._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                # Handle array of objects - take first object as sample
                items.extend(SchemaDetectionService._flatten_dict(v[0], f"{new_key}[0]", sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def _analyze_field(field_name: str, records: List[Dict]) -> Dict[str, Any]:
        """Analyze a specific field across all records"""
        values = []
        null_count = 0
        
        # Extract values for this field from all records
        for record in records:
            flat_record = SchemaDetectionService._flatten_dict(record)
            value = flat_record.get(field_name)
            
            if value is None or value == '':
                null_count += 1
            else:
                values.append(value)
        
        if not values:
            return {
                'detected_type': DataType.TEXT.value,
                'confidence': 0.0,
                'null_count': null_count,
                'sample_values': []
            }
        
        # Detect data type
        detected_type = SchemaDetectionService._detect_data_type(values)
        
        # Detect field role
        suggested_role = SchemaDetectionService._suggest_field_role(field_name, values)
        
        # Calculate statistics
        unique_values = list(set(str(v) for v in values))
        sample_values = unique_values[:10]  # First 10 unique values
        
        # String length statistics for text fields
        str_lengths = [len(str(v)) for v in values]
        
        analysis = {
            'field_name': field_name,
            'detected_type': detected_type.value,
            'suggested_role': suggested_role.value,
            'confidence': SchemaDetectionService._calculate_field_confidence(field_name, values, detected_type),
            'sample_values': sample_values,
            'unique_count': len(unique_values),
            'null_count': null_count,
            'total_count': len(values) + null_count,
            'min_length': min(str_lengths) if str_lengths else 0,
            'max_length': max(str_lengths) if str_lengths else 0,
            'avg_length': sum(str_lengths) / len(str_lengths) if str_lengths else 0,
            'ai_suggestions': SchemaDetectionService._generate_ai_suggestions(field_name, values, detected_type)
        }
        
        return analysis
    
    @staticmethod
    def _detect_data_type(values: List[Any]) -> DataType:
        """Detect the most likely data type for a list of values"""
        if not values:
            return DataType.TEXT
        
        # Test different data types
        type_scores = {
            DataType.INTEGER: 0,
            DataType.FLOAT: 0,
            DataType.BOOLEAN: 0,
            DataType.DATE: 0,
            DataType.DATETIME: 0,
            DataType.EMAIL: 0,
            DataType.URL: 0,
            DataType.TEXT: 0
        }
        
        for value in values[:50]:  # Sample first 50 values
            str_value = str(value).strip().lower()
            
            # Integer check
            try:
                int(value)
                type_scores[DataType.INTEGER] += 1
                continue
            except (ValueError, TypeError):
                pass
            
            # Float check
            try:
                float(value)
                type_scores[DataType.FLOAT] += 1
                continue
            except (ValueError, TypeError):
                pass
            
            # Boolean check
            if str_value in ['true', 'false', '1', '0', 'yes', 'no', 'y', 'n']:
                type_scores[DataType.BOOLEAN] += 1
                continue
            
            # Email check
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str_value):
                type_scores[DataType.EMAIL] += 1
                continue
            
            # URL check
            if re.match(r'^https?://', str_value):
                type_scores[DataType.URL] += 1
                continue
            
            # Date/datetime check
            if SchemaDetectionService._is_date_string(str_value):
                if 'T' in str_value or ':' in str_value:
                    type_scores[DataType.DATETIME] += 1
                else:
                    type_scores[DataType.DATE] += 1
                continue
            
            # Default to text
            type_scores[DataType.TEXT] += 1
        
        # Return type with highest score
        best_type = max(type_scores.items(), key=lambda x: x[1])[0]
        return best_type
    
    @staticmethod
    def _is_date_string(value: str) -> bool:
        """Check if string represents a date"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value):
                return True
        return False
    
    @staticmethod
    def _suggest_field_role(field_name: str, values: List[Any]) -> FieldRole:
        """Suggest the role of a field based on name and content"""
        field_name_lower = field_name.lower()
        
        # Check field name patterns
        for role, patterns in SchemaDetectionService.FIELD_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, field_name_lower):
                    return role
        
        # Analyze content to suggest role
        if values:
            # Check if values look like categories (limited unique values)
            unique_ratio = len(set(str(v) for v in values)) / len(values)
            avg_length = sum(len(str(v)) for v in values) / len(values)
            
            if unique_ratio < 0.1 and avg_length < 50:  # Low uniqueness, short text
                return FieldRole.CATEGORY
            elif avg_length > 100:  # Long text
                return FieldRole.PRIMARY_TEXT
            elif avg_length > 20:
                return FieldRole.SECONDARY_TEXT
        
        return FieldRole.METADATA  # Default
    
    @staticmethod
    def _calculate_field_confidence(field_name: str, values: List[Any], detected_type: DataType) -> float:
        """Calculate confidence score for field type detection"""
        if not values:
            return 0.0
        
        # Base confidence from type detection consistency
        type_consistent_count = 0
        for value in values[:20]:  # Sample
            if SchemaDetectionService._value_matches_type(value, detected_type):
                type_consistent_count += 1
        
        type_confidence = type_consistent_count / min(len(values), 20)
        
        # Boost confidence for clear field name patterns
        name_boost = 0.0
        field_name_lower = field_name.lower()
        for role, patterns in SchemaDetectionService.FIELD_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, field_name_lower):
                    name_boost = 0.2
                    break
        
        return min(1.0, type_confidence + name_boost)
    
    @staticmethod
    def _value_matches_type(value: Any, data_type: DataType) -> bool:
        """Check if a value matches the expected data type"""
        try:
            if data_type == DataType.INTEGER:
                int(value)
                return True
            elif data_type == DataType.FLOAT:
                float(value)
                return True
            elif data_type == DataType.BOOLEAN:
                str_val = str(value).lower()
                return str_val in ['true', 'false', '1', '0', 'yes', 'no']
            elif data_type == DataType.EMAIL:
                return '@' in str(value)
            elif data_type == DataType.URL:
                return str(value).startswith(('http://', 'https://'))
            elif data_type in [DataType.DATE, DataType.DATETIME]:
                return SchemaDetectionService._is_date_string(str(value))
            else:
                return True  # Text always matches
        except:
            return False
    
    @staticmethod
    def _calculate_confidence(fields_analysis: Dict[str, Any]) -> float:
        """Calculate overall schema confidence"""
        if not fields_analysis:
            return 0.0
        
        confidences = [field.get('confidence', 0.0) for field in fields_analysis.values()]
        return sum(confidences) / len(confidences)
    
    @staticmethod
    def _generate_ai_suggestions(field_name: str, values: List[Any], detected_type: DataType) -> Dict[str, Any]:
        """Generate AI-powered suggestions for field configuration"""
        suggestions = {
            'recommended_for_analysis': False,
            'suggested_transformations': [],
            'data_quality_issues': []
        }
        
        if not values:
            return suggestions
        
        # Suggest for analysis if it's text content
        if detected_type == DataType.TEXT:
            avg_length = sum(len(str(v)) for v in values) / len(values)
            if avg_length > 10:  # Substantial text content
                suggestions['recommended_for_analysis'] = True
        
        # Suggest transformations
        if detected_type == DataType.TEXT:
            # Check for inconsistent casing
            casing_types = set()
            for value in values[:20]:
                str_val = str(value)
                if str_val.islower():
                    casing_types.add('lower')
                elif str_val.isupper():
                    casing_types.add('upper')
                elif str_val.istitle():
                    casing_types.add('title')
                else:
                    casing_types.add('mixed')
            
            if len(casing_types) > 1:
                suggestions['suggested_transformations'].append('normalize_case')
        
        # Check data quality
        null_ratio = sum(1 for v in values if not v or str(v).strip() == '') / len(values)
        if null_ratio > 0.2:
            suggestions['data_quality_issues'].append(f'High null rate: {null_ratio:.1%}')
        
        return suggestions
    
    @staticmethod
    async def create_schema_from_detection(
        dataset_id: str,
        schema_data: Dict[str, Any],
        db: Session
    ) -> DataSchema:
        """Create DataSchema and SchemaField records from detection results"""
        
        # Create main schema record
        schema = DataSchema(
            dataset_id=dataset_id,
            schema_name=f"Auto-detected schema",
            description="Automatically detected schema from uploaded file",
            file_format=schema_data['file_format'],
            detected_encoding=schema_data.get('detected_encoding'),
            detected_delimiter=schema_data.get('detected_delimiter'),
            has_headers=schema_data.get('has_headers', True),
            raw_schema=schema_data,
            sample_data=schema_data.get('sample_data', []),
            total_records=schema_data.get('total_records', 0),
            field_mappings={},  # Will be set by user
            analysis_config={},  # Will be set by user
            confidence_score=schema_data.get('confidence_score', 0.0)
        )
        
        db.add(schema)
        db.flush()  # Get the ID
        
        # Create field records
        fields_data = schema_data.get('fields', {})
        for field_name, field_info in fields_data.items():
            schema_field = SchemaField(
                schema_id=schema.id,
                field_name=field_name,
                field_path=field_name,  # For flat structures, path = name
                display_name=field_name.replace('_', ' ').title(),
                detected_type=DataType(field_info['detected_type']),
                suggested_type=DataType(field_info['detected_type']),
                field_role=FieldRole(field_info['suggested_role']),
                sample_values=field_info.get('sample_values', []),
                unique_count=field_info.get('unique_count', 0),
                null_count=field_info.get('null_count', 0),
                min_length=field_info.get('min_length', 0),
                max_length=field_info.get('max_length', 0),
                avg_length=field_info.get('avg_length', 0),
                ai_suggestions=field_info.get('ai_suggestions', {}),
                confidence_score=field_info.get('confidence', 0.0),
                include_in_analysis=field_info.get('suggested_role') in [
                    FieldRole.PRIMARY_TEXT.value, 
                    FieldRole.SECONDARY_TEXT.value
                ]
            )
            db.add(schema_field)
        
        db.commit()
        return schema
