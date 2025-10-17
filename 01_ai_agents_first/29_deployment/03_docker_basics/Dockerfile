FROM python:3.11-slim

WORKDIR /app

# Create a safe user so we do not run as root inside the container.
RUN useradd -m -u 1000 appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    CHAINLIT_HOST=0.0.0.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser

EXPOSE 8000

CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]