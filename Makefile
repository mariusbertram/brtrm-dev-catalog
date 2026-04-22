.PHONY: help generate validate build serve clean

help: ## Display this help message
	@echo "IP Rules Catalog - Makefile Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-deps: ## Install required dependencies
	@echo "Installing Python dependencies..."
	pip3 install pyyaml

generate: ## Generate FBC from operator templates (sequential)
	@echo "Generating FBC per operator..."
	@if command -v opm &> /dev/null; then \
		python3 scripts/generate-fbc.py; \
	else \
		echo "⚠ Warning: opm not found."; \
		echo "  Install opm to generate FBC locally."; \
		echo "  Download from: https://github.com/operator-framework/operator-registry/releases"; \
	fi

validate: generate ## Validate the generated FBC
	@echo "Validating FBC..."
	@if command -v opm &> /dev/null; then \
		opm validate catalog/fbc; \
	else \
		echo "Error: opm not found. Please install operator-sdk or download opm binary."; \
		echo "Download from: https://github.com/operator-framework/operator-registry/releases"; \
		exit 1; \
	fi

build: validate ## Build the catalog container image
	@echo "Building catalog image..."
	cd catalog && \
	opm generate dockerfile fbc && \
	docker build -f fbc.Dockerfile -t localhost:5000/brtrm-dev-catalog:latest .

serve: generate ## Serve the catalog locally with opm
	@echo "Starting catalog server on port 50051..."
	@echo "Press Ctrl+C to stop"
	opm serve catalog/fbc -p 50051

clean: ## Clean generated files
	@echo "Cleaning generated files..."
	rm -rf catalog/fbc/
	rm -f catalog/fbc.Dockerfile

test: validate ## Run tests (validation)
	@echo "Tests passed!"
