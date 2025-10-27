import streamlit as st
import pandas as pd
from pef_logica_economica import calcola_pef  # logica separata

st.set_page_config(page_title="Mini PEF Tool", page_icon="💰", layout="centered")

st.title("Mini PEF – Simulatore didattico di Project Financing")
st.markdown("Simulatore didattico semplificato per la costruzione di un Piano Economico Finanziario (PEF).")

# ---------------------------------------------------------------------
# SEZIONE 0: LOGICA ECONOMICA DIDATTICA (espandibile)
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# LOGICA ECONOMICA DEL PEF — VERSIONE SENZA NUMERI
# ---------------------------------------------------------------------

with st.expander("Linea temporale e CapEx"):
    st.markdown("""
- **Linea temporale:** anni di costruzione + anni di gestione.  
- **CapEx:** distribuite uniformemente sugli anni di costruzione  
  (ipotesi semplificata – nella realtà possono aumentare ogni anno con l’inflazione).  
- Durante la **costruzione** non si generano ricavi, solo investimenti.  
- Durante la **gestione** iniziano i ricavi e i costi operativi (OPEX).  
""")

with st.expander("Ricavi e Opex"):
    st.markdown("""
- **Ricavi:** nulli durante la costruzione, poi crescono con l’inflazione.  
  In uno scenario realistico dovremmo stimare anche l’andamento della **domanda** (in crescita o in decrescita).  
- **Opex:** costi operativi annui (manutenzione, utenze, personale, ecc.) anch’essi soggetti a inflazione.  
""")

with st.expander(" Conto economico operativo"):
    st.markdown("""
**EBITDA** = Ricavi − Opex  
**Ammortamenti** = CAPEX / durata gestione  *(ammortamento lineare, ipotesi semplificativa)*  
**EBIT** = EBITDA − Ammortamenti  
**Imposte** = max(EBIT, 0) × aliquota fiscale  *(non si pagano imposte se l’EBIT è negativo)*  
**Utile netto** = EBIT − Imposte  
**Flusso operativo (unlevered)** = Utile netto + Ammortamenti  
→ flusso di cassa disponibile per remunerare debito ed equity  
""")

with st.expander(" Struttura finanziaria"):
    st.markdown(r"""
- **Debito (D):** CAPEX × (1 − %Equity)  
- **Equity (E):** CAPEX × %Equity  
- **Servizio del debito:** rata costante (formula francese)  

**Costo medio ponderato del capitale (WACC):**

\[
\text{WACC} = \left(\frac{E}{V}\right)\cdot K_e \;+\; \left(\frac{D}{V}\right)\cdot K_d \cdot (1 - t)
\]

dove:  
- \(Ke\): costo dell’equity  
- \(Kd\): costo del debito  
- \(t\): aliquota fiscale  
- \(V = D + E\): valore complessivo del capitale investito  
""")

with st.expander(" Indicatori principali"):
    st.markdown("""
- **VAN progetto:** valore attuale netto dei flussi *unlevered* al **WACC**  
  → misura la creazione di valore del progetto per tutti i finanziatori (debito + equity).  
- **TIR progetto:** IRR dei flussi *unlevered*  
  → rendimento complessivo prima della leva finanziaria.  
- **TIR Equity:** IRR dei flussi *levered* (dopo il servizio del debito)  
  → redditività per l’azionista.  
- **DSCR (Debt Service Coverage Ratio):** CF operativo / Servizio del debito  
  → capacità di rimborsare il debito anno per anno.  
""")

with st.expander(" Ipotesi esemplificative"):
    st.markdown("""
- Nessun capitale circolante operativo  
- Nessun scudo fiscale sugli interessi passivi  
- Nessun CAPEX di manutenzione o valore residuo  
- Nessun interesse capitalizzato durante la costruzione  
- Nessun costo di transazione o commissione bancaria  
""")

with st.expander(" Logica di bancabilità (criterio semaforo)"):
    st.markdown("""
**✅ Progetto potenzialmente bancabile:**  
- **TIR_progetto > WACC**  **e**  **DSCR_min > 1.20**  

**⚠️ Progetto borderline:**  
- **DSCR_min tra 1.00 e 1.20**  

**❌ Progetto non bancabile:**  
- **DSCR_min ≤ 1.00**  
""")

with st.expander(" Note didattiche"):
    st.markdown("""
- Il confronto **TIR_progetto vs WACC** è una semplificazione didattica.  
- La soglia **DSCR_min = 1.20** è prassi bancaria diffusa.  
- Il modello non calcola **LLCR, PLCR** o un **TIR Equity** basato su dividendi.  
- Obiettivo: capire la relazione tra **struttura finanziaria**, **leva** e **sostenibilità del debito**.  
""")


    
# ---------------------------------------------------------------------
# SEZIONE 1: INPUT PARAMETRI DI BASE
# ---------------------------------------------------------------------
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
    tasso_interesse = st.number_input("Tasso d’interesse sul debito (Kd, %)", min_value=0.0, step=0.1, value=4.0)
    aliquota_fiscale = st.number_input("Aliquota fiscale (%)", min_value=0.0, step=1.0, value=24.0)

