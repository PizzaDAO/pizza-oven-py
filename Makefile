.PHONY: all environment lint install-poetry start test test-natron

.EXPORT_ALL_VARIABLES:
OS ?= $(shell python -c 'import platform; print(platform.system())')
ifeq ($(OS), Linux)
# TODO: find it
NATRON_PATH=/Applications/Natron.app/Contents/MacOS
endif
ifeq ($(OS), Darwin)
NATRON_PATH=/Applications/Natron.app/Contents/MacOS
endif
NATRON_PROJECT_PATH=$(realpath .)/natron

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
	pip3 install 'poetry==1.1.6'
	poetry config virtualenvs.in-project true 
	poetry install
	$(NATRON_PATH)/natron-python -m pip install numpy

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

# Deploy

# Tests
test:
	@echo ✅ Testing
	poetry run pytest . -x

test-natron:
	@echo ☢️ Test Natron
	poetry run python app/core/renderer.py -r $(realpath .)/data/sample_recipe.json -f 111

test-natron-all:
	@echo ☢️ Test Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order.json -f 1111

test-natron-box:
	@echo ☢️ Run Box Paper Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order_box_paper.json -f 1

test-natron-paper:
	@echo ☢️ Run Cheese Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order_paper.json -f 1

test-natron-crust:
	@echo ☢️ Run Cheese Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order_crust.json -f 1

test-natron-sauce:
	@echo ☢️ Run Cheese Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order_sauce.json -f 1

test-natron-cheese:
	@echo ☢️ Run Cheese Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order_cheese.json -f 1

test-natron-topping:
	@echo ☢️ Run Cheese Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order_topping.json -f 1

test-natron-extra:
	@echo ☢️ Test Natron Extra
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_extra.json -f 1

test-natron-mvp:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order_mvp.json -f 1