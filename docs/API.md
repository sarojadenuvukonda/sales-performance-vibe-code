# API Usage Guide

## Overview

The Sales Performance Analytics API provides endpoints for:
- Sales data analytics and reporting
- Revenue predictions using machine learning
- AI-powered insights using natural language

Base URL: `http://localhost:8000`

## Interactive Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

Currently, no authentication is required. In production, implement:
- API key authentication
- OAuth 2.0
- JWT tokens

## Endpoints

### Health Check

**GET /health**

Check if the API is running.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-06-15T10:30:00"
}
```

### Statistics

**GET /api/stats**

Get overall sales statistics.

```bash
curl http://localhost:8000/api/stats
```

Response:
```json
{
  "total_revenue": 125430.50,
  "total_transactions": 5000,
  "avg_transaction_value": 25.09,
  "date_range_start": "2023-06-15T00:00:00",
  "date_range_end": "2024-06-15T00:00:00"
}
```

### Categories

**GET /api/categories**

List all product categories.

```bash
curl http://localhost:8000/api/categories
```

Response:
```json
["Beverages", "Snacks", "Dairy", "Bakery", "Personal Care"]
```

### Regions

**GET /api/regions**

List all regions with metadata.

```bash
curl http://localhost:8000/api/regions
```

Response:
```json
[
  {
    "region_code": "NE",
    "region_name": "Northeast"
  },
  {
    "region_code": "SE",
    "region_name": "Southeast"
  }
]
```

### Revenue by Category

**GET /api/revenue/by-category?days=30**

Get revenue breakdown by category for the last N days.

Parameters:
- `days` (optional): Number of days to look back (default: 30)

```bash
curl "http://localhost:8000/api/revenue/by-category?days=30"
```

Response:
```json
[
  {
    "category": "Beverages",
    "revenue": 45230.50,
    "transactions": 1823
  },
  {
    "category": "Snacks",
    "revenue": 32145.75,
    "transactions": 1542
  }
]
```

### Revenue by Region

**GET /api/revenue/by-region?days=30**

Get revenue breakdown by region for the last N days.

Parameters:
- `days` (optional): Number of days to look back (default: 30)

```bash
curl "http://localhost:8000/api/revenue/by-region?days=30"
```

Response:
```json
[
  {
    "region": "NE",
    "revenue": 38420.30,
    "transactions": 1654
  },
  {
    "region": "SE",
    "revenue": 29310.25,
    "transactions": 1231
  }
]
```

### Predict Revenue

**POST /api/predict**

Predict revenue for specific parameters.

Request body:
```json
{
  "category": "Beverages",
  "region": "NE",
  "target_date": "2024-07-15T00:00:00",
  "quantity": 100
}
```

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Beverages",
    "region": "NE",
    "target_date": "2024-07-15T00:00:00",
    "quantity": 100
  }'
```

Response:
```json
{
  "predicted_revenue": 2543.75,
  "confidence_lower": 2156.19,
  "confidence_upper": 2931.31,
  "category": "Beverages",
  "region": "NE",
  "target_date": "2024-07-15T00:00:00"
}
```

### Train Model

**POST /api/train**

Train or retrain the prediction model with latest data.

```bash
curl -X POST http://localhost:8000/api/train
```

Response:
```json
{
  "status": "success",
  "metrics": {
    "model_version": "1.0.0",
    "train_score": 0.8542,
    "n_samples": 4875,
    "features": [
      "category_encoded",
      "region_encoded",
      "month",
      "day_of_week",
      "quarter",
      "month_sin",
      "month_cos",
      "dow_sin",
      "dow_cos",
      "quantity"
    ]
  },
  "timestamp": "2024-06-15T10:45:00"
}
```

### AI Summary

**GET /api/insights/summary?days=30**

Get AI-generated performance summary.

Parameters:
- `days` (optional): Number of days to analyze (default: 30)

```bash
curl "http://localhost:8000/api/insights/summary?days=30"
```

Response:
```json
{
  "summary": "Over the past 30 days, the company has generated $125,430 in total revenue across 5,000 transactions, with an average transaction value of $25.09. The Beverages category leads with $45,230 in revenue, followed by Snacks at $32,146. The Northeast region shows the strongest performance with $38,420 in sales. The data suggests consistent demand with seasonal patterns favoring the current period.",
  "period_days": 30,
  "generated_at": "2024-06-15T10:50:00"
}
```

### Ask Question

**POST /api/insights/question**

Ask a natural language question about the data.

Request body:
```json
{
  "question": "What are the top 3 performing product categories?"
}
```

