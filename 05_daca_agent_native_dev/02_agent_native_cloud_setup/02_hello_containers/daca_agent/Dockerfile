FROM python:3.12-slim

# Set working directory
WORKDIR /code

# Copy code
COPY . .

# Install dependencies
RUN pip install uv

RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]