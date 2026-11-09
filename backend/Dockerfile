
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python project metadata
COPY pyproject.toml ./

# Copy application packages
COPY backend ./backend
COPY packages ./packages

# Install application and dependencies
RUN pip install --upgrade pip && pip install .

# Render supplies PORT at runtime
EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
