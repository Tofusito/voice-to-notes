import os
import json
import subprocess

# Cargar la configuración desde config.json
CONFIG_FILE = "config/config.json"

def load_config():
    """
    Carga la configuración desde el archivo config.json.
    """
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def check_and_run():
    """
    Verifica si hay archivos en el directorio de input, y si los hay, ejecuta el script principal.
    """
    config = load_config()
    input_dir = config.get("input_dir")

    if input_dir and os.path.isdir(input_dir):
        # Listar solo archivos no ocultos
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and not f.startswith('.')]
        if files:
            print(f"Archivos detectados en {input_dir}, ejecutando el script principal...")
            subprocess.run(["python3", "tofu_notes.py"])
        else:
            print(f"No se detectaron archivos en {input_dir}.")
    else:
        print(f"Error: El directorio '{input_dir}' no existe o no está configurado correctamente.")

if __name__ == "__main__":
    check_and_run()