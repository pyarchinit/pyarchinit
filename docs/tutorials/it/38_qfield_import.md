# Tutorial 38: Importa da QField (GPKG)

## Introduzione

La funzione **Importa da QField (GPKG)** porta in pyArchInit i dati raccolti sul
campo con **QField** tramite il plugin companion **pyarchinit-qfield**. Il
comando legge i GeoPackage (`.gpkg`) del progetto QField e le foto scattate sul
campo, e **appende** i record al database di pyArchInit senza duplicare le US e
i reperti già presenti: dei record esistenti riempie **solo i campi vuoti**,
senza mai sovrascrivere i valori già inseriti.

Il flusso è pensato per essere **sicuro**: prima si esegue un'**Anteprima
(dry-run)** che simula tutto senza scrivere nulla, poi — solo dopo conferma — si
lancia l'**Import** vero e proprio in un'unica transazione.

> Prerequisito: i dati devono essere stati raccolti sul campo con **QField**
> usando il plugin companion **pyarchinit-qfield**.

---

## 1. Prerequisiti

- Dati raccolti sul campo con **QField** tramite il plugin **pyarchinit-qfield**.
- La cartella del progetto QField contiene i file **`.gpkg`** e le fotografie
  sotto **`DCIM/pyarchinit`**.
- Un database pyArchInit configurato (SQLite/Spatialite o PostgreSQL/PostGIS):
  il DB viene **risolto automaticamente** dalla configurazione del plugin.

---

## 2. Aprire il dialog

Il comando è raggiungibile in **due modi**:

1. **Menu**: **Plugin → pyArchInit - Archaeological GIS Tools → Importa da
   QField (GPKG)**.
2. **Toolbar** (novità): nella barra degli strumenti di pyArchInit apri il
   **pulsante a tendina degli strumenti di analisi** — lo stesso che raccoglie
   GeoArchaeo, MoveCost, Palimpsest e altri strumenti — e scegli **Importa da
   QField (GPKG)**. La voce si riconosce dalla **nuova icona dedicata**: una
   tessera verde arrotondata in stile QField con un segnaposto bianco che
   scende in un vassoio di importazione.

In entrambi i casi si apre il dialog *Importa da QField*: QGIS **non si
blocca** durante l'operazione perché la copia delle foto e l'accesso a WebDAV
girano in un thread separato.

---

## 3. Selezionare la cartella del progetto QField

1. Premi **Sfoglia…** e scegli la **cartella del progetto QField**.
2. Il dialog **scansiona i GeoPackage** e popola automaticamente la tendina
   **Sito** con i siti trovati.
3. Scegli un sito specifico oppure lascia **Tutti i siti** per importare tutto.

---

## 4. Opzioni di importazione

| Opzione | Significato |
|---|---|
| **SRID (vuoto = dal GPKG)** | sistema di riferimento; lascia vuoto per leggerlo dal GeoPackage |
| **Destinazione foto** | precompilata con la cartella media configurata (locale o WebDAV) |
| **Deduplica geometrie** | evita di reinserire geometrie identiche già presenti |
| **Copia foto** | copia le fotografie nel backend media |
| **Genera thumbnail** | crea automaticamente le miniature delle foto |

Le tre caselle sono **attive di default**.

---

## 5. Anteprima (dry-run)

Premi **Anteprima (dry-run)**: l'intera importazione viene eseguita in
**simulazione**, **senza scrivere nulla** nel database. Il log mostra:

- quante **US**, **reperti**, **geometrie**, **punti quota**, **foto** e
  **collegamenti** verrebbero importati;
- esattamente **quali campi vuoti** dei record esistenti verrebbero riempiti.

È il passaggio da usare sempre per verificare l'esito prima di scrivere.

---

## 6. Importa

Premi **Importa** (viene chiesta una **conferma**). L'operazione:

- **appende** i record in **un'unica transazione**;
- **non duplica** le US e i reperti già esistenti: ne riempie **solo i campi
  vuoti**, senza mai sovrascrivere i valori già presenti;
- **copia le foto** nel backend media e ne **genera le miniature**
  automaticamente;
- assegna ai record importati un **`node_uuid`** e li marca con
  **`created_by = 'qfield_import'`**.

---

## 7. Dopo l'importazione

Controlla i **rapporti stratigrafici** delle US importate: **non vengono
dedotti automaticamente** e vanno completati a mano nella scheda US.

---

## 8. Alternativa da riga di comando (CLI)

Per usi avanzati o headless è disponibile lo script CLI. Il **dry-run è il
comportamento predefinito**; aggiungi `--apply` per scrivere davvero:

```bash
# Anteprima (dry-run, default)
python3 scripts/import_qfield.py --qfield-dir <cartella>

# Importazione reale
python3 scripts/import_qfield.py --qfield-dir <cartella> --apply
```

---

*Documentazione PyArchInit — Luglio 2026*
