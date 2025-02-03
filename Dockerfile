FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python-dev \
    libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN pip install --no-cache-dir -r req.txt

EXPOSE 8000

CMD ["python", "geoutils.py]
