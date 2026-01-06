# Setup Guide

Complete installation and configuration instructions for the LIMS-ELN Integration Platform.

## Prerequisites

### Required Software
- Python 3.11 or higher
- Docker 24.0 or higher
- Docker Compose 2.20 or higher
- Git

### System Requirements
- 4GB RAM minimum (8GB recommended)
- 10GB available disk space
- Linux, macOS, or Windows with WSL2

## Installation Methods

### Method 1: Docker Compose (Recommended)

This method sets up the complete stack including all dependencies.

```bash
# Clone repository
git clone https://github.com/tobilola/LIMS-ELN_Integration.git
cd LIMS-ELN_Integration

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Verify services
docker-compose ps
```

Access the API at http://localhost:8000

### Method 2: Local Development

For active development with hot reload.

```bash
# Clone repository
git clone https://github.com/tobilola/LIMS-ELN_Integration.git
cd LIMS-ELN_Integration

# Start infrastructure services only
docker-compose up -d postgres mongodb redis rabbitmq

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download NLP model
python -m spacy download en_core_web_sm

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run application
uvicorn app.main:app --reload --port 8000
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

**API Configuration**
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
DEBUG=false
LOG_LEVEL=INFO
```

**Database Configuration**
```bash
DATABASE_URL=postgresql+asyncpg://lims:password@localhost:5432/lims_eln
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=lims_eln
REDIS_URL=redis://localhost:6379/0
```

**Security**
```bash
JWT_SECRET_KEY=generate-secure-random-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**External Systems**
```bash
LIMS_API_URL=https://your-lims-system.com/api
LIMS_API_KEY=your-api-key
ELN_API_URL=https://your-eln-system.com/api
ELN_API_KEY=your-api-key
```

### Generating Secrets

Generate secure JWT secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Setup

### PostgreSQL

Tables are created automatically on first run. To run migrations manually:

```bash
alembic upgrade head
```

### MongoDB

Collections are created automatically. No manual setup required.

## Verification

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-06T...",
  "services": {
    "postgresql": {"status": "healthy", "latency_ms": 2.5},
    "mongodb": {"status": "healthy", "latency_ms": 1.8},
    "api": {"status": "healthy"}
  }
}
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Run Specific Tests

```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## Common Issues

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Change port in .env
API_PORT=8001
```

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

### Import Errors

```bash
# Verify virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

## Development Workflow

### Starting Development

```bash
# Activate virtual environment
source venv/bin/activate

# Start infrastructure
docker-compose up -d postgres mongodb redis

# Run application with hot reload
uvicorn app.main:app --reload
```

### Making Changes

```bash
# Create feature branch
git checkout -b feature/description

# Make changes, test locally
pytest

# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin feature/description
```

### Code Quality

Before committing:

```bash
# Format code
black app/

# Check types
mypy app/

# Lint
flake8 app/
```

## Production Deployment

### Docker

```bash
# Build production image
docker build -t lims-eln-integration:1.0.0 .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env.prod \
  --name lims-eln-api \
  lims-eln-integration:1.0.0
```

### Kubernetes

```bash
# Create namespace
kubectl create namespace lims-integration

# Apply configurations
kubectl apply -f k8s/ -n lims-integration

# Verify deployment
kubectl get pods -n lims-integration
```

## Monitoring

### Logs

```bash
# Docker Compose
docker-compose logs -f api

# Docker
docker logs -f lims-eln-api

# Kubernetes
kubectl logs -f deployment/lims-eln-api -n lims-integration
```

### Metrics

Prometheus metrics available at http://localhost:8000/metrics

## Troubleshooting

### Application Won't Start

1. Check Docker services are running
2. Verify environment variables are set correctly
3. Check database connections
4. Review application logs

### API Errors

1. Check service health endpoint
2. Verify external API credentials
3. Review error logs
4. Check database connectivity

### Performance Issues

1. Monitor database query times
2. Check API response times
3. Verify cache hit rates
4. Review resource utilization

## Support

For issues or questions:
- Check existing documentation in docs/
- Review GitHub issues
- Contact: ogunbowaleadeola@gmail.com

## Next Steps

After successful setup:
1. Review API documentation at /docs
2. Configure external system connections
3. Run test suite to verify installation
4. Begin implementing service layer logic
5. Train ML models with sample data
