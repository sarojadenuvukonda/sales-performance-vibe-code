# Setup and Deployment Guide

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- (Optional) Docker and Docker Compose

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd sales-performance-vibe-code
   ```

2. **Create Virtual Environment**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment (Optional)**
   ```bash
   # Create .env file for OpenAI API key
   cp .env.example .env  # If example exists
   # OR
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   ```

5. **Initialize Database**
   ```bash
   # Database is auto-initialized on first run
   # Sample data is auto-generated if database is empty
   ```

6. **Run the Application**
   ```bash
   # Development mode with auto-reload
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   
   # Production mode
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

7. **Access the Application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Docker Directly

```bash
# Build image
docker build -t sales-performance-analytics .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key-here \
  --name sales-analytics \
  sales-performance-analytics

# View logs
docker logs -f sales-analytics

# Stop container
docker stop sales-analytics
docker rm sales-analytics
```

## Testing

### Run All Tests

```bash
# Basic test run
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Run Specific Tests

```bash
# Test specific module
pytest tests/test_api.py -v

# Test specific function
pytest tests/test_api.py::TestHealthEndpoint::test_health_check -v

# Run with verbose output
pytest tests/ -vv
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME=Sales Performance Analytics
ENVIRONMENT=development  # or production
DEBUG=true

# Database
DATABASE_URL=sqlite:///./data/sales_performance.db
# For PostgreSQL: ******localhost/dbname

# OpenAI (Optional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4

# Paths
RAW_DATA_PATH=./data/raw
PROCESSED_DATA_PATH=./data/processed
```

### Database Migration to PostgreSQL

To switch from SQLite to PostgreSQL:

1. **Install PostgreSQL driver:**
   ```bash
   pip install psycopg2-binary
   ```

2. **Update DATABASE_URL in .env:**
   ```env
   DATABASE_URL=******localhost:5432/sales_db
   ```

3. **Restart application** - SQLAlchemy will auto-create tables

## Production Deployment

### Prerequisites for Production

1. PostgreSQL database
2. OpenAI API key (for LLM features)
3. Docker host or Kubernetes cluster
4. Reverse proxy (nginx/traefik)
5. SSL certificate

### Production Checklist

- [ ] Switch to PostgreSQL database
- [ ] Set `ENVIRONMENT=production` in .env
- [ ] Configure proper logging (file-based, external service)
- [ ] Set up database backups
- [ ] Configure SSL/TLS
- [ ] Set up monitoring (health checks, metrics)
- [ ] Configure CORS for your domain
- [ ] Set resource limits (CPU, memory)
- [ ] Enable rate limiting on API
- [ ] Set up log aggregation
- [ ] Configure secrets management (AWS Secrets Manager, etc.)

### Example Production Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: sales_db
      POSTGRES_USER: sales_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://sales_user:${DB_PASSWORD}@db:5432/sales_db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
```

### Kubernetes Deployment

See `k8s/` directory for example manifests (if created by project team).

## Monitoring and Logging

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Docker health
docker ps  # Check container health status
```

### Logs

```bash
# Docker logs
docker logs -f sales-analytics

# Docker Compose logs
docker-compose logs -f app

# Application logs
tail -f logs/app.log  # If file logging configured
```

### Metrics

Consider adding:
- Prometheus for metrics collection
- Grafana for visualization
- Application Performance Monitoring (APM) tool

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port 8000
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   
   # Kill the process or use different port
   uvicorn src.main:app --port 8001
   ```

2. **Database locked (SQLite)**
   - Stop all running instances
   - Delete `data/sales_performance.db-journal` if exists
   - Restart application

3. **Module not found**
   ```bash
   # Ensure virtual environment is activated
   which python  # Should point to venv/bin/python
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Docker build fails**
   ```bash
   # Clear Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker build --no-cache -t sales-performance-analytics .
   ```

5. **LLM features not working**
   - Verify OPENAI_API_KEY is set
   - Check API key has credits
   - System works without API key (shows message)

## Database Management

### Backup SQLite Database

```bash
# Create backup
cp data/sales_performance.db data/sales_performance.backup.db

# With timestamp
cp data/sales_performance.db data/sales_performance.$(date +%Y%m%d).db
```

### Reset Database

```bash
# Stop application
# Delete database
rm data/sales_performance.db

# Restart application - will auto-create with sample data
```

### Export Data

```bash
# Using sqlite3 command
sqlite3 data/sales_performance.db .dump > backup.sql

# Import
sqlite3 data/sales_performance.db < backup.sql
```

## Performance Tuning

### Database Optimization

1. **Add indexes** for common queries (already included)
2. **Use connection pooling** (SQLAlchemy handles this)
3. **Consider read replicas** for high read loads

### Application Optimization

1. **Enable caching** for ML model predictions
2. **Use async endpoints** for I/O-bound operations
3. **Implement request rate limiting**
4. **Add Redis** for session/cache management

### Docker Optimization

1. **Multi-stage builds** to reduce image size
2. **Use alpine base** images where possible
3. **Set resource limits** in docker-compose.yml

## Maintenance

### Regular Tasks

- Review and rotate logs
- Update dependencies: `pip list --outdated`
- Retrain ML model with new data: `POST /api/train`
- Backup database regularly
- Monitor disk space for logs and data

### Updates and Patches

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Rebuild Docker image
docker-compose build --no-cache

# Run tests after updates
pytest tests/ -v
```
