# Usar Ubuntu 22.04 como imagen base
FROM ubuntu:22.04

# Establecer variables de entorno para no pedir confirmación durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar las dependencias necesarias
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    wget \
    ffmpeg \
    curl \
    bash \
    libcurl4-openssl-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Clonar el repositorio de whisper.cpp
RUN git clone https://github.com/ggerganov/whisper.cpp.git /whisper.cpp

# Establecer el directorio de trabajo
WORKDIR /whisper.cpp

# Construir whisper.cpp
RUN make

# Descargar el modelo base durante la construcción
RUN /bin/bash ./models/download-ggml-model.sh base

# Copiar el script en Bash al contenedor
COPY scripts/process_audios.sh /whisper/process_audios.sh

# Hacer el script ejecutable
RUN chmod +x /whisper/process_audios.sh

# Configurar el contenedor para ejecutar el script en Bash por defecto
CMD ["/bin/bash", "/whisper/process_audios.sh"]