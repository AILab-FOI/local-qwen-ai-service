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
qwen-local-ai/
├── backend/
│   ├── app.py
│   ├── test_performance.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── logo.png
├── generiraj_grafove.py
├── rezultati_context_length.csv
├── rezultati_system_prompts.csv
├── graf_brzina_vs_kontekst.pdf
├── graf_duljina_po_promptu.pdf
├── access.log
├── .gitignore
├── LICENSE
└── README.md
```
## Pokretanje

### Opcija 1: Lokalno pokretanje

Za pokretanje na vlastitom računalu.

**Preduvjeti:**
- Python 3.10+
- Ollama (https://ollama.com/download)
- NVIDIA GPU s min. 8 GB VRAM-a

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

4. Otvoriti `http://localhost:5000` u browseru

### Opcija 2: Udaljeni pristup

Aplikacija je dostupna na: **https://openfoi.com**

Udaljeni pristup ostvaren je putem trajnog Cloudflare Tunnela koji povezuje domenu s lokalnim Flask backend serverom.

**Preduvjeti (na računalu koje pokreće model):**
- Ollama s preuzetim Qwen 3-14B modelom
- Cloudflared instaliran kao Windows servis (pokreće se automatski)

**Pokretanje:**
```
cd backend
python app.py
```

Aplikacija je automatski dostupna na https://openfoi.com.

**Napomena:** Računalo s modelom mora biti uključeno i backend pokrenut.



## Sigurnosne mjere

Aplikacija je zaštićena višeslojnim sigurnosnim mehanizmima radi smanjenja 
izloženosti javno dostupnog endpointa na domeni openfoi.com.

### Identificirane prijetnje

Javna dostupnost aplikacije putem Cloudflare Tunnela uvodi sljedeće 
potencijalne prijetnje:

1. Neovlašteni pristup API endpointima
2. Preopterećenje sustava automatiziranim zahtjevima
3. Cross-Site Scripting (XSS) kroz korisnički unos
4. Izloženost privatne IP adrese (riješeno reverse tunnel arhitekturom)

### Implementirane mjere

**Izolacija konverzacija po sesiji** - backend pohranjuje povijest 
razgovora u memorijski rječnik `conversations` gdje je ključ jedinstveni 
`session_id` (UUID generiran na frontendu kroz `crypto.randomUUID()` pri 
svakom učitavanju stranice). Time se postiže razdvajanje konverzacija 
između istovremenih korisnika - svaki browser tab dobiva vlastiti, 
izolirani kontekst. Povijest razgovora nije perzistentna; briše se pri 
ponovnom pokretanju backend aplikacije ili osvježavanju stranice korisnika.

**Reverse tunnel arhitektura** - Cloudflare Tunnel uspostavlja trajnu izlaznu 
vezu između lokalnog računala i Cloudflareove edge mreže.

**Autentifikacija API ključem** - osjetljivi endpointi `/chat` i `/reset` 
zaštićeni su provjerom tajnog ključa u HTTP zaglavlju `X-API-Key`. 

**Rate limiting** - biblioteka Flask-Limiter ograničava broj zahtjeva po 
IP adresi na 30 u minuti, odnosno 200 u satu. Pri prekoračenju poslužitelj 
vraća HTTP 429 bez prosljeđivanja zahtjeva Ollama servisu, čime se štiti 
GPU od preopterećenja.

**XSS zaštita** - frontend JavaScript sadrži funkciju `escapeHtml()` koja 
pretvara korisnički unos u siguran tekstualni sadržaj prije umetanja u DOM, 
čime se sprječava izvršavanje injiciranog HTML ili JavaScript koda.

### Namjerno otvoreni endpointi

Rute `/` i `/<path:filename>` ostaju javno dostupne jer serviraju statičke 
datoteke frontenda (HTML, CSS, JavaScript, logo). Ruta `/health` također je 
otvorena kao dijagnostički endpoint za provjeru statusa Ollama servisa.

### Ograničenja

Implementirane mjere postavljene su prema kontekstu završnog rada, a ne 
prema standardima produkcijske primjene. Ključne napomene:

- API ključ je ugrađen u frontend kod radi jednostavnosti demonstracije. 
  U produkcijskom okruženju koristila bi se prava korisnička autentifikacija 
- Rate limiting je memorijski baziran i resetira se pri ponovnom pokretanju 
  aplikacije. Za produkciju bi se koristio perzistentni storage.
- Aplikacija je dostupna samo dok je lokalno računalo uključeno i backend 
  pokrenut.
  - Konverzacije se ne perzistiraju između restarta backenda niti preko 
  refresh-a stranice - svaka nova sesija počinje s praznim kontekstom. 
  U daljnjem razvoju mogla bi se dodati lagana perzistentna pohrana 
  (npr. SQLite baza).
- Zbog prirode lokalnog GPU inferenca, Ollama sekvencijalno obrađuje 
  upite - istovremeni zahtjevi više korisnika ulaze u red čekanja. 
 