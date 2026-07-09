# -----------------------------------------------------------------------------
# Local AI Assistant — application image (Phase 1)
# -----------------------------------------------------------------------------
# This image contains ONLY the Python assistant app. It does not bundle a model
# or a GPU runtime. On the Mac Mini it talks to Ollama running natively (which
# uses the M4 GPU via Metal). See docker-compose.yml for how services connect.
# -----------------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Install optional Python deps first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source. (Outputs are mounted as a volume at runtime.)
COPY src ./src
COPY .env.example ./.env.example

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OUTPUTS_DIR=outputs \
    TTS_BACKEND=none

# Default: run the LLM smoke test. Override in compose or on the CLI.
CMD ["python", "src/scripts/test_llm.py"]
