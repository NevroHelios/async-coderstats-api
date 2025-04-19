FROM python:3.13-slim

WORKDIR /app

# Copy project metadata first for faster rebuilds
COPY pyproject.toml .

# Copy the rest of the code
COPY . .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install .

# Expose the default FastAPI port
EXPOSE 8000

# Use the PORT env var if set by Azure, otherwise default to 8000
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]