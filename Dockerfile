FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
COPY src/ ./src/
RUN uv sync --no-dev --frozen

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "src/imbalance_dashboard/app.py", \
     "--server.address=0.0.0.0", "--server.port=8501"]
