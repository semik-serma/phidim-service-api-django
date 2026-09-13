.DEFAULT_GOAL := help

.PHONY: help start-server stop-server django redis worker beat

help:
	@echo ""
	@echo "Phidim Service API - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "  make start-server   Start Django + Redis + Celery Worker + Beat"
	@echo "  make stop-server    Stop all development services"
	@echo ""
	@echo "  make django         Start Django development server"
	@echo "  make redis          Start Redis"
	@echo "  make worker         Start Celery worker"
	@echo "  make beat           Start Celery Beat"
	@echo ""

start-server:
	@echo "🚀 Starting Django + Redis + Celery Worker + Celery Beat..."
	@bash -c '\
		trap "echo; echo 🛑 Stopping all services...; kill 0" SIGINT SIGTERM EXIT; \
		echo "🌐 Starting Django server..."; \
		( source venv/bin/activate && python manage.py runserver ) & \
		echo "🔴 Starting Redis..."; \
		( source venv/bin/activate && redis-server ) & \
		echo "⚙️ Starting Celery worker..."; \
		( source venv/bin/activate && celery -A config worker --loglevel=info ) & \
		echo "⏰ Starting Celery Beat..."; \
		( source venv/bin/activate && celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler ) & \
		echo ""; \
		echo "✅ All services started."; \
		echo "Press Ctrl+C to stop everything."; \
		wait \
	'

django:
	@source venv/bin/activate && python manage.py runserver

redis:
	@source venv/bin/activate && redis-server

worker:
	@source venv/bin/activate && celery -A config worker --loglevel=info

beat:
	@source venv/bin/activate && celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

stop-server:
	@pkill -f "manage.py runserver" || true
	@pkill -f "celery -A config worker" || true
	@pkill -f "celery -A config beat" || true
	@pkill -f "redis-server" || true
	@echo "🛑 Services stopped."