# Architecture Decision Record: Data Pipeline Design

**Status:** Accepted  
**Date:** 2024-06-15  
**Decision Makers:** Engineering Team

## Context

The system needs to handle realistic CPG data with quality issues (nulls, inconsistent formats, duplicates, late arrivals). We need a data pipeline that validates, cleans, and stores data from multiple sources (transactions, products, regions).

## Decision

Implement a validation-first ingestion pipeline with the following design:

```
Raw Data → Validator → Ingestor → Database
             ↓
        Quality Logs
```

### Components

1. **DataValidator:** Stateless validation class with methods per entity type
2. **DataIngestor:** Manages database sessions and orchestrates ingestion
3. **Models:** SQLAlchemy ORM models with appropriate indexes
4. **Sample Data Generator:** Creates realistic test data with quality issues

### Validation Strategy

- **Critical fields:** Null values cause row rejection (logged)
- **Optional fields:** Filled with defaults (e.g., 'UNKNOWN')
- **Duplicates:** De-duplicated by key (keep last)
- **Data types:** Coerced where possible, reject invalid
- **Business rules:** Quantity > 0, Price >= 0, etc.

### Database Schema

```
sales_transactions
  - Composite indexes on (date, region) and (date, category)
  - Revenue pre-calculated and stored

products
  - SKU as primary key
  - Updated_at for SCD handling

regions
  - Region_code as primary key
  - Demographics for enrichment

predictions
  - Separate table for storing forecasts
  - Indexed on created_at for versioning
```

## Rationale

### Validation-First Approach
- Fails fast on bad data
- Provides clear error messages
- Separates validation logic from ingestion
- Easy to test independently

### Pre-calculated Revenue
- **Pro:** Faster queries, simpler analytics
- **Con:** Slight denormalization
- **Decision:** Worth the trade-off for read performance

### Composite Indexes
- **Pro:** Speeds up common query patterns (time-series by category/region)
- **Con:** Increases write time and storage
- **Decision:** Read-heavy workload justifies cost

### Separate Predictions Table
- **Pro:** Model versioning, A/B testing, audit trail
- **Con:** Additional storage
- **Decision:** Essential for production ML systems

### Sample Data Generator
- **Pro:** Self-contained demo, reproducible tests
- **Con:** Not production data
- **Decision:** Critical for skeleton - allows system to work without external data

## Consequences

### Positive
- Clear separation of concerns
- Easy to test each component
- Logging provides visibility into data quality
- Schema supports common analytics patterns
- Sample data makes system immediately usable

### Negative
- Validation adds latency to ingestion (acceptable for batch)
- Pre-calculated fields require maintenance if business logic changes
- Sample data may not reflect all real-world edge cases

### Trade-offs Made
1. **Simplicity over flexibility:** Fixed validation rules rather than configurable
2. **Performance over purity:** Pre-calculated revenue vs. on-query calculation
3. **Demo-ready over production-ready:** Sample data generator vs. external data connectors

## Extension Points for Project Team

1. **Add validation rules:** Extend DataValidator methods
2. **Add data sources:** 
   - Create new model in models.py
   - Add validate_{entity} method to DataValidator
   - Add ingest_{entity} method to DataIngestor
3. **Schema evolution:**
   - Use Alembic for migrations
   - SQLAlchemy handles DDL changes
4. **Real-time ingestion:**
   - Current design supports batch
   - Can add streaming ingestion using same validation layer
5. **Data quality monitoring:**
   - Logging foundation in place
   - Add metrics collection to validators

## Rejected Alternatives

### Alternative 1: Schema-on-Read
- **Idea:** Store raw data as-is, validate on query
- **Rejected:** Pushes complexity to analytics layer, harder to debug

### Alternative 2: External ETL Tool (Airflow, dbt)
- **Idea:** Use dedicated ETL framework
- **Rejected:** Overkill for skeleton, adds operational complexity

### Alternative 3: NoSQL Database
- **Idea:** Use MongoDB/DynamoDB for flexibility
- **Rejected:** Relational model fits CPG transaction data; SQL better for analytics

### Alternative 4: Star Schema with Fact/Dimension Tables
- **Idea:** Full data warehouse design
- **Rejected:** Over-engineering for current scale; can evolve there if needed

## Assumptions and Constraints

### Assumptions
- Batch ingestion is acceptable (no real-time requirement)
- Data volume fits single-node database
- Business rules are relatively stable

### Constraints
- Must handle realistic data quality issues
- Must be easy for project team to extend
- Must work without external data sources (for demo)

## Success Metrics

- ✅ All sample data loads successfully
- ✅ Invalid rows are logged and rejected
- ✅ Queries return in < 100ms for typical analytics
- ✅ New data source can be added in < 2 hours

## References

- CPG industry data patterns: Typical retail transaction schemas
- SQLAlchemy best practices: https://docs.sqlalchemy.org/
- Data validation patterns: "Data Quality: The Accuracy Dimension" (Redman)
