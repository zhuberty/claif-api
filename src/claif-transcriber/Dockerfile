FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-alpine3.14-2024-03-11

# Install bash, curl, and necessary build tools for Poetry and dependencies
RUN apk add --no-cache bash curl gcc musl-dev ffmpeg git g++ make wget

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the system path
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy pyproject.toml and poetry.lock (if available)
COPY pyproject.toml poetry.lock* ./ 

# Install dependencies with Poetry
RUN poetry install --no-root --no-interaction --no-ansi

RUN git clone https://github.com/ggerganov/whisper.cpp.git

# Build whisper.cpp
RUN cd whisper.cpp && make && cd ..

# Create a link to the whisper.cpp binary
RUN ln -s /app/whisper.cpp/main /usr/local/bin/whisper

# Get the tinydiarize model
RUN whisper.cpp/models/download-ggml-model.sh small.en-tdrz

# Copy all project files
COPY . .

EXPOSE 8000

# Command to wait for Keycloak, DB, and start Uvicorn
CMD ["bash", "-c", "poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug"]
