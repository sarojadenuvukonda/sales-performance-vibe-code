"""FastAPI application for sales performance analytics."""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from src.database import get_db, init_db
from src.models import SalesTransaction, Product, Region, Prediction
from src.ingestion import DataIngestor, generate_sample_data
from src.predictor import RevenuePredictor
from src.insights import InsightsGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sales Performance Analytics API",
    description="API for sales data analysis, predictions, and AI-powered insights",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models for API
class PredictionRequest(BaseModel):
    category: str
    region: str
    target_date: datetime
    quantity: int = 100

class PredictionResponse(BaseModel):
    predicted_revenue: float
    confidence_lower: float
    confidence_upper: float
    category: str
    region: str
    target_date: datetime

class InsightRequest(BaseModel):
    question: str

class InsightResponse(BaseModel):
    question: str
    answer: str
    generated_at: datetime

class SalesStats(BaseModel):
    total_revenue: float
    total_transactions: int
    avg_transaction_value: float
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and load sample data if needed."""
    logger.info("Starting up application...")
    init_db()
    
    # Check if we need to load sample data
    db = next(get_db())
    try:
        transaction_count = db.query(SalesTransaction).count()
        if transaction_count == 0:
            logger.info("No data found. Loading sample data...")
            products_df, regions_df, transactions_df = generate_sample_data()
            
            ingestor = DataIngestor(db)
            ingestor.ingest_products(products_df)
            ingestor.ingest_regions(regions_df)
            ingestor.ingest_sales_transactions(transactions_df)
            
            logger.info("Sample data loaded successfully")
            
            # Train initial model
            try:
                predictor = RevenuePredictor()
                predictor.train(db)
                logger.info("Initial model trained")
            except Exception as e:
                logger.error(f"Failed to train initial model: {e}")
    finally:
        db.close()


# Web UI endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}


# Analytics endpoints
@app.get("/api/stats", response_model=SalesStats)
async def get_stats(db: Session = Depends(get_db)):
    """Get overall sales statistics."""
    from sqlalchemy import func
    
    stats = db.query(
        func.sum(SalesTransaction.revenue).label('total_revenue'),
        func.count(SalesTransaction.id).label('total_transactions'),
        func.min(SalesTransaction.transaction_date).label('date_start'),
        func.max(SalesTransaction.transaction_date).label('date_end')
    ).first()
    
    total_revenue = float(stats.total_revenue or 0)
    total_transactions = stats.total_transactions or 0
    
    return SalesStats(
        total_revenue=total_revenue,
        total_transactions=total_transactions,
        avg_transaction_value=total_revenue / max(total_transactions, 1),
        date_range_start=stats.date_start,
        date_range_end=stats.date_end
    )


@app.get("/api/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of product categories."""
    from sqlalchemy import func, distinct
    
    categories = db.query(distinct(SalesTransaction.category)).all()
    return [cat[0] for cat in categories if cat[0]]


@app.get("/api/regions")
async def get_regions(db: Session = Depends(get_db)):
    """Get list of regions."""
    regions = db.query(Region).all()
    if not regions:
        # Fallback to distinct regions from transactions
        from sqlalchemy import distinct
        region_codes = db.query(distinct(SalesTransaction.region)).all()
        return [{'region_code': r[0], 'region_name': r[0]} for r in region_codes if r[0]]
    
    return [
        {'region_code': r.region_code, 'region_name': r.region_name}
        for r in regions
    ]


@app.get("/api/revenue/by-category")
async def revenue_by_category(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get revenue breakdown by category."""
    from sqlalchemy import func
    
    cutoff = datetime.now() - timedelta(days=days)
    
    results = db.query(
        SalesTransaction.category,
        func.sum(SalesTransaction.revenue).label('revenue'),
        func.count(SalesTransaction.id).label('transactions')
    ).filter(
        SalesTransaction.transaction_date >= cutoff
    ).group_by(
        SalesTransaction.category
    ).all()
    
    return [
        {
            'category': r.category,
            'revenue': float(r.revenue),
            'transactions': r.transactions
        }
        for r in results
    ]


@app.get("/api/revenue/by-region")
async def revenue_by_region(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get revenue breakdown by region."""
    from sqlalchemy import func
    
    cutoff = datetime.now() - timedelta(days=days)
    
    results = db.query(
        SalesTransaction.region,
        func.sum(SalesTransaction.revenue).label('revenue'),
        func.count(SalesTransaction.id).label('transactions')
    ).filter(
        SalesTransaction.transaction_date >= cutoff
    ).group_by(
        SalesTransaction.region
    ).all()
    
    return [
        {
            'region': r.region,
            'revenue': float(r.revenue),
            'transactions': r.transactions
        }
        for r in results
    ]


# Prediction endpoints
@app.post("/api/predict", response_model=PredictionResponse)
async def predict_revenue(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """Predict revenue for given parameters."""
    try:
        predictor = RevenuePredictor()
        result = predictor.predict(
            category=request.category,
            region=request.region,
            target_date=request.target_date,
            quantity=request.quantity
        )
        
        return PredictionResponse(
            predicted_revenue=result['predicted_revenue'],
            confidence_lower=result['confidence_lower'],
            confidence_upper=result['confidence_upper'],
            category=request.category,
            region=request.region,
            target_date=request.target_date
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/train")
async def train_model(db: Session = Depends(get_db)):
    """Train/retrain the prediction model."""
    try:
        predictor = RevenuePredictor()
        metrics = predictor.train(db)
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# AI Insights endpoints
@app.get("/api/insights/summary")
async def get_summary(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get AI-generated summary of sales performance."""
    try:
        generator = InsightsGenerator()
        summary = generator.generate_summary(db, days=days)
        return {
            "summary": summary,
            "period_days": days,
            "generated_at": datetime.now()
        }
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/insights/question", response_model=InsightResponse)
async def ask_question(
    request: InsightRequest,
    db: Session = Depends(get_db)
):
    """Ask a question about the sales data."""
    try:
        generator = InsightsGenerator()
        answer = generator.answer_question(db, request.question)
        return InsightResponse(
            question=request.question,
            answer=answer,
            generated_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights/trends")
async def get_trends(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get AI-powered trend analysis."""
    try:
        generator = InsightsGenerator()
        analysis = generator.analyze_trends(db, category=category)
        return {
            "analysis": analysis,
            "category": category or "All",
            "generated_at": datetime.now()
        }
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
