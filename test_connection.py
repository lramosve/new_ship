import requests

try:
    response = requests.get('http://localhost:8080/health')
    print("Server response:", response.json())
except Exception as e:
    print("Failed to connect:", str(e))
