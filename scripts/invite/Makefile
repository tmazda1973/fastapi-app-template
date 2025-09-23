.PHONY: help send verify accept
.DEFAULT_GOAL := help

# Base command for running the CLI tool in container
INVITE_CMD = docker exec fastapi-app bash -c "source activate myenv && cd /usr/src/app && PYTHONPATH=/usr/src/app python scripts/invite/cli.py"

help: ## Show this help message
	@echo "📧 Invite CLI Tool Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📋 Usage Examples:"
	@echo "  make send EMAIL=user@example.com"
	@echo "  make verify TOKEN=<招待トークン>"
	@echo "  make accept TOKEN=<招待トークン> PASSWORD=<パスワード>"

send: ## Send invitation email (requires EMAIL parameter)
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL parameter is required"; \
		echo "Usage: make send EMAIL=user@example.com"; \
		exit 1; \
	fi
	@echo "📧 Sending invitation to $(EMAIL)..."
	@$(INVITE_CMD) send-invite $(EMAIL)

verify: ## Verify invitation token (requires TOKEN parameter)
	@if [ -z "$(TOKEN)" ]; then \
		echo "❌ Error: TOKEN parameter is required"; \
		echo "Usage: make verify TOKEN=<招待トークン>"; \
		exit 1; \
	fi
	@echo "🔍 Verifying invitation token..."
	@$(INVITE_CMD) verify-invite $(TOKEN)

accept: ## Accept invitation (requires TOKEN and PASSWORD parameters)
	@if [ -z "$(TOKEN)" ] || [ -z "$(PASSWORD)" ]; then \
		echo "❌ Error: TOKEN and PASSWORD parameters are required"; \
		echo "Usage: make accept TOKEN=<招待トークン> PASSWORD=<パスワード>"; \
		exit 1; \
	fi
	@echo "✅ Accepting invitation..."
	@$(INVITE_CMD) accept-invite $(TOKEN) $(PASSWORD)

show-commands: ## Show detailed CLI commands help
	@echo "🔧 Available CLI commands:"
	@echo ""
	@echo "  For full help: docker exec fastapi-app bash -c \"source activate myenv && cd /usr/src/app && PYTHONPATH=/usr/src/app python scripts/invite/cli.py --help\""
	@echo "  For command help: add --help after any command (e.g., make send EMAIL=test@example.com --help)"

# Development shortcuts
test-send: ## Test send invitation (uses test user)
	@echo "🧪 Testing invitation send with test user..."
	@$(INVITE_CMD) send-invite user@example.com

# Status check
check-container: ## Check if FastAPI container is running
	@echo "🔍 Checking FastAPI container status..."
	@docker ps | grep fastapi-app || (echo "❌ FastAPI container is not running. Run 'make env-up-all' first." && exit 1)
	@echo "✅ FastAPI container is running"
