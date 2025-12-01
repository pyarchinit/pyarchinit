# PyArchInit Storage Proxy Server

Server proxy per storage remoto di PyArchInit usando Google Drive con Service Account.

## Deploy su Railway

### 1. Crea il Service Account Google

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona esistente
3. Abilita **Google Drive API**:
   - Menu → APIs & Services → Library
   - Cerca "Google Drive API" → Enable
4. Crea Service Account:
   - Menu → IAM & Admin → Service Accounts
   - **+ CREATE SERVICE ACCOUNT**
   - Nome: `pyarchinit-storage`
   - Click **CREATE AND CONTINUE** → **DONE**
5. Crea la chiave JSON:
   - Click sul service account creato
   - Tab **KEYS** → **ADD KEY** → **Create new key**
   - Tipo: **JSON**
   - Scarica il file

### 2. Condividi la cartella Google Drive

1. Vai su [Google Drive](https://drive.google.com/)
2. Crea una cartella (es. "PyArchInit_Media")
3. Tasto destro → **Condividi**
4. Aggiungi l'email del service account:
   - Es: `pyarchinit-storage@tuoprogetto.iam.gserviceaccount.com`
5. Dai permesso **Editor**
6. (Opzionale) Copia l'ID della cartella dall'URL:
   - `https://drive.google.com/drive/folders/XXXXXX` → `XXXXXX` è l'ID

### 3. Deploy su Railway

1. Vai su [Railway](https://railway.app/)
2. **New Project** → **Deploy from GitHub repo** (o upload)
3. Seleziona la cartella `storage_server`
4. Configura le **Environment Variables**:

```
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...TUTTO IL JSON..."}
GDRIVE_ROOT_FOLDER_ID=XXXXXX  (opzionale - ID cartella root)
API_KEY=una-chiave-segreta    (opzionale - per autenticazione)
```

**IMPORTANTE**: Per `GOOGLE_SERVICE_ACCOUNT_JSON` copia TUTTO il contenuto del file JSON su una singola riga.

5. Railway fa il deploy automatico
6. Copia l'URL generato (es. `https://pyarchinit-storage.up.railway.app`)

### 4. Configura PyArchInit

Negli utenti PyArchInit, imposta i path:

```
Thumbnail path: https://pyarchinit-storage.up.railway.app/files/thumbnails/
Resize path: https://pyarchinit-storage.up.railway.app/files/resize/
```

Se hai configurato `API_KEY`, gli utenti devono aggiungere l'header nelle richieste HTTP.

## API Endpoints

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/files/{path}` | Legge un file |
| PUT | `/files/{path}` | Scrive un file |
| DELETE | `/files/{path}` | Elimina un file |
| HEAD | `/files/{path}` | Verifica esistenza file |
| GET | `/list/{path}` | Lista file in directory |

## Test locale

```bash
# Installa dipendenze
pip install -r requirements.txt

# Imposta variabili ambiente
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
export GDRIVE_ROOT_FOLDER_ID='your-folder-id'

# Avvia server
uvicorn main:app --reload --port 8000

# Test
curl http://localhost:8000/
curl http://localhost:8000/list/
```

## Sicurezza

- Il Service Account ha accesso SOLO alle cartelle condivise con lui
- Usa `API_KEY` per proteggere l'accesso al server
- Non esporre le credenziali nel codice

## Costi

- **Railway**: Free tier include 500 ore/mese, poi ~$5/mese
- **Google Drive**: 15 GB gratuiti, poi Google One pricing
- **Alternative**: Render, Fly.io, Heroku (simile setup)
