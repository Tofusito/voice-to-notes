import requests

# URL base del webhook proporcionada por ngrok
url = "https://habemustrash.duckdns.org:8888"

# Construir la URL del webhook completa
webhook_url = f'{url}/transcribe'

# Datos a enviar
data = {'message': 'Hello from Python!'}
print('Sending data to webhook...')
print(data)

# Enviar una solicitud POST
response = requests.post(webhook_url, json=data)

# Imprimir la respuesta
print('Status Code:', response.status_code)
print('Response Text:', response.text)