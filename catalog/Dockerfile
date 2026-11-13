FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CATALOG_PATH=/srv/data/ms-learn-api.json

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# The catalog is downloaded when the image is built, so the running service makes no outbound calls.
# The build fails if the download is incomplete. Rebuild the image to refresh the catalog.
RUN python -m app.fetch "$CATALOG_PATH"

RUN useradd --system --uid 10001 appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
