import streamlit as st
import pandas as pd
from pef_logica_economica import calcola_pef  # 👈 import logica separata

st.set_page_config(page_title="Mini PEF Tool", page_icon="💰", layout="centered")

st.title("📘 Logica economica del PEF")

# --- SEZIONE 1: Linea temporale e CapEx ---
with st.expander("1. Linea temporale e CapEx"):
    st.markdown("""
**Linea temporale:** anni di costruzione + anni di gestione  

**CapEx:** distribuite uniformemente sugli anni di costruzione  
(dovrebbero aumentare di anno in anno indicizzati all'inflazione)
""")

# --- SEZIONE 2: Ricavi e Opex ---
with st.expander("2. Ricavi e Opex"):
    st.markdown("""
**Ricavi:** sono zero durante la costruzione e poi crescono per inflazione.  
Dovremmo fare anche delle stime sulla domanda (in crescita o in decrescita).

**Opex:** costi operativi ricorrenti, monetari (manutenzione, personale, utenze, ecc.).
""")

# --- SEZIONE 3: Conto economico ---
with st.expander("3. Conto economico della struttura operativa"):
    st.markdown("""
**EBITDA** = Ricavi - Opex  
**Ammortamenti** = CAPEX / durata gestione (ammortamento lineare, ipotesi esemplificativa)  
**EBIT** = EBITDA - Ammortamenti  
**Imposte** = max(EBIT, 0) × aliquota fiscale  
(non si pagano tasse se EBIT < 0)  
**Utile netto** = EBIT - Imposte  
**Flusso operativo** = Utile netto + Ammortamenti (post-imposte, pre-debito)
""")

# --- SEZIONE 4: Struttura finanziaria ---
with st.expander("4. Struttura finanziaria"):
    st.markdown("""
- **Debito:** CAPEX × (1 - %equity)  
- **Equity:** CAPEX × %equity  
- **Servizio del debito:** rata costante (formula francese)
""")

# --- SEZIONE 5: Indicatori principali ---
with st.expander("5. Indicatori principali"):
    st.markdown("""
- **VAN progetto:** NPV dei flussi unlevered al tasso del debito (semplificazione)  
- **TIR progetto:** IRR dei flussi unlevered  
- **DSCR:** CF operativo / Servizio del debito
""")

# --- SEZIONE 6: Ipotesi semplificative ---
with st.expander("6. Ipotesi semplificative"):
    st.markdown("""
- Nessun capitale circolante  
- Nessun scudo fiscale sugli interessi  
- Nessun CAPEX di manutenzione o valore residuo  
- Nessun interesse durante costruzione
""")

# --- SEZIONE 7: Criteri di bancabilità ---
with st.expander("7. Ipotesi di bancabilità (criterio semaforo)"):
    st.markdown("""
**✅ Progetto potenzialmente bancabile:**  
- TIR > tasso del debito **e** DSCR_min > 1.20  

**⚠️ Progetto borderline:**  
- DSCR_min tra 1.00 e 1.20  

**❌ Progetto non bancabile:**  
- DSCR_min ≤ 1.00
""")

# --- SEZIONE 8: Note didattiche ---
with st.expander("8. Note didattiche e interpretative"):
    st.markdown("""
- Il confronto **TIR vs tasso debito** è una semplificazione: in realtà si userebbe il **WACC**.  
- La soglia **DSCR_min = 1.20** è una prassi bancaria standard.  
- Soglie più basse (1.05–1.15) sono possibili con garanzie pubbliche o ricavi regolati.  
- Il modello non calcola LLCR, PLCR, TIR equity.  
- L’obiettivo è mostrare la **relazione diretta tra struttura finanziaria, flussi e sostenibilità del debito**.
""")


                
# --- INPUT SECTION ---
st.header("Parametri di base")

col1, col2 = st.columns(2)
with col1:
    capex = st.number_input("CAPEX (Investimento iniziale, €)", min_value=10000, step=10000, value=1_000_000)
    opex = st.number_input("OPEX annuo (Costi operativi, €)", min_value=0, step=10000, value=100_000)
    ricavi = st.number_input("Ricavi annui (caratteristici + ancillari, €)", min_value=0, step=10000, value=500_000)
    inflazione = st.number_input("Inflazione annua (%)", min_value=0.0, step=0.1, value=2.0)

with col2:
    durata_costruzione = st.number_input("Durata costruzione (anni)", min_value=1, max_value=5, step=1, value=2)
    durata_gestione = st.number_input("Durata gestione (anni)", min_value=1, max_value=50, step=1, value=10)
    tasso_interesse = st.number_input("Tasso d’interesse sul debito (%)", min_value=0.0, step=0.1, value=4.0)
    aliquota_fiscale = st.number_input("Aliquota fiscale (%)", min_value=0.0, step=1.0, value=24.0)

perc_equity = st.slider("Percentuale Equity (% su CAPEX)", 0, 100, 30)
st.markdown(f"**Struttura finanziaria:** {perc_equity}% Equity / {100 - perc_equity}% Debito")

# --- CALCULATIONS ---
st.header("Calcoli economico-finanziari")

df, van, tir, dscr_medio, dscr_min = calcola_pef(
    capex, opex, ricavi, inflazione,
    durata_costruzione, durata_gestione,
    tasso_interesse, aliquota_fiscale, perc_equity
)

# --- OUTPUT SECTION ---
st.header("Risultati")

st.dataframe(df.style.format("{:,.0f}").highlight_max(color='lightgreen'))

st.subheader("Indicatori principali")
col1, col2, col3 = st.columns(3)
col1.metric("VAN progetto (€)", f"{van:,.0f}")
col2.metric("TIR progetto (%)", f"{tir*100:,.1f}")
col3.metric("DSCR medio / min", f"{dscr_medio:.2f} / {dscr_min:.2f}")

if tir > tasso_interesse/100 and dscr_min > 1.2:
    st.success("✅ Progetto potenzialmente **bancabile**")
elif dscr_min > 1.0:
    st.warning("⚠️ Progetto **borderline**, margine di sicurezza basso")
else:
    st.error("❌ Progetto **non bancabile** (rischio elevato)")

st.caption("Simulazione didattica semplificata – non sostituisce un'analisi professionale.")
