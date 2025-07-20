from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import json

from app.database.connection import get_db
from app.models.user import User
from app.models.transaction import DailyTransaction, UserTotal
from app.models.suggestion import AISuggestion

# MCP Tool Response Models
class MCPToolResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    tool_name: str

class MCPUserFinancialData(BaseModel):
    user_id: str
    total_score: float
    tree_level: int
    days_in_system: int
    total_income: float
    total_expenses: float
    savings_rate: float
    avg_monthly_income: float
    category_breakdown: Dict[str, float]

class MCPRecentTransactions(BaseModel):
    user_id: str
    transactions_count: int
    last_7_days_spending: Dict[str, float]
    last_transaction_date: Optional[str]
    spending_trend: str

class MCPSuggestionSave(BaseModel):
    user_id: str
    suggestion_text: str
    ai_model: str = "gemini"
    user_score_at_time: Optional[float] = None

# MCP Server Class
class MCPServer:
    """MCP Server - Gemini AI için database tool'ları sağlar"""
    
    def __init__(self):
        self.tools = {
            "get_user_financial_data": self.get_user_financial_data,
            "get_user_score": self.get_user_score,
            "get_recent_transactions": self.get_recent_transactions,
            "save_ai_suggestion": self.save_ai_suggestion,
            "get_spending_analysis": self.get_spending_analysis
        }

    async def get_user_financial_data(self, db: AsyncSession, user_id: str) -> MCPToolResponse:
        """Tool: Kullanıcının tüm finansal verilerini getir"""
        try:
            # Get user totals
            result = await db.execute(
                select(UserTotal).where(UserTotal.user_id == user_id)
            )
            user_total = result.scalar_one_or_none()
            
            if not user_total:
                return MCPToolResponse(
                    success=False,
                    error="User not found in system",
                    tool_name="get_user_financial_data"
                )
            
            # Get transactions for category breakdown
            transactions_result = await db.execute(
                select(DailyTransaction).where(DailyTransaction.user_id == user_id)
            )
            transactions = transactions_result.scalars().all()
            
            # Calculate category breakdown
            categories = ['food', 'transport', 'bills', 'entertainment', 'health', 'clothing']
            category_breakdown = {}
            for category in categories:
                total = sum(float(getattr(t, category, 0) or 0) for t in transactions)
                category_breakdown[category] = total
            
            # Calculate savings rate
            savings_rate = 0.0
            if user_total.total_income and user_total.total_income > 0:
                savings_rate = (user_total.total_income - user_total.total_expenses) / user_total.total_income
            
            # Calculate avg monthly income
            avg_monthly_income = 0.0
            if user_total.days_in_system and user_total.days_in_system > 0:
                avg_monthly_income = (user_total.total_income or 0) / max(1, user_total.days_in_system / 30)
            
            financial_data = MCPUserFinancialData(
                user_id=user_id,
                total_score=float(user_total.total_score or 50.0),
                tree_level=user_total.tree_level or 1,
                days_in_system=user_total.days_in_system or 0,
                total_income=float(user_total.total_income or 0),
                total_expenses=float(user_total.total_expenses or 0),
                savings_rate=savings_rate,
                avg_monthly_income=avg_monthly_income,
                category_breakdown=category_breakdown
            )
            
            return MCPToolResponse(
                success=True,
                data=financial_data.dict(),
                tool_name="get_user_financial_data"
            )
            
        except Exception as e:
            return MCPToolResponse(
                success=False,
                error=str(e),
                tool_name="get_user_financial_data"
            )

    async def get_user_score(self, db: AsyncSession, user_id: str) -> MCPToolResponse:
        """Tool: Kullanıcının sadece skor bilgilerini getir"""
        try:
            result = await db.execute(
                select(UserTotal).where(UserTotal.user_id == user_id)
            )
            user_total = result.scalar_one_or_none()
            
            if not user_total:
                score_data = {
                    "user_id": user_id,
                    "total_score": 50.0,
                    "tree_level": 1,
                    "status": "new_user"
                }
            else:
                score_data = {
                    "user_id": user_id,
                    "total_score": float(user_total.total_score or 50.0),
                    "tree_level": user_total.tree_level or 1,
                    "days_in_system": user_total.days_in_system or 0,
                    "status": "existing_user"
                }
            
            return MCPToolResponse(
                success=True,
                data=score_data,
                tool_name="get_user_score"
            )
            
        except Exception as e:
            return MCPToolResponse(
                success=False,
                error=str(e),
                tool_name="get_user_score"
            )

    async def get_recent_transactions(self, db: AsyncSession, user_id: str, days: int = 7) -> MCPToolResponse:
        """Tool: Son N günün işlemlerini getir"""
        try:
            # Get recent transactions
            days_ago = datetime.now().date() - timedelta(days=days)
            result = await db.execute(
                select(DailyTransaction).where(
                    DailyTransaction.user_id == user_id,
                    DailyTransaction.date >= days_ago
                ).order_by(desc(DailyTransaction.date))
            )
            transactions = result.scalars().all()
            
            if not transactions:
                return MCPToolResponse(
                    success=True,
                    data={
                        "user_id": user_id,
                        "transactions_count": 0,
                        "last_7_days_spending": {},
                        "last_transaction_date": None,
                        "spending_trend": "no_data",
                        "message": f"No transactions found in last {days} days"
                    },
                    tool_name="get_recent_transactions"
                )
            
            # Calculate spending by category
            categories = ['food', 'transport', 'bills', 'entertainment', 'health', 'clothing']
            spending = {}
            for category in categories:
                total = sum(float(getattr(t, category, 0) or 0) for t in transactions)
                if total > 0:
                    spending[category] = total
            
            # Determine spending trend
            if len(transactions) >= 3:
                recent_avg = sum(float(t.total_expenses or 0) for t in transactions[:3]) / 3
                older_avg = sum(float(t.total_expenses or 0) for t in transactions[3:]) / max(1, len(transactions[3:]))
                
                if recent_avg > older_avg * 1.2:
                    trend = "increasing"
                elif recent_avg < older_avg * 0.8:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            recent_data = MCPRecentTransactions(
                user_id=user_id,
                transactions_count=len(transactions),
                last_7_days_spending=spending,
                last_transaction_date=transactions[0].date.isoformat() if transactions else None,
                spending_trend=trend
            )
            
            return MCPToolResponse(
                success=True,
                data=recent_data.dict(),
                tool_name="get_recent_transactions"
            )
            
        except Exception as e:
            return MCPToolResponse(
                success=False,
                error=str(e),
                tool_name="get_recent_transactions"
            )

    async def get_spending_analysis(self, db: AsyncSession, user_id: str) -> MCPToolResponse:
        """Tool: Detaylı harcama analizi"""
        try:
            # Get all transactions
            result = await db.execute(
                select(DailyTransaction).where(DailyTransaction.user_id == user_id)
                .order_by(desc(DailyTransaction.date))
            )
            transactions = result.scalars().all()
            
            if not transactions:
                return MCPToolResponse(
                    success=True,
                    data={
                        "user_id": user_id,
                        "analysis": "No spending data available",
                        "recommendations": ["Start tracking your expenses to get personalized insights"]
                    },
                    tool_name="get_spending_analysis"
                )
            
            # Calculate spending patterns
            categories = ['food', 'transport', 'bills', 'entertainment', 'health', 'clothing']
            total_expenses = sum(float(t.total_expenses or 0) for t in transactions)
            
            category_percentages = {}
            recommendations = []
            
            for category in categories:
                category_total = sum(float(getattr(t, category, 0) or 0) for t in transactions)
                if total_expenses > 0:
                    percentage = (category_total / total_expenses) * 100
                    category_percentages[category] = round(percentage, 1)
                    
                    # Generate recommendations
                    if category == 'entertainment' and percentage > 25:
                        recommendations.append(f"Entertainment expenses are {percentage:.1f}% of total - consider reducing")
                    elif category == 'food' and percentage > 40:
                        recommendations.append(f"Food expenses are {percentage:.1f}% of total - look for savings opportunities")
                    elif category == 'health' and percentage < 5:
                        recommendations.append("Consider allocating more budget for health expenses")
            
            # Calculate monthly average
            months = max(1, len(set((t.date.year, t.date.month) for t in transactions)))
            monthly_avg = total_expenses / months
            
            analysis_data = {
                "user_id": user_id,
                "total_transactions": len(transactions),
                "total_expenses": total_expenses,
                "monthly_average": round(monthly_avg, 2),
                "category_percentages": category_percentages,
                "recommendations": recommendations[:3],  # Top 3 recommendations
                "spending_pattern": "analyzed"
            }
            
            return MCPToolResponse(
                success=True,
                data=analysis_data,
                tool_name="get_spending_analysis"
            )
            
        except Exception as e:
            return MCPToolResponse(
                success=False,
                error=str(e),
                tool_name="get_spending_analysis"
            )

    async def save_ai_suggestion(self, db: AsyncSession, suggestion_data: MCPSuggestionSave) -> MCPToolResponse:
        """Tool: AI önerisini database'e kaydet"""
        try:
            # Create new suggestion
            new_suggestion = AISuggestion(
                user_id=suggestion_data.user_id,
                date=date.today(),
                suggestion_text=suggestion_data.suggestion_text,
                gemini_prompt="MCP_GENERATED",
                user_score_at_time=suggestion_data.user_score_at_time
            )
            
            db.add(new_suggestion)
            await db.commit()
            await db.refresh(new_suggestion)
            
            return MCPToolResponse(
                success=True,
                data={
                    "suggestion_id": str(new_suggestion.id),
                    "user_id": suggestion_data.user_id,
                    "created_at": new_suggestion.created_at.isoformat(),
                    "message": "AI suggestion saved successfully"
                },
                tool_name="save_ai_suggestion"
            )
            
        except Exception as e:
            await db.rollback()
            return MCPToolResponse(
                success=False,
                error=str(e),
                tool_name="save_ai_suggestion"
            )

# Global MCP Server instance
mcp_server = MCPServer() 