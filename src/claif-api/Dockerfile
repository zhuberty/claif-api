FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-alpine3.14-2024-03-11

# Install bash, curl, and necessary build tools for Poetry and dependencies
RUN apk add --no-cache bash curl gcc musl-dev postgresql-dev

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the system path
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy pyproject.toml and poetry.lock (if available)
COPY pyproject.toml poetry.lock* ./ 

# Install dependencies with Poetry
RUN poetry install --no-root --no-interaction --no-ansi

# Copy all project files
COPY . .

# Make the database and Keycloak wait scripts executable
RUN chmod +x /app/scripts/wait_for_db.sh /app/scripts/wait_for_keycloak.sh

EXPOSE 8000

# Command to wait for Keycloak, DB, and start Uvicorn
CMD ["bash", "-c", "./scripts/wait_for_db.sh claif-db:5432 && ./scripts/wait_for_keycloak.sh keycloak:8080 && poetry run uvicorn main:app --host 0.0.0.0 --port 8000"]
