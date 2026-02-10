# PyArchInit - StratiGraph: Pannello Sincronizzazione

## Indice
1. [Introduzione](#introduzione)
2. [Accesso al pannello](#accesso-al-pannello)
3. [Comprensione dell'interfaccia](#comprensione-dellinterfaccia)
4. [Esportazione dei bundle](#esportazione-dei-bundle)
5. [Sincronizzazione](#sincronizzazione)
6. [Gestione della coda](#gestione-della-coda)
7. [Configurazione](#configurazione)
8. [Risoluzione dei problemi](#risoluzione-dei-problemi)
9. [Domande Frequenti](#domande-frequenti)

---

## Introduzione

A partire dalla versione **5.0.2-alpha**, PyArchInit include un pannello **StratiGraph Sync** che consente la sincronizzazione offline-first dei dati con il Knowledge Graph di StratiGraph. Questo pannello fa parte del progetto europeo **StratiGraph** (Horizon Europe) e implementa il flusso di lavoro offline-first: si lavora localmente senza internet, si esportano i bundle quando si e pronti e il sistema si sincronizza automaticamente quando la connettivita viene ripristinata.

<!-- VIDEO: Introduzione a StratiGraph Sync -->
> **Video Tutorial**: [Inserire link video introduzione StratiGraph Sync]

### Panoramica del flusso di lavoro

```
1. Lavoro offline       2. Esporta Bundle      3. Sincronizzazione
   (OFFLINE_EDITING)       (LOCAL_EXPORT)        (QUEUED_FOR_SYNC)
        |                      |                      |
   Inserimento dati      Esporta + Valida       Upload quando online
   normale in            + Accoda               con retry automatico
   PyArchInit
```

---

## Accesso al pannello

Il pannello StratiGraph Sync e nascosto per impostazione predefinita e puo essere attivato tramite un pulsante nella barra degli strumenti.

### Dalla barra degli strumenti

1. Cercare il pulsante **StratiGraph Sync** nella barra degli strumenti di PyArchInit -- ha un'icona verde con frecce di sincronizzazione e la lettera "S"
2. Fare clic sul pulsante per **mostrare** il pannello (e un pulsante a commutazione)
3. Fare clic nuovamente per **nascondere** il pannello

Il pannello appare come un **dock widget a sinistra** nell'interfaccia di QGIS. E possibile trascinarlo e riposizionarlo come qualsiasi altro pannello di QGIS.

<!-- IMAGE: Pulsante nella barra degli strumenti per StratiGraph Sync -->
> **Fig. 1**: Il pulsante StratiGraph Sync nella barra degli strumenti (icona verde con frecce di sincronizzazione e "S")

<!-- IMAGE: Pannello agganciato sul lato sinistro di QGIS -->
> **Fig. 2**: Il pannello StratiGraph Sync agganciato sul lato sinistro della finestra QGIS

---

## Comprensione dell'interfaccia

Il pannello StratiGraph Sync e suddiviso in diverse sezioni, dall'alto verso il basso.

### Indicatore di stato

L'**indicatore di stato** nella parte superiore del pannello mostra lo stato corrente della sincronizzazione dei dati. Gli stati possibili sono:

| Stato | Icona | Descrizione |
|-------|-------|-------------|
| **OFFLINE_EDITING** | Matita | Si sta lavorando localmente, modificando i dati normalmente |
| **LOCAL_EXPORT** | Pacchetto | Un bundle viene esportato dai dati locali |
| **LOCAL_VALIDATION** | Spunta | Il bundle esportato viene validato |
| **QUEUED_FOR_SYNC** | Orologio | Il bundle e stato validato e attende di essere caricato |
| **SYNC_SUCCESS** | Cerchio verde | L'ultima sincronizzazione e stata completata con successo |
| **SYNC_FAILED** | Cerchio rosso | L'ultimo tentativo di sincronizzazione e fallito |

### Indicatore di connessione

Sotto l'indicatore di stato, l'**indicatore di connessione** mostra se il sistema puo raggiungere il server StratiGraph:

| Stato | Significato |
|-------|-------------|
| **Online** | L'endpoint di health check e raggiungibile; la sincronizzazione automatica e attiva |
| **Offline** | L'endpoint di health check non e raggiungibile; i bundle verranno accodati |

Il sistema controlla automaticamente la connettivita ogni **30 secondi** (configurabile).

### Contatore della coda

Il **contatore della coda** visualizza due numeri:

- **Bundle in attesa**: Numero di bundle in attesa di essere caricati
- **Bundle falliti**: Numero di bundle il cui caricamento e fallito (verranno ritentati automaticamente)

### Ultima sincronizzazione

Mostra il **timestamp** e il **risultato** (successo o fallimento) dell'ultimo tentativo di sincronizzazione.

### Pulsanti di azione

| Pulsante | Azione |
|----------|--------|
| **Export Bundle** | Crea un bundle dai dati locali, lo valida e lo aggiunge alla coda di sincronizzazione |
| **Sync Now** | Forza un tentativo immediato di sincronizzazione (disponibile solo quando online) |
| **Queue...** | Apre la finestra di gestione della coda con tutti gli elementi |

### Log delle attivita

Nella parte inferiore del pannello, un **log delle attivita** scorrevole mostra voci con timestamp delle attivita recenti, inclusi cambiamenti di stato, esportazioni, validazioni e tentativi di sincronizzazione.

<!-- IMAGE: Pannello completo con tutte le sezioni annotate -->
> **Fig. 3**: Il pannello StratiGraph Sync completo con tutte le sezioni etichettate

---

## Esportazione dei bundle

L'esportazione di un bundle impacchetta i dati archeologici locali in un formato strutturato pronto per il caricamento sul Knowledge Graph di StratiGraph.

### Procedura passo per passo

1. Assicurarsi di aver salvato tutto il lavoro corrente in PyArchInit
2. Aprire il pannello StratiGraph Sync (se non gia visibile)
3. Fare clic sul pulsante **Export Bundle**
4. Il sistema esegue automaticamente tre operazioni:
   - **Esportazione**: I dati locali vengono impacchettati in un file bundle
   - **Validazione**: Il bundle viene controllato per completezza e integrita dei dati
   - **Accodamento**: Il bundle validato viene aggiunto alla coda di sincronizzazione
5. Osservare l'**indicatore di stato** che attraversa: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. Il **log delle attivita** registra ogni passaggio con un timestamp

### Cosa contiene un bundle

Un bundle contiene tutte le entita archeologiche che hanno UUID (vedere il Tutorial 31 per i dettagli sugli UUID). Ogni entita e identificata dal suo `entity_uuid`, garantendo che lo stesso record venga sempre riconosciuto sul server.

<!-- IMAGE: Pulsante Export Bundle e transizione di stato -->
> **Fig. 4**: Clic su "Export Bundle" e osservazione dei cambiamenti di stato nel pannello

---

## Sincronizzazione

### Sincronizzazione automatica

Quando il sistema rileva che si e **online** (l'health check ha successo), carica automaticamente tutti i bundle in attesa dalla coda. Non e richiesto alcun intervento manuale.

Il processo di sincronizzazione automatica:

1. Il controllo della connettivita ha successo (l'endpoint di health check risponde)
2. L'indicatore di connessione passa a **Online**
3. I bundle in attesa nella coda vengono caricati uno alla volta
4. I bundle caricati con successo vengono contrassegnati come `SYNC_SUCCESS`
5. Il timestamp e il risultato dell'**ultima sincronizzazione** vengono aggiornati

### Sincronizzazione manuale

Se si vuole forzare un tentativo immediato di sincronizzazione:

1. Assicurarsi che l'indicatore di connessione mostri **Online**
2. Fare clic sul pulsante **Sync Now**
3. Il sistema tenta immediatamente di caricare tutti i bundle in attesa

Il pulsante **Sync Now** e efficace solo quando il sistema e online.

### Retry automatico con backoff esponenziale

Se un caricamento fallisce, il sistema **non** si arrende. Invece, ritenta automaticamente con ritardi crescenti:

| Tentativo | Ritardo |
|-----------|---------|
| 1o retry | 30 secondi |
| 2o retry | 60 secondi |
| 3o retry | 120 secondi |
| 4o retry | 5 minuti |
| 5o retry | 15 minuti |

Questo impedisce di sovraccaricare il server quando e temporaneamente non disponibile, garantendo comunque la consegna finale.

<!-- IMAGE: Pulsante Sync Now e indicatore di connessione -->
> **Fig. 5**: Il pulsante "Sync Now" e l'indicatore dello stato di connessione

---

## Gestione della coda

Il pulsante **Queue...** apre una finestra di dialogo dettagliata dove e possibile ispezionare tutti i bundle nella coda di sincronizzazione.

### Colonne della finestra di dialogo della coda

| Colonna | Descrizione |
|---------|-------------|
| **ID** | Identificatore univoco dell'elemento nella coda |
| **Status** | Stato corrente dell'elemento (pending, syncing, success, failed) |
| **Attempts** | Numero di tentativi di caricamento effettuati |
| **Created** | Timestamp di quando il bundle e stato aggiunto alla coda |
| **Last Error** | Messaggio di errore dell'ultimo tentativo fallito (vuoto se nessun errore) |
| **Bundle path** | Percorso del file bundle nel file system |

### Interpretare gli elementi della coda

- Gli elementi **Pending** sono in attesa di essere caricati
- Gli elementi **Success** sono stati caricati e confermati dal server
- Gli elementi **Failed** verranno ritentati automaticamente; controllare la colonna **Last Error** per i dettagli
- Il conteggio **Attempts** aiuta a capire quante volte il sistema ha tentato di caricare un particolare bundle

### Archiviazione della coda

Il database della coda e memorizzato come file SQLite in:

```
$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite
```

Questo file persiste tra le sessioni di QGIS, quindi i bundle in attesa non vengono persi se si chiude QGIS.

<!-- IMAGE: Finestra di dialogo della coda con diversi elementi -->
> **Fig. 6**: La finestra di gestione della coda con gli elementi dei bundle

---

## Configurazione

### URL di Health Check

Il sistema utilizza un URL di health check per determinare la connettivita verso il server StratiGraph. E possibile configurarlo nelle impostazioni di QGIS:

| Impostazione | Chiave | Predefinito |
|-------------|--------|-------------|
| URL Health check | `pyArchInit/stratigraph/health_check_url` | `http://localhost:8080/health` |

Per modificare l'URL di health check:

1. Aprire **QGIS** -> **Impostazioni** -> **Opzioni** (oppure usare la console Python di QGIS)
2. Navigare alle impostazioni di PyArchInit o impostare tramite:

```python
from qgis.core import QgsSettings
s = QgsSettings()
s.setValue("pyArchInit/stratigraph/health_check_url", "https://il-tuo-server.esempio.com/health")
```

### Intervallo di controllo

L'intervallo di controllo della connettivita predefinito e di **30 secondi**. Anche questo puo essere configurato tramite QgsSettings.

---

## Risoluzione dei problemi

### Il pannello non appare

- Assicurarsi di utilizzare PyArchInit versione **5.0.2-alpha** o successiva
- Verificare che il pulsante StratiGraph Sync sia visibile nella barra degli strumenti
- Provare a disattivare e riattivare il pulsante
- Controllare **Sketchy** -> **Pannelli** in QGIS per vedere se il dock widget e elencato

### L'indicatore di connessione mostra sempre "Offline"

- Verificare che il server StratiGraph sia in esecuzione e raggiungibile
- Controllare l'URL di health check nelle impostazioni (predefinito: `http://localhost:8080/health`)
- Testare l'URL manualmente nel browser o con `curl`:

```bash
curl http://localhost:8080/health
```

- Se il server si trova su una macchina diversa, assicurarsi che non ci siano regole firewall che bloccano la connessione

### L'esportazione del bundle fallisce

- Assicurarsi che il database sia connesso e accessibile
- Verificare che i record abbiano UUID validi (Tutorial 31)
- Controllare il log delle attivita per messaggi di errore specifici
- Assicurarsi che ci sia spazio su disco sufficiente per il file bundle

### La sincronizzazione fallisce ripetutamente

- Controllare la colonna **Last Error** nella finestra della coda per i dettagli
- Cause comuni:
  - Il server e temporaneamente non disponibile (il sistema ritentera automaticamente)
  - Problemi di connettivita di rete
  - Il server ha rifiutato il bundle (controllare i log del server)
- Se un bundle fallisce costantemente dopo molti tentativi, considerare di riesportarlo

### Problemi con il database della coda

- Il database della coda si trova in `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite`
- Se corrotto, e possibile eliminarlo in sicurezza -- i bundle in attesa verranno persi, ma possono essere riesportati
- Eseguire il backup di questo file se e necessario preservare lo stato della coda

---

## Domande Frequenti

### Ho bisogno di internet per usare PyArchInit?

**No.** PyArchInit funziona completamente offline. Il pannello StratiGraph Sync gestisce solo la sincronizzazione con il server StratiGraph. E possibile lavorare interamente offline ed esportare/sincronizzare quando si e pronti.

### Cosa succede se chiudo QGIS con bundle in attesa?

I bundle in attesa sono salvati nel database della coda e saranno disponibili al riavvio di QGIS. Il sistema riprende la sincronizzazione automaticamente quando la connettivita viene ripristinata.

### Posso esportare piu bundle?

Si. Ogni volta che si fa clic su "Export Bundle", viene creato un nuovo bundle e aggiunto alla coda. Piu bundle possono essere accodati e verranno caricati in sequenza.

### Come faccio a sapere se i miei dati sono stati sincronizzati?

Controllare l'indicatore dell'**ultima sincronizzazione** nel pannello per il risultato piu recente. E anche possibile aprire la finestra **Queue...** per vedere lo stato di ogni singolo bundle.

### StratiGraph Sync funziona sia con PostgreSQL che con SQLite?

Si. Il sistema di sincronizzazione funziona con entrambi i backend di database supportati da PyArchInit. I bundle vengono esportati in un formato indipendente dal database.

### Qual e la relazione tra UUID e sincronizzazione?

Gli UUID (Tutorial 31) forniscono gli identificatori stabili che rendono possibile la sincronizzazione. Ogni entita in un bundle e identificata dal suo UUID, consentendo al server di abbinare, creare o aggiornare correttamente i record.

---

*Documentazione PyArchInit - StratiGraph Sync*
*Versione: 5.0.2-alpha*
*Ultimo aggiornamento: Febbraio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../../stratigraph_sync_animation.html)
