FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala pacotes do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto completo
COPY . .

# Expõe a porta padrão do Hugging Face (7860)
EXPOSE 7860

# Comando de inicialização: roda migrações, estáticos, cria superusuário e inicia o Gunicorn na porta 7860
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --no-input && python create_superuser.py && gunicorn --bind 0.0.0.0:7860 fut_stream.wsgi:application"]
