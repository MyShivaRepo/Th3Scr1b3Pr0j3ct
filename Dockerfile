FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

# Copie des fichiers de dépendances en premier pour profiter du cache Docker
COPY pyproject.toml .

# Installation de uv puis des dépendances (sans -e pour éviter les conflits de chemins)
RUN pip install --no-cache-dir uv && \
    uv pip install --system "rdflib>=7.0.0" "streamlit>=1.35.0"

# Copie du code source
COPY src/ ./src/
COPY data/ ./data/

EXPOSE 1111

CMD ["streamlit", "run", "src/ui/app.py", \
     "--server.port=1111", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
