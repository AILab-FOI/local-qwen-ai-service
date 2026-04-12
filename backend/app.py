from flask import Flask, request, jsonify, send_from_directory
import os
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

# Putanja do frontend mape
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route("/")
def serve_frontend():
    """Servira glavnu stranicu."""
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    """Servira statičke datoteke (CSS, JS, logo)."""
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/chat", methods=["POST"])
def chat():
    """Prima korisničku poruku i prosljeđuje je Ollama modelu."""
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

    # Izračun performansi iz Ollama metapodataka
    eval_count = response_data.get("eval_count", 0)
    eval_duration = response_data.get("eval_duration", 0)
    prompt_eval_count = response_data.get("prompt_eval_count", 0)
    total_duration = response_data.get("total_duration", 0)

    tokens_per_second = 0
    if eval_duration > 0:
        tokens_per_second = eval_count / (eval_duration / 1_000_000_000)

    return jsonify({"response": assistant_message,
                    "performance": {
                        "generirani_tokeni": eval_count,
                        "tokeni_u_promptu": prompt_eval_count,
                        "tokeni_po_sekundi": round(tokens_per_second, 2),
                        "vrijeme_generiranja_s": round(eval_duration / 1_000_000_000, 2),
                        "ukupno_vrijeme_s": round(total_duration / 1_000_000_000, 2),
                        "poruka_u_kontekstu": len(conversation_history)
                    }
                    })

@app.route("/reset", methods=["POST"])
def reset():
    """Briše povijest razgovora."""
    global conversation_history
    conversation_history = []
    return jsonify({"status": "Povijest razgovora obrisana."})

@app.route("/health", methods=["GET"])
def health():
    """Provjerava je li Ollama servis aktivan."""
    try:
        r = requests.get("http://localhost:11434/api/tags")
        models = [m["name"] for m in r.json().get("models", [])]
        return jsonify({"status": "OK", "dostupni_modeli": models})
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "Ollama nije dostupna"}), 503


if __name__ == "__main__":
    print("Backend pokrenut na http://localhost:5000")
    app.run(debug=True, port=5000)
    

