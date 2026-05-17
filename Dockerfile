FROM python:3.12.1-slim@sha256:a64ac5be6928c6a94f00b16e09cdf3ba3edd44452d10ffa4516a58004873573e

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        i2c-tools \
        libgpiod2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN useradd --system --uid 1000 --home /app --shell /usr/sbin/nologin app \
    && mkdir -p /data_storage /homekit_state \
    && chown -R app:app /data_storage /homekit_state

COPY --chown=app:app . .

USER app

CMD ["python", "app.py"]
