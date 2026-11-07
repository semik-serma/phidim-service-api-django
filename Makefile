
.DEFAULT_GOAL := help

.PHONY: help start-server stop-server django redis worker beat

PYTHON := venv/bin/python
CELERY := venv/bin/celery
HOST := 127.0.0.1
PORT := 8000

help:
	@echo ""
	@echo "Phidim Service API - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "  make start-server   Start Uvicorn + Redis + Celery Worker + Beat"
	@echo "  make stop-server    Stop all development services"
	@echo ""
	@echo "  make django         Start Django using Uvicorn (ASGI)"
	@echo "  make redis          Start Redis"
	@echo "  make worker         Start Celery worker"
	@echo "  make beat           Start Celery Beat"
	@echo ""

start-server:
	@echo "🚀 Starting ASGI + Redis + Celery Worker + Celery Beat..."
	@bash -c '\
		trap '\''echo; echo "🛑 Stopping all services..."; trap - INT TERM EXIT; jobs -pr | xargs -r kill; wait'\'' INT TERM EXIT; \
		echo "🌐 Starting Uvicorn ASGI server..."; \
		$(PYTHON) -m uvicorn config.asgi:application --reload --host $(HOST) --port $(PORT) & \
		echo "🔴 Starting Redis..."; \
		redis-server & \
		echo "⚙️ Starting Celery worker..."; \
		$(CELERY) -A config worker --loglevel=info & \
		echo "⏰ Starting Celery Beat..."; \
		$(CELERY) -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler & \
		echo ""; \
		echo "✅ All services started."; \
		echo "🌐 API: http://$(HOST):$(PORT)"; \
		echo "Press Ctrl+C to stop everything."; \
		wait \
	'

django:
	@$(PYTHON) -m uvicorn config.asgi:application --reload --host $(HOST) --port $(PORT)

redis:
	@redis-server

worker:
	@$(CELERY) -A config worker --loglevel=info

beat:
	@$(CELERY) -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

stop-server:
	@echo "🛑 Stop services started by make start-server using Ctrl+C."
	@echo "If running separately, stop each service in its terminal."
