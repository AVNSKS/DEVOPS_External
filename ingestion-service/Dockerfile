# Use an official, lightweight Python run environment
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system --gid 10001 agronet \
    && adduser --system --uid 10001 --ingroup agronet agronet

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /app/main.py
RUN chown -R agronet:agronet /app

USER agronet

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
