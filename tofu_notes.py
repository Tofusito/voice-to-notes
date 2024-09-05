import os
import sys
import subprocess
import time
import re
import requests
from python.checks import load_config, setup_ollama_and_model, print_status, save_config

def print_banner(message):
    """
    Imprime un mensaje de banner en la CLI.
    """
    print("\n" + "=" * 60)
    print(f"{message:^60}")
    print("=" * 60 + "\n")

def build_docker_image(image_name, dockerfile_dir):
    """
    Realiza el build de una imagen de Docker usando el Dockerfile en el directorio especificado.
    """
    print_status(f"Construyendo la imagen Docker '{image_name}'...")
    
    try:
        # Ejecutar el comando de construcción de la imagen
        subprocess.run(["docker", "build", "-t", image_name, dockerfile_dir], check=True)
        print_status(f"Imagen Docker '{image_name}' construida con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al construir la imagen Docker: {e}")
        raise

def docker_image_exists(image_name):
    """
    Verifica si una imagen de Docker ya existe.
    """
    try:
        result = subprocess.run(
            ["docker", "images", "-q", image_name],
            check=True,
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())  # Si hay un resultado, la imagen existe
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al verificar la imagen Docker: {e}")
        return False

def run_docker_container(config):
    """
    Ejecuta el contenedor Docker para procesar los archivos de audio con Whisper.cpp.
    Verifica si la imagen existe, si no, la construye a partir del Dockerfile.
    Solo se ejecuta si hay archivos en el directorio de input.
    """
    input_dir = config.get("input_dir")
    
    # Verificar si el directorio de entrada existe y tiene archivos
    if input_dir and os.path.isdir(input_dir):
        # Listar solo archivos no ocultos
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and not f.startswith('.')]
        
        if not files:
            print(f"No se detectaron archivos en {input_dir}. Docker no se ejecutará.")
            sys.exit(1)  # Esto detendrá la ejecución del programa completamente
        
        print(f"Archivos detectados en {input_dir}, continuando con la ejecución del contenedor Docker...")
    else:
        print(f"Error: El directorio '{input_dir}' no existe o no está configurado correctamente.")
        return

    image_name = "whisper-cpp-alpine"  # Nombre de la imagen que se construirá
    dockerfile_dir = os.path.dirname(os.path.abspath("tofu_notes.py"))  # Directorio donde está el Dockerfile
    
    # Verificar si la imagen ya existe
    if not docker_image_exists(image_name):
        print_status(f"La imagen Docker '{image_name}' no existe. Procediendo a construirla...")
        build_docker_image(image_name, dockerfile_dir)
    else:
        print_status(f"La imagen Docker '{image_name}' ya existe. No es necesario reconstruir.")

    # Ejecutar el contenedor
    print_banner("Iniciando procesamiento con Whisper.cpp")
    print_status("Ejecutando el contenedor Docker...")
    
    try:
        subprocess.run(
            ["docker", "run", "-it", "--rm", 
             "-v", f"{config['input_dir']}:/whisper/input",
             "-v", f"{config['output_dir']}:/whisper/output", 
             image_name],  # Usamos la imagen verificada o construida
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
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

    # Configura Ollama y el modelo
    setup_ollama_and_model(config)

    # Ejecuta el contenedor Docker
    run_docker_container(config)

    # Carga el template
    template = load_template("templates/template.md")

    # Procesa los archivos de texto
    process_files(template, config)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print_banner(f"Proceso completado en {elapsed_time:.2f} segundos")