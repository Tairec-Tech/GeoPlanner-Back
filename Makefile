.PHONY: help install setup test run clean docker-build docker-run

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias
	pip install -r requirements.txt

setup: ## Configurar el proyecto (crear .env, instalar dependencias, ejecutar migraciones)
	python setup.py

test: ## Ejecutar pruebas
	pytest

test-verbose: ## Ejecutar pruebas con salida verbose
	pytest -v

run: ## Ejecutar el servidor de desarrollo
	python run.py

run-dev: ## Ejecutar el servidor con recarga automática
	uvicorn app:app --reload --host 0.0.0.0 --port 8000

clean: ## Limpiar archivos temporales
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

docker-build: ## Construir imagen Docker
	docker build -t geoplanner-backend .

docker-run: ## Ejecutar contenedor Docker
	docker run -p 8000:8000 geoplanner-backend

docker-compose-up: ## Ejecutar con Docker Compose
	docker-compose up --build

docker-compose-down: ## Detener Docker Compose
	docker-compose down

migrate: ## Ejecutar migraciones
	alembic upgrade head

migrate-create: ## Crear nueva migración
	alembic revision --autogenerate -m "$(message)"

migrate-rollback: ## Revertir última migración
	alembic downgrade -1

format: ## Formatear código con black
	black .

lint: ## Verificar código con flake8
	flake8 .

check: ## Ejecutar todas las verificaciones
	make format
	make lint
	make test 