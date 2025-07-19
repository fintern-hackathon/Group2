from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
import uuid
from app.database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    daily_transactions = relationship("DailyTransaction", back_populates="user", cascade="all, delete-orphan")
    user_total = relationship("UserTotal", back_populates="user", uselist=False, cascade="all, delete-orphan")
    monthly_snapshots = relationship("MonthlySnapshot", back_populates="user", cascade="all, delete-orphan")
    ai_suggestions = relationship("AISuggestion", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        } 