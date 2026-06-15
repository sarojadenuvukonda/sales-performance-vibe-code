# Sales Performance Analytics System

An AI-powered sales performance analytics platform for CPG companies, featuring data ingestion, ML-based revenue predictions, and LLM-powered insights.

## 🎯 Overview

This system provides:
- **Data Foundation:** Validated ingestion pipeline for sales transactions, products, and regions
- **Predictive Intelligence:** ML-based revenue forecasting with confidence intervals
- **AI Insights:** Natural language summaries and Q&A using LLM
- **REST API:** Comprehensive API for all analytics and predictions
- **Web Interface:** Simple, interactive dashboard for business users

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose (recommended)
- OR Python 3.11+ and pip

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd sales-performance-vibe-code

# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Web UI: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Clone the repository
git clone <repository-url>
cd sales-performance-vibe-code

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn src.main:app --reload

# Access the application
# Web UI: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Optional: Configure LLM Integration

For AI-powered insights (optional):

```bash
# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Or set environment variable
export OPENAI_API_KEY=your-key-here
```

**Note:** The system works without an API key. LLM features will show a graceful message if not configured.

## 📊 Features

### Data Management
- **Automated Sample Data:** System generates realistic sample data on first run
- **Data Validation:** Handles nulls, duplicates, and data quality issues
- **Multi-Source Support:** Products, regions, and transactions with proper relationships

### Predictive Analytics
- **Revenue Forecasting:** Predict revenue by category, region, and date
- **Confidence Intervals:** 95% confidence ranges for all predictions
- **Model Training API:** Retrain models with latest data

### AI-Powered Insights
- **Performance Summaries:** Natural language summaries of sales trends
- **Question Answering:** Ask questions about your data in plain English
- **Trend Analysis:** AI-generated insights on sales patterns

### Web Interface
- **Dashboard:** Real-time sales statistics
- **Interactive Forms:** Easy prediction and insight generation
- **Tabbed Navigation:** Insights, predictions, and analytics views

## 🏗️ Architecture

```
┌─────────────────┐
│  Web Interface  │
│  (HTML/JS)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   REST API      │
└────────┬────────┘
         │
    ┌────┴──────────┬───────────┬──────────┐
    ▼               ▼           ▼          ▼
┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐
│ Data    │  │ ML Model │  │ LLM    │  │ Database │
│ Ingestor│  │ (sklearn)│  │ Client │  │ (SQLite) │
└─────────┘  └──────────┘  └────────┘  └──────────┘
```

### Key Components

- **src/main.py:** FastAPI application and API endpoints
- **src/models.py:** SQLAlchemy database models
- **src/ingestion.py:** Data validation and ingestion pipeline
- **src/predictor.py:** Revenue prediction ML model
- **src/insights.py:** LLM-powered insights generator
- **src/database.py:** Database connection and session management
- **src/config.py:** Configuration management

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## 🔧 API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Key Endpoints

#### Analytics
- `GET /api/stats` - Overall sales statistics
- `GET /api/categories` - List product categories
- `GET /api/regions` - List regions
- `GET /api/revenue/by-category` - Revenue breakdown by category
- `GET /api/revenue/by-region` - Revenue breakdown by region

#### Predictions
- `POST /api/predict` - Predict revenue for given parameters
- `POST /api/train` - Train/retrain the ML model

#### AI Insights
- `GET /api/insights/summary` - Generate performance summary
- `POST /api/insights/question` - Ask a question about the data
- `GET /api/insights/trends` - Analyze sales trends

## 📁 Project Structure

```
sales-performance-vibe-code/
├── src/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # Database connection
│   ├── config.py            # Configuration
│   ├── ingestion.py         # Data ingestion pipeline
│   ├── predictor.py         # ML prediction model
│   └── insights.py          # LLM insights generator
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_api.py          # API tests
│   ├── test_ingestion.py   # Data ingestion tests
│   └── test_predictor.py   # Prediction tests
├── templates/
│   └── index.html           # Web interface
├── static/                  # Static files
├── data/
│   ├── raw/                 # Raw data files
│   └── processed/           # Processed data and models
├── docs/
│   └── adr/                 # Architecture Decision Records
│       ├── 001-technology-stack.md
│       └── 002-data-pipeline.md
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🎓 Extension Points

The architecture is designed for easy extension:

1. **Add New Data Sources:**
   - Add model in `src/models.py`
   - Add validation in `src/ingestion.py`
   - Create corresponding API endpoints

2. **Improve ML Model:**
   - Replace implementation in `src/predictor.py`
   - Interface remains the same
   - Consider: XGBoost, Prophet, ARIMA

3. **Switch Database:**
   - Update connection string in `src/config.py`
   - SQLAlchemy handles the rest

4. **Replace LLM Provider:**
   - Modify client initialization in `src/insights.py`
   - Or use local model (Ollama, etc.)

5. **Enhance Frontend:**
   - Replace `templates/index.html` with React/Vue
   - Use existing API endpoints

## 🔒 Security Considerations

- API keys should be stored in environment variables (never commit)
- Input validation on all API endpoints via Pydantic
- SQL injection protection via SQLAlchemy ORM
- CORS configured for production deployment

## 📈 Performance Considerations

- Database indexes on common query patterns
- Pre-calculated revenue fields for faster analytics
- Model caching (load once, reuse)
- Async endpoints for LLM calls

## 🚢 CI/CD Pipeline

GitHub Actions workflow includes:
- **Testing:** Automated test suite on every push
- **Linting:** Code quality checks (flake8, black, isort)
- **Docker Build:** Container build and health check
- **Security Scanning:** Dependency and code security checks

## 📚 Documentation

- **Architecture Decision Records:** See `docs/adr/`
- **API Documentation:** Available at `/docs` when running
- **Code Comments:** Comprehensive docstrings throughout

## 🤝 Contributing

This is a skeleton project designed for handoff. The project team should:

1. Review Architecture Decision Records in `docs/adr/`
2. Examine extension points in this README
3. Run tests to understand system behavior
4. Start with small enhancements before major changes

## 📝 License

[Add appropriate license]

## 🆘 Support

For questions or issues, please refer to:
1. API documentation at `/docs`
2. Architecture Decision Records in `docs/adr/`
3. Test files for usage examples
4. Inline code documentation