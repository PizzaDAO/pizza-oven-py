.PHONY: all environment lint install-poetry start

IMAGE_NAME = pizza-oven
# Supports either "development" or "production" modes
API_MODE ?= development
ifeq ($(API_MODE), development)
PORT ?= 8000
else
# runs on port 80 for testing but you really shouldnt do that. use docker.
PORT ?= 80 
endif

all: environment start

environment:
	@echo 🔧 Setting Up Environment
	pip install 'poetry==1.1.5'
	poetry install

# Dev Server
start:
	poetry run uvicorn app.main:app --reload --port $(PORT)

# Docker
docker-build:
	@echo 🐳 Building Docker
	DOCKER_BUILDKIT=1 docker build -t $(IMAGE_NAME) .

docker-run:
	@echo 🐳 Running Docker
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose up --build

docker-dev:
	@echo 🐳 Running Docker in dev mode
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose -f docker-compose.dev.yml up --build

docker-postman-test:
	@echo 🧪 Running Postman Tests in Docker
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose \
	-f tests/postman/docker-compose.yml up \
	--build \
	--abort-on-container-exit \
	--exit-code-from test-runner

# Linting
lint:
	@echo 💚 Making things Pretty
	@echo 1.Pylint
	poetry run pylint --extension-pkg-whitelist=pydantic app tests
	@echo 2.Black Formatting
	poetry run black --diff --check app tests
	@echo 3.Mypy Static Typing
	poetry run mypy --config-file=pyproject.toml app tests

auto-lint:
	poetry run black app tests
	make lint

# Tests
test:
	@echo ✅ Testing
	poetry run pytest . -x