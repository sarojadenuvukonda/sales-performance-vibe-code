"""Database models for sales performance analytics."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class SalesTransaction(Base):
    """Sales transaction model."""
    __tablename__ = "sales_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    sku = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    revenue = Column(Float, nullable=False)
    region = Column(String, nullable=False, index=True)
    store_id = Column(String, nullable=False)
    category = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_date_region', 'transaction_date', 'region'),
        Index('idx_date_category', 'transaction_date', 'category'),
    )


class Product(Base):
    """Product master data model."""
    __tablename__ = "products"
    
    sku = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=False)
    package_size = Column(String)
    list_price = Column(Float, nullable=False)
    launch_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Region(Base):
    """Regional reference data model."""
    __tablename__ = "regions"
    
    region_code = Column(String, primary_key=True)
    region_name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    population = Column(Integer)
    avg_income = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    """Stored predictions model."""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_date = Column(DateTime, nullable=False)
    category = Column(String, nullable=False)
    region = Column(String, nullable=False)
    predicted_revenue = Column(Float, nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
