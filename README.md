# Analytics Service

> Analytics and reporting service for Mission Engadi platform

[![CI/CD Pipeline](https://docs.github.com/assets/cb-40551/images/help/actions/superlinter-workflow-sidebar.png)
[![codecov](https://i.ytimg.com/vi/AAl4HmJ3YuM/maxresdefault.jpg)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.108+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Part of the [Mission Engadi](https://engadi.org) microservices architecture.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running Locally](#running-locally)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Database Migrations](#database-migrations)
  - [Testing](#testing)
  - [Code Quality](#code-quality)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Analytics Service is a FastAPI-based microservice that aggregates, analyzes, and reports on data from all Mission Engadi platform services. It provides comprehensive analytics for partners, projects, social media, notifications, and overall platform metrics. The service enables data-driven decision-making through real-time metrics, dashboards, and trend analysis.

**Key Capabilities:**
- **Metric Aggregation**: Collects and aggregates metrics from 6 microservices
- **Dashboard Management**: Customizable dashboards for different user roles
- **Partner Analytics**: Donation tracking, engagement metrics, and partner insights
- **Project Analytics**: Impact measurement, completion tracking, and beneficiary metrics
- **Social Media Analytics**: Platform comparison, engagement trends, and performance metrics
- **Notification Analytics**: Delivery statistics, channel effectiveness, and campaign analysis
- **Data Synchronization**: Automated sync with source services

## ✨ Features

### Core Features
- **35+ API Endpoints**: Comprehensive REST API covering all analytics needs
- **8 Service Layers**: Modular business logic for metrics, dashboards, and analytics
- **Multi-Service Integration**: Connects with Partners CRM, Projects, Social Media, and Notification services
- **Real-Time Metrics**: Live metric collection and aggregation
- **Time-Series Data**: Historical trend analysis with configurable intervals
- **Custom Dashboards**: User-defined dashboards with widget support
- **Executive Reporting**: Pre-configured executive dashboards
- **Data Sync Management**: Automated and manual sync operations

### Technical Features
- **RESTful API**: Clean, versioned API with automatic OpenAPI documentation
- **Async/Await**: Fully asynchronous for high performance
- **PostgreSQL Database**: Advanced indexing for 3-year data retention
- **JSONB Storage**: Flexible metadata and dimension storage
- **Authentication**: JWT-based authentication with role-based access control
- **Validation**: Request/response validation using Pydantic
- **Testing**: 70%+ test coverage with pytest
- **Docker**: Containerized application with docker-compose
- **Monitoring**: Health checks and readiness probes
- **Logging**: Structured logging with contextual information

## 🏗️ Architecture

This service follows a clean architecture pattern:

```
analytics_service/
├── app/
│   ├── api/               # API layer
│   │   └── v1/            # API version 1
│   │       ├── endpoints/ # Route handlers
│   │       └── api.py     # API router aggregation
│   ├── core/              # Core utilities
│   │   ├── config.py      # Configuration management
│   │   ├── security.py    # Auth utilities
│   │   └── logging.py     # Logging configuration
│   ├── db/                # Database layer
│   │   ├── base.py        # Base classes
│   │   └── session.py     # Database session management
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── dependencies/      # Dependency injection
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── conftest.py        # Test fixtures
├── migrations/            # Alembic migrations
└── docs/                  # Additional documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- Docker & Docker Compose (optional, for containerized development)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/mission-engadi/analytics_service.git
cd analytics_service
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Configuration

1. **Copy environment template**

```bash
cp .env.example .env
```

2. **Edit `.env` file with your configuration**

```env
# Application
PROJECT_NAME="Analytics Service"
PORT=8009
ENVIRONMENT="development"
DEBUG="true"

# Security
SECRET_KEY="your-secret-key-here"  # Generate with: openssl rand -hex 32

# Database
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/analytics_service_db"

# Redis
REDIS_URL="redis://localhost:6379/0"
```

### Running Locally

#### Option 1: Docker Compose (Recommended)

```bash
# Start all services (app, database, redis)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8009`

#### Option 2: Local Development

1. **Start PostgreSQL and Redis**

```bash
# Using Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

2. **Run database migrations**

```bash
alembic upgrade head
```

3. **Start the application**

```bash
uvicorn app.main:app --reload --port 8009
```

The API will be available at `http://localhost:8009`

## 💻 Development

### Project Structure

#### API Layer (`app/api/`)
- **Endpoints**: Define HTTP routes and handle requests/responses
- **Validation**: Automatic request validation using Pydantic schemas
- **Documentation**: Auto-generated OpenAPI/Swagger docs

#### Business Logic (`app/services/`)
- **Services**: Contain business logic and orchestrate operations
- **Separation**: Keep business logic separate from API layer
- **Reusability**: Services can be used across multiple endpoints

#### Data Layer (`app/models/` & `app/schemas/`)
- **Models**: SQLAlchemy ORM models (database structure)
- **Schemas**: Pydantic schemas (API contracts)
- **Separation**: Clear distinction between database and API representations

#### Core Utilities (`app/core/`)
- **Configuration**: Centralized settings management
- **Security**: Authentication and authorization utilities
- **Logging**: Structured logging setup

### Database Migrations

This project uses Alembic for database migrations.

#### Create a new migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration (for data migrations)
alembic revision -m "Description of changes"
```

#### Apply migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision>

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Testing

#### Run all tests

```bash
pytest
```

#### Run with coverage

```bash
pytest --cov=app --cov-report=html
```

#### Run specific test categories

```bash
# Unit tests only
pytest tests/unit/ -m unit

# Integration tests only
pytest tests/integration/ -m integration

# Run specific test file
pytest tests/unit/test_security.py

# Run specific test
pytest tests/unit/test_security.py::TestPasswordHashing::test_password_hash_and_verify
```

#### Writing Tests

##### Unit Tests
Test individual functions or classes in isolation:

```python
def test_password_hashing():
    password = "secure_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
```

##### Integration Tests
Test API endpoints with database:

```python
def test_create_example(client, auth_headers):
    response = client.post(
        "/api/v1/examples/",
        json={"title": "Test", "status": "active"},
        headers=auth_headers,
    )
    assert response.status_code == 201
```

### Code Quality

#### Format code

```bash
# Format with black
black app tests

# Sort imports
isort app tests
```

#### Lint code

```bash
# Check with flake8
flake8 app tests

# Type checking with mypy
mypy app

# Security checks
bandit -r app
```

#### Pre-commit checks

```bash
# Run all checks before committing
make check
```

## 📚 API Documentation

### Interactive Documentation

Once the service is running, visit:

- **Swagger UI**: `http://localhost:8009/api/v1/docs`
- **ReDoc**: `http://localhost:8009/api/v1/redoc`
- **OpenAPI Schema**: `http://localhost:8009/api/v1/openapi.json`

### Health Endpoints

#### Basic Health Check

```bash
GET /api/v1/health
```

Returns service status without checking dependencies.

**Response:**
```json
{
  "status": "healthy",
  "service": "Analytics Service",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### Readiness Check

```bash
GET /api/v1/ready
```

Returns service readiness including dependency checks.

**Response:**
```json
{
  "status": "ready",
  "service": "Analytics Service",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "checks": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### Authentication

Most endpoints require authentication. Include JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8009/api/v1/examples/
```

### Example Endpoints

See the interactive documentation for complete API reference.

## 🚢 Deployment

### Deploy to Fly.io

1. **Install Fly.io CLI**

```bash
curl -L https://fly.io/install.sh | sh
```

2. **Login to Fly.io**

```bash
fly auth login
```

3. **Create and configure app**

```bash
fly launch --name analytics_service
```

4. **Set secrets**

```bash
fly secrets set SECRET_KEY=<your-secret-key>
fly secrets set DATABASE_URL=<your-database-url>
```

5. **Deploy**

```bash
fly deploy
```

### Environment Variables for Production

**Required:**
- `SECRET_KEY`: Strong random secret key
- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: Set to "production"
- `DEBUG`: Set to "false"

**Optional:**
- `REDIS_URL`: Redis connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka servers
- `DATADOG_API_KEY`: DataDog monitoring key
- `CORS_ORIGINS`: Allowed CORS origins

### Database Setup

For production, use a managed PostgreSQL service:

1. **Fly.io Postgres**

```bash
fly postgres create --name analytics_service-db
fly postgres attach analytics_service-db
```

2. **Run migrations**

```bash
fly ssh console
alembic upgrade head
```

## 📊 Monitoring

### Health Checks

Configure your load balancer or monitoring system to check:

- **Liveness**: `GET /api/v1/health` (should always return 200)
- **Readiness**: `GET /api/v1/ready` (checks dependencies)

### Logging

The service uses structured JSON logging in production. Logs include:

- Request/response details
- User context
- Error stack traces
- Performance metrics

View logs:

```bash
# Docker Compose
docker-compose logs -f app

# Fly.io
fly logs
```

### Metrics

Enable metrics collection by setting:

```env
ENABLE_METRICS=true
DATADOG_API_KEY=<your-key>
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and write tests
4. Run tests and linting: `make check`
5. Commit with conventional commits: `git commit -m "feat: add new feature"`
6. Push and create a pull request

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Run tests
pytest

# Format and lint
make format
make lint

# Commit changes
git add .
git commit -m "feat: description of feature"

# Push to GitHub
git push origin feature/my-feature
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com)
- Database ORM by [SQLAlchemy](https://www.sqlalchemy.org)
- Testing with [pytest](https://pytest.org)
- Part of [Mission Engadi](https://engadi.org)

## 📞 Support

- **Documentation**: [docs.engadi.org](https://docs.engadi.org)
- **Issues**: [GitHub Issues](https://github.com/mission-engadi/analytics_service/issues)
- **Email**: support@engadi.org

---

Made with ❤️ by the Mission Engadi team
