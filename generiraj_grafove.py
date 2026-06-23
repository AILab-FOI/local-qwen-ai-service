"""
Skripta za generiranje grafova iz rezultata testiranja Qwen 3-14B.
Pokrenuti iz direktorija (gdje su CSV-ovi), nakon test_performance.py.
Zahtijeva: pip install matplotlib pandas
Izlaz: 2 PDF-a (za LaTeX \includegraphics).
"""

import pandas as pd
import matplotlib.pyplot as plt

# Jedinstven stil za sve grafove
plt.rcParams.update({
    "font.size": 11,
    "font.family": "serif",        
    "axes.spines.top": False,      
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
    "figure.figsize": (6.5, 4),
})

ACCENT = "#2a6b5a"  # ista boja kao aplikacija


# ---------- GRAF 1: brzina vs duljina konteksta ----------
ctx = pd.read_csv("rezultati_context_length.csv")

fig, ax = plt.subplots()
ax.plot(ctx["tokeni_u_promptu"], ctx["tokeni_po_sekundi"],
        color=ACCENT, marker="o", markersize=5, linewidth=1.5, zorder=3)

ax.set_xlabel("Broj tokena u kontekstu (ulaz)")
ax.set_ylabel("Brzina generiranja (tokena/s)")
fig.tight_layout()
fig.savefig("graf_brzina_vs_kontekst.pdf")
print("Spremljeno: graf_brzina_vs_kontekst.pdf")


# ---------- GRAF 2: duljina odgovora po system promptu ----------
sp = pd.read_csv("rezultati_system_prompts.csv")

fig, ax = plt.subplots()
bars = ax.bar(sp["system_prompt"], sp["generirani_tokeni"],
              color=ACCENT, width=0.6, zorder=3)

for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h, f"{int(h)}",
            ha="center", va="bottom", fontsize=9)

ax.set_xlabel("Vrsta system prompta")
ax.set_ylabel("Broj generiranih tokena")
fig.tight_layout()
fig.savefig("graf_duljina_po_promptu.pdf")
print("Spremljeno: graf_duljina_po_promptu.pdf")

print("\nZavrseno. 2 PDF-a spremna za Overleaf.")
