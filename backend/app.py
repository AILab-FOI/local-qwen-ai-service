from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Inicijalizacija Flask aplikacije
app = Flask(__name__)
CORS(app)

# Konfiguracija Ollama servisa
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:14b"

# Lista za pohranu povijesti razgovora
conversation_history = []

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    system_prompt = data.get("system_prompt", "Ti si koristan AI asistent. Odgovaraj jasno i koncizno.")

    # Dodavanje korisničke poruke u povijest razgovora
    conversation_history.append({"role": "user", "content": user_message})
    
    # Kreiranje liste poruka: system prompt + cijela povijest razgovora
    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    # Slanje zahtjeva Ollama servisu
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False
        })
        response_data = response.json()
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Ollama servis nije pokrenut."}), 503
    
    # Izvuci odgovor modela i spremi u povijest
    assistant_message = response_data["message"]["content"]   
    conversation_history.append({"role": "assistant", "content": assistant_message})

    return jsonify({"response": assistant_message})

if __name__ == "__main__":
    print("Backend pokrenut na http://localhost:5000")
    app.run(debug=True, port=5000)
    

