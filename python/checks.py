import os
import subprocess
import json

# Archivos y rutas
CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
RECOMMENDED_MODELS = ["llama3.1:8b-instruct-q8_0", "llama2:7b-instruct", "mistral:7b"]

def print_status(message):
    """
    Imprime un mensaje de estado simple.
    """
    print(f"➡️  {message}")

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
        print_status("config.json no encontrado. Creando nueva configuración.")
        config = {
            "input_dir": "",
            "output_dir": "",
            "output_md_dir": "",
            "model": "",
            "api_url": "http://127.0.0.1:11434/api/chat"
        }
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
    return config

def save_config(config):
    """
    Guarda la configuración en el archivo config.json.
    """
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)
    print_status("Configuración actualizada y guardada en config.json.")

def check_command_installed(command):
    """
    Verifica si un comando está instalado en el sistema.
    """
    try:
        subprocess.run([command, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ollama():
    """
    Instala Ollama en MacOS.
    """
    print_status("Instalando Ollama en MacOS...")
    try:
        subprocess.run(["brew", "install", "ollama"], check=True)
        print_status("Ollama instalado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar Ollama: {e}")

def check_ollama_installed():
    """
    Verifica si Ollama está instalado. Si no lo está, lo instala.
    """
    ollama_installed = check_command_installed("ollama")
    if not ollama_installed:
        print("❌ Ollama no está instalado.")
        install_ollama()

def get_ollama_models():
    """
    Ejecuta 'ollama list' para obtener solo los nombres de los modelos disponibles en el sistema.
    """
    try:
        result = subprocess.run(["ollama", "list"], check=True, capture_output=True, text=True)
        
        # Separar las líneas de salida
        lines = result.stdout.splitlines()
        
        # Ignorar la primera línea de encabezado ("NAME ID SIZE MODIFIED")
        models = []
        for line in lines[1:]:  # Saltamos el encabezado
            # Separar por espacio/tabulación y tomar la primera columna, que es el nombre del modelo
            model_name = line.split()[0]
            models.append(model_name)
        
        return models
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar 'ollama list': {e}")
        return []

def install_model(model):
    """
    Instala un modelo especificado en Ollama.
    """
    print_status(f"Instalando modelo {model}...")
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        print_status(f"Modelo {model} instalado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar el modelo {model}: {e}")

def prompt_model_choice(available_models, config):
    """
    Ofrece al usuario la opción de instalar un modelo o elegir uno de la lista existente.
    Si el valor de 'model' ya está en config.json, no se pregunta por el modelo.
    """
    # Si el modelo ya está configurado en config.json, no preguntar
    if config.get("model"):
        print_status(f"Modelo '{config['model']}' ya configurado en config.json.")
        return

    if available_models:
        # Mostrar modelos con numeración
        for idx, model in enumerate(available_models, start=1):
            print(f"[{idx}] {model}")
        
        install_new = input("¿Deseas instalar un nuevo modelo (s/n)? ").lower()
        if install_new == 's':
            model_choice = input(f"Especifica un modelo para instalar o presiona Enter para instalar '{RECOMMENDED_MODELS[0]}': ")
            if not model_choice:
                model_choice = RECOMMENDED_MODELS[0]
            elif model_choice not in RECOMMENDED_MODELS:
                print(f"❌ Modelo no recomendado. Elige entre: {', '.join(RECOMMENDED_MODELS)}.")
                return
            install_model(model_choice)
        else:
            # Pedir que el usuario seleccione el número del modelo
            model_index = input(f"Elige el número del modelo de la lista (1-{len(available_models)}): ")
            try:
                model_index = int(model_index)
                if model_index < 1 or model_index > len(available_models):
                    print(f"❌ Selección inválida. Debes elegir un número entre 1 y {len(available_models)}.")
                    return
                model_choice = available_models[model_index - 1]
            except ValueError:
                print("❌ Entrada inválida. Debes ingresar un número.")
                return
    else:
        print("No hay modelos disponibles. Instalando modelo recomendado por defecto.")
        model_choice = input(f"Especifica un modelo para instalar o presiona Enter para instalar '{RECOMMENDED_MODELS[0]}': ")
        if not model_choice:
            model_choice = RECOMMENDED_MODELS[0]
        elif model_choice not in RECOMMENDED_MODELS:
            print(f"❌ Modelo no recomendado. Elige entre: {', '.join(RECOMMENDED_MODELS)}.")
            return
        install_model(model_choice)

    # Guardar el modelo seleccionado en la configuración
    config["model"] = model_choice
    save_config(config)

def setup_ollama_and_model(config):
    """
    Configura Ollama y el modelo a utilizar.
    """
    # Verifica si Ollama está instalado
    check_ollama_installed()

    # Lista los modelos instalados en Ollama
    available_models = get_ollama_models()

    # Ofrecer instalación o selección de modelo
    prompt_model_choice(available_models, config)

def check_docker_installed():
    """
    Verifica si Docker está instalado.
    """
    return check_command_installed("docker")

def is_docker_running():
    """
    Verifica si Docker está en ejecución.
    """
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def start_docker():
    """
    Inicia Docker. En macOS, usa 'open /Applications/Docker.app'. 
    En Linux, se puede usar 'sudo systemctl start docker'.
    """
    print_status("Iniciando Docker...")
    try:
        if os.uname().sysname == 'Darwin':  # Para macOS
            subprocess.run(["open", "/Applications/Docker.app"], check=True)
        else:  # Para Linux
            subprocess.run(["sudo", "systemctl", "start", "docker"], check=True)
        print_status("Docker iniciado.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al intentar iniciar Docker: {e}")

def setup_docker():
    """
    Verifica si Docker está instalado y corriendo. Si no está corriendo, intenta iniciarlo.
    """
    if not check_docker_installed():
        print("❌ Docker no está instalado. Por favor, instala Docker para continuar.")
        return

    if not is_docker_running():
        print("⚠️ Docker no está en ejecución.")
        start_docker()
    else:
        print_status("Docker está en ejecución.")