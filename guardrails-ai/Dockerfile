FROM mcr.microsoft.com/devcontainers/python:3.10

# Guardrails AI pode precisar de pacotes específicos no futuro, 
# por enquanto mantemos o básico
RUN pip install --upgrade pip

COPY guardrails-ai/requirements.txt .
RUN pip install -r requirements.txt