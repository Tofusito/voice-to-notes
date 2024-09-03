import os
import subprocess
import requests
import json
import time
import re

# Archivos y rutas
CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
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

def get_valid_directory_path(prompt):
    """
    Solicita al usuario una ruta de directorio y verifica que exista.
    Si no existe, solicita la ruta nuevamente.
    """
    while True:
        path = input(prompt)
        if os.path.isdir(path):
            return path
        else:
            print(f"❌ Error: El directorio '{path}' no existe. Por favor, intenta nuevamente.")

def load_config():
    """
    Carga la configuración desde un archivo config.json.
    Si no existe, solicita al usuario las rutas y guarda la configuración.
    """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if os.path.exists(CONFIG_FILE):
        print_status("Cargando configuración desde config.json...")
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
    else:
        print_status("config.json no encontrado. Solicitando rutas al usuario...")
        input_dir = get_valid_directory_path("Por favor, ingresa la ruta COMPLETA de la carpeta de input con las notas de voz: ")
        output_dir = get_valid_directory_path("Por favor, ingresa la ruta COMPLETA del directorio de output para los archivos markdown: ")
        output_md_dir = get_valid_directory_path("Por favor, ingresa la ruta COMPLETA del directorio para los archivos markdown generados: ")

        config = {
            "input_dir": input_dir,
            "output_dir": output_dir,
            "output_md_dir": output_md_dir,
            "model": "llama3.1:latest",
            "api_url": "http://127.0.0.1:11434/api/chat"
        }

        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
        print_status("Configuración guardada en config.json.")

    return config

def run_docker_container(config):
    """
    Ejecuta el contenedor Docker para procesar los archivos de audio con Whisper.cpp.
    """
    print_banner("Iniciando procesamiento con Whisper.cpp")
    print_status("Ejecutando el contenedor Docker...")
    
    try:
        subprocess.run(
            ["docker", "run", "-it", "--rm", 
             "-v", f"{config['input_dir']}:/whisper/input",
             "-v", f"{config['output_dir']}:/whisper/output", 
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

def send_request(content, config, title_request=False):
    """
    Envía una solicitud a la API con el contenido dado.
    Si title_request es True, se pide a la API un título simple para el archivo.
    """
    headers = {
        "Content-Type": "application/json"
    }

    if title_request:
        data = {
            "model": config["model"],
            "messages": [
                {"role": "user", "content": f"Dado el siguiente texto, dame SOLO un filename con el formato Titulo_de_la_nota que explique fácil de que va el texto, sólo el filename:\n\n{content}"}
            ],
            "stream": False
        }
    else:
        data = {
            "model": config["model"],
            "messages": [
                {"role": "user", "content": content}
            ],
            "stream": False
        }
    
    print_status(f"Enviando {'solicitud de título' if title_request else 'solicitud'} a la API...")
    response = requests.post(config["api_url"], headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print_status("Solicitud completada con éxito.")
        response_json = response.json()
        message_content = response_json.get("message", {}).get("content", "")
        
        if message_content:
            return message_content.strip()
        else:
            print("❌ No se recibió contenido en la respuesta de la API.")
            return None
    else:
        print(f"❌ Error en la solicitud: {response.status_code}")
        return None

def save_to_markdown(filename, content, config):
    """
    Guarda el contenido en un archivo markdown dentro de la carpeta output_md.
    """
    if not os.path.exists(config['output_md_dir']):
        os.makedirs(config['output_md_dir'])
    
    output_filepath = os.path.join(config['output_md_dir'], f"{filename}.md")
    
    with open(output_filepath, 'w') as file:
        file.write(content)
    
    print_status(f"Resultado guardado en {output_filepath}")
    return output_filepath

def process_files(template, config):
    """
    Procesa todos los archivos .txt en el directorio OUTPUT_DIR.
    """
    if not os.path.exists(config['output_dir']):
        print(f"❌ Error: El directorio {config['output_dir']} no existe.")
        return

    files_processed = 0

    for filename in os.listdir(config['output_dir']):
        if filename.endswith(".txt"):
            print_status(f"Procesando archivo: {filename}")
            filepath = os.path.join(config['output_dir'], filename)
            with open(filepath, 'r') as file:
                content = file.read().strip()
                if content:
                    full_content = template + "\n\n" + content
                    
                    # Primera solicitud para obtener el contenido principal
                    response_content = send_request(full_content, config)
                    
                    if response_content:
                        # Segunda solicitud para obtener un título simple
                        title = send_request(response_content, config, title_request=True)
                        
                        if title:
                            # Limpiar el título para ser usado como nombre de archivo
                            valid_title = re.sub(r'[^\w\-_\. ]', '_', title).strip()
                            markdown_filepath = save_to_markdown(valid_title, response_content, config)
                            
                            if os.path.exists(markdown_filepath):
                                # Eliminar el archivo .txt después de generar el archivo markdown
                                os.remove(filepath)
                                print_status(f"Archivo de texto {filepath} eliminado.")
                                
                            files_processed += 1
                        else:
                            print(f"❌ No se pudo obtener un título para {filename}.")
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
    
    # Carga la configuración
    config = load_config()

    # Primero, ejecuta el contenedor Docker
    run_docker_container(config)

    # Luego, carga el template
    template = load_template(TEMPLATE_FILE)

    # Procesa los archivos de texto
    process_files(template, config)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print_banner(f"Proceso completado en {elapsed_time:.2f} segundos")