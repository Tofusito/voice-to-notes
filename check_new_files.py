import os
import json
import subprocess

# Cargar la configuración desde config.json
CONFIG_FILE = "config/config.json"

def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def check_and_run():
    config = load_config()
    input_dir = config.get("input_dir")

    if input_dir and os.path.isdir(input_dir):
        files = os.listdir(input_dir)
        if files:
            print(f"Archivos detectados en {input_dir}, ejecutando el script principal...")
            subprocess.run(["python3", "tofu_notes.py"])
        else:
            print(f"No se detectaron archivos en {input_dir}.")
    else:
        print(f"Error: El directorio '{input_dir}' no existe o no está configurado correctamente.")

if __name__ == "__main__":
    check_and_run()