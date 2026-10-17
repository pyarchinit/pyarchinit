# Tutorial 13: Gestione Thesaurus

## Introduzione

Il **Thesaurus** di PyArchInit e il sistema centralizzato per la gestione dei vocabolari controllati. Permette di definire e mantenere le liste di valori utilizzate in tutte le schede del plugin, garantendo coerenza terminologica e facilitando la ricerca.

### Funzioni Principali

- Gestione vocabolari per ogni scheda
- Supporto multilingua
- Sigle e descrizioni estese
- Integrazione con GPT per suggerimenti
- Import/export da file CSV

---

## Accesso al Thesaurus

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Thesaurus** (o **Thesaurus form**)

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Thesaurus** (libro/dizionario)

---

## Panoramica dell'Interfaccia

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigazione, ricerca, salvataggio |
| 2 | Selezione Tabella | Scelta della scheda da configurare |
| 3 | Campi Sigla | Codice, estensione, tipologia |
| 4 | Descrizione | Descrizione dettagliata del termine |
| 5 | Lingua | Selezione lingua |
| 6 | Strumenti | Import CSV, suggerimenti GPT |

---

## Campi del Thesaurus

### Nome Tabella

**Campo**: `comboBox_nome_tabella`
**Database**: `nome_tabella`

Seleziona la scheda per cui definire i valori.

**Tabelle disponibili:**
| Tabella | Descrizione |
|---------|-------------|
| `us_table` | Scheda US/USM |
| `site_table` | Scheda Sito |
| `periodizzazione_table` | Periodizzazione |
| `inventario_materiali_table` | Inventario Materiali |
| `pottery_table` | Scheda Pottery |
| `campioni_table` | Scheda Campioni |
| `documentazione_table` | Documentazione |
| `tomba_table` | Scheda Tomba |
| `individui_table` | Scheda Individui |
| `fauna_table` | Archeozoologia |
| `ut_table` | Scheda UT |

### Sigla

**Campo**: `comboBox_sigla`
**Database**: `sigla`

Codice breve/abbreviazione del termine.

**Esempi:**
- `MR` per Muro
- `US` per Unita Stratigrafica
- `CR` per Ceramica

### Sigla Estesa

**Campo**: `comboBox_sigla_estesa`
**Database**: `sigla_estesa`

Forma completa del termine.

**Esempi:**
- `Muro perimetrale`
- `Unita Stratigrafica`
- `Ceramica comune`

### Descrizione

**Campo**: `textEdit_descrizione_sigla`
**Database**: `descrizione`

Descrizione dettagliata del termine, definizione, note d'uso.

### Tipologia Sigla

**Campo**: `comboBox_tipologia_sigla`
**Database**: `tipologia_sigla`

Codice numerico che identifica il campo di destinazione.

**Struttura codici:**
```
X.Y dove:
X = numero della scheda (1 Sito, 2 US/USM, 3 Inventario materiali, 4 Campioni, 6 Struttura,
    7 Tomba, 8 Individui, 9 Documentazione, 10 TMA, 11 Pottery, 12 UT, 13 Fauna)
Y = numero del campo
```

**Esempi per us_table:**
| Codice | Campo |
|--------|-------|
| 2.1 | Settore |
| 2.3 | Definizione stratigrafica |
| 2.4 | Definizione interpretata |

### Lingua

**Campo**: `comboBox_lingua`
**Database**: `lingua`

Lingua del termine.

**Lingue supportate:**
- IT (Italiano)
- EN_US (Inglese)
- DE (Tedesco)
- FR (Francese)
- ES (Spagnolo)
- AR (Arabo)
- CA (Catalano)

---

## Campi Gerarchia

### ID Parent

**Campo**: `comboBox_id_parent`
**Database**: `id_parent`

ID del termine padre (per strutture gerarchiche).

### Parent Sigla

**Campo**: `comboBox_parent_sigla`
**Database**: `parent_sigla`

Sigla del termine padre.

### Hierarchy Level

**Campo**: `spinBox_hierarchy`
**Database**: `hierarchy_level`

Livello nella gerarchia (0=radice, 1=primo livello, ecc.).

---

## Funzionalita Speciali

### Suggerimenti GPT

Il pulsante "Suggerimenti" utilizza OpenAI GPT per:
- Generare descrizioni automatiche
- Fornire link Wikipedia di riferimento
- Suggerire definizioni in contesto archeologico

**Utilizzo:**
1. Selezionare o inserire un termine in "Sigla estesa"
2. Click su "Suggerimenti"
3. Selezionare il modello GPT
4. Attendere la generazione
5. Revisione e salvataggio

**Nota:** Richiede API key OpenAI configurata.

### Import CSV

Per database SQLite e possibile importare vocabolari da file CSV.

