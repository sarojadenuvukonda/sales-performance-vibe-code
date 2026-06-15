"""Tests for data ingestion module."""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.ingestion import DataValidator, DataIngestor, generate_sample_data
from src.models import SalesTransaction, Product, Region


class TestDataValidator:
    """Test data validation functions."""
    
    def test_validate_sales_transaction_basic(self):
        """Test basic sales transaction validation."""
        df = pd.DataFrame([
            {
                'transaction_date': '2024-01-01',
                'sku': 'SKU001',
                'quantity': 5,
                'price': 10.0,
                'revenue': 50.0,
                'region': 'NE',
                'store_id': 'STORE001'
            }
        ])
        
        result = DataValidator.validate_sales_transaction(df)
        assert len(result) == 1
        assert result['revenue'].iloc[0] == 50.0
    
    def test_validate_sales_transaction_missing_critical_fields(self):
        """Test handling of missing critical fields."""
        df = pd.DataFrame([
            {'sku': 'SKU001', 'quantity': 5},  # Missing price and date
            {'transaction_date': '2024-01-01', 'sku': 'SKU002', 'quantity': 3, 'price': 10.0}
        ])
        
        result = DataValidator.validate_sales_transaction(df)
        assert len(result) == 1  # Only valid row
    
    def test_validate_sales_transaction_calculates_revenue(self):
        """Test revenue calculation when missing."""
        df = pd.DataFrame([
            {
                'transaction_date': '2024-01-01',
                'sku': 'SKU001',
                'quantity': 5,
                'price': 10.0,
                'region': 'NE',
                'store_id': 'STORE001'
            }
        ])
        
        result = DataValidator.validate_sales_transaction(df)
        assert result['revenue'].iloc[0] == 50.0
    
    def test_validate_product_removes_duplicates(self):
        """Test duplicate SKU removal."""
        df = pd.DataFrame([
            {'sku': 'SKU001', 'name': 'Product 1', 'category': 'Cat1', 'brand': 'Brand1', 'list_price': 10.0},
            {'sku': 'SKU001', 'name': 'Product 1 Updated', 'category': 'Cat1', 'brand': 'Brand1', 'list_price': 12.0},
        ])
        
        result = DataValidator.validate_product(df)
        assert len(result) == 1
        assert result['list_price'].iloc[0] == 12.0  # Should keep last
    
    def test_validate_region_basic(self):
        """Test basic region validation."""
        df = pd.DataFrame([
            {'region_code': 'NE', 'region_name': 'Northeast', 'country': 'USA'}
        ])
        
        result = DataValidator.validate_region(df)
        assert len(result) == 1


class TestDataIngestor:
    """Test data ingestion functions."""
    
    def test_ingest_sales_transactions(self, test_db):
        """Test sales transaction ingestion."""
        ingestor = DataIngestor(test_db)
        
        df = pd.DataFrame([
            {
                'transaction_date': datetime.now(),
                'sku': 'SKU001',
                'quantity': 5,
                'price': 10.0,
                'revenue': 50.0,
                'region': 'NE',
                'store_id': 'STORE001',
                'category': 'Beverages'
            }
        ])
        
        count = ingestor.ingest_sales_transactions(df)
        assert count == 1
        
        transactions = test_db.query(SalesTransaction).all()
        assert len(transactions) == 1
        assert transactions[0].sku == 'SKU001'
    
    def test_ingest_products(self, test_db):
        """Test product ingestion."""
        ingestor = DataIngestor(test_db)
        
        df = pd.DataFrame([
            {
                'sku': 'SKU001',
                'name': 'Product 1',
                'category': 'Beverages',
                'brand': 'BrandA',
                'list_price': 10.0
            }
        ])
        
        count = ingestor.ingest_products(df)
        assert count == 1
        
        products = test_db.query(Product).all()
        assert len(products) == 1
        assert products[0].name == 'Product 1'
    
    def test_ingest_regions(self, test_db):
        """Test region ingestion."""
        ingestor = DataIngestor(test_db)
        
        df = pd.DataFrame([
            {
                'region_code': 'NE',
                'region_name': 'Northeast',
                'country': 'USA',
                'population': 5000000
            }
        ])
        
        count = ingestor.ingest_regions(df)
        assert count == 1
        
        regions = test_db.query(Region).all()
        assert len(regions) == 1
        assert regions[0].region_code == 'NE'


class TestGenerateSampleData:
    """Test sample data generation."""
    
    def test_generate_sample_data(self):
        """Test sample data generation."""
        products_df, regions_df, transactions_df = generate_sample_data()
        
        assert len(products_df) == 50
        assert len(regions_df) == 5
        assert len(transactions_df) == 5000
        
        # Check required columns
        assert 'sku' in products_df.columns
        assert 'region_code' in regions_df.columns
        assert 'transaction_date' in transactions_df.columns
        assert 'revenue' in transactions_df.columns
