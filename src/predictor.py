"""Revenue prediction and forecasting module."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
from pathlib import Path

from src.models import SalesTransaction, Prediction

logger = logging.getLogger(__name__)


class RevenuePredictor:
    """Predicts revenue using machine learning."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.category_encoder = LabelEncoder()
        self.region_encoder = LabelEncoder()
        self.model_path = model_path or "./data/processed/model.pkl"
        self.model_version = "1.0.0"
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for model training/prediction."""
        df = df.copy()
        
        # Extract time features
        df['year'] = df['transaction_date'].dt.year
        df['month'] = df['transaction_date'].dt.month
        df['day_of_week'] = df['transaction_date'].dt.dayofweek
        df['day_of_month'] = df['transaction_date'].dt.day
        df['quarter'] = df['transaction_date'].dt.quarter
        
        # Cyclical encoding for seasonal patterns
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def train(self, db: Session) -> Dict[str, Any]:
        """Train the revenue prediction model."""
        logger.info("Training revenue prediction model...")
        
        # Fetch training data
        query = db.query(SalesTransaction).filter(
            SalesTransaction.transaction_date.isnot(None)
        )
        transactions = pd.read_sql(query.statement, db.bind)
        
        if len(transactions) == 0:
            raise ValueError("No training data available")
        
        # Prepare features
        df = self.prepare_features(transactions)
        
        # Aggregate by date, category, region
        agg_df = df.groupby(['transaction_date', 'category', 'region']).agg({
            'revenue': 'sum',
            'quantity': 'sum',
            'month': 'first',
            'day_of_week': 'first',
            'quarter': 'first',
            'month_sin': 'first',
            'month_cos': 'first',
            'dow_sin': 'first',
            'dow_cos': 'first'
        }).reset_index()
        
        # Encode categorical variables
        agg_df['category_encoded'] = self.category_encoder.fit_transform(agg_df['category'])
        agg_df['region_encoded'] = self.region_encoder.fit_transform(agg_df['region'])
        
        # Prepare X and y
        feature_cols = [
            'category_encoded', 'region_encoded', 'month', 'day_of_week', 
            'quarter', 'month_sin', 'month_cos', 'dow_sin', 'dow_cos', 'quantity'
        ]
        X = agg_df[feature_cols]
        y = agg_df['revenue']
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X, y)
        
        # Calculate metrics
        train_score = self.model.score(X, y)
        
        # Save model
        self._save_model()
        
        logger.info(f"Model training complete. R² score: {train_score:.4f}")
        
        return {
            'model_version': self.model_version,
            'train_score': train_score,
            'n_samples': len(agg_df),
            'features': feature_cols
        }
    
    def predict(
        self, 
        category: str, 
        region: str, 
        target_date: datetime,
        quantity: int = 100
    ) -> Dict[str, float]:
        """Predict revenue for given parameters."""
        if self.model is None:
            self._load_model()
        
        # Prepare features
        df = pd.DataFrame([{
            'transaction_date': target_date,
            'category': category,
            'region': region,
            'quantity': quantity
        }])
        
        df = self.prepare_features(df)
        
        # Encode
        try:
            df['category_encoded'] = self.category_encoder.transform([category])[0]
            df['region_encoded'] = self.region_encoder.transform([region])[0]
        except ValueError as e:
            logger.warning(f"Unknown category/region: {e}")
            # Use default encoding
            df['category_encoded'] = 0
            df['region_encoded'] = 0
        
        # Prepare features
        feature_cols = [
            'category_encoded', 'region_encoded', 'month', 'day_of_week',
            'quarter', 'month_sin', 'month_cos', 'dow_sin', 'dow_cos', 'quantity'
        ]
        X = df[feature_cols]
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        # Estimate confidence interval (simplified)
        std_dev = prediction * 0.15  # Assume 15% standard deviation
        
        return {
            'predicted_revenue': float(prediction),
            'confidence_lower': float(max(0, prediction - 1.96 * std_dev)),
            'confidence_upper': float(prediction + 1.96 * std_dev)
        }
    
    def batch_predict(
        self,
        db: Session,
        categories: List[str],
        regions: List[str],
        days_ahead: int = 30
    ) -> List[Prediction]:
        """Generate batch predictions."""
        if self.model is None:
            self._load_model()
        
        predictions = []
        start_date = datetime.now()
        
        for category in categories:
            for region in regions:
                for days in range(1, days_ahead + 1):
                    target_date = start_date + timedelta(days=days)
                    
                    result = self.predict(category, region, target_date)
                    
                    pred = Prediction(
                        prediction_date=target_date,
                        category=category,
                        region=region,
                        predicted_revenue=result['predicted_revenue'],
                        confidence_lower=result['confidence_lower'],
                        confidence_upper=result['confidence_upper'],
                        model_version=self.model_version
                    )
                    predictions.append(pred)
        
        # Save to database
        db.bulk_save_objects(predictions)
        db.commit()
        
        logger.info(f"Generated {len(predictions)} predictions")
        return predictions
    
    def _save_model(self):
        """Save model to disk."""
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'category_encoder': self.category_encoder,
            'region_encoder': self.region_encoder,
            'version': self.model_version
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {self.model_path}")
    
    def _load_model(self):
        """Load model from disk."""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.category_encoder = model_data['category_encoder']
            self.region_encoder = model_data['region_encoder']
            self.model_version = model_data.get('version', '1.0.0')
            
            logger.info(f"Model loaded from {self.model_path}")
        except FileNotFoundError:
            logger.error(f"Model file not found: {self.model_path}")
            raise
