TARGET_LIST=$(shell egrep -o ^[a-zA-Z_-]+: $(MAKEFILE_LIST) | sed 's/://')
.PHONY: $(TARGET_LIST)
.DEFAULT_GOAL := help

# --------------------------------------
# Tasks
# --------------------------------------
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

env-up-all: ## Start the all services with docker compose
	@docker compose up --build -d && \
	sleep 10 && \
	docker compose exec app bash -c "source activate myenv && make db-migration"

env-up-app: ## Start the backend service with docker compose
	@docker compose up --build app && \
	sleep 10 && \
	docker compose exec app bash -c "source activate myenv && make db-migration"

env-up-app-d: ## Start the backend service with docker compose in detached mode
	@docker compose up --build -d app && \
	sleep 10 && \
	docker compose exec app bash -c "source activate myenv && make db-migration"

env-up-db: ## Start the platform database service with docker compose
	@docker compose up --build -d app-db

env-down: ## Stop the all services with docker compose
	@docker compose down

env-down-app: ## Stop the backend service with docker compose
	@docker compose stop app

env-reload-all: ## Reload the all services with docker compose
	@docker compose down && \
	docker compose up --build -d && \
	sleep 10 && \
	docker compose exec app bash -c "source activate myenv && make db-migration"

env-reload-app: ## Reload the backend service with docker compose
	@docker compose stop app && \
	docker compose up --build app

env-reload-app-d: ## Reload the backend service with docker compose in detached mode
	@docker compose stop app && \
	docker compose up --build -d app

env-down-v: ## Stop the all services with docker compose and remove volumes
	@docker compose down -v

db-migration: ## Apply the migration scripts
	@alembic upgrade head

db-rev-generate: ## Generate a new migration script
	@if [ -z "$(MSG)" ]; then \
		echo "ERROR: マイグレーションメッセージを指定してください。使用例: make db-rev-generate MSG=\"add example_col column to example_table\""; \
		exit 1; \
	fi
	alembic revision -m "$(MSG)"

db-rev-downgrade: ## Downgrade the database to a specific revision
	@if [ -z "$(REV)" ]; then \
		echo "ERROR: リビジョンを指定してください。使用例: make db-rev-downgrade REV=1234567890"; \
		exit 1; \
	fi
	alembic downgrade "$(REV)"

env-db-migration: ## Apply the migration scripts in the container
	@docker compose run --rm app make db-migration

run-local: ## Run the backend application in host machine
	@uvicorn app.main:app --reload

app-logs: ## Show the logs of the backend service
	@docker compose logs -f app

exec-bash: ## Open a bash shell in the backend container
	@docker compose exec app bash

exec-bash-db: ## Open a bash shell in the admin database container
	@docker compose exec app-db bash

pkg-install-local: ## Install the Python packages locally
	@source .venv/bin/activate && \
	poetry install

check-format-be: ## Check the code formatting for the backend
	@poetry run ruff check . && \
	poetry run ruff format --check .

check-format-fe: ## Check the code formatting for the frontend
	@cd frontend-inertia && npm run format:check && npm run lint

run-format-be: ## Run the code formatting for the backend
	@poetry run ruff check --fix . && \
	poetry run ruff format .

run-format-fe: ## Run the code formatting for the frontend
	@cd frontend-inertia && npm run format && npm run lint:fix

test: ## Run the tests
	@poetry run pytest -s --cov=app --cov-report=term-missing

seed-all: ## Seed all test data to database (local)
	@poetry run python -m app.seeds.seed_manager

seed-user: ## Seed user test data to database (local)
	@poetry run python -m app.seeds.seed_manager --seed user

env-seed-all: ## Seed all test data to database (container)
	@docker compose exec app bash -c "source activate myenv && python -m app.seeds.seed_manager"

env-seed-user: ## Seed user test data to database (container)
	@docker compose exec app bash -c "source activate myenv && python -m app.seeds.seed_manager --seed user"

env-reset-users: ## Reset test users with new passwords (container)
	@docker compose exec app bash -c "source activate myenv && python -m app.seeds.reset_test_users"

build-fe: ## Build the frontend application
	@cd frontend-inertia && npm run build

build-fe-watch: ## Build the frontend application in watch mode
	@cd frontend-inertia && npm run build -- --watch

vite-restart: ## Restart Vite development server in container
	@echo "🔄 Restarting Vite server..."
	@docker compose exec app pkill -f "vite --host" || true
	@sleep 2
	@echo "🚀 Starting Vite server in background..."
	@docker compose exec -d app bash -c "cd /usr/src/app/frontend-inertia && npm run dev -- --host 0.0.0.0"
	@sleep 2
	@echo "✅ Vite server restarted!"
	@echo "📍 Check status with: make vite-status"

vite-logs: ## Show Vite server logs
	@docker compose logs app | grep -E "(vite|VITE)"

vite-status: ## Check Vite server status
	@echo "📊 Checking Vite server status..."
	@if docker compose exec app pgrep -f "vite --host" > /dev/null 2>&1; then \
		echo "✅ Vite server is running"; \
		docker compose exec app ps aux | grep -v grep | grep "vite --host" | head -5; \
	else \
		echo "❌ Vite server is not running"; \
		echo "💡 Start with: make vite-restart or make vite-start"; \
	fi

vite-start: ## Start Vite development server (foreground)
	@echo "🚀 Starting Vite server in foreground..."
	@docker compose exec app bash -c "cd /usr/src/app/frontend-inertia && npm run dev -- --host 0.0.0.0"

fe-restart: ## Restart frontend development server (alias for vite-restart)
	@make vite-restart

## Development Environment Setup
setup-vscode-auto: ## Auto-detect and setup VSCode settings.json (local or container)
	@./scripts/vscode-auto-setup-dev.sh

setup-vscode-local: ## Setup VSCode settings.json for local development
	@./scripts/vscode-setup-local-dev.sh

setup-vscode-container: ## Setup VSCode settings.json for container development
	@./scripts/vscode-setup-container-dev.sh
