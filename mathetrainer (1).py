import streamlit as st
import numpy as np

st.set_page_config(page_title="Mathetrainer von Lias", page_icon="🧮")

st.title("🧮 Persönlicher Mathetrainer von Lias")

# --- Session State initialisieren ---
def init_state():
    defaults = {
        "phase": "start",        # start | training | result
        "auswahl": None,
        "max_versuche": 5,
        "aktueller_versuch": 0,
        "richtige_versuche": 0,
        "a": None,
        "b": None,
        "feedback": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def neue_aufgabe():
    auswahl = st.session_state.auswahl
    if auswahl == 3:
        a = np.random.randint(1, 10)
        b = np.random.randint(1, 10)
    elif auswahl == 1:
        a = np.random.randint(1, 99)
        b = np.random.randint(1, 99 - a)  # Summe bleibt unter 100
    else:
        a = np.random.randint(1, 100)
        b = np.random.randint(1, 100)
        if b > a:
            a, b = b, a  # größere Zahl immer vorne bei Subtraktion
    st.session_state.a = a
    st.session_state.b = b
    st.session_state.feedback = None

def reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()

# ── PHASE: START ──────────────────────────────────────────────────────────────
if st.session_state.phase == "start":
    st.subheader("Willkommen! 👋")
    st.write("Wähle eine Rechenart und die Anzahl der Aufgaben.")

    auswahl = st.radio(
        "Rechenart:",
        options=[1, 2, 3],
        format_func=lambda x: {1: "➕  Addition", 2: "➖  Subtraktion", 3: "✖️  Einmaleins (1×1)"}[x],
    )
    max_versuche = st.number_input("Anzahl der Aufgaben:", min_value=1, max_value=50, value=5, step=1)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚀 Starten", use_container_width=True):
            st.session_state.auswahl = auswahl
            st.session_state.max_versuche = int(max_versuche)
            st.session_state.aktueller_versuch = 0
            st.session_state.richtige_versuche = 0
            st.session_state.phase = "training"
            neue_aufgabe()
            st.rerun()
    with col2:
        if st.button("❌ Beenden", use_container_width=True):
            st.info("Bis zum nächsten Mal! 👋")
            st.stop()

# ── PHASE: TRAINING ───────────────────────────────────────────────────────────
elif st.session_state.phase == "training":
    versuch_nr = st.session_state.aktueller_versuch + 1
    max_v = st.session_state.max_versuche
    a = st.session_state.a
    b = st.session_state.b
    auswahl = st.session_state.auswahl

    # Fortschrittsbalken
    st.progress(st.session_state.aktueller_versuch / max_v)
    st.caption(f"Aufgabe {versuch_nr} von {max_v}")

    # Aufgabe anzeigen
    op = {1: "+", 2: "−", 3: "×"}[auswahl]
    st.markdown(f"## {a} {op} {b} = ?")

    # Feedback aus vorherigem Versuch
    if st.session_state.feedback == "richtig":
        st.success("✅ Richtig!")
    elif st.session_state.feedback == "falsch":
        richtig = {1: a + b, 2: a - b, 3: a * b}[auswahl]
        st.error(f"❌ Leider falsch! Die richtige Lösung wäre **{richtig}**.")

    with st.form(key=f"form_{versuch_nr}", clear_on_submit=True):
        eingabe = st.number_input("Deine Antwort:", step=1, value=None, placeholder="Ergebnis eingeben...", label_visibility="visible")
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("✔️ Antworten", use_container_width=True)
        with col2:
            abbrechen = st.form_submit_button("❌ Abbrechen", use_container_width=True)

    if submitted:
        if eingabe is None:
            st.warning("⚠️ Bitte gib eine Zahl ein!")
            st.stop()
        richtig = {1: a + b, 2: a - b, 3: a * b}[auswahl]
        if int(eingabe) == richtig:
            st.session_state.richtige_versuche += 1
            st.session_state.feedback = "richtig"
        else:
            st.session_state.feedback = "falsch"

        st.session_state.aktueller_versuch += 1

        if st.session_state.aktueller_versuch >= max_v:
            st.session_state.phase = "result"
        else:
            neue_aufgabe()
        st.rerun()

    if abbrechen:
        st.session_state.phase = "result"
        st.rerun()

# ── PHASE: RESULT ─────────────────────────────────────────────────────────────
elif st.session_state.phase == "result":
    richtig = st.session_state.richtige_versuche
    gesamt = st.session_state.aktueller_versuch  # tatsächlich beantwortete Aufgaben
    prozent = (richtig / gesamt * 100) if gesamt > 0 else 0

    st.subheader("🏁 Auswertung")
    st.metric("Richtige Antworten", f"{richtig} / {gesamt}")
    st.metric("Ergebnis", f"{prozent:.1f} %")

    if prozent == 100:
        st.balloons()
        st.success("🌟 Perfekt! Alle Aufgaben richtig!")
    elif prozent >= 70:
        st.success("👍 Gut gemacht!")
    elif prozent >= 50:
        st.warning("🙂 Weiter üben – du schaffst das!")
    else:
        st.error("💪 Nicht aufgeben – Übung macht den Meister!")

    if st.button("🔄 Nochmal spielen", use_container_width=True):
        reset()
        st.rerun()
