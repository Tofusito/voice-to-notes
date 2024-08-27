import os
import requests
import json

# Configuración de la API
MODEL = "llama3.1:latest"
URL = "http://127.0.0.1:11434/api/chat"
OUTPUT_DIR = "outputs"
OUTPUT_MD_DIR = "outputs_md"
TEMPLATE_FILE = "templates/template.md"

def load_template(template_file):
    """
    Carga el contenido del template Markdown desde el archivo.
    """
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
    
    # Realizar la solicitud POST
    response = requests.post(URL, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        # Extraer el contenido del mensaje de la respuesta
        response_json = response.json()
        message_content = response_json.get("message", {}).get("content", "")
        return message_content
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return None

def save_to_markdown(filename, content):
    """
    Guarda el contenido en un archivo markdown dentro de la carpeta outputs_md.
    """
    # Asegurarse de que la carpeta de salida exista
    if not os.path.exists(OUTPUT_MD_DIR):
        os.makedirs(OUTPUT_MD_DIR)
    
    # Construir la ruta completa del archivo de salida
    output_filepath = os.path.join(OUTPUT_MD_DIR, filename)
    
    # Guardar el contenido en el archivo
    with open(output_filepath, 'w') as file:
        file.write(content)

def process_files(template):
    """
    Procesa todos los archivos .txt en el directorio OUTPUT_DIR.
    """
    if not os.path.exists(OUTPUT_DIR):
        print(f"Error: El directorio {OUTPUT_DIR} no existe.")
        return

    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'r') as file:
                content = file.read().strip()
                if content:
                    print(f"Procesando archivo: {filename}")
                    full_content = template + "\n\n" + content
                    response = send_request(full_content)
                    if response:
                        # Crear el nombre del archivo markdown de salida
                        md_filename = filename.replace(".txt", ".md")
                        save_to_markdown(md_filename, response)
                        print(f"Resultado guardado en: {md_filename}")
                    else:
                        print(f"No se pudo obtener una respuesta para {filename}.\n")
                else:
                    print(f"El archivo {filename} está vacío.\n")

if __name__ == "__main__":
    # Cargar el template
    template = load_template(TEMPLATE_FILE)
    # Procesar los archivos de texto
    process_files(template)