// Konfiguracija API adrese 
const API = "";
const API_KEY = "foi-qwen-2026-lucija-sinko-k7mxq9p2";
const SESSION_ID = crypto.randomUUID();

// Dohvacanje HTML elemenata
const chat = document.getElementById("chat-container");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const perfToggle = document.getElementById("perf-toggle");
const resetBtn = document.getElementById("reset-btn");

// Prikaz performansi
let showPerf = true;

// Event listeneri
input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !sendBtn.disabled) {
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);
perfToggle.addEventListener("click", togglePerf);
resetBtn.addEventListener("click", resetChat);

// Funkcija za ukljucivanje/iskljucivanje prikaza metrika
function togglePerf() {
    showPerf = !showPerf;
    perfToggle.textContent = "Metrike: " + (showPerf ? "ON" : "OFF");

    var bars = document.querySelectorAll(".perf-bar");
    for (var i = 0; i < bars.length; i++) {
        bars[i].style.display = showPerf ? "flex" : "none";
    }
}

// Funkcija za slanje poruke backendu
async function sendMessage() {
    var msg = input.value.trim();
    if (!msg) return;

    // Ukloni welcome poruku
    var welcome = document.getElementById("welcome");
    if (welcome) welcome.remove();

    var sysPrompt = document.getElementById("system-prompt").value;

    addBubble(msg, "user");
    input.value = "";
    sendBtn.disabled = true;

    // Animacija tipkanja dok model generira odgovor
    var typingRow = document.createElement("div");
    typingRow.className = "message-row assistant";
    typingRow.innerHTML =
        '<div class="typing-indicator">' +
        '  <div class="typing-dots"><span></span><span></span><span></span></div>'+
        '  <span class="typing-text">Model generira odgovor...</span>'+
        '</div>';
    chat.appendChild(typingRow);
    chat.scrollTop = chat.scrollHeight;

    // Slanje POST zahtjeva na backend API
    try {
        var res = await fetch(API + "/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json",
                        "X-API-Key": API_KEY
            },
            body: JSON.stringify({
                message: msg,
                system_prompt: sysPrompt,
                session_id: SESSION_ID
            })
        });

        var data = await res.json();
        typingRow.remove();
        addBubble(data.response || data.error || "Greška: nepoznati odgovor.", "assistant", data.performance);
    } catch(error) {
        typingRow.remove();
        addBubble("Greška: backend nije dostupan.", "assistant");
    }
    sendBtn.disabled = false;
    input.focus();
}

// Funkcija za kreiranje poruke u chatu
function addBubble(text, role, perf) {
    var row = document.createElement("div");
    row.className = "message-row " + role;

    var html = '<div class="bubble">' + escapeHtml(text) + '</div>';    

    if (perf) {
        var display = showPerf ? "flex" : "none";
        html +=
            '<div class="perf-bar" style="display:' + display + '">' +
            '  <div class="perf-item">' +
            '    <span class="perf-label">Brzina</span>' +
            '    <span class="perf-value">' + perf.tokeni_po_sekundi + ' tok/s</span>' +
            '  </div>' +
            '  <div class="perf-item">' +
            '    <span class="perf-label">Generirano</span>' +
            '    <span class="perf-value">' + perf.generirani_tokeni + ' tokena</span>' +
            '  </div>' +
            '  <div class="perf-item">' +
            '    <span class="perf-label">Prompt</span>' +
            '    <span class="perf-value">' + perf.tokeni_u_promptu + ' tokena</span>' +
            '  </div>' +
            '  <div class="perf-item">' +
            '    <span class="perf-label">Generiranje</span>' +
            '    <span class="perf-value">' + perf.vrijeme_generiranja_s + ' s</span>' +
            '  </div>' +
            '  <div class="perf-item">' +
            '    <span class="perf-label">Vrijeme</span>' +
            '    <span class="perf-value">' + perf.ukupno_vrijeme_s + ' s</span>' +
            '  </div>' +
            '  <div class="perf-item">' +
            '    <span class="perf-label">Kontekst</span>' +
            '    <span class="perf-value">' + perf.poruka_u_kontekstu + ' msg</span>' +
            '   </div>' +
            '</div>';
    }

    row.innerHTML = html;
    chat.appendChild(row);  
    chat.scrollTop = chat.scrollHeight;
}

// Funkcija za zastitu od XSS napada
function escapeHtml(text) {
    var d = document.createElement("div");
    d.textContent = text;
    return d.innerHTML;
}

// Funcija za resetiranje chata
async function resetChat() {
    await fetch(API + "/reset", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        body: JSON.stringify({session_id: SESSION_ID})
    });
    chat.innerHTML =
        '<div class="welcome" id="welcome">' +
        '  <img src="logo.png" alt="Qwen Local AI" class="welcome-logo" />' +
        '  <h2>Qwen 3-14B lokalni model</h2>' +
        '  <p>Postavite pitanje i model će generirati odgovor lokalno, bez slanja podataka u oblak</p>' +
        '</div>';
}
