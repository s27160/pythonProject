FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    git \
    gcc \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
