# Architecture Decision Record: Technology Stack Selection

**Status:** Accepted  
**Date:** 2024-06-15  
**Decision Makers:** Engineering Team

## Context

We need to build a sales performance analytics system that includes data ingestion, ML-based predictions, LLM-powered insights, and a user-friendly interface. The system must be containerized, testable, and maintainable by a project team.

## Decision

We will use the following technology stack:

1. **Backend Framework:** FastAPI
2. **Database:** SQLite (with path to PostgreSQL)
3. **ML Framework:** scikit-learn
4. **LLM Integration:** OpenAI API
5. **Frontend:** Simple HTML/JavaScript (no heavy framework)
6. **Containerization:** Docker
7. **CI/CD:** GitHub Actions

## Rationale

### FastAPI
- **Pros:**
  - Automatic API documentation (OpenAPI/Swagger)
  - Built-in async support for scalability
  - Type hints and validation with Pydantic
  - Fast development and excellent developer experience
  - Modern Python framework with strong ecosystem
- **Cons:**
  - Relatively newer than Flask/Django
  - Smaller community (but growing rapidly)
- **Why chosen:** Best balance of developer productivity, performance, and modern features

### SQLite (with PostgreSQL path)
- **Pros:**
  - Zero configuration for development
  - Single file database, easy to distribute
  - SQLAlchemy makes migration to PostgreSQL straightforward
  - Perfect for prototype/skeleton phase
- **Cons:**
  - Not suitable for high-concurrency production
  - Limited concurrent writes
- **Why chosen:** Fastest path to working system; architecture supports easy migration to PostgreSQL via SQLAlchemy ORM

### scikit-learn
- **Pros:**
  - Battle-tested, stable ML library
  - Excellent documentation and examples
  - RandomForest provides good baseline performance
  - Easy to deploy (no GPU requirements)
  - Simple serialization with pickle
- **Cons:**
  - Not as sophisticated as deep learning for complex patterns
  - Limited real-time learning capabilities
- **Why chosen:** Requirements emphasize "a linear regression that works beats a neural network that doesn't" - scikit-learn provides robust, explainable models

### OpenAI API
- **Pros:**
  - State-of-the-art language understanding
  - Simple API integration
  - Handles context and generates coherent insights
  - No model training/hosting required
- **Cons:**
  - External dependency and API costs
  - Requires API key configuration
  - Network latency
- **Why chosen:** Fastest way to demonstrate AI/LLM integration; gracefully degrades if API key not configured

### Simple HTML/JavaScript
- **Pros:**
  - No build process required
  - Works in any browser
  - Easy for other developers to understand and modify
  - Self-contained (no npm/webpack complexity)
- **Cons:**
  - Less sophisticated than React/Vue
  - Manual DOM manipulation
- **Why chosen:** Requirements prioritize "small, coherent system" over sophistication; pure HTML/JS reduces complexity

### Docker + GitHub Actions
- **Pros:**
  - Industry standard containerization
  - GitHub Actions free for public repos
  - Simple yaml configuration
  - Integrated with GitHub
- **Cons:**
  - Docker image size
  - Build time on CI
- **Why chosen:** Standard tools that project team will already know; low friction for inheritance

## Consequences

### Positive
- Fast development velocity
- Easy to understand and extend
- Low operational complexity
- Clear upgrade paths (SQLite → PostgreSQL, simple HTML → React, etc.)
- All components have strong documentation

### Negative
- SQLite limits production scalability (documented mitigation: SQLAlchemy abstraction)
- OpenAI dependency requires API key and has costs (documented fallback: graceful degradation)
- Simple frontend may need rewrite for complex dashboards (acceptable for skeleton)

### Risks and Mitigations
1. **Risk:** SQLite performance bottleneck
   - **Mitigation:** SQLAlchemy ORM enables seamless PostgreSQL migration
2. **Risk:** OpenAI API costs
   - **Mitigation:** Caching, graceful degradation, clear documentation
3. **Risk:** Model accuracy
   - **Mitigation:** Focus on working pipeline; model improvements can iterate

## Extension Points for Project Team

The architecture provides clear extension points:
1. **Database:** Change connection string in config.py to migrate to PostgreSQL
2. **ML Model:** Replace RevenuePredictor implementation while maintaining interface
3. **LLM Provider:** Swap OpenAI client in insights.py for local model or other provider
4. **Frontend:** Replace templates/index.html with React/Vue app using same API
5. **Additional Data Sources:** Add new models in models.py and extend DataIngestor

## Alternatives Considered

1. **Django + DRF:** More opinionated, slower development for API-first design
2. **Flask:** Less modern, requires more boilerplate for validation
3. **PostgreSQL from start:** Adds operational complexity without current need
4. **TensorFlow/PyTorch:** Overkill for tabular time-series revenue prediction
5. **Local LLM:** Adds infrastructure complexity, slower development
6. **React Frontend:** Requires build process, more moving parts

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- scikit-learn: https://scikit-learn.org/
- OpenAI API: https://platform.openai.com/docs/
