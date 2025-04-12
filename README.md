# 🗾 Viaggio in Giappone - Applicazione di Pianificazione

## Panoramica
Applicazione web per pianificare e tenere traccia dei dettagli di un viaggio in Giappone. Permette di gestire costi, attività e memorie fotografiche del viaggio.

## Setup
1. **Installazione**
```bash
pip install streamlit folium streamlit-folium pandas pytz pillow
```

2. **Struttura Directory**
```
viaggio-giappone/
├── app.py                # Applicazione principale
├── data/                 # Directory per i dati
│   ├── viaggio_data.json # File dati principale
│   └── backup/          # Backup automatici
└── photos/              # Directory per le foto
```

## 🗺️ Sezioni dell'App

### 1. Home
- Mappa interattiva del Giappone con marker per le città
- Statistiche generali dei costi
- Galleria casuale di 12 foto del viaggio

### 2. Volo e Assicurazione
Gestione dei costi pre-partenza:
- Dettagli volo (data, orari, compagnia)
- Costi assicurativi
- Altri costi (eSIM, contanti, etc.)

### 3. Attività per Città
Per ogni città puoi gestire:
- **🏨 Alloggi**
  - Nome struttura
  - Tipo alloggio
  - Date check-in/out
  - Costi
  - Note

- **🍜 Ristoranti**
  - Nome locale
  - Tipo cucina
  - Costi stimati
  - Prenotazione necessaria
  - Note

- **🛍️ Negozi**
  - Nome
  - Tipo
  - Budget stimato
  - Note

- **🎯 Attività**
  - Nome
  - Tipo
  - Data e durata
  - Costi
  - Prenotazione necessaria
  - Note

- **🚄 Trasporti**
  - JR Pass
  - Tratte individuali
  - Costi
  - Note

### 4. Riepilogo
- Dettagli volo e costi pre-partenza
- Riepilogo costi per città
- Riepilogo finale con statistiche

### 5. Galleria Foto
- Visualizzazione completa delle foto caricate
- Organizzazione in griglia
- Nomi foto visibili

## 💾 Gestione Dati

### Salvataggio
- Salvataggio automatico dopo ogni modifica
- Backup automatici
- Dati memorizzati in JSON

### Struttura Dati
```json
{
    "costi_partenza": {
        "voli": [],
        "assicurazioni": [],
        "altro": [],
        "totale_generale": 0
    },
    "dati_citta": {
        "nome_citta": {
            "alloggi": {},
            "ristoranti": {},
            "negozi": {},
            "attivita": {},
            "trasporti": {},
            "coordinate": {}
        }
    },
    "meta": {
        "ultima_modifica": "",
        "versione_dati": "1.0"
    }
}
```

## 📸 Gestione Foto

### Come Aggiungere Foto
1. Crea una cartella `photos` nella directory principale
2. Inserisci le foto (formati supportati: jpg, jpeg, png, gif)
3. Le foto verranno automaticamente visualizzate nella home e nella galleria

### Visualizzazione
- Home: 12 foto casuali
- Galleria: tutte le foto organizzate in griglia

## 🔧 Manutenzione

### Backup
- I backup vengono creati automaticamente dopo ogni modifica
- Si mantengono gli ultimi 10 backup
- I backup sono nella cartella `data/backup/`

### Problemi Comuni
1. **Foto non visibili**
   - Verifica che la cartella `photos` esista
   - Controlla i formati delle immagini

2. **Dati non salvati**
   - Verifica i permessi della cartella `data`
   - Controlla lo spazio disponibile

## 🚀 Avvio dell'App
```bash
streamlit run app.py
```

## 💡 Suggerimenti
1. **Organizzazione Foto**
   - Usa nomi descrittivi per le foto
   - Mantieni le dimensioni ragionevoli

2. **Gestione Dati**
   - Aggiorna regolarmente i costi
   - Usa le note per dettagli importanti
   - Verifica i totali nel riepilogo

3. **Pianificazione**
   - Inserisci prima i costi principali
   - Aggiorna le attività man mano che prenoti
   - Controlla regolarmente il budget totale

## 🔄 Aggiornamenti Futuri Pianificati
- Export dati in PDF/Excel
- Gestione multi-valuta
- Timeline del viaggio
- Integrazione mappe offline
- Gestione documenti di viaggio
