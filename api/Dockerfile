# /home/deployer/scraper/api/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias (ajusta si necesitas más)
RUN pip install --no-cache-dir fastapi uvicorn httpx beautifulsoup4 lxml pydantic

# Copiar todo el contenido del directorio api/ al contenedor
COPY . .

# Exponer el puerto (opcional, útil para debug)
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
