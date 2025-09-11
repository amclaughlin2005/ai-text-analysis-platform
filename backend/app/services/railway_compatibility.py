"""
Railway Database Compatibility Layer

This module provides a compatibility layer for Railway's legacy database schema.
It handles the differences between our SQLAlchemy models and Railway's actual schema.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid

logger = logging.getLogger(__name__)

class RailwayCompatibilityService:
    """Service to handle Railway database compatibility issues"""
    
    @staticmethod
    def create_minimal_dataset_record(
        session: Session,
        dataset_id: uuid.UUID,
        name: str,
        description: Optional[str],
        file_info: Dict[str, Any],
        csv_info: Dict[str, Any]
    ) -> bool:
        """
        Create a dataset record using raw SQL to avoid SQLAlchemy model mismatches
        This bypasses our Dataset model entirely and works directly with Railway's schema
        """
        try:
            # Use raw SQL to insert only the fields we know exist
            # This is the safest approach given Railway's unpredictable schema
            
            insert_sql = """
            INSERT INTO datasets (
                id, 
                name, 
                file_path, 
                file_size,
                created_at,
                updated_at
            ) VALUES (
                :id,
                :name,
                :file_path,
                :file_size,
                NOW(),
                NOW()
            )
            """
            
            params = {
                'id': str(dataset_id),
                'name': name.strip()[:255],  # Ensure it fits
                'file_path': file_info['file_path'],
                'file_size': file_info['file_size']
            }
            
            logger.info(f"🔧 Creating minimal dataset record for: {name}")
            
            result = session.execute(text(insert_sql), params)
            session.commit()
            
            logger.info(f"✅ Successfully created minimal dataset: {dataset_id}")
            return True
            
        except IntegrityError as e:
            logger.error(f"❌ Database integrity error: {e}")
            session.rollback()
            
            # Try even more minimal approach
            return RailwayCompatibilityService._create_ultra_minimal_record(
                session, dataset_id, name, file_info
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create minimal dataset: {e}")
            session.rollback()
            return False
    
    @staticmethod
    def _create_ultra_minimal_record(
        session: Session,
        dataset_id: uuid.UUID,
        name: str,
        file_info: Dict[str, Any]
    ) -> bool:
        """
        Ultra-minimal fallback - insert only ID and name
        """
        try:
            insert_sql = """
            INSERT INTO datasets (id, name) VALUES (:id, :name)
            """
            
            params = {
                'id': str(dataset_id),
                'name': name.strip()[:255]
            }
            
            logger.info(f"🆘 Creating ultra-minimal dataset record")
            
            session.execute(text(insert_sql), params)
            session.commit()
            
            logger.info(f"✅ Ultra-minimal dataset created: {dataset_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Even ultra-minimal insert failed: {e}")
            session.rollback()
            return False
    
    @staticmethod
    def update_dataset_with_safe_fields(
        session: Session,
        dataset_id: uuid.UUID,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update dataset with only safe fields that are likely to exist
        """
        try:
            # Build update SQL dynamically with only safe fields
            safe_fields = ['file_path', 'file_size', 'updated_at']
            
            set_clauses = []
            params = {'id': str(dataset_id)}
            
            for field, value in updates.items():
                if field in safe_fields:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = value
            
            if not set_clauses:
                logger.warning("⚠️ No safe fields to update")
                return True
            
            # Always update the timestamp
            set_clauses.append("updated_at = NOW()")
            
            update_sql = f"""
            UPDATE datasets 
            SET {', '.join(set_clauses)}
            WHERE id = :id
            """
            
            session.execute(text(update_sql), params)
            session.commit()
            
            logger.info(f"✅ Updated dataset with safe fields: {dataset_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update dataset: {e}")
            session.rollback()
            return False