```bash
curl -X POST http://localhost:8000/api/insights/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the top 3 performing product categories?"
  }'
```

Response:
```json
{
  "question": "What are the top 3 performing product categories?",
  "answer": "Based on the sales data, the top 3 performing product categories are:\n\n1. Beverages: $45,230 in revenue from 1,823 transactions\n2. Snacks: $32,146 in revenue from 1,542 transactions\n3. Dairy: $28,940 in revenue from 1,389 transactions\n\nBeverages clearly lead the categories, generating nearly 40% more revenue than the second-place Snacks category.",
  "generated_at": "2024-06-15T10:55:00"
}
```

### Trend Analysis

**GET /api/insights/trends?category=Beverages**

Get AI-powered trend analysis.

Parameters:
- `category` (optional): Filter by specific category

```bash
curl "http://localhost:8000/api/insights/trends?category=Beverages"
```

Response:
```json
{
  "analysis": "The Beverages category shows a positive trend over the 90-day analysis period. The average daily revenue is $502, with the recent 7-day average at $548, indicating a +9.2% growth rate. This upward trend suggests increasing consumer demand, potentially driven by seasonal factors or successful marketing initiatives. Recommendations: Consider expanding inventory for top-selling beverage SKUs and explore promotional opportunities to maintain momentum.",
  "category": "Beverages",
  "generated_at": "2024-06-15T11:00:00"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently no rate limiting implemented. For production:
- Implement rate limiting per IP/API key
- Consider: 100 requests per minute per client
- Return `429 Too Many Requests` when exceeded

## Best Practices

1. **Caching**: Cache frequently accessed data on client side
2. **Pagination**: Use `days` parameter to limit data returned
3. **Error Handling**: Always check status codes and handle errors
4. **Validation**: Validate dates and parameters before sending
5. **LLM Costs**: Use AI endpoints judiciously (requires OpenAI API)

## Example Integration

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Get statistics
response = requests.get(f"{BASE_URL}/api/stats")
stats = response.json()
print(f"Total Revenue: ${stats['total_revenue']:,.2f}")

# Make prediction
prediction_data = {
    "category": "Beverages",
    "region": "NE",
    "target_date": "2024-07-15T00:00:00",
    "quantity": 100
}
response = requests.post(f"{BASE_URL}/api/predict", json=prediction_data)
prediction = response.json()
print(f"Predicted Revenue: ${prediction['predicted_revenue']:,.2f}")

# Ask question
question_data = {"question": "What are the top regions?"}
response = requests.post(f"{BASE_URL}/api/insights/question", json=question_data)
answer = response.json()
print(f"Answer: {answer['answer']}")
```

### JavaScript

```javascript
const BASE_URL = 'http://localhost:8000';

// Get statistics
fetch(`${BASE_URL}/api/stats`)
  .then(response => response.json())
  .then(stats => {
    console.log(`Total Revenue: $${stats.total_revenue.toFixed(2)}`);
  });

// Make prediction
fetch(`${BASE_URL}/api/predict`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    category: 'Beverages',
    region: 'NE',
    target_date: '2024-07-15T00:00:00',
    quantity: 100
  })
})
  .then(response => response.json())
  .then(prediction => {
    console.log(`Predicted: $${prediction.predicted_revenue.toFixed(2)}`);
  });
```

### cURL Scripts

Save as `test_api.sh`:

```bash
#!/bin/bash
BASE_URL="http://localhost:8000"

echo "=== Health Check ==="
curl -s $BASE_URL/health | jq

echo -e "\n=== Statistics ==="
curl -s $BASE_URL/api/stats | jq

echo -e "\n=== Categories ==="
curl -s $BASE_URL/api/categories | jq

echo -e "\n=== Revenue by Category ==="
curl -s "$BASE_URL/api/revenue/by-category?days=30" | jq

echo -e "\n=== Make Prediction ==="
curl -s -X POST $BASE_URL/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Beverages",
    "region": "NE",
    "target_date": "2024-07-15T00:00:00",
    "quantity": 100
  }' | jq

echo -e "\n=== Get Summary ==="
curl -s "$BASE_URL/api/insights/summary?days=30" | jq
```

Make executable: `chmod +x test_api.sh`

## Monitoring

Monitor these metrics for production:
- Response times per endpoint
- Error rates
- Prediction accuracy over time
- LLM API usage and costs
- Database query performance

## Next Steps

1. Implement authentication
2. Add request validation
3. Implement rate limiting
4. Add response caching
5. Set up monitoring and alerts
6. Create client SDKs for common languages
