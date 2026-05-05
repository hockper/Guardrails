FROM mcr.microsoft.com/devcontainers/python:3.10

# Dependências para NeMo
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY nemo-guardrails/requirements.txt .
RUN pip install -r requirements.txt
