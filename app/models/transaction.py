from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from app.database.connection import Base

class DailyTransaction(Base):
    __tablename__ = "daily_transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    income = Column(Numeric(12, 2), default=0.00)
    
    # Expense categories as separate columns
    food = Column(Numeric(12, 2), default=0.00)
    transport = Column(Numeric(12, 2), default=0.00)
    bills = Column(Numeric(12, 2), default=0.00)
    entertainment = Column(Numeric(12, 2), default=0.00)
    health = Column(Numeric(12, 2), default=0.00)
    clothing = Column(Numeric(12, 2), default=0.00)
    
    total_expenses = Column(Numeric(12, 2), default=0.00)
    net_balance = Column(Numeric(12, 2), default=0.00)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('income >= 0', name='valid_income'),
        CheckConstraint('total_expenses >= 0', name='valid_expenses'),
        CheckConstraint('food >= 0', name='valid_food'),
        CheckConstraint('transport >= 0', name='valid_transport'),
        CheckConstraint('bills >= 0', name='valid_bills'),
        CheckConstraint('entertainment >= 0', name='valid_entertainment'),
        CheckConstraint('health >= 0', name='valid_health'),
        CheckConstraint('clothing >= 0', name='valid_clothing'),
    )
    
    # Relationships
    user = relationship("User", back_populates="daily_transactions")
    
    def __repr__(self):
        return f"<DailyTransaction(id={self.id}, user_id={self.user_id}, date={self.date})>"
    
    def calculate_totals(self):
        """Calculate total expenses and net balance"""
        self.total_expenses = (
            (self.food or 0) + 
            (self.transport or 0) + 
            (self.bills or 0) + 
            (self.entertainment or 0) + 
            (self.health or 0) + 
            (self.clothing or 0)
        )
        self.net_balance = (self.income or 0) - self.total_expenses
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat() if self.date else None,
            "income": float(self.income) if self.income else 0.0,
            "food": float(self.food) if self.food else 0.0,
            "transport": float(self.transport) if self.transport else 0.0,
            "bills": float(self.bills) if self.bills else 0.0,
            "entertainment": float(self.entertainment) if self.entertainment else 0.0,
            "health": float(self.health) if self.health else 0.0,
            "clothing": float(self.clothing) if self.clothing else 0.0,
            "total_expenses": float(self.total_expenses) if self.total_expenses else 0.0,
            "net_balance": float(self.net_balance) if self.net_balance else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class UserTotal(Base):
    __tablename__ = "user_totals"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_income = Column(Numeric(15, 2), default=0.00)
    total_expenses = Column(Numeric(15, 2), default=0.00)
    days_in_system = Column(Integer, default=0)
    total_score = Column(Numeric(5, 2), default=50.00)
    tree_level = Column(Integer, default=1)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    first_transaction_date = Column(Date, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_score >= 0 AND total_score <= 100', name='valid_total_score'),
        CheckConstraint('tree_level >= 1 AND tree_level <= 10', name='valid_tree_level'),
    )
    
    # Relationships
    user = relationship("User", back_populates="user_total")
    
    def __repr__(self):
        return f"<UserTotal(user_id={self.user_id}, total_score={self.total_score}, tree_level={self.tree_level})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "user_id": str(self.user_id),
            "total_income": float(self.total_income) if self.total_income else 0.0,
            "total_expenses": float(self.total_expenses) if self.total_expenses else 0.0,
            "days_in_system": self.days_in_system,
            "total_score": float(self.total_score) if self.total_score else 0.0,
            "tree_level": self.tree_level,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "first_transaction_date": self.first_transaction_date.isoformat() if self.first_transaction_date else None
        }

class MonthlySnapshot(Base):
    __tablename__ = "monthly_snapshots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    tree_level = Column(Integer, nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
    total_income = Column(Numeric(12, 2), nullable=False)
    total_expenses = Column(Numeric(12, 2), nullable=False)
    monthly_savings = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('month >= 1 AND month <= 12', name='valid_month'),
    )
    
    # Relationships
    user = relationship("User", back_populates="monthly_snapshots")
    
    def __repr__(self):
        return f"<MonthlySnapshot(id={self.id}, user_id={self.user_id}, year={self.year}, month={self.month})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "year": self.year,
            "month": self.month,
            "tree_level": self.tree_level,
            "score": float(self.score) if self.score else 0.0,
            "total_income": float(self.total_income) if self.total_income else 0.0,
            "total_expenses": float(self.total_expenses) if self.total_expenses else 0.0,
            "monthly_savings": float(self.monthly_savings) if self.monthly_savings else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 