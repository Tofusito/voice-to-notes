import os
import subprocess
import requests
import json
import time

# Configuración de la API y rutas
MODEL = "llama3.1:latest"
URL = "http://127.0.0.1:11434/api/chat"
OUTPUT_DIR = "outputs"
OUTPUT_MD_DIR = "outputs_md"
TEMPLATE_FILE = "templates/template.md"

def print_banner(message):
    """
    Imprime un mensaje de banner en la CLI.
    """
    print("\n" + "=" * 60)
    print(f"{message:^60}")
    print("=" * 60 + "\n")

def print_status(message):
    """
    Imprime un mensaje de estado simple.
    """
    print(f"➡️  {message}")

def run_docker_container():
    """
    Ejecuta el contenedor Docker para procesar los archivos de audio con Whisper.cpp.
    """
    print_banner("Iniciando procesamiento con Whisper.cpp")
    print_status("Ejecutando el contenedor Docker...")
    
    try:
        subprocess.run(
            ["docker", "run", "-it", "--rm", 
             "-v", f"{os.getcwd()}/inputs:/whisper/input",
             "-v", f"{os.getcwd()}/outputs:/whisper/output", 
             "whisper-cpp-alpine"], 
            check=True,
            stdout=subprocess.DEVNULL,  # Redirigir la salida estándar a DEVNULL
            stderr=subprocess.DEVNULL   # Redirigir la salida de error a DEVNULL
        )
        print_status("Procesamiento de audio completado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar el contenedor Docker: {e}")
        raise

def load_template(template_file):
    """
    Carga el contenido del template Markdown desde el archivo.
    """
    print_status("Cargando el template Markdown...")
    with open(template_file, 'r') as file:
        return file.read()

def send_request(content):
    """
    Envía una solicitud a la API con el contenido dado.
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": content}
        ],
        "stream": False
    }
    
    print_status("Enviando solicitud a la API...")
    response = requests.post(URL, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print_status("Solicitud completada con éxito.")
        response_json = response.json()
        message_content = response_json.get("message", {}).get("content", "")
        return message_content
    else:
        print(f"❌ Error en la solicitud: {response.status_code}")
        return None

def save_to_markdown(filename, content):
    """
    Guarda el contenido en un archivo markdown dentro de la carpeta outputs_md.
    """
    if not os.path.exists(OUTPUT_MD_DIR):
        os.makedirs(OUTPUT_MD_DIR)
    
    output_filepath = os.path.join(OUTPUT_MD_DIR, filename)
    
    with open(output_filepath, 'w') as file:
        file.write(content)
    
    print_status(f"Resultado guardado en {output_filepath}")

def process_files(template):
    """
    Procesa todos los archivos .txt en el directorio OUTPUT_DIR.
    """
    if not os.path.exists(OUTPUT_DIR):
        print(f"❌ Error: El directorio {OUTPUT_DIR} no existe.")
        return

    files_processed = 0

    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".txt"):
            print_status(f"Procesando archivo: {filename}")
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'r') as file:
                content = file.read().strip()
                if content:
                    full_content = template + "\n\n" + content
                    response = send_request(full_content)
                    if response:
                        md_filename = filename.replace(".txt", ".md")
                        save_to_markdown(md_filename, response)
                        files_processed += 1
                    else:
                        print(f"❌ No se pudo obtener una respuesta para {filename}.")
                else:
                    print(f"❌ El archivo {filename} está vacío.")
    
    if files_processed > 0:
        print_banner(f"Procesamiento completado: {files_processed} archivos procesados")
    else:
        print_status("No se procesaron archivos.")

if __name__ == "__main__":
    start_time = time.time()

    print_banner("Inicio del proceso completo")
    
    # Primero, ejecuta el contenedor Docker
    run_docker_container()

    # Luego, carga el template
    template = load_template(TEMPLATE_FILE)

    # Procesa los archivos de texto
    process_files(template)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print_banner(f"Proceso completado en {elapsed_time:.2f} segundos")