# Default: list available recipes
default:
    @just --list

# Install dependencies
install:
    uv sync

# Run Streamlit app locally (without Docker)
run:
    uv run streamlit run src/imbalance_dashboard/app.py

# Run tests
test:
    uv run pytest

# Build and start all services
up:
    docker compose up --build

# Start with live reload (syncs src/ changes into the container)
watch:
    docker compose up --watch

# Stop all services
down:
    docker compose down

# Stop services and remove volumes (deletes postgres data)
clean:
    docker compose down -v

# Build Docker image only
build:
    docker compose build

# Open a psql shell against the running postgres container
db:
    docker compose exec db psql -U imbalance imbalance
