FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmagic1 \
        libmagic-dev \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (IMPORTANT!)
ENV PATH="/root/.local/bin:$PATH"

# Copy only poetry files first (for Docker layer caching)
COPY pyproject.toml poetry.lock ./

# Install dependencies via Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the project
COPY . .

# Expose port (optional if you're running a webserver)
EXPOSE 8000

# Command to run the application (adapt to your app)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:9000"]
