# Qwen 3:14B - Lokalni AI Servis

Završni rad -  Praktična primjena otvorenog LLM modela Qwen 3-14B kroz izgradnju lokalnog servisa umjetne inteligencije. 


**Mentor:** Prof. dr. sc. Markus Schatten
**Studentica:** Lucija Šinko
**Fakultet:** FOI, Sveučilište u Zagrebu
**Akademska godina:** 2025./2026.

## Tehnologije
- Python 3.13 + Flask
- Ollama + Qwen 3-14B
- HTML / CSS / JavaScript

## Struktura projekta

```
backend/
├── app.py
├── test_performance.py
└── requirements.txt

frontend/
├── index.html
├── style.css
├── script.js
└── logo.png
```

## Preduvjeti
- Python 3.10+
- Ollama (https://ollama.com/download)
- NVIDIA GPU s min. 8 GB VRAM-a

## Pokretanje

1. Preuzimanje modela:
```
ollama pull qwen3:14b
```

2. Instalacija Python ovisnosti:
```
cd backend
pip install -r requirements.txt
```

3. Pokretanje backend servera:
```
python app.py
```

4. Otvoriti `frontend/index.html` u browseru

