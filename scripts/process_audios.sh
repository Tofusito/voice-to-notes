#!/bin/bash

# Directorios de entrada y salida
INPUT_DIR="/whisper/input"
OUTPUT_DIR="/whisper/output"

# Verificar si hay archivos en el directorio de entrada
for file in "$INPUT_DIR"/*.{wav,mp3,m4a,ogg,flac}; do
    if [ -f "$file" ]; then
        # Nombre del archivo sin la extensión
        filename=$(basename -- "$file")
        filename="${filename%.*}"

        # Convertir a .wav si el archivo no es un .wav
        if [ "${file##*.}" != "wav" ]; then
            ffmpeg -i "$file" -ar 16000 "$INPUT_DIR/$filename.wav"
            file="$INPUT_DIR/$filename.wav"
        fi

        # Ejecutar Whisper.cpp y guardar la transcripción en la carpeta de salida
        ./main -m models/ggml-base.bin -f "$file" --no-timestamps > "$OUTPUT_DIR/$filename.txt"

        # Eliminar el archivo de entrada procesado (opcional)
        #rm "$file"
    fi
    sleep 5
done