"""Data ingestion and validation pipeline."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import logging
from sqlalchemy.orm import Session
from src.models import SalesTransaction, Product, Region

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates and cleans data before ingestion."""
    
    @staticmethod
    def validate_sales_transaction(df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean sales transaction data."""
        logger.info(f"Validating {len(df)} sales transactions")
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Convert date columns
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # Remove rows with null critical fields
        critical_fields = ['transaction_date', 'sku', 'quantity', 'price']
        initial_count = len(df)
        df = df.dropna(subset=critical_fields)
        dropped = initial_count - len(df)
        if dropped > 0:
            logger.warning(f"Dropped {dropped} rows with missing critical fields")
        
        # Data quality checks
        df = df[df['quantity'] > 0]
        df = df[df['price'] >= 0]
        
        # Calculate revenue if not present
        if 'revenue' not in df.columns or df['revenue'].isna().any():
            df['revenue'] = df['quantity'] * df['price']
        
        # Fill missing optional fields
        if 'region' in df.columns:
            df['region'] = df['region'].fillna('UNKNOWN')
        if 'store_id' in df.columns:
            df['store_id'] = df['store_id'].fillna('UNKNOWN')
        
        logger.info(f"Validation complete: {len(df)} valid transactions")
        return df
    
    @staticmethod
    def validate_product(df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean product master data."""
        logger.info(f"Validating {len(df)} products")
        
        df = df.copy()
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['sku'], keep='last')
        if initial_count != len(df):
            logger.warning(f"Removed {initial_count - len(df)} duplicate SKUs")
        
        # Critical fields
        critical_fields = ['sku', 'name', 'category', 'brand', 'list_price']
        df = df.dropna(subset=critical_fields)
        
        # Convert dates
        if 'launch_date' in df.columns:
            df['launch_date'] = pd.to_datetime(df['launch_date'], errors='coerce')
        
        logger.info(f"Validation complete: {len(df)} valid products")
        return df
    
    @staticmethod
    def validate_region(df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean regional reference data."""
        logger.info(f"Validating {len(df)} regions")
        
        df = df.copy()
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['region_code'], keep='last')
        
        # Critical fields
        critical_fields = ['region_code', 'region_name', 'country']
        df = df.dropna(subset=critical_fields)
        
        logger.info(f"Validation complete: {len(df)} valid regions")
        return df


class DataIngestor:
    """Handles data ingestion from various sources."""
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = DataValidator()
    
    def ingest_sales_transactions(self, df: pd.DataFrame) -> int:
        """Ingest sales transaction data."""
        df = self.validator.validate_sales_transaction(df)
        
        count = 0
        for _, row in df.iterrows():
            transaction = SalesTransaction(
                transaction_date=row['transaction_date'],
                sku=row['sku'],
                quantity=int(row['quantity']),
                price=float(row['price']),
                revenue=float(row['revenue']),
                region=row.get('region', 'UNKNOWN'),
                store_id=row.get('store_id', 'UNKNOWN'),
                category=row.get('category', 'UNKNOWN')
            )
            self.db.add(transaction)
            count += 1
        
        self.db.commit()
        logger.info(f"Ingested {count} sales transactions")
        return count
    
    def ingest_products(self, df: pd.DataFrame) -> int:
        """Ingest product master data."""
        df = self.validator.validate_product(df)
        
        count = 0
        for _, row in df.iterrows():
            product = Product(
                sku=row['sku'],
                name=row['name'],
                category=row['category'],
                brand=row['brand'],
                package_size=row.get('package_size', ''),
                list_price=float(row['list_price']),
                launch_date=row.get('launch_date')
            )
            self.db.merge(product)
            count += 1
        
        self.db.commit()
        logger.info(f"Ingested {count} products")
        return count
    
    def ingest_regions(self, df: pd.DataFrame) -> int:
        """Ingest regional reference data."""
        df = self.validator.validate_region(df)
        
        count = 0
        for _, row in df.iterrows():
            region = Region(
                region_code=row['region_code'],
                region_name=row['region_name'],
                country=row['country'],
                population=row.get('population'),
                avg_income=row.get('avg_income')
            )
            self.db.merge(region)
            count += 1
        
        self.db.commit()
        logger.info(f"Ingested {count} regions")
        return count


def generate_sample_data():
    """Generate sample data for demonstration."""
    np.random.seed(42)
    
    # Generate product data
    categories = ['Beverages', 'Snacks', 'Dairy', 'Bakery', 'Personal Care']
    brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE']
    
    products = []
    for i in range(50):
        products.append({
            'sku': f'SKU{i:04d}',
            'name': f'Product {i}',
            'category': np.random.choice(categories),
            'brand': np.random.choice(brands),
            'package_size': np.random.choice(['Small', 'Medium', 'Large']),
            'list_price': round(np.random.uniform(2.99, 49.99), 2),
            'launch_date': datetime.now() - timedelta(days=np.random.randint(30, 365))
        })
    
    # Generate region data
    regions = [
        {'region_code': 'NE', 'region_name': 'Northeast', 'country': 'USA', 'population': 5000000, 'avg_income': 65000},
        {'region_code': 'SE', 'region_name': 'Southeast', 'country': 'USA', 'population': 7000000, 'avg_income': 55000},
        {'region_code': 'MW', 'region_name': 'Midwest', 'country': 'USA', 'population': 6000000, 'avg_income': 58000},
        {'region_code': 'SW', 'region_name': 'Southwest', 'country': 'USA', 'population': 4500000, 'avg_income': 52000},
        {'region_code': 'W', 'region_name': 'West', 'country': 'USA', 'population': 8000000, 'avg_income': 72000},
    ]
    
    # Generate sales transaction data
    region_codes = [r['region_code'] for r in regions]
    skus = [p['sku'] for p in products]
    
    transactions = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(5000):
        date = start_date + timedelta(days=np.random.randint(0, 365))
        sku = np.random.choice(skus)
        product = next(p for p in products if p['sku'] == sku)
        quantity = np.random.randint(1, 20)
        
        # Add some seasonality
        month_factor = 1 + 0.3 * np.sin(2 * np.pi * date.month / 12)
        price = product['list_price'] * np.random.uniform(0.8, 1.1) * month_factor
        
        transactions.append({
            'transaction_date': date,
            'sku': sku,
            'quantity': quantity,
            'price': round(price, 2),
            'revenue': round(price * quantity, 2),
            'region': np.random.choice(region_codes),
            'store_id': f'STORE{np.random.randint(1, 21):03d}',
            'category': product['category']
        })
    
    return pd.DataFrame(products), pd.DataFrame(regions), pd.DataFrame(transactions)
