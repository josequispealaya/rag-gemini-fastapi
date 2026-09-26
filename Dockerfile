# Usamos una imagen oficial y liviana de Python
FROM python:3.11-slim

# Configuraciones para que Python corra más rápido y limpio en contenedores
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Creamos la carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero el archivo de dependencias
COPY pyproject.toml ./

# Instalamos las librerías (Docker usa esto para cachear y no descargar todo cada vez)
RUN pip install --no-cache-dir .

# Copiamos el resto de tu código fuente al contenedor
COPY . .

# Exponemos los puertos que usan FastAPI y Streamlit
EXPOSE 8000 8501