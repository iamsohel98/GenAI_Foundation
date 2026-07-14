# =========================================================
# Dockerfile - Home Rent Prediction Flask App
# =========================================================
# Multi-stage-style, production-oriented image:
#   - Slim Python base for a small footprint
#   - Non-root user for security
#   - Model is trained INSIDE the image build (so the image is
#     self-contained and reproducible), then served via gunicorn
# =========================================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files & buffering stdout (better logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies required by scikit-learn / pandas wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching -- only
# re-installs when requirements.txt actually changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source
COPY . .

# Generate the dataset (if not already present) and train the model
# as part of the image build, so the container is immediately ready
# to serve predictions with no extra runtime steps.
RUN python src/generate_data.py \
    && python src/data_validation.py \
    && MLFLOW_TRACKING_URI="file:///app/mlruns" python src/train.py

# Create a non-root user and switch to it (security best practice)
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Docker-level health check, hits the Flask /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request,sys; \
    sys.exit(0) if urllib.request.urlopen('http://localhost:5000/health').getcode()==200 else sys.exit(1)"

# Use gunicorn for a production-grade WSGI server (instead of Flask's dev server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "60", "app:app"]
