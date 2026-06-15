"""Tests for prediction module."""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.predictor import RevenuePredictor
from src.ingestion import DataIngestor, generate_sample_data


class TestRevenuePredictor:
    """Test revenue prediction functions."""
    
    @pytest.fixture
    def predictor_with_data(self, test_db):
        """Create a predictor with trained model."""
        # Load sample data
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_products(products_df)
        ingestor.ingest_regions(regions_df)
        ingestor.ingest_sales_transactions(transactions_df)
        
        # Train model
        predictor = RevenuePredictor(model_path="/tmp/test_model.pkl")
        predictor.train(test_db)
        
        return predictor
    
    def test_prepare_features(self):
        """Test feature preparation."""
        predictor = RevenuePredictor()
        
        df = pd.DataFrame([
            {'transaction_date': datetime(2024, 1, 15)}
        ])
        
        result = predictor.prepare_features(df)
        
        assert 'month' in result.columns
        assert 'day_of_week' in result.columns
        assert 'month_sin' in result.columns
        assert 'month_cos' in result.columns
        assert result['month'].iloc[0] == 1
    
    def test_train_model(self, test_db):
        """Test model training."""
        # Load sample data
        products_df, regions_df, transactions_df = generate_sample_data()
        ingestor = DataIngestor(test_db)
        ingestor.ingest_products(products_df)
        ingestor.ingest_regions(regions_df)
        ingestor.ingest_sales_transactions(transactions_df)
        
        predictor = RevenuePredictor(model_path="/tmp/test_model.pkl")
        metrics = predictor.train(test_db)
        
        assert 'train_score' in metrics
        assert 'n_samples' in metrics
        assert metrics['train_score'] > 0
        assert predictor.model is not None
    
    def test_predict(self, predictor_with_data):
        """Test revenue prediction."""
        result = predictor_with_data.predict(
            category='Beverages',
            region='NE',
            target_date=datetime.now() + timedelta(days=7),
            quantity=100
        )
        
        assert 'predicted_revenue' in result
        assert 'confidence_lower' in result
        assert 'confidence_upper' in result
        assert result['predicted_revenue'] > 0
        assert result['confidence_lower'] >= 0
        assert result['confidence_upper'] > result['confidence_lower']
    
    def test_batch_predict(self, predictor_with_data, test_db):
        """Test batch predictions."""
        predictions = predictor_with_data.batch_predict(
            test_db,
            categories=['Beverages', 'Snacks'],
            regions=['NE', 'SE'],
            days_ahead=7
        )
        
        assert len(predictions) == 2 * 2 * 7  # categories * regions * days