**Formato CSV richiesto:**
```text
nome_tabella,sigla,sigla_estesa,descrizione,tipologia_sigla,lingua
us_table,MR,Muro,Struttura muraria,2.4,IT
us_table,PV,Pavimento,Superficie di calpestio,2.4,IT
```

**Procedura:**
1. Click su "Import CSV"
2. Selezionare il file
3. Confermare l'importazione
4. Verificare i dati importati

---

## Workflow Operativo

### Aggiunta Nuovo Termine

1. **Apertura Thesaurus**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su "New Record"

3. **Selezione tabella**
   ```
   Nome tabella: us_table
   ```

4. **Definizione termine**
   ```
   Sigla: PZ
   Sigla estesa: Pozzo
   Tipologia sigla: 2.4
   Lingua: IT
   ```

5. **Descrizione**
   ```
   Struttura scavata nel terreno per
   l'approvvigionamento idrico.
   Generalmente di forma circolare
   con rivestimento in pietra o laterizi.
   ```

6. **Salvataggio**
   - Click su "Save"

### Ricerca Termini

1. Click su "New Search"
2. Compilare criteri:
   - Nome tabella
   - Sigla o sigla estesa
   - Lingua
3. Click su "Search"
4. Navigare tra i risultati

### Modifica Termine Esistente

1. Cercare il termine da modificare
2. Modificare i campi necessari
3. Click su "Save"

---

## Organizzazione Codici Tipologia

### I codici delle schede

I codici non si scelgono: ogni tendina di una scheda legge il suo codice, fisso. Qualche esempio — l'elenco completo, scheda per scheda, si apre dalla finestra del Thesaurus con il pulsante **Vedi lista codici**:

**site_table (1.x):**
| Codice | Campo |
|--------|-------|
| 1.1 | Definizione sito |
| 1.2 | Nazione |
| 1.3 | Regione |
| 1.4 | Provincia |
| 1.5 | Comune |

**us_table (2.x):**
| Codice | Campo |
|--------|-------|
| 2.1 | Settore |
| 2.3 | Definizione stratigrafica |
| 2.4 | Definizione interpretata |
| 2.8 | Metodo di scavo |

**inventario_materiali_table (3.x):**
| Codice | Campo |
|--------|-------|
| 3.1 | Tipo reperto |
| 3.2 | Classe materiale |
| 3.3 | Definizione |

**pottery_table (11.x):**
| Codice | Campo |
|--------|-------|
| 11.1 | Fabric |
| 11.4 | Forma |
| 11.6 | Ware |

---

## Best Practices

### Coerenza Terminologica

- Usare sempre gli stessi termini per gli stessi concetti
- Evitare sinonimi non documentati
- Documentare le convenzioni adottate

### Multilingua

- Creare i termini in tutte le lingue necessarie
- Mantenere le corrispondenze tra lingue
- Usare traduzioni ufficiali quando disponibili

### Gerarchia

- Utilizzare la struttura gerarchica per termini correlati
- Definire chiaramente i livelli
- Documentare le relazioni

### Manutenzione

- Revisionare periodicamente i vocabolari
- Eliminare termini obsoleti
- Aggiornare le descrizioni

---

## Troubleshooting

### Problema: Termine non visibile nei ComboBox

**Causa:** Codice tipologia errato o lingua non corrispondente.

**Soluzione:**
1. Verificare il codice tipologia_sigla
2. Controllare la lingua impostata
3. Verificare che il record sia salvato

### Problema: Import CSV fallito

**Causa:** Formato file non corretto.

**Soluzione:**
1. Verificare la struttura del CSV
2. Controllare i delimitatori (virgola)
3. Verificare la codifica (UTF-8)

### Problema: Suggerimenti GPT non funzionano

**Causa:** API key mancante o non valida.

**Soluzione:**
1. Verificare la configurazione API key
2. Controllare la connessione internet
3. Verificare il credito OpenAI

---

## Riferimenti

### Database

- **Tabella**: `pyarchinit_thesaurus_sigle`
- **Classe mapper**: `PYARCHINIT_THESAURUS_SIGLE`
- **ID**: `id_thesaurus_sigle`

### File Sorgente

- **UI**: `gui/ui/Thesaurus.ui`
- **Controller**: `tabs/Thesaurus.py`

---

## Video Tutorial

### Gestione Vocabolari
**Durata**: 10-12 minuti
- Struttura del thesaurus
- Aggiunta termini
- Organizzazione codici

[Placeholder video: video_thesaurus_gestione.mp4]

### Multilingua e Import
**Durata**: 8-10 minuti
- Configurazione lingue
- Import da CSV
- Suggerimenti GPT

[Placeholder video: video_thesaurus_avanzato.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../../animations/pyarchinit_thesaurus_animation.html)
