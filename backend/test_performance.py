import requests
import csv 

API_URL = "http://localhost:5000"
API_KEY = "local-qwen-demo-key-2026"
HEADERS = {"X-API-Key": API_KEY}

def save_results_to_csv(filename, rows, headers):
    """Sprema rezultate testova u CSV datoteku."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f" Rezultati spremljeni u {filename}")
    
def test_single_query(message, system_prompt="Ti si koristan AI asistent."):
    """Šalje jedan upit i vraća performanse."""
    requests.post(f"{API_URL}/reset", headers=HEADERS, json={"session_id": "default"})

    response = requests.post(f"{API_URL}/chat", headers=HEADERS, json={
        "message": message,
        "system_prompt": system_prompt
    })
    data = response.json()
    return data["performance"]

def test_system_prompts():
    """Testira utjecaj različitih system promptova na odgovore."""
    requests.post(f"{API_URL}/chat", headers=HEADERS,
                  json={"message": "Pozdrav", "system_prompt": "Ti si asistent."})
    print("\n=== Test utjecaja system promptova ===\n")
    test_message = "Što je strojno učenje?"

    prompts = {
        "Neutralan": "Ti si koristan AI asistent.",
        "Hrvatski": "Odgovaraj isključivo na hrvatskom jeziku, jasno i jednostavno.",
        "Kratak": "Odgovaraj u maksimalno dvije rečenice.",
        "Stručan": "Ti si profesor na fakultetu. Koristi akademski stil pisanja.",
    }

    PONAVLJANJA = 3
    rows = []
    for name, prompt in prompts.items():
        mjerenja = [test_single_query(test_message, prompt) for _ in range(PONAVLJANJA)]
        perf = {
            'generirani_tokeni': round(sum(m['generirani_tokeni'] for m in mjerenja) / PONAVLJANJA),
            'tokeni_u_promptu': mjerenja[0]['tokeni_u_promptu'],
            'tokeni_po_sekundi': round(sum(m['tokeni_po_sekundi'] for m in mjerenja) / PONAVLJANJA, 2),
            'vrijeme_generiranja_s': round(sum(m['vrijeme_generiranja_s'] for m in mjerenja) / PONAVLJANJA, 2),
            'ukupno_vrijeme_s': round(sum(m['ukupno_vrijeme_s'] for m in mjerenja) / PONAVLJANJA, 2),
        }
        print(f"System prompt: {name}")
        print(f"  Generirani tokeni (prosjek od {PONAVLJANJA}): {perf['generirani_tokeni']}")
        print(f"  Brzina: {perf['tokeni_po_sekundi']} tok/s")
        print(f"  Vrijeme: {perf['ukupno_vrijeme_s']}s")
        print()

        rows.append([
            name,
            perf['generirani_tokeni'],
            perf['tokeni_u_promptu'],
            perf['tokeni_po_sekundi'],
            perf['vrijeme_generiranja_s'],
            perf['ukupno_vrijeme_s']
        ])
    headers = ["system_prompt", "generirani_tokeni", "tokeni_u_promptu", "tokeni_po_sekundi", "vrijeme_generiranja_s", "ukupno_vrijeme_s"]
    save_results_to_csv("rezultati_system_prompts.csv", rows, headers)


def test_context_length():
    print("\n=== Test utjecaja duljine konteksta ===\n")
    base = "Ovo je testna rečenica za umjetno punjenje konteksta modela. "
    ponavljanja = [10, 40, 80, 150, 250, 350, 450]   

    PONAVLJANJA = 3
    rows = []
    for i, n in enumerate(ponavljanja, 1):
        mjerenja = []
        for _ in range(PONAVLJANJA):
            requests.post(f"{API_URL}/reset", headers=HEADERS, json={"session_id": "default"})
            message = base * n + "\nUkratko objasni što je strojno učenje."
            response = requests.post(f"{API_URL}/chat", headers=HEADERS, json={
                "message": message,
                "system_prompt": "Odgovaraj sažeto.",
                "num_predict": 200
            })
            mjerenja.append(response.json()["performance"])

        perf = {
            'tokeni_u_promptu': mjerenja[0]['tokeni_u_promptu'],
            'generirani_tokeni': round(sum(m['generirani_tokeni'] for m in mjerenja) / PONAVLJANJA),
            'tokeni_po_sekundi': round(sum(m['tokeni_po_sekundi'] for m in mjerenja) / PONAVLJANJA, 2),
            'vrijeme_generiranja_s': round(sum(m['vrijeme_generiranja_s'] for m in mjerenja) / PONAVLJANJA, 2),
            'ukupno_vrijeme_s': round(sum(m['ukupno_vrijeme_s'] for m in mjerenja) / PONAVLJANJA, 2),
        }
        print(f"Mjerenje {i}: {perf['tokeni_u_promptu']} tok u promptu -> {perf['tokeni_po_sekundi']} tok/s")
        rows.append([
            i, perf['tokeni_u_promptu'], perf['generirani_tokeni'],
            perf['tokeni_po_sekundi'], perf['vrijeme_generiranja_s'], perf['ukupno_vrijeme_s']
        ])
    headers = ["redni_broj", "tokeni_u_promptu", "generirani_tokeni", "tokeni_po_sekundi", "vrijeme_generiranja_s", "ukupno_vrijeme_s"]
    save_results_to_csv("rezultati_context_length.csv", rows, headers)

if __name__ == "__main__":
    print("Testovi performansi Qwen 3-14B modela")
    test_system_prompts()
    test_context_length()
    print("Testovi završeni.")