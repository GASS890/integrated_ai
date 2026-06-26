from demo.demo_status import get_demo_status

status = get_demo_status()

print("demo_ready:", status.get("demo_ready"))
print("git:", status.get("version"))
print("tts default:", status.get("tts", {}).get("default_backend"))
print("piper_plus ready:", status.get("tts", {}).get("backends", {}).get("piper_plus", {}).get("ready"))
print("speaker worker:", status.get("speaker", {}).get("worker"))
print("memory:", status.get("memory"))
print("personality:", status.get("personality"))
