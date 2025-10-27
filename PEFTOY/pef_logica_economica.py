import numpy as np
import numpy_financial as npf
import pandas as pd


################### LOGICA DEL PEF #####################
### 1 - Linea temporale: anni di costruzione + anni di gestione
### 2 - CapEx: distribuite uniformemente sugli anni di costruzione (dovrebbero aumentare di anno in anno indicizzati all'inflazione)
### 3 - Ricavi: sono zero durante la costruzione e poi crescono per inflazione. Dovremmo fare anche delle stime sulla domanda (in crescita o in decrescita)

###### CONTO ECONOMICO STRUTTURA OPERATIVA ######  
### 1 - EBITDA: Ricavi - Opex
### 2 - Ammortamenti: CAPEX / durata gestione (ammortamento lineare, ipotesi esemplificativa)
### 3 - EBIT: EBITDA - Ammortamenti
### 4 - Imposte: max(EBIT, 0) * aliquota fiscale
### 5 - Utile netto: EBIT - Imposte
### 6 - Flusso operativo: Utile netto + Ammortamenti (post-imposte, pre-debito)

###### STRUTTURA FINANZIARIA ######
### - Debito: CAPEX * (1 - %equity)
### - Equity: CAPEX * %equity
### - Servizio del debito: rata costante (formula francese)
### - Costo medio ponderato del capitale (WACC): 
###   WACC = (%Equity * Ke) + (%Debito * Kd * (1 - Aliquota fiscale))

###### INDICATORI PRINCIPALI ######
### - VAN progetto: NPV dei flussi unlevered al WACC
### - TIR progetto: IRR dei flussi unlevered
### - TIR equity: IRR dei flussi levered (solo per la quota equity)
### - DSCR: CF operativo / Servizio del debito

###### IPOTESI ESEMPLIFICATIVE ######
### - Nessun capitale circolante
### - Nessun scudo fiscale sugli interessi
### - Nessun CAPEX di manutenzione o valore residuo
### - Nessun interesse durante costruzione
########################################################


def calcola_pef(capex, opex, ricavi, inflazione, durata_costruzione, durata_gestione,
                tasso_interesse, aliquota_fiscale, perc_equity, costo_equity=8.0):
    """
    Calcola i flussi di cassa e gli indicatori principali del PEF.
    Restituisce (df, van_progetto, tir_progetto, tir_equity, wacc, dscr_medio, dscr_min)
    """

    perc_debito = 100 - perc_equity
    anni = np.arange(1, durata_gestione + durata_costruzione + 1)

    # Ricavi e costi con inflazione
    ricavi_annui = np.array(
        [0]*durata_costruzione + [ricavi*((1+inflazione/100)**i) for i in range(durata_gestione)]
    )
    opex_annui = np.array(
        [0]*durata_costruzione + [opex*((1+inflazione/100)**i) for i in range(durata_gestione)]
    )

    # Investimenti in costruzione
    investimenti = np.array(
        [capex/durata_costruzione if i < durata_costruzione else 0 for i in range(len(anni))]
    )

    # Conto economico semplificato
    ebitda = ricavi_annui - opex_annui
    ammortamenti = np.array(
        [capex/durata_gestione if i >= durata_costruzione else 0 for i in range(len(anni))]
    )
    ebit = ebitda - ammortamenti

    # Imposte e utile netto
    imposte = np.maximum(ebit, 0) * (aliquota_fiscale / 100)
    utile_netto = ebit - imposte

    # Flusso operativo (unlevered)
    flusso_cassa_operativo = utile_netto + ammortamenti

    # Servizio del debito
    debito_iniziale = capex * (perc_debito / 100)
    rata_annua = npf.pmt(tasso_interesse/100, durata_gestione, -debito_iniziale)
    rata_annua = np.array([0]*durata_costruzione + [rata_annua]*durata_gestione)

    # Flusso di cassa per l’equity (levered)
    equity_iniziale = capex * (perc_equity / 100)
    flussi_equity = np.array(
        [-equity_iniziale] + [f - r for f, r in zip(flusso_cassa_operativo[1:], rata_annua[1:])]
    )

    # Calcolo del WACC
    ke = costo_equity / 100
    kd = tasso_interesse / 100
    we = perc_equity / 100
    wd = perc_debito / 100
    wacc = we * ke + wd * kd * (1 - aliquota_fiscale / 100)

    # Calcolo VAN e TIR progetto (unlevered)
    van_progetto = npf.npv(wacc, np.concatenate(([-capex], flusso_cassa_operativo[durata_costruzione:])))
    tir_progetto = npf.irr(np.concatenate(([-capex], flusso_cassa_operativo[durata_costruzione:])))

    # Calcolo TIR equity (levered)
    tir_equity = npf.irr(flussi_equity)

    # DSCR
    dscr = (flusso_cassa_operativo[durata_costruzione:] / rata_annua[durata_costruzione:])
    dscr_medio = np.nanmean(dscr)
    dscr_min = np.nanmin(dscr)

    # DataFrame riepilogativo
    df = pd.DataFrame({
        "Anno": anni,
        "Ricavi": ricavi_annui,
        "OPEX": opex_annui,
        "EBITDA": ebitda,
        "Ammortamenti": ammortamenti,
        "Utile netto": utile_netto,
        "Flusso operativo": flusso_cassa_operativo,
        "Servizio debito": rata_annua,
    })

    return df, van_progetto, tir_progetto, tir_equity, wacc, dscr_medio, dscr_min
