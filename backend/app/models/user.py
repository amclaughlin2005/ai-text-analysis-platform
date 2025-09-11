"""
User model for Clerk integration
Stores user information and preferences
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class User(Base):
    """User model with Clerk integration"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Clerk integration
    clerk_user_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Basic user information
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    profile_image_url = Column(Text, nullable=True)
    
    # User preferences and settings
    preferences = Column(JSON, nullable=True, default=dict)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Subscription and usage information
    subscription_tier = Column(String(50), default="free", nullable=False)
    usage_quota = Column(JSON, nullable=True, default=dict)  # Store usage limits and current usage
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships (temporarily disabled for Railway compatibility)
    # datasets = relationship("Dataset", back_populates="user", cascade="all, delete-orphan")
    # analysis_jobs = relationship("AnalysisJob", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": str(self.id),
            "clerk_user_id": self.clerk_user_id,
            "email": self.email,
            "name": self.name,
            "profile_image_url": self.profile_image_url,
            "preferences": self.preferences,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "subscription_tier": self.subscription_tier,
            "usage_quota": self.usage_quota,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    @classmethod
    def from_clerk_user(cls, clerk_user_data):
        """Create User instance from Clerk user data"""
        return cls(
            clerk_user_id=clerk_user_data.get("id"),
            email=clerk_user_data.get("email_addresses", [{}])[0].get("email_address", ""),
            name=f"{clerk_user_data.get('first_name', '')} {clerk_user_data.get('last_name', '')}".strip(),
            profile_image_url=clerk_user_data.get("profile_image_url"),
            is_verified=clerk_user_data.get("email_addresses", [{}])[0].get("verification", {}).get("status") == "verified"
        )
    
    def update_preferences(self, new_preferences: dict):
        """Update user preferences"""
        if self.preferences is None:
            self.preferences = {}
        self.preferences.update(new_preferences)
    
    def get_preference(self, key: str, default=None):
        """Get specific preference value"""
        if self.preferences is None:
            return default
        return self.preferences.get(key, default)
    
    def update_usage_quota(self, resource: str, amount: int):
        """Update usage quota for a specific resource"""
        if self.usage_quota is None:
            self.usage_quota = {}
        
        current_usage = self.usage_quota.get(resource, 0)
        self.usage_quota[resource] = current_usage + amount
    
    def check_quota_limit(self, resource: str, requested_amount: int = 1) -> bool:
        """Check if user can use a specific resource within their quota"""
        if self.subscription_tier == "unlimited":
            return True
        
        # Define quota limits by subscription tier
        quota_limits = {
            "free": {
                "datasets": 5,
                "questions_per_month": 1000,
                "api_calls_per_day": 100
            },
            "pro": {
                "datasets": 50,
                "questions_per_month": 10000,
                "api_calls_per_day": 1000
            },
            "enterprise": {
                "datasets": 500,
                "questions_per_month": 100000,
                "api_calls_per_day": 10000
            }
        }
        
        tier_limits = quota_limits.get(self.subscription_tier, quota_limits["free"])
        limit = tier_limits.get(resource, 0)
        
        if limit == 0:  # No limit defined
            return True
        
        current_usage = self.usage_quota.get(resource, 0) if self.usage_quota else 0
        return (current_usage + requested_amount) <= limit
    
    def reset_usage_quota(self, resource: str = None):
        """Reset usage quota for specific resource or all resources"""
        if self.usage_quota is None:
            self.usage_quota = {}
        
        if resource:
            self.usage_quota[resource] = 0
        else:
            self.usage_quota = {}
    
    @property
    def is_premium_user(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_tier in ["pro", "enterprise", "unlimited"]
    
    @property
    def full_name(self) -> str:
        """Get full name or email if name not available"""
        return self.name if self.name else self.email.split("@")[0]
