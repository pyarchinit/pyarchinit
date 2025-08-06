# Sincronizzazione Bidirezionale Thesaurus TMA

## Panoramica

Il sistema ora supporta la sincronizzazione bidirezionale del thesaurus:

1. **Da Tabelle → Thesaurus**: Sincronizza i dati esistenti nelle tabelle verso il thesaurus
2. **Da TMA → Altre Tabelle**: Copia le voci predefinite del thesaurus TMA verso US e Inventario

## Come Funziona

### 1. Da Tabelle → Thesaurus (Sincronizzazione Originale)
Questa modalità cerca nelle tabelle del database e aggiunge al thesaurus solo i valori effettivamente utilizzati:
- Aree da us_table, tma_materiali_archeologici, inventario_materiali_table, etc.
- Settori da us_table e tma_materiali_archeologici
- Materiali da inventario_materiali_table

### 2. Da TMA → Altre Tabelle (Nuova Funzionalità)
Questa modalità copia le voci predefinite del thesaurus TMA verso le altre tabelle:

#### Aree
- Copia tutte le aree TMA (tipologia 10.7) verso US (tipologia 2.43)
- Le 96 aree predefinite (AREA001-AREA092, etc.) diventano disponibili per US
- La descrizione indica "Sincronizzato da thesaurus TMA"

#### Materiali
- Copia i valori dei materiali da TMA Materiali Ripetibili verso INVENTARIO_MATERIALI:
  - Categoria (10.10) → tipo_reperto
  - Classe (10.11) → corpo_ceramico  
  - Precisazione tipologica (10.12) → tipo
  - Definizione (10.13) → definizione

## Utilizzo

1. Vai alla scheda Thesaurus
2. Clicca su "Sincronizza Thesaurus TMA"
3. Scegli la direzione:
   - **"Da Tabelle → Thesaurus"**: Per aggiungere al thesaurus i valori usati nei dati
   - **"Da TMA → Altre tabelle"**: Per rendere disponibili le voci TMA predefinite in US e Inventario

## Esempio Pratico

Se hai 96 aree predefinite nel thesaurus TMA (AREA001-AREA092) e vuoi che siano disponibili anche quando lavori con le US:
1. Scegli "Da TMA → Altre tabelle"
2. Il sistema copierà tutte le 96 aree nel thesaurus US con codice 2.43
3. Ora quando lavori nella scheda US, vedrai tutte le aree TMA disponibili

## Note Importanti

- La sincronizzazione non duplica le voci già esistenti
- Ogni voce sincronizzata ha una descrizione che indica l'origine
- I codici tipologia_sigla vengono adattati correttamente per ogni tabella