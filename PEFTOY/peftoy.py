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
  (ipotesi semplificata – le spese in conto capitale possono dipendere da variabili macroeconomiche come l'inflazione).  
- Durante la **costruzione** non si generano ricavi, solo investimenti.  
- Durante la **gestione** iniziano i ricavi e i costi operativi (OPEX).  
""")

with st.expander("Ricavi e Opex"):
    st.markdown("""
- **Ricavi:** nulli durante la costruzione. Crescono annualmente in base all’inflazione. 
  In uno scenario realistico dovremmo stimare anche l’andamento della domanda (in crescita o in decrescita) ed eventualmente stimare l'esistenza ad eventuali shock di domanda,
                nonché considerare tutti i rischi connessi alla domanda.  
- **Opex:** costi operativi annui (manutenzione, utenze, personale, ecc.) anch’essi soggetti ad inflazione.  
""")

with st.expander(" Conto economico operativo"):
    st.markdown("""
**EBITDA** = Ricavi − Opex  
**Ammortamenti** = CAPEX / durata gestione  *(ammortamento lineare, ipotesi semplificativa)*  
**EBIT** = EBITDA − Ammortamenti  
**Imposte** = max(EBIT, 0) × aliquota fiscale  *(non si pagano imposte se l’EBIT è negativo)*  
**Utile netto** = EBIT − Imposte  
**Flusso operativo (unlevered)** = Utile netto + Ammortamenti  
""")

with st.expander(" Struttura finanziaria"):
    st.markdown("""
- **Debito (D):** CAPEX × (1 − %Equity)  
- **Equity (E):** CAPEX × %Equity  
- **Servizio del debito:** rata costante (formula francese)  
""")
    st.markdown("**Costo medio ponderato del capitale (WACC):**")
    st.latex(r"""
    \text{WACC} = \left(\frac{E}{V}\right)\cdot K_e + \left(\frac{D}{V}\right)\cdot K_d\cdot(1 - t)
    """)
    st.markdown("""
dove:  
- \(K_e\): costo dell’equity  
- \(K_d\): costo del debito  
- \(t\): aliquota fiscale  
- \(V = D + E\): valore complessivo del capitale investito  
""")


with st.expander(" Indicatori principali"):
    st.markdown("""
- **TIR progetto:**  
  Rendimento complessivo del progetto, prima della leva finanziaria.
  E' ricavato dalla formula del VAN, trovando il WACC che fa sì che il VAN sia zero.
  Se il TIR è maggiore del WACC "di equilibrio" il progetto crea valore per tutti gli investitori.
  """)
    st.latex(r"""
    0 = -CAPEX + \sum_{t=1}^{T} \frac{FCF_t}{(1 + TIR_{proj})^t}
    """)

    st.markdown("""
- **TIR Equity**  
  Rendimento per l’azionista, dopo il servizio del debito.  
  """)
    st.latex(r"""
    0 = -E + \sum_{t=1}^{T} \frac{(FCF_t - DS_t)}{(1 + TIR_{eq})^t}
    """)
    st.markdown("""
  dove:  
  - \(E\): equity investito  
  - \(DS_t\): servizio del debito nel periodo \(t\)  
  - \(FCF_t\): flusso operativo (unlevered)
  """)

    st.markdown("""
- **DSCR (Debt Service Coverage Ratio):**  
  Misura la capacità di rimborso del debito anno per anno.  
  """)
    st.latex(r"""
    DSCR_t = \frac{FCF_t}{Servizio\_del\_debito_t}
    """)

    st.markdown("""
- **VAN progetto (Valore Attuale Netto):**  
  Misura la creazione di valore del progetto per tutti i finanziatori.  
  Tiene conto del **WACC** (costo medio ponderato del capitale), e quindi del costo del finanziamento tramite equity e debito, considerando
  i flussi di cassa operativi e gli investimenti iniziali.  
  Se inseriamo il TIR di equilibrio il VAN è 0. Quindi per TIR maggiori a quelli di equilibrio il VAN è positivo ed il progetto genera rendimento.
                
  Ricapitoliamo le condizioni economiche di fattibilità: 
                Se TIR > WACC ⇒  VAN > 0  : il progetto crea valore economico.
                Se TIR < WACC ⇒  VAN < 0  : il progetto distrugge valore economico.
  Ricordiamo la prospettiva delle banche (fattibilità finanziaria): 
                Un progetto può avere un VAN positivo ma non essere bancabile se i flussi non sono distribuiti bene nel tempo.
                Se DSCR > 1.2 il progetto ha una buona capacità di rimborso del debito.
                Se DSCR < 1.0 il progetto non riesce a coprire le rate del debito.
                Per valori compresi tra 1.2 e 1 la bancabilità del progetto non è al riparto da eventuali spese impreviste.
  Ricordiamo la prospettiva per l'azionista:
                Se Tir equity è maggiore di Ke atteso, l'investimento in equity è conveniente per l'azionista.

  """)
    st.latex(r"""
    VAN = -CAPEX + \sum_{t=1}^{T} \frac{FCF_t}{(1 + WACC)^t}
    """)



with st.expander(" Ipotesi esemplificative"):
    st.markdown("""
Le seguenti ipotesi semplificano la costruzione del modello per scopi didattici,
ma nella realtà di un Project Financing professionale dovrebbero essere affinate o integrate
con elementi aggiuntivi di complessità finanziaria.

- **Nessun capitale circolante operativo:**  
  Si assume che i crediti, debiti e scorte non assorbano né generino liquidità.  
  Nella realtà, la gestione del capitale circolante (ritardi nei pagamenti, tempi di incasso, ecc.)
  influenza significativamente i flussi di cassa.

- **Nessuno scudo fiscale sugli interessi passivi:**  
  Non si considera la deducibilità fiscale degli interessi passivi sul debito.  
  Questa ipotesi è conservativa: nella realtà, lo "scudo fiscale" riduce l’imposizione complessiva e migliora la redditività del progetto.

- **Nessun CAPEX di manutenzione o valore residuo:**  
  L’infrastruttura si considera integralmente ammortizzata alla fine della gestione e non si prevede
  un valore di rivendita o di subentro.  
  In un PEF reale, sarebbe importante considerare gli investimenti ricorrenti e il valore residuo dell’opera.

- **Nessun interesse capitalizzato durante la costruzione:**  
  Si ipotizza che gli oneri finanziari non vengano sommati al costo di costruzione.  
  In un caso reale, i costi del debito durante la costruzione possono essere “capitalizzati”
  e aggiunti al valore dell’investimento iniziale.

- **Nessun costo di transazione o commissione bancaria:**  
  Non si considerano costi accessori come commissioni di strutturazione, advisory, garanzie o notarili.  
  Questi costi riducono il rendimento effettivo e devono essere inclusi in un’analisi completa.
  """)


with st.expander(" Logica di bancabilità (criterio semaforo)"):
    st.markdown("""
La valutazione di bancabilità serve a verificare **se il progetto è sostenibile dal punto di vista economico e finanziario**.

**🟢 Progetto bancabile:**  
- **VAN > 0** → crea valore economico complessivo.  
- **TIR_progetto > WACC** → rendimento del progetto superiore al costo del capitale.  
- **DSCR_min ≥ 1.20** → capacità di rimborso solida e flussi stabili.  

**🟡 Progetto borderline:**  
- **VAN > 0** ma **DSCR_min tra 1.00 e 1.20** → valore economico positivo ma rischio di tensione di cassa.  
- Potrebbe essere bancabile con garanzie integrative o revisione della struttura finanziaria.  

**🔴 Progetto non bancabile:**  
- **VAN < 0** → distruzione di valore economico (il progetto non remunera il capitale).  
- **DSCR_min < 1.00** → flussi di cassa insufficienti per coprire il servizio del debito.  
- Anche un progetto economicamente buono (VAN > 0) può risultare non bancabile
  se i flussi non sono ben distribuiti nel tempo.
  """)


with st.expander(" Note didattiche"):
    st.markdown("""
- Il confronto **TIR_progetto vs WACC** fornisce un criterio sintetico di convenienza economica:  
  se il TIR è superiore al WACC, il progetto **crea valore**; se è inferiore, **lo distrugge**.

- Il parametro **DSCR_min = 1.20** è uno standard di riferimento comunemente usato
  dagli istituti di credito: rappresenta il margine minimo accettabile per considerare un progetto sostenibile.

- Il modello non calcola indicatori più avanzati come:
  - **LLCR (Loan Life Coverage Ratio):** misura la copertura del debito residuo nel tempo;  
  - **PLCR (Project Life Coverage Ratio):** analizza la copertura del debito sull’intera vita del progetto;  
  - **TIR Equity su dividendi effettivi**, utile per valutare progetti con politiche di distribuzione complesse.

- L’obiettivo del modello è **didattico**: mostrare come la struttura finanziaria
  (rapporto debito/equity, costo del capitale, inflazione, ecc.)
  influenzi la **redditività complessiva e la sostenibilità finanziaria** del progetto.
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

with st.expander("ℹSpiegazione degli indicatori"):
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
# SEZIONE 4: VALUTAZIONE DI BANCABILITÀ (aggiornata)
# ---------------------------------------------------------------------
st.header("Valutazione di bancabilità")

if van > 0 and tir_proj > wacc and dscr_min >= 1.2:
    st.success("🟢 Progetto **bancabile**")
    st.markdown("""
    - **VAN > 0** → il progetto crea valore economico.  
    - **TIR_progetto > WACC** → rendimento complessivo superiore al costo del capitale.  
    - **DSCR_min ≥ 1.20** → buona capacità di rimborso del debito.
    """)

elif (van > 0 and (0.95 * wacc) <= tir_proj <= (1.05 * wacc)) or (1.0 <= dscr_min < 1.2):
    st.warning("🟡 Progetto **borderline**")
    st.markdown("""
    - **DSCR_min tra 1.0 e 1.2** → margine di sicurezza ridotto.  
    - **Oppure TIR_progetto ≈ WACC** → rendimento vicino al costo del capitale.  
    - **VAN > 0** → il progetto può creare valore, ma con equilibrio delicato.  

    **Azioni possibili:**  
    - Aumentare la quota **Equity** o la durata della concessione.  
    - Ridurre **CAPEX/OPEX** o negoziare un tasso più basso (Kd).
    """)

elif van < 0 or dscr_min < 1.0 or tir_proj < 0.95 * wacc:
    st.error("🔴 Progetto **non bancabile**")
    st.markdown("""
    - **VAN < 0** → distruzione di valore economico.  
    - **DSCR_min < 1.0** → flussi insufficienti per il servizio del debito.  
    - **TIR_progetto < WACC** → rendimento inferiore al costo del capitale.  
    """)

else:
    st.info("ℹ️ Progetto in equilibrio limite")
    st.markdown("""
    Il progetto presenta indicatori misti o in equilibrio incerto.  
    Si consiglia un’analisi di sensibilità sui principali parametri.
    """)
st.caption("""
Legenda:
- **WACC** = costo medio del capitale (mix debito + equity)  
- **TIR_progetto** = rendimento complessivo del progetto  
- **DSCR_min** = sostenibilità finanziaria minima nel tempo  
""")

st.caption("Simulazione didattica semplificata – non sostituisce un'analisi professionale.")
