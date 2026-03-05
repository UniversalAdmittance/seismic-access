# 🏗️ SEISMIC ACCESS — Validatore di Accessibilità Sismica Urbana

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://seismic-access.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-Under_Review-orange.svg)](#)

**A Two-Tier Framework for Post-Seismic Urban Road Network Accessibility**  
*Deterministic Geometric Screening and Probabilistic Correlated Network Risk*

> **Il tuo piano CLE protegge davvero i tuoi cittadini?**  
> Questo strumento dimostra come il metodo CLE standard sovrastimi i blocchi stradali fino all'87%, rendendo i piani di emergenza inutilizzabili — mentre manca i blocchi reali causati dai vincoli cinematici dei veicoli.

---

## 🎯 Cosa Fa

Questa web app confronta in tempo reale il metodo **CLE-2D** (standard italiano per la Condizione Limite per l'Emergenza) con il nostro **framework cinematico a due livelli**:

| | CLE-2D Standard | Nostro Framework |
|---|---|---|
| **Detriti** | Cerchio isotropo R = h | Cuneo direzionale θ(tipologia) |
| **Distanza** | Centroide → Mezzeria | Edge-to-edge poligonale |
| **Veicolo** | Nessun vincolo | Sagoma autopompa + margini + curva |
| **Incertezza** | Deterministica | Monte Carlo spazialmente correlato |
| **Output** | Bloccato / Non bloccato | USAI + percentili + corridoi critici |

## 🚀 Demo Online

**[▶️ Prova la Demo](https://seismic-access.streamlit.app)**

Tre modalità:
1. **🔬 Sezione Stradale** — Analisi interattiva di una singola sezione: imposta larghezza, altezza, tipologia e vedi immediatamente il confronto CLE vs Tier I
2. **🏘️ Rete Urbana (Demo)** — Inventario sintetico di 451 edifici calibrato su Amatrice (RI) con curve USAI e analisi di ablazione
3. **📁 Dati Personalizzati** — Carica i CSV del tuo Comune ed esegui l'analisi completa

## 📊 Risultati Chiave (dal Paper)

A **PGA = 0.15g** su un centro storico appenninico:

- CLE-2D dichiara **87%** dei segmenti bloccati → USAI = 0.00 (comune irraggiungibile)
- Tier I identifica **25%** dei blocchi → USAI = 0.67 (ospedale, municipio, carabinieri raggiungibili)
- **71%** di riduzione dei falsi positivi
- Il vincolo veicolo è il componente più influente: **ΔUSAI = −0.22**

## 🛠️ Installazione Locale

```bash
git clone https://github.com/[your-username]/seismic-access.git
cd seismic-access
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Formato Dati per Analisi Personalizzata

### Inventario Edifici (`edifici.csv`)

```csv
id,x,y,height,typology,storeys,confinement,slope,soil
1,100.5,200.3,9.0,URM_low,3,mid_row,0.05,C
2,105.2,201.1,12.0,URM_mid,4,end_row,0.08,B
```

| Campo | Tipo | Valori |
|-------|------|--------|
| `id` | int | identificativo univoco |
| `x`, `y` | float | coordinate metriche (UTM consigliato) |
| `height` | float | altezza geometrica in metri |
| `typology` | str | `URM_low`, `URM_mid`, `RC_old`, `RC_new` |
| `storeys` | int | numero di piani |
| `confinement` | str | `isolated`, `end_row`, `mid_row`, `courtyard` |
| `slope` | float | pendenza locale (0.0–0.3) |
| `soil` | str | classe suolo EC8: `A`, `B`, `C`, `D`, `E` |

### Rete Stradale (`strade.csv`)

```csv
id,x1,y1,x2,y2,width,r_min
1,90.0,200.0,120.0,200.0,4.5,100
2,120.0,200.0,120.0,230.0,3.5,15
```

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | int | identificativo segmento |
| `x1,y1,x2,y2` | float | coordinate nodi (m) |
| `width` | float | larghezza carreggiata (m) |
| `r_min` | float | raggio minimo di curvatura (m) |

## 🏗️ Deploy su Streamlit Cloud (Gratuito)

1. Fai fork di questo repository
2. Vai su [share.streamlit.io](https://share.streamlit.io)
3. Seleziona il tuo repository → Main file: `app.py`
4. Deploy 🚀

## 📄 Riferimento Scientifico

```bibtex
@article{giannini2025seismic,
  title={A Two-Tier Framework for Seismic Road Network Accessibility:
         Deterministic Geometric Screening and Probabilistic Correlated Network Risk},
  author={Giannini, Leonardo and Nescatelli, Nicola},
  journal={Under Review},
  year={2025}
}
```

## 📧 Contatti

- **Leonardo Giannini** — Sapienza Università di Roma — leonardo.giannini@uniroma1.it
- **Nicola Nescatelli** — Plantiverse S.r.l. — Roma

---

<p align="center">
  <em>Il metodo CLE standard non è conservativo: è disinformativo.<br>
  Un metodo che genera l'87% di falsi positivi mentre manca il collo di bottiglia critico non protegge nessuno.</em>
</p>
