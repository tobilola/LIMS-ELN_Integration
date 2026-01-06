# LIMS-ELN Integration Platform

Middleware system for automating data synchronization between Laboratory Information Management Systems (LIMS) and Electronic Laboratory Notebooks (ELN).

## Overview

This platform addresses operational inefficiencies in pharmaceutical and clinical laboratories where LIMS and ELN systems operate independently. The solution automates bidirectional data synchronization, implements AI-based validation, and maintains complete audit trails for regulatory compliance.

### Problem

Laboratory scientists spend significant time manually transferring data between disconnected systems, resulting in:
- Inconsistent data across platforms
- Incomplete audit trails
- High transcription error rates
- Delayed research cycles
- Regulatory compliance risks

### Solution

Automated middleware that:
- Synchronizes data in real-time between LIMS and ELN
- Validates data quality using machine learning
- Extracts structured information from unstructured text
- Maintains complete audit trails
- Supports FDA 21 CFR Part 11 compliance requirements

## Technical Stack

- **Backend:** Python 3.11, FastAPI
- **Databases:** PostgreSQL 15, MongoDB 6.0, Redis 7.0
- **ML/AI:** scikit-learn, TensorFlow, spaCy
- **Infrastructure:** Docker, Kubernetes
- **Testing:** pytest

## Architecture

The system uses a microservices architecture with event-driven communication:

- API Gateway (FastAPI) handles authentication and request routing
- Validation Engine applies ML models for data quality checks
- NLP Service extracts metadata from free-text protocols
- Message Queue (RabbitMQ) manages async operations
- Dual database strategy: PostgreSQL for transactional data, MongoDB for unstructured content

## Installation

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git

### Setup

```bash
git clone https://github.com/tobilola/LIMS-ELN_Integration.git
cd LIMS-ELN_Integration

cp .env.example .env
# Edit .env with your configuration

docker-compose up -d

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

API documentation available at http://localhost:8000/docs

## Project Structure

```
app/
├── main.py                 # Application entry point
├── api/routes/             # Endpoint definitions
├── core/                   # Configuration and utilities
├── models/                 # Database models
├── schemas/                # Request/response validation
├── services/               # Business logic
├── ml/                     # Machine learning models
├── integrations/           # External system adapters
└── database/               # Database connections

tests/                      # Test suite
docker-compose.yml          # Infrastructure definition
requirements.txt            # Python dependencies
```

## API Endpoints

### Health Monitoring
- `GET /api/v1/health` - System health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

### Data Synchronization
- `POST /api/v1/sync/sample` - Sync single sample
- `POST /api/v1/sync/batch` - Batch synchronization
- `GET /api/v1/sync/status/{sample_id}` - Sync status

### Validation
- `POST /api/v1/validate/sample` - Validate sample data
- `POST /api/v1/validate/test-result` - Validate test results
- `POST /api/v1/validate/batch` - Batch validation

### NLP Processing
- `POST /api/v1/nlp/parse-protocol` - Parse lab protocols
- `POST /api/v1/nlp/extract-metadata` - Extract metadata
- `POST /api/v1/nlp/classify-protocol` - Classify protocols

## Configuration

Key environment variables in `.env`:

```bash
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/lims_eln
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
LIMS_API_URL=https://lims.example.com/api
ELN_API_URL=https://eln.example.com/api
```

## Development

### Running Tests

```bash
pytest
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
mypy app/
flake8 app/
black app/
```

### Making Changes

```bash
git checkout -b feature/description
# Make changes
git commit -m "Add feature description"
git push origin feature/description
```

## Deployment

### Docker

```bash
docker build -t lims-eln-integration:latest .
docker run -p 8000:8000 lims-eln-integration:latest
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

## Implementation Status

### Completed
- FastAPI application with async support
- Database models and schemas
- API endpoint structure
- Docker containerization
- Health monitoring endpoints

### In Progress
- Service layer implementation
- ML model training
- External system adapters
- Comprehensive test coverage

## Performance Targets

- API response time: < 200ms (p95)
- Sync latency: < 30 seconds
- System uptime: 99.9%
- Data consistency: 99.9%

## Security

- OAuth 2.0 authentication
- JWT token-based authorization
- Encrypted data at rest and in transit
- Complete audit trail logging
- Role-based access control

## Documentation

- **README.md** - Project overview (this file)
- **SETUP.md** - Detailed installation guide
- **API.md** - Complete API reference
- **ARCHITECTURE.md** - System architecture documentation

## License

MIT License - see LICENSE file for details

## Contact

Tobilola Ogunbowale  
ogunbowaleadeola@gmail.com  
https://github.com/tobilola

## Contributing

This is a portfolio project demonstrating full-stack development capabilities in laboratory informatics. The codebase follows production best practices and is designed to showcase modern software engineering approaches.
