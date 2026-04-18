from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import os
import logging 
from datetime import datetime
import requests


# Konfiguracija logiranja u datoteku
logging.basicConfig(
    filename='access.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

# Inicijalizacija Flask aplikacije
app = Flask(__name__)
CORS(app)

# Sigurnosni API kljuc za pristup zasticenim endpointima
API_KEY = "foi-qwen-2026-lucija-sinko-k7mxq9p2"

# Rate limiter - ogranicava broj zahtjeva po IP adresi
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["30 per minute", "200 per hour"]
)

# Dekorator za provjeru API kljuca u zaglavlju zahtjeva
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"error": "Neautoriziran pristup"}), 401
        return f(*args, **kwargs)
    return decorated

# Konfiguracija Ollama servisa
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:14b"

# Lista za pohranu povijesti razgovora
conversation_history = []

# Putanja do frontend mape
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.before_request
def log_request():
    """Zapisuje svaki dolazni zahtjev u access.log"""
    has_token = request.headers.get("X-API-Key") == API_KEY
    logging.info(f"IP={request.remote_addr} | {request.method} {request.path} | token_valid={has_token}")

@app.route("/")
def serve_frontend():
    """Servira glavnu stranicu."""
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    """Servira statičke datoteke (CSS, JS, logo)."""
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/chat", methods=["POST"])
@require_api_key
def chat():
    """Prima korisničku poruku i prosljeđuje je Ollama modelu."""
    data = request.json
    user_message = data.get("message", "")
    system_prompt = data.get("system_prompt", "Ti si koristan AI asistent integriran u lokalni servis umjetne inteligencije. Odgovaraj isključivo na hrvatskom jeziku, koristeći akademski ton, preciznost i konkretnost. Ne koristi nikakve markdown oznake poput **, ##, *, - ni bilo kakve posebne znakove za formatiranje. Piši čistim tekstom bez ikakvih simbola za naglašavanje ili strukturiranje. Ako nemaš dovoljno podataka ili nisi siguran u točnost informacije, jasno obavijesti korisnika da ne raspolažeš pouzdanim podacima o tome. Nikada ne izmišljaj činjenice niti daj neprovjerene informacije.Obrati posebnu pozornost na pravilnu uporabu padeža, deklinacija i gramatičkih oblika hrvatskog jezika.")

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
    # Ukloni markdown formatiranje iz odgovora
    assistant_message = assistant_message.replace("**", "").replace("##", "").replace("*", "").replace("#", "")
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
@require_api_key
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
    

