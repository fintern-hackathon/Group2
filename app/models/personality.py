from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json

from app.database.connection import Base

class UserFinancialPersonality(Base):
    __tablename__ = "user_financial_personalities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Personality Type
    personality_type = Column(String, nullable=True)  # 'akilli_baykus', 'ozgur_kelebegi', etc.
    personality_name = Column(String, nullable=True)  # Turkish display name
    confidence_score = Column(Float, default=0.0)     # 0.0-1.0
    
    # Pattern Analysis Results
    traits_json = Column(Text, nullable=True)          # JSON string of traits
    pattern_analysis_json = Column(Text, nullable=True) # JSON string of patterns
    
    # Metadata
    analysis_count = Column(Integer, default=0)        # Kaç kez analiz edildi
    last_analysis_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_traits(self, traits_dict):
        """Traits dictionary'yi JSON string olarak kaydet"""
        self.traits_json = json.dumps(traits_dict, ensure_ascii=False)
    
    def get_traits(self):
        """JSON string'i traits dictionary olarak döndür"""
        if self.traits_json:
            return json.loads(self.traits_json)
        return {}
    
    def set_pattern_analysis(self, pattern_dict):
        """Pattern analysis dictionary'yi JSON string olarak kaydet"""
        self.pattern_analysis_json = json.dumps(pattern_dict, ensure_ascii=False)
    
    def get_pattern_analysis(self):
        """JSON string'i pattern analysis dictionary olarak döndür"""
        if self.pattern_analysis_json:
            return json.loads(self.pattern_analysis_json)
        return {}
    
    def to_dict(self):
        """Model'i dictionary'e çevir"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'personality_type': self.personality_type,
            'personality_name': self.personality_name,
            'confidence_score': self.confidence_score,
            'traits': self.get_traits(),
            'pattern_analysis': self.get_pattern_analysis(),
            'analysis_count': self.analysis_count,
            'last_analysis_date': self.last_analysis_date.isoformat() if self.last_analysis_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 