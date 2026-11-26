# PyArchInit - StratiGraph: Pannello Sincronizzazione

> Il pannello e la finestra della stanza seguono la lingua dell'interfaccia di QGIS; qui sotto i pulsanti sono citati come appaiono in italiano.

## Indice
1. [Introduzione](#introduzione)
2. [Accesso al pannello](#accesso-al-pannello)
3. [Comprensione dell'interfaccia](#comprensione-dellinterfaccia)
4. [Esportazione dei bundle](#esportazione-dei-bundle)
5. [Sincronizzazione](#sincronizzazione)
6. [Gestione della coda](#gestione-della-coda)
7. [Inviare un sito a una stanza StratiGraph](#inviare-un-sito-a-una-stanza-stratigraph)
8. [Configurazione](#configurazione)
9. [Risoluzione dei problemi](#risoluzione-dei-problemi)
10. [Domande Frequenti](#domande-frequenti)

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
| **Esporta pacchetto** | Crea un bundle dai dati locali, lo valida e lo aggiunge alla coda di sincronizzazione |
| **Sincronizza ora** | Forza un tentativo immediato di sincronizzazione (disponibile solo quando online) |
| **Coda...** | Apre la finestra di gestione della coda con tutti gli elementi |
| **Invia il sito a una stanza...** | Accede a un nodo StratiGraph e porta un sito in una stanza (vedi sotto) |

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
3. Fare clic sul pulsante **Esporta pacchetto**
4. Il sistema esegue automaticamente tre operazioni:
   - **Esportazione**: I dati locali vengono impacchettati in un file bundle
   - **Validazione**: Il bundle viene controllato per completezza e integrita dei dati
   - **Accodamento**: Il bundle validato viene aggiunto alla coda di sincronizzazione
5. Osservare l'**indicatore di stato** che attraversa: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. Il **log delle attivita** registra ogni passaggio con un timestamp

### Cosa contiene un bundle

Un bundle contiene tutte le entita archeologiche che hanno UUID (vedere il Tutorial 31 per i dettagli sugli UUID). Ogni entita e identificata dal suo `entity_uuid`, garantendo che lo stesso record venga sempre riconosciuto sul server.

<!-- IMAGE: Pulsante Esporta pacchetto e transizione di stato -->
> **Fig. 4**: Clic su "Esporta pacchetto" e osservazione dei cambiamenti di stato nel pannello

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
2. Fare clic sul pulsante **Sincronizza ora**
3. Il sistema tenta immediatamente di caricare tutti i bundle in attesa

Il pulsante **Sincronizza ora** e efficace solo quando il sistema e online.

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

<!-- IMAGE: Pulsante Sincronizza ora e indicatore di connessione -->
> **Fig. 5**: Il pulsante "Sincronizza ora" e l'indicatore dello stato di connessione

---

## Gestione della coda

Il pulsante **Coda...** apre una finestra di dialogo dettagliata dove e possibile ispezionare tutti i bundle nella coda di sincronizzazione.

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

## Inviare un sito a una stanza StratiGraph

Dalla versione **5.14.0-alpha** il pulsante **Invia il sito a una stanza...** porta un sito in una *stanza* di un nodo StratiGraph (StratiGraph Server). Il grafo del sito diventa il contenuto della stanza, dove EMStudio, EM Tools e gli altri strumenti del progetto lo vedono e ci lavorano.

![Pannello StratiGraph Sync](images/32_stratigraph_sync/06_sync_panel_send_button.png)

> **Fig. 7**: Il pannello StratiGraph Sync con il pulsante **Invia il sito a una stanza...**

### Procedura passo per passo

1. Nel pannello **StratiGraph Sync** premere **Invia il sito a una stanza...**
2. **Nodo**: l'indirizzo del nodo, per esempio `https://nodo.example.org/em`. Viene ricordato tra una sessione e l'altra.
3. **Sito**: scegliere il sito. **Id della stanza** e **Titolo della stanza** si compilano dal nome del sito e si possono cambiare; l'id della stanza e una sola parola, senza spazi.
4. Premere **Accedi...**: si apre nel browser la pagina di accesso del nodo. Accedere con il proprio account e tornare in QGIS: la riga **Identità** mostra il nome e se si possono creare stanze.
5. Facoltativo: **Solo piano** mostra cosa verrebbe inviato senza scrivere niente sul nodo.
6. Premere **Invia il sito**: il log riporta i nodi e gli archi esportati e l'esito dell'invio.

![Finestra Invia il sito a una stanza](images/32_stratigraph_sync/07_send_site_dialog.png)

> **Fig. 8**: La finestra dopo l'accesso e l'invio del sito di esempio a un nodo di sviluppo: 745 operazioni applicate, 0 rifiutate, il database tenuto come riferimento

### Cosa viene inviato

- Il grafo del sito intero, come un solo grafo anche quando il sito ha piu saggi: cosi i rapporti fra unita di saggi diversi viaggiano con il resto.
- I file citati dal grafo vengono caricati una sola volta. Inviare di nuovo lo stesso sito non duplica niente.
- **I file di database non vengono mai caricati** (sqlite, spatialite, gpkg): nella stanza resta solo un riferimento. Cosi gli altri siti del database restano sul proprio computer.
- La password non passa da pyArchInit: si scrive solo nella pagina del nodo. Il token di accesso resta in memoria e si perde chiudendo la finestra.

### Da riga di comando

Lo stesso invio, senza QGIS (senza `--dry-run` scrive davvero; senza `--token` apre il browser per l'accesso):

```bash
python scripts/stratigraph_send_site.py --db ~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite \
    --site "Scavo archeologico" --node https://nodo.example.org/em --room scavo-2026 --dry-run
```

### Lavorare con una stanza che ha gia dei dati

Quando nella stanza lavorano anche altri (EMStudio, StratiField, EM Tools), dopo l'accesso:

1. **Confronta con la stanza** confronta il sito con la stanza nei due sensi, senza scrivere niente: cosa ha di nuovo la stanza per pyArchInit (unita nuove, definizioni cambiate, rapporti) e cosa aggiunge pyArchInit alla stanza.
2. **Invia le modifiche** invia alla stanza il lavoro fatto qui: unità e rapporti nuovi, campi cambiati qui, rapporti tolti qui. Quello che è cambiato solo nella stanza non viene toccato; un campo cambiato da entrambe le parti è un conflitto e viene solo mostrato (vedi «Sincronizzazione con memoria»).
3. **Porta dalla stanza** porta la stanza nelle schede di pyArchInit (US, definizioni, periodizzazione, rapporti), riconoscendo ogni scheda dal suo identificativo. Se il pull togliesse rapporti locali che la stanza non conosce, la finestra li elenca e chiede conferma.

Con **Porta dalla stanza** si puo anche ricostruire un sito in un database che non lo ha: le unita tornano con numero, tipo, definizioni e periodizzazione. Le unita di continuita (CON) non viaggiano: pyArchInit le rigenera con **Genera continuita**.

La stanza riceve la scheda US intera, non solo i campi del grafo: descrizione, interpretazione, colore, consistenza, quote, misure, saggio, ambiente, quadrato, settore, i campi USM. Una scheda ricostruita da una stanza e uguale all'originale; i rapporti cambiano solo nella scrittura (con area e sito). Una stanza inviata con una versione precedente di pyArchInit ha solo i campi del grafo: il confronto mostra molti campi diversi; basta un nuovo **Invia il sito** per completarla.

Tutto questo vale sia per SQLite sia per PostgreSQL. Per ricostruire un sito basta un database pyArchInit creato e vuoto, aperto in pyArchInit: **Porta dalla stanza** lo popola (sito, schede, periodizzazione, rapporti, media). I rapporti hanno sempre quattro elementi: tipo, US, area, sito.

![Confronto con la stanza](images/32_stratigraph_sync/08_compare_with_room.png)

> **Fig. 9**: Il confronto con una stanza in cui si e lavorato anche in EMStudio: una US nuova e una definizione rivista nella stanza, una US nuova di pyArchInit da inviare

### Foto e media nella stanza

Le foto, i video, i modelli 3D e i documenti collegati alle schede US viaggiano con il sito, nei due sensi. Le ortofoto e gli altri raster restano fuori: sono layer di QGIS, non media di pyArchInit.

- **Invia il sito** e **Invia le modifiche** caricano ogni file nel deposito della stanza una sola volta: un file che la stanza ha gia (stesso contenuto) non viene rimandato. Se l'originale non e piu sul disco si usa la copia della cartella Resize.
- **Porta dalla stanza** scarica i media nuovi nella cartella `stratigraph_media/<stanza>` della home di pyArchInit, crea miniatura e copia come quando si carica un file dalla scheda e li collega alla loro US, con descrizione e tag. Un media che il database ha gia (riconosciuto dal suo identificativo) non viene riscaricato: si controlla solo il collegamento.
- I media di reperti, ceramica, tombe e strutture per ora restano locali: la finestra li conta.

![Una foto nuova inviata alla stanza](images/32_stratigraph_sync/09_room_media.png)

> **Fig. 10**: Una foto aggiunta alla US 3 dopo l'invio del sito: il confronto la trova e Invia le modifiche carica il file e il suo collegamento

### Sincronizzazione con memoria

Dopo il primo **Porta dalla stanza** (o il primo **Invia il sito**) pyArchInit ricorda la stanza com'era in quel momento: è la *base* comune, salvata nella cartella `stratigraph_rooms` della home di pyArchInit, una per database, sito e stanza. Da allora:

- il confronto legge dalla stanza **solo le novità** arrivate dopo l'ultima sincronizzazione, non tutto il documento;
- ogni differenza ha un autore: **cambiato qui** (si invia), **cambiato nella stanza** (lo porta il pull), **cambiato da entrambe le parti** (conflitto, mostrato con i due valori), **tolto nella stanza** (il pull lo toglie anche qui), **tolto qui** (si invia);
- **Porta dalla stanza** non sovrascrive mai in silenzio il lavoro non ancora inviato: se ci sono modifiche locali, conflitti, rapporti aggiunti o tolti qui, la finestra li elenca e consiglia di inviarli prima. In un conflitto confermato vince il valore della stanza.

Le unità che il pull non porta di proposito (le continuità CON generate e i loro media) restano nella stanza e non contano come rimozioni. Funziona allo stesso modo con SQLite e PostgreSQL.

![Confronto a tre vie](images/32_stratigraph_sync/10_three_way_compare.png)

> **Fig. 11**: Il confronto dopo una sincronizzazione: un campo cambiato qui da inviare, uno cambiato nella stanza da portare, un conflitto sullo stesso campo

### Problemi frequenti

| Messaggio | Cosa fare |
|-----------|-----------|
| `401` o accesso scaduto | La sessione si rinnova da sola mentre si lavora; se e scaduta del tutto (molte ore senza usarla) premere di nuovo **Accedi...** |
| `403` / *may create rooms: False* | L'account non ha un ruolo nella stanza o non puo creare stanze: chiedere all'amministratore del nodo |
| `CERTIFICATE_VERIFY_FAILED` | Il nodo usa un certificato locale (nodo di sviluppo o da campo): installarne la CA sul computer, oppure da riga di comando usare `--ca-file` |
| `409 ... already declared` | La stanza esiste e appartiene a un altro utente: scegliere un altro id |

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

Si. Ogni volta che si fa clic su "Esporta pacchetto", viene creato un nuovo bundle e aggiunto alla coda. Piu bundle possono essere accodati e verranno caricati in sequenza.

### Come faccio a sapere se i miei dati sono stati sincronizzati?

Controllare l'indicatore dell'**ultima sincronizzazione** nel pannello per il risultato piu recente. E anche possibile aprire la finestra **Coda...** per vedere lo stato di ogni singolo bundle.

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

[Apri Animazione Interattiva](../../animations/stratigraph_sync_animation.html)