perc_equity = st.slider("Percentuale Equity (% su CAPEX)", 0, 100, 30)
costo_equity = st.number_input("Costo atteso dell’equity (Ke, %)", min_value=1.0, step=0.5, value=8.0)
st.markdown(f"**Struttura finanziaria:** {perc_equity}% Equity / {100 - perc_equity}% Debito")

# ---------------------------------------------------------------------
# SEZIONE 2: CALCOLI
# ---------------------------------------------------------------------
st.subheader("Indicatori principali")

df, van, tir_proj, tir_eq, wacc, dscr_medio, dscr_min = calcola_pef(
    capex, opex, ricavi, inflazione,
    durata_costruzione, durata_gestione,
    tasso_interesse, aliquota_fiscale, perc_equity, costo_equity
)

# Mostra indicatori chiave in una griglia
col1, col2, col3 = st.columns(3)
col1.metric("WACC (%)", f"{wacc*100:.2f}")
col2.metric("VAN progetto (€)", f"{van:,.0f}")
col3.metric("TIR progetto (%)", f"{tir_proj*100:.1f}")

col4, col5 = st.columns(2)
col4.metric("TIR Equity (%)", f"{tir_eq*100:.1f}")
col5.metric("DSCR medio / min", f"{dscr_medio:.2f} / {dscr_min:.2f}")

with st.expander("ℹ️ Spiegazione degli indicatori"):
    st.markdown("""
**WACC (Weighted Average Cost of Capital):** costo medio del capitale impiegato.  
**VAN:** valore economico generato dal progetto (VAN > 0 = crea valore).  
**TIR progetto:** rendimento complessivo del progetto, prima del debito.  
**TIR Equity:** rendimento per l’azionista, dopo il servizio del debito.  
**DSCR:** misura la capacità di rimborso del debito (DSCR > 1 = flusso sufficiente).  
""")


# ---------------------------------------------------------------------
# SEZIONE 3: RISULTATI
# ---------------------------------------------------------------------
st.header("Risultati")

st.dataframe(df.style.format("{:,.0f}").highlight_max(color='lightgreen'))

# st.subheader("Indicatori principali")

# col1, col2, col3 = st.columns(3)
# col1.metric("VAN progetto (€)", f"{van:,.0f}")
# col2.metric("TIR progetto (%)", f"{tir_proj*100:,.1f}")
# col3.metric("WACC (%)", f"{wacc*100:,.1f}")

# col1, col2, col3 = st.columns(3)
# col1.metric("TIR Equity (%)", f"{tir_eq*100:,.1f}")
# col2.metric("DSCR medio", f"{dscr_medio:.2f}")
# col3.metric("DSCR minimo", f"{dscr_min:.2f}")

# ---------------------------------------------------------------------
# SEZIONE 4: VALUTAZIONE DI BANCABILITÀ
# ---------------------------------------------------------------------
st.header("Valutazione di bancabilità")

if tir_proj > wacc and dscr_min > 1.2:
    st.success("✅ Progetto potenzialmente **bancabile**")
    st.markdown("""
    - **TIR_progetto > WACC** → il progetto crea valore economico.  
    - **DSCR_min > 1.2** → buona capacità di rimborso del debito.  
    💡 *Condizione tipica per un project finance “bancabile”.*
    """)

elif dscr_min > 1.0:
    st.warning("⚠️ Progetto **borderline**")
    st.markdown("""
    - **DSCR_min tra 1.0 e 1.2:** margine di sicurezza ridotto.  
    - **TIR_progetto ≈ WACC:** redditività complessiva limitata.  

    **Aree di miglioramento:**
    - Aumentare la quota **Equity** per ridurre l’onere del debito  
    - Negoziare un **tasso di interesse più basso (Kd)**  
    - Ottimizzare i **costi operativi (OPEX)**  
    - Allungare la **durata del finanziamento o della concessione**
    """)

else:
    st.error("❌ Progetto **non bancabile**")
    st.markdown("""
    - **DSCR_min ≤ 1.0:** i flussi non coprono le rate del debito.  
    - **TIR_progetto < WACC:** il progetto distrugge valore economico.  

    **Aree di miglioramento:**
    - Ridurre i **costi di investimento (CAPEX)**  
    - Aumentare i **ricavi** o introdurre **canoni garantiti**  
    - Aumentare la **durata della gestione** per ammortizzare i costi  
    - Incrementare la **quota di equity** o cercare **garanzie pubbliche**
    """)

st.caption("""
Legenda:
- **WACC** = costo medio del capitale (mix debito + equity)  
- **TIR_progetto** = rendimento complessivo del progetto  
- **DSCR_min** = sostenibilità finanziaria minima nel tempo  
""")

st.caption("Simulazione didattica semplificata – non sostituisce un'analisi professionale.")
