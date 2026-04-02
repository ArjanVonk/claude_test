# Imbalance Dashboard

![Unicorn](assets/unicorn.svg)

A Streamlit dashboard for Belgian electricity imbalance prices from [Elia](https://opendata.elia.be), deployable locally with Docker Compose and to Azure with Terraform.

## Running locally

```bash
docker compose up --build
```

Open [http://localhost:8501](http://localhost:8501).

For live reload during development:

```bash
docker compose up --watch
```

Without Docker:

```bash
uv sync
uv run streamlit run src/imbalance_dashboard/app.py
```

## Running tests

```bash
uv run pytest
```

## Deploying to Azure

Infrastructure is defined in `modules/` using Terraform (Azure Container Registry + Azure Container Instances).

1. Copy and fill in the variables:
   ```bash
   cd modules
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Provision infrastructure:
   ```bash
   az login
   terraform init
   terraform apply
   ```

3. Build and push the Docker image to ACR:
   ```bash
   az acr login --name <acr_name>
   docker build -t <acr_login_server>/imbalance-dashboard:latest .
   docker push <acr_login_server>/imbalance-dashboard:latest
   ```

The `dashboard_url` output from `terraform apply` gives the public URL.

## Project structure

```
src/imbalance_dashboard/
├── app.py          # Streamlit entrypoint
├── base.py         # Abstract DataLoader
├── offline.py      # OfflineDataLoader — synthetic test data
└── elia.py         # EliaDataLoader — Elia API (stub)

modules/            # Terraform for Azure deployment
```
