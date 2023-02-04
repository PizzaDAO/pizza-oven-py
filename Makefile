.PHONY: all environment docker-dev docker-prod lint install-poetry start test test-natron

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
	pip3 install 'poetry==1.2.2'
	poetry config virtualenvs.in-project true 
	poetry install
	$(NATRON_PATH)/natron-python -m pip install numpy

# Run locally
local-start:
	poetry run uvicorn app.main:app --reload --port $(PORT)

# Docker
docker-build:
	@echo 🐳 Building Docker
	DOCKER_BUILDKIT=1 DOCKER_DEFAULT_PLATFORM=linux/amd64 docker build -t $(IMAGE_NAME):latest .

docker-run:
	@echo 🐳 Running Docker
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose up --build

docker-dev:
	@echo 🐳 Running Docker in dev mode with services
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose -f docker-compose.dev.yml up --build

docker-local: docker-build
	@echo 🐳 Running Docker in local mode without services
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 DOCKER_DEFAULT_PLATFORM=linux/amd64 docker-compose -f docker-compose.local.yml up --build

docker-prod:
	@echo 🐳 Running Docker in prod mode with services
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 DOCKER_DEFAULT_PLATFORM=linux/amd64 docker-compose -f docker-compose.prod.yml up --build

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

test-recipe-gen:
	@echo ☢️ Run Recipe Generator for testing
	poetry run python app/core/test/recipe_gen.py -r $(id) -c $(num)

test-natron:
	@echo ☢️ Test Natron
	poetry run python app/core/renderer.py -r $(realpath .)/ -f 111


test-natron-mvp:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/sample_kitchen_order_mvp.json -f 1

test-0000:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0000_Random.json -f 0

test-0001:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0003_Random.json -f 1
	
test-0002:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0002_Random.json -f 2

test-0003:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0003_Random.json -f 3
	
test-0004:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0004_Random.json -f 4

test-0005:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0005_Random.json -f 5

test-0006:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0006_Random.json -f 6

test-0007:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0007_Random.json -f 7

test-0008:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0008_Random.json -f 8
	
test-0009:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0009_Random.json -f 9

test-0010:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0010_Random.json -f 10

test-0011:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0011_Random.json -f 11

test-0012:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0012_Random.json -f 12
	
test-0013:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0013_Random.json -f 13
	
test-0014:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0014_Random.json -f 14

test-0015:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0015_Random.json -f 15

test-0016:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0016_Random.json -f 16

test-0017:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0017_Random.json -f 17
	
test-0018:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0018_Random.json -f 18

test-0019:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0019_Random.json -f 19

test-0020:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0020_Random.json -f 20

test-0021:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0021_Random.json -f 21

test-0022:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0022_Random.json -f 22

test-0023:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0023_Random.json -f 23
	
test-0024:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0024_Random.json -f 24

test-0025:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0025_Random.json -f 25

test-0026:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0026_Random.json -f 26

test-0027:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0027_Random.json -f 27
	
test-0028:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0028_Random.json -f 28

test-0029:
	@echo ☢️ Run MVP Natron
	poetry run python app/core/renderer.py -k $(realpath .)/data/kitchen_orders/0029_Random.json -f 29
