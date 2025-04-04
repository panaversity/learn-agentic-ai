# We will use this Dockerfile for Cloud and Kubernetes Environment
# Dependency Resolution Stage:
FROM python:3.12 as requirements-stage
LABEL maintainer="ameen-alam"
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
# Application Build Stage:
FROM python:3.12-slim
WORKDIR /code
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
# We will comment COPY .env /code/ later 
# COPY .env /code/
# Set up a non-root user for better security
RUN useradd --create-home --home-dir /home/appuser appuser \
    && chown -R appuser:appuser /code
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]