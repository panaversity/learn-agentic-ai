FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock .env /app/
RUN pip install uv
RUN uv sync --frozen
COPY . /app
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]