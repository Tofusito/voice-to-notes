from flask import Flask, request
import whisperx
import os
import gc
import threading
import time

# Configuración de directorios
input_folder = "/whisper/inputs"
output_folder = "/whisper/outputs"

# Configuración del modelo
device = "cuda"
batch_size = 16
compute_type = "float16"

# Cargar el modelo
model = whisperx.load_model("medium", device, compute_type=compute_type)

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def webhook():
    # Iniciar la verificación de archivos y transcripción en un hilo separado
    threading.Thread(target=verificar_y_transcribir, args=(input_folder, output_folder)).start()

    # Devolver respuesta inmediatamente
    return 'Webhook received. Processing files if available.', 200

def verificar_y_transcribir(input_folder, output_folder):
    start_time = time.time()
    timeout = 5 * 60  # 5 minutos en segundos
    check_interval = 30  # Intervalo de comprobación en segundos

    while time.time() - start_time < timeout:
        # Verificar si hay archivos en la carpeta de entrada
        if any(f.endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')) for f in os.listdir(input_folder)):
            print("Files detected. Starting transcription process.")
            transcribir_audio(input_folder, output_folder)
            return
        else:
            print("No files detected. Waiting to retry...")

        # Esperar antes de volver a comprobar
        time.sleep(check_interval)

    print("Timeout reached. No files found.")

def transcribir_audio(input_folder, output_folder):
    # Verificar que la carpeta de salida exista
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Procesar todos los archivos de audio en la carpeta de entrada
    for audio_file in os.listdir(input_folder):
        if audio_file.endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):  # Filtrar solo archivos de audio
            audio_path = os.path.join(input_folder, audio_file)
            print(f"Processing file: {audio_file}")

            try:
                # Cargar el audio
                audio = whisperx.load_audio(audio_path)

                # Transcribir
                result = model.transcribe(audio, batch_size=batch_size)

                # Alineación
                model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
                aligned_result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

                # Crear el archivo de salida en la carpeta output
                output_file = os.path.join(output_folder, os.path.splitext(audio_file)[0] + ".txt")
                with open(output_file, "w") as f:
                    for segment in aligned_result["segments"]:
                        f.write(segment["text"] + "\n")

            except Exception as e:
                print(f"Failed to process {audio_file}: {e}")

            finally:
                # Liberar memoria
                gc.collect()

if __name__ == '__main__':
    # Ejecutar el servidor Flask
    app.run(host='0.0.0.0', port=8888, debug=True, use_reloader=False)