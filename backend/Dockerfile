FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
USER 10001
EXPOSE 5000
CMD ["waitress-serve", "--listen=0.0.0.0:5000", "--max-request-header-size=16384", "--max-request-body-size=8388608", "app.app:app"]
