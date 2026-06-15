"""Tests for API endpoints."""
import pytest
from datetime import datetime, timedelta
from src.ingestion import DataIngestor, generate_sample_data


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestStatsEndpoint:
    """Test statistics endpoint."""
    
    def test_get_stats_empty_db(self, client):
        """Test stats with empty database."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] == 0
        assert data["total_transactions"] == 0
    
    def test_get_stats_with_data(self, client, test_db):
        """Test stats with sample data."""
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_products(products_df)
        ingestor.ingest_regions(regions_df)
        ingestor.ingest_sales_transactions(transactions_df)
        
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] > 0
        assert data["total_transactions"] > 0


class TestCategoriesEndpoint:
    """Test categories endpoint."""
    
    def test_get_categories(self, client, test_db):
        """Test getting categories."""
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_sales_transactions(transactions_df)
        
        response = client.get("/api/categories")
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) > 0
        assert isinstance(categories, list)


class TestRegionsEndpoint:
    """Test regions endpoint."""
    
    def test_get_regions(self, client, test_db):
        """Test getting regions."""
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_regions(regions_df)
        
        response = client.get("/api/regions")
        assert response.status_code == 200
        regions = response.json()
        assert len(regions) > 0
        assert all('region_code' in r for r in regions)


class TestRevenueEndpoints:
    """Test revenue breakdown endpoints."""
    
    def test_revenue_by_category(self, client, test_db):
        """Test revenue by category."""
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_sales_transactions(transactions_df)
        
        response = client.get("/api/revenue/by-category?days=30")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all('category' in item for item in data)
        assert all('revenue' in item for item in data)
    
    def test_revenue_by_region(self, client, test_db):
        """Test revenue by region."""
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_sales_transactions(transactions_df)
        
        response = client.get("/api/revenue/by-region?days=30")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all('region' in item for item in data)


class TestPredictionEndpoints:
    """Test prediction endpoints."""
    
    def test_train_endpoint(self, client, test_db):
        """Test model training endpoint."""
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_products(products_df)
        ingestor.ingest_regions(regions_df)
        ingestor.ingest_sales_transactions(transactions_df)
        
        response = client.post("/api/train")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "metrics" in data
    
    def test_predict_endpoint(self, client, test_db):
        """Test prediction endpoint."""
        # Setup data and train model
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_products(products_df)
        ingestor.ingest_regions(regions_df)
        ingestor.ingest_sales_transactions(transactions_df)
        
        # Train model
        client.post("/api/train")
        
        # Make prediction
        target_date = (datetime.now() + timedelta(days=7)).isoformat()
        response = client.post("/api/predict", json={
            "category": "Beverages",
            "region": "NE",
            "target_date": target_date,
            "quantity": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "predicted_revenue" in data
        assert data["predicted_revenue"] > 0
