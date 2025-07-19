from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey, Text, Numeric, func
from sqlalchemy.orm import relationship
import uuid
from app.database.connection import Base

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    suggestion_text = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    gemini_prompt = Column(Text, nullable=True)
    user_score_at_time = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ai_suggestions")
    
    def __repr__(self):
        return f"<AISuggestion(id={self.id}, user_id={self.user_id}, date={self.date})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat() if self.date else None,
            "suggestion_text": self.suggestion_text,
            "is_read": self.is_read,
            "user_score_at_time": float(self.user_score_at_time) if self.user_score_at_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 