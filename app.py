import streamlit as st
import json
import os
import math
import pandas as pd
import plotly.express as px

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Peni di Merito", layout="centered")

DATA_FILE = "dati_peni.json"
DENSITA_TESSUTO = 1.05  # g/cm³

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

# ------------------ HEADER ------------------
st.markdown("## 📊 Peni di Merito")
st.markdown("Inserisci i tuoi dati anatomici in forma anonima e visualizza le statistiche aggregate per etnia.")

# ------------------ INPUT ------------------
with st.form("inserimento_dati", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        diametro = st.number_input("Diametro (cm)", min_value=0.1, step=0.1)
        etnia = st.selectbox("Etnia", ["Caucasica", "Africana", "Asiatica", "Latina", "Mediorientale", "Altro"])
    with col2:
        lunghezza = st.number_input("Lunghezza (cm)", min_value=0.1, step=0.1)

    submitted = st.form_submit_button("📥 Invia")

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

    st.markdown("### 📈 Statistiche generali")

    max_row = df.loc[df["volume"].idxmax()]
    min_row = df.loc[df["volume"].idxmin()]

    col1, col2, col3 = st.columns(3)
    col1.metric("📏 Lunghezza max", f"{max_row['lunghezza']} cm")
    col2.metric("⚪ Diametro max", f"{max_row['diametro']} cm")
    col3.metric("📦 Volume max", f"{max_row['volume']:.2f} cm³")

    col4, col5, col6 = st.columns(3)
    col4.metric("📏 Lunghezza min", f"{min_row['lunghezza']} cm")
    col5.metric("⚪ Diametro min", f"{min_row['diametro']} cm")
    col6.metric("📦 Volume min", f"{min_row['volume']:.2f} cm³")

    st.markdown("### ⚖️ Peso medio stimato")
    st.metric("Peso medio globale", f"{peso_medio:.2f} g")

    st.markdown("---")
    st.markdown("### 🎨 Visualizzazione per etnia")

    etnie = df["etnia"].unique().tolist()
    etnia_selezionata = st.selectbox("Filtro etnia", ["Tutte"] + etnie)

    if etnia_selezionata != "Tutte":
        df_filtrato = df[df["etnia"] == etnia_selezionata]
    else:
        df_filtrato = df

    # Indici utente per rappresentazione
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
