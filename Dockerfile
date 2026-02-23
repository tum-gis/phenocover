# ── Stage 1: build wheels ────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install only the C-build toolchain needed to compile native extensions
# (numpy, scipy, matplotlib all need it on slim/alpine)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ── Stage 2: runtime image ───────────────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="joseph.gitahi@tum.de" \
    org.opencontainers.image.title="phenocover" \
    org.opencontainers.image.description="Weather-Enhanced Wheat Phenology and Ground Cover Estimation Tool" \
    org.opencontainers.image.source="https://github.com/tum-gis/phenocover"

# Create a non-root user and the writable logs directory
RUN useradd --create-home --shell /bin/bash phenocover \
    && mkdir -p /app/logs \
    && chown -R phenocover:phenocover /app

WORKDIR /app

# Install wheels built in the previous stage (no compiler needed here)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# Install the package itself (runs as root so pip can write to site-packages)
COPY --chown=phenocover:phenocover . .
RUN pip install --no-cache-dir --no-deps .

# Switch to non-root user
USER phenocover

ENTRYPOINT ["phenocover"]
CMD ["--help"]
