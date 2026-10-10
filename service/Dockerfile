# Multi-stage build for QuantX REST sidecar
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy layered packages and service
COPY packages /build/packages
COPY service /build/service

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        -e /build/packages/quantx-core \
        -e /build/packages/quantx-crypto-adapters \
        -e /build/packages/quantx-combiners \
        -e /build/packages/quantx-registry \
        -e /build/packages/quantx-session \
        -e /build/service

FROM python:3.11-slim AS runner

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /build /app

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["quantx", "run", "--file", "/etc/quantx/quantx.yaml"]
