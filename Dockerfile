# Usa una imagen base de NVIDIA con CUDA
FROM nvidia/cuda:12.6.0-base-ubuntu22.04

# Establecer el directorio de trabajo
WORKDIR /whisper

# Agregar el repositorio de NVIDIA y actualizar paquetes
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:graphics-drivers/ppa && \
    apt-get update

# Instalar cuDNN (última versión compatible con CUDA 12.6)
RUN apt-get install -y --no-install-recommends \
    libcudnn8 \
    libcudnn8-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias del sistema y herramientas básicas
RUN apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    lsb-release \
    ffmpeg \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar las dependencias de Python
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copiar los archivos necesarios al contenedor
COPY python/notes-to-text.py .
COPY python/test.py .

# Exponer el puerto en el que Flask escuchará
EXPOSE 8888

# Ejecutar el script Python
CMD ["python3", "notes-to-text.py"]
