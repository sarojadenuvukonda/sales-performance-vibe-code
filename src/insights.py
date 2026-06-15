"""AI-powered insights using LLM."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import json

from src.config import get_settings
from src.models import SalesTransaction

logger = logging.getLogger(__name__)
settings = get_settings()


class InsightsGenerator:
    """Generate AI-powered insights using LLM."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if self.settings.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.settings.openai_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
    
    def _query_llm(self, prompt: str) -> str:
        """Query the LLM with a prompt."""
        if not self.client:
            return "LLM not configured. Please set OPENAI_API_KEY environment variable."
        
        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a data analyst helping a CPG company understand their sales performance. Provide clear, actionable insights based on the data provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return f"Unable to generate insight: {str(e)}"
    
    def generate_summary(self, db: Session, days: int = 30) -> str:
        """Generate a natural language summary of recent sales trends."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get summary statistics
        total_revenue = db.query(
            func.sum(SalesTransaction.revenue)
        ).filter(
            SalesTransaction.transaction_date >= cutoff_date
        ).scalar() or 0
        
        total_transactions = db.query(
            func.count(SalesTransaction.id)
        ).filter(
            SalesTransaction.transaction_date >= cutoff_date
        ).scalar() or 0
        
        # Top categories
        top_categories = db.query(
            SalesTransaction.category,
            func.sum(SalesTransaction.revenue).label('revenue')
        ).filter(
            SalesTransaction.transaction_date >= cutoff_date
        ).group_by(
            SalesTransaction.category
        ).order_by(
            desc('revenue')
        ).limit(5).all()
        
        # Top regions
        top_regions = db.query(
            SalesTransaction.region,
            func.sum(SalesTransaction.revenue).label('revenue')
        ).filter(
            SalesTransaction.transaction_date >= cutoff_date
        ).group_by(
            SalesTransaction.region
        ).order_by(
            desc('revenue')
        ).limit(5).all()
        
        # Prepare data for LLM
        data_summary = {
            'period': f'Last {days} days',
            'total_revenue': f'${total_revenue:,.2f}',
            'total_transactions': total_transactions,
            'avg_transaction': f'${total_revenue/max(total_transactions, 1):,.2f}',
            'top_categories': [
                {'name': cat, 'revenue': f'${rev:,.2f}'} 
                for cat, rev in top_categories
            ],
            'top_regions': [
                {'name': reg, 'revenue': f'${rev:,.2f}'} 
                for reg, rev in top_regions
            ]
        }
        
        prompt = f"""
Analyze the following sales performance data and provide a concise executive summary:

Period: {data_summary['period']}
Total Revenue: {data_summary['total_revenue']}
Total Transactions: {data_summary['total_transactions']}
Average Transaction Value: {data_summary['avg_transaction']}

Top 5 Categories by Revenue:
{json.dumps(data_summary['top_categories'], indent=2)}

Top 5 Regions by Revenue:
{json.dumps(data_summary['top_regions'], indent=2)}

Provide a 2-3 paragraph summary highlighting:
1. Overall performance
2. Key drivers of revenue
3. Notable patterns or recommendations
"""
        
        return self._query_llm(prompt)
    
    def answer_question(self, db: Session, question: str) -> str:
        """Answer a natural language question about the data."""
        # Get relevant data context
        total_revenue = db.query(
            func.sum(SalesTransaction.revenue)
        ).scalar() or 0
        
        total_transactions = db.query(
            func.count(SalesTransaction.id)
        ).scalar() or 0
        
        # Date range
        date_range = db.query(
            func.min(SalesTransaction.transaction_date),
            func.max(SalesTransaction.transaction_date)
        ).first()
        
        # Categories
        categories = db.query(
            SalesTransaction.category,
            func.sum(SalesTransaction.revenue).label('revenue'),
            func.count(SalesTransaction.id).label('count')
        ).group_by(
            SalesTransaction.category
        ).order_by(
            desc('revenue')
        ).all()
        
        # Regions
        regions = db.query(
            SalesTransaction.region,
            func.sum(SalesTransaction.revenue).label('revenue'),
            func.count(SalesTransaction.id).label('count')
        ).group_by(
            SalesTransaction.region
        ).order_by(
            desc('revenue')
        ).all()
        
        context = {
            'total_revenue': f'${total_revenue:,.2f}',
            'total_transactions': total_transactions,
            'date_range': f"{date_range[0]} to {date_range[1]}" if date_range[0] else "No data",
            'categories': [
                {'name': cat, 'revenue': f'${rev:,.2f}', 'transactions': count}
                for cat, rev, count in categories
            ],
            'regions': [
                {'name': reg, 'revenue': f'${rev:,.2f}', 'transactions': count}
                for reg, rev, count in regions
            ]
        }
        
        prompt = f"""
You are analyzing sales performance data for a CPG company. Here's the data context:

Total Revenue: {context['total_revenue']}
Total Transactions: {context['total_transactions']}
Date Range: {context['date_range']}

Categories (by revenue):
{json.dumps(context['categories'][:10], indent=2)}

Regions (by revenue):
{json.dumps(context['regions'][:10], indent=2)}

Question: {question}

Provide a clear, data-driven answer based on the information above. If the data doesn't support a definitive answer, explain what additional data would be needed.
"""
        
        return self._query_llm(prompt)
    
    def analyze_trends(self, db: Session, category: Optional[str] = None) -> str:
        """Analyze trends in sales data."""
        query = db.query(
            func.date(SalesTransaction.transaction_date).label('date'),
            func.sum(SalesTransaction.revenue).label('revenue'),
            func.count(SalesTransaction.id).label('transactions')
        )
        
        if category:
            query = query.filter(SalesTransaction.category == category)
        
        # Get last 90 days
        cutoff = datetime.now() - timedelta(days=90)
        daily_data = query.filter(
            SalesTransaction.transaction_date >= cutoff
        ).group_by(
            func.date(SalesTransaction.transaction_date)
        ).order_by('date').all()
        
        if not daily_data:
            return "Insufficient data for trend analysis."
        
        # Calculate simple statistics
        revenues = [float(d.revenue) for d in daily_data]
        avg_revenue = sum(revenues) / len(revenues)
        recent_avg = sum(revenues[-7:]) / min(7, len(revenues[-7:]))
        growth = ((recent_avg - avg_revenue) / avg_revenue * 100) if avg_revenue > 0 else 0
        
        data_summary = {
            'period': '90 days',
            'category': category or 'All categories',
            'avg_daily_revenue': f'${avg_revenue:,.2f}',
            'recent_7day_avg': f'${recent_avg:,.2f}',
            'growth_rate': f'{growth:+.1f}%',
            'total_days': len(daily_data)
        }
        
        prompt = f"""
Analyze the following sales trend data:

Period: Last {data_summary['period']}
Focus: {data_summary['category']}
Average Daily Revenue: {data_summary['avg_daily_revenue']}
Recent 7-Day Average: {data_summary['recent_7day_avg']}
Growth Rate (7-day vs 90-day avg): {data_summary['growth_rate']}
Days with Data: {data_summary['total_days']}

Provide a brief trend analysis including:
1. Overall trend direction
2. Potential explanations for the pattern
3. Recommendations for stakeholders
"""
        
        return self._query_llm(prompt)
