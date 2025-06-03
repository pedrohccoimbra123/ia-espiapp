import requests

url = "http://localhost:8000/match"
payload = {
    "user_query": "Quero um lugar histórico em Belém"
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Resposta da API:", response.json())
else:
    print(f"Erro {response.status_code}: {response.text}")
