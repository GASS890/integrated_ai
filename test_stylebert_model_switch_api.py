import requests

BASE = "http://127.0.0.1:8000"

print("models:")
r = requests.get(BASE + "/stylebert/models")
print(r.status_code)
print(r.json())

models = r.json().get("models", [])
if not models:
    raise RuntimeError("Style-Bert model not found")

first = models[0]

print("select:")
r = requests.post(BASE + "/stylebert/select", json={
    "model_id": first["model_id"],
    "speaker_id": 0,
    "style": "Neutral",
    "style_weight": 5.0,
    "length": 1.0,
})
print(r.status_code)
print(r.json())
