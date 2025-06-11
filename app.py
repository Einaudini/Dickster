import streamlit as st
import json
import os
import math
import pandas as pd
import plotly.express as px
from streamlit.runtime.scriptrunner import get_script_run_ctx

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Peni di Merito", layout="centered")

DATA_FILE = "dati_peni.json"
DENSITA_TESSUTO = 1.05  # g/cm³
DEBUG_MODE = False  # Imposta a True per testare in locale come admin

# ------------------ FUNZIONI ------------------
def carica_dati():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f, indent=2)

def calcola_volume(diametro, lunghezza):
    raggio = diametro / 2
    return math.pi * (raggio ** 2) * lunghezza

def calcola_peso(volume):
    return volume * DENSITA_TESSUTO

def is_admin():
    if DEBUG_MODE:
        return True
    password = st.session_state.get("admin_password", None)
    return password == st.secrets.get("admin_password")

# ------------------ HEADER ------------------
st.markdown("## 📊 Peni di Merito")
st.markdown("Inserisci i tuoi dati anatomici in forma anonima e visualizza le statistiche aggregate per etnia.")

# ------------------ INPUT ------------------
with st.form("inserimento_dati", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        diametro = st.number_input("Diametro (cm)", min_value=1.0, max_value=10.0, step=0.1)
        etnia = st.selectbox("Etnia", ["Caucasica", "Africana", "Asiatica", "Latina", "Mediorientale", "Altro"])
    with col2:
        lunghezza = st.number_input("Lunghezza (cm)", min_value=2.0, max_value=30.0, step=0.1)

    submitted = st.form_submit_button("🗕️ Invia")

    if submitted:
        dati = carica_dati()
        volume = calcola_volume(diametro, lunghezza)
        peso = calcola_peso(volume)
        dati.append({
            "diametro": diametro,
            "lunghezza": lunghezza,
            "volume": volume,
            "peso": peso,
            "etnia": etnia
        })
        salva_dati(dati)
        st.success("✅ Dati salvati con successo!")

# ------------------ ANALISI ------------------
dati = carica_dati()
if dati:
    df = pd.DataFrame(dati)
    peso_medio = df["peso"].mean()
    dev_std_volume = df["volume"].std()
    dev_std_peso = df["peso"].std()

    st.markdown("### 📊 Statistiche generali")

    max_row = df.loc[df["volume"].idxmax()]
    min_row = df.loc[df["volume"].idxmin()]

    col1, col2, col3 = st.columns(3)
    col1.metric("📏 Lunghezza max", f"{max_row['lunghezza']} cm")
    col2.metric("⚪ Diametro max", f"{max_row['diametro']} cm")
    col3.metric("🟖 Volume max", f"{max_row['volume']:.2f} cm³")

    col4, col5, col6 = st.columns(3)
    col4.metric("📏 Lunghezza min", f"{min_row['lunghezza']} cm")
    col5.metric("⚪ Diametro min", f"{min_row['diametro']} cm")
    col6.metric("🟖 Volume min", f"{min_row['volume']:.2f} cm³")

    st.markdown("### ⚖️ Peso medio stimato")
    st.metric("Peso medio globale", f"{peso_medio:.2f} g")

    st.markdown("### 📉 Deviazione standard")
    col7, col8 = st.columns(2)
    col7.metric("Volume (σ)", f"{dev_std_volume:.2f} cm³")
    col8.metric("Peso (σ)", f"{dev_std_peso:.2f} g")

    st.markdown("---")
    st.markdown("### 🎨 Visualizzazione per etnia")

    etnie = df["etnia"].unique().tolist()
    etnia_selezionata = st.selectbox("Filtro etnia", ["Tutte"] + etnie)

    if etnia_selezionata != "Tutte":
        df_filtrato = df[df["etnia"] == etnia_selezionata]
    else:
        df_filtrato = df

    df_filtrato = df_filtrato.reset_index(drop=True)
    df_filtrato["Utente"] = df_filtrato.index + 1

    fig = px.bar(
        df_filtrato,
        x="Utente",
        y="volume",
        color="etnia" if etnia_selezionata == "Tutte" else None,
        labels={"volume": "Volume (cm³)", "Utente": "Utente"},
        title="Distribuzione dei volumi",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Non sono ancora stati inseriti dati.")

# ------------------ LOGIN ADMIN ------------------
if "admin_password" not in st.session_state:
    st.session_state.admin_password = ""

with st.expander("🔐 Login Admin"):
    password_input = st.text_input("Inserisci password admin", type="password")
    if st.button("Login"):
        st.session_state.admin_password = password_input
        st.rerun()

# ------------------ ADMIN PANEL ------------------
if is_admin():
    st.markdown("---")
    st.markdown("## 🛠️ Pannello Admin")

    with st.expander("📋 Dati grezzi"):
        st.dataframe(pd.DataFrame(dati))

    st.markdown("### ➕ Aggiungi manualmente un dato")
    with st.form("admin_add"):
        diametro_admin = st.number_input("Diametro (cm)", min_value=1.0, max_value=10.0, step=0.1, key="admin_d")
        lunghezza_admin = st.number_input("Lunghezza (cm)", min_value=2.0, max_value=30.0, step=0.1, key="admin_l")
        etnia_admin = st.selectbox("Etnia", ["Caucasica", "Africana", "Asiatica", "Latina", "Mediorientale", "Altro"], key="admin_e")
        submit_admin = st.form_submit_button("Aggiungi")

        if submit_admin:
            volume = calcola_volume(diametro_admin, lunghezza_admin)
            peso = calcola_peso(volume)
            dati.append({
                "diametro": diametro_admin,
                "lunghezza": lunghezza_admin,
                "volume": volume,
                "peso": peso,
                "etnia": etnia_admin
            })
            salva_dati(dati)
            st.success("Aggiunto con successo.")

    st.markdown("### ❌ Rimuovi dato per indice")
    if len(dati) > 0:
        indice_da_rimuovere = st.number_input("Indice da eliminare (0 a N-1)", min_value=0, max_value=len(dati)-1, step=1)
        if st.button("Elimina dato"):
            dati.pop(indice_da_rimuovere)
            salva_dati(dati)
            st.success(f"Dato all'indice {indice_da_rimuovere} eliminato.")