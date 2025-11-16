.PHONY: help build up down restart logs shell test clean

# Default target
help:
	@echo "GovPlan_AI Docker Commands"
	@echo "=========================="
	@echo "build       - Build Docker images"
	@echo "up          - Start all services"
	@echo "down        - Stop all services"
	@echo "restart     - Restart all services"
	@echo "logs        - View logs"
	@echo "shell       - Open shell in API container"
	@echo "test        - Run tests"
	@echo "clean       - Remove containers and volumes"
	@echo "db-init     - Initialize database"
	@echo "db-migrate  - Run database migrations"
	@echo "crawl       - Run crawler manually"
	@echo ""
	@echo "Production:"
	@echo "prod-build  - Build production images"
	@echo "prod-up     - Start production services"
	@echo "prod-down   - Stop production services"

# Development
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Flower: http://localhost:5555"
	@echo "pgAdmin: http://localhost:5050 (with --profile tools)"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f celery_worker

shell:
	docker-compose exec api bash

shell-db:
	docker-compose exec postgres psql -U govplan -d govplan_ai

test:
	docker-compose exec api pytest tests/ -v

clean:
	docker-compose down -v
	docker system prune -f

# Database
db-init:
	docker-compose exec api python scripts/init_db.py

db-shell:
	docker-compose exec postgres psql -U govplan -d govplan_ai

# Crawler
crawl:
	docker-compose exec api python scripts/run_crawler.py --site all --max-pages 5

crawl-bizinfo:
	docker-compose exec api python scripts/run_crawler.py --site bizinfo --max-pages 3

crawl-kstartup:
	docker-compose exec api python scripts/run_crawler.py --site kstartup --max-pages 3

# Production
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Tools
pgadmin:
	docker-compose --profile tools up -d pgadmin
	@echo "pgAdmin: http://localhost:5050"
	@echo "Email: admin@govplan.ai"
	@echo "Password: admin"

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "API is not responding"
	@docker-compose ps
