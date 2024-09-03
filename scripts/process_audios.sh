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

        # Variable para almacenar la ruta del archivo WAV generado (si aplica)
        original_file="$file"
        wav_file=""

        # Convertir a .wav si el archivo no es un .wav
        if [ "${file##*.}" != "wav" ]; then
            wav_file="$INPUT_DIR/$filename.wav"
            ffmpeg -i "$file" -ar 16000 "$wav_file"
            file="$wav_file"  # Actualizar la variable file para que apunte al nuevo archivo WAV
        fi

        # Ejecutar Whisper.cpp y guardar la transcripción en la carpeta de salida
        ./main -m models/ggml-base.bin -f "$file" --no-timestamps > "$OUTPUT_DIR/$filename.txt"

        # Eliminar el archivo WAV generado si no era el original
        if [ -n "$wav_file" ]; then
            rm "$wav_file"
        fi

        # Eliminar el archivo de entrada original
        rm "$original_file"
    fi
    sleep 5
done