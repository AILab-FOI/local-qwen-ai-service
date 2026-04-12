import requests

API_URL = "http://localhost:5000"

def test_single_query(message, system_prompt="Ti si koristan AI asistent."):
    """Šalje jedan upit i vraća performanse."""
    requests.post(f"{API_URL}/reset")
    response = requests.post(f"{API_URL}/chat", json={
        "message": message,
        "system_prompt": system_prompt
    })
    data = response.json()
    return data["performance"]

def test_system_prompts():
    """Testira utjecaj različitih system promptova na odgovore."""
    print("\n=== Test utjecaja system promptova ===\n")
    test_message = "Što je strojno učenje?"

    prompts = {
        "Neutralan": "Ti si koristan AI asistent.",
        "Hrvatski": "Odgovaraj isključivo na hrvatskom jeziku, jasno i jednostavno.",
        "Kratak": "Odgovaraj u maksimalno dvije rečenice.",
        "Stručan": "Ti si profesor na fakultetu. Koristi akademski stil pisanja.",
    }

    for name, prompt in prompts.items():
        perf = test_single_query(test_message, prompt)
        print(f"System prompt: {name}")
        print(f"  Generirani tokeni: {perf['generirani_tokeni']}")
        print(f"  Brzina: {perf['tokeni_po_sekundi']} tok/s")
        print(f"  Vrijeme: {perf['ukupno_vrijeme_s']}s")
        print()


def test_context_length():
    """Testira utjecaj duljine konteksta na brzinu generiranja."""
    print("\n=== Test utjecaja duljine konteksta ===\n")
    requests.post(f"{API_URL}/reset")

    messages = [
        "Što je Python?",
        "Koje su prednosti Pythona?",
        "Kako se definira funkcija u Pythonu?",
        "Što su liste u Pythonu?",
        "Objasni rječnike u Pythonu.",
        "Što je petlja for u Pythonu?",
        "Kako se radi s datotekama u Pythonu?",
        "Što su klase u Pythonu?",
    ]

    for i, msg in enumerate(messages, 1):
        response = requests.post(f"{API_URL}/chat", json={
            "message": msg,
            "system_prompt": "Odgovaraj kratko, u 2-3 rečenice."
        })
        data = response.json()
        perf = data["performance"]
        print(f"Poruka {i}: \"{msg}\"")
        print(f"  Tokeni u promptu: {perf['tokeni_u_promptu']}")
        print(f"  Generirani tokeni: {perf['generirani_tokeni']}")
        print(f"  Brzina: {perf['tokeni_po_sekundi']} tok/s")
        print(f"  Vrijeme: {perf['ukupno_vrijeme_s']}s")
        print()


if __name__ == "__main__":
    print("Testovi performansi Qwen 3-14B modela")
    test_system_prompts()
    test_context_length()
    print("Testovi završeni.")