FROM python:3.12-slim
WORKDIR /app
# Install system dependencies required for potential Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock .env /app/
RUN pip install uv
RUN uv sync --frozen
COPY . /app
EXPOSE 8001
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]