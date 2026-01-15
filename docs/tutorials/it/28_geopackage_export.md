# Tutorial 28: Export GeoPackage

## Introduzione

La funzione **Export GeoPackage** permette di impacchettare i layer vettoriali e raster di PyArchInit in un singolo file GeoPackage (.gpkg). Questo formato e ideale per la condivisione, l'archiviazione e la portabilita dei dati GIS.

### Vantaggi del GeoPackage

| Aspetto | Vantaggio |
|---------|-----------|
| File singolo | Tutti i dati in un unico file |
| Portabilita | Facile condivisione |
| Standard OGC | Compatibilita universale |
| Multi-layer | Vettoriali e raster insieme |
| SQLite-based | Leggero e veloce |

## Accesso

### Dal Menu
**PyArchInit** → **Impacchetta per GeoPackage**

## Interfaccia

### Pannello Export

```
+--------------------------------------------------+
|        Importa in GeoPackage                      |
+--------------------------------------------------+
| Destinazione:                                     |
|   [____________________________] [Sfoglia]       |
+--------------------------------------------------+
| [Esporta Layer Vettoriali]                       |
| [Esporta Layer Raster]                           |
+--------------------------------------------------+
```

## Procedura

### Export Layer Vettoriali

1. Selezionare i layer da esportare nel pannello Layer QGIS
2. Aprire lo strumento GeoPackage Export
3. Specificare percorso e nome file di destinazione
4. Cliccare **"Esporta Layer Vettoriali"**

### Export Layer Raster

1. Selezionare layer raster nel pannello Layer
2. Specificare destinazione (stesso file o nuovo)
3. Cliccare **"Esporta Layer Raster"**

### Export Combinato

Per includere vettoriali e raster nello stesso GeoPackage:
1. Prima esportare i vettoriali
2. Poi esportare i raster nello stesso file
3. Il sistema aggiunge i layer al GeoPackage esistente

## Selezione Layer

### Metodo

1. Nel pannello Layer di QGIS, selezionare i layer desiderati
   - Ctrl+click per selezione multipla
   - Shift+click per range
2. Aprire Export GeoPackage
3. I layer selezionati saranno esportati

### Layer Consigliati

| Layer | Tipo | Note |
|-------|------|------|
| pyunitastratigrafiche | Vettoriale | US deposito |
| pyunitastratigrafiche_usm | Vettoriale | US murarie |
| pyarchinit_quote | Vettoriale | Punti quota |
| pyarchinit_siti | Vettoriale | Siti |
| Ortofoto | Raster | Ortofoto di scavo |

## Output

### Struttura GeoPackage

```
output.gpkg
├── pyunitastratigrafiche (vector)
├── pyunitastratigrafiche_usm (vector)
├── pyarchinit_quote (vector)
└── ortofoto (raster)
```

### Percorso Default

```
~/pyarchinit/pyarchinit_DB_folder/
```

## Opzioni Export

### Layer Vettoriali

- Mantiene geometrie originali
- Preserva tutti gli attributi
- Converte automaticamente nomi con spazi (usa underscore)

### Layer Raster

- Supporta formati comuni (GeoTIFF, etc.)
- Mantiene georeferenziazione
- Preserva sistema di riferimento

## Utilizzi Tipici

### Condivisione Progetto

```
1. Selezionare tutti i layer del progetto
2. Esportare in GeoPackage
3. Condividere il file .gpkg
4. Il destinatario apre direttamente in QGIS
```

### Archiviazione Campagna

```
1. A fine campagna, selezionare layer finali
2. Esportare in GeoPackage datato
3. Archiviare con documentazione
```

### Backup GIS

```
1. Periodicamente esportare stato corrente
2. Mantenere versioni datate
3. Usare per disaster recovery
```

## Best Practices

### 1. Prima dell'Export

- Verificare completezza layer
- Controllare sistema di riferimento
- Salvare progetto QGIS

### 2. Naming

- Usare nomi descrittivi per il file
- Includere data nel nome
- Evitare caratteri speciali

### 3. Verifica

- Aprire GeoPackage creato
- Verificare tutti i layer presenti
- Controllare attributi

## Risoluzione Problemi

### Export Fallito

**Cause**:
- Layer non valido
- Percorso non scrivibile
- Spazio disco insufficiente

**Soluzioni**:
- Verificare validita layer
- Controllare permessi cartella
- Liberare spazio disco

### Layer Mancanti

**Causa**: Layer non selezionato

**Soluzione**: Verificare selezione nel pannello Layer

### Raster Non Esportato

**Cause**:
- Formato non supportato
- File sorgente non accessibile

**Soluzioni**:
- Convertire raster in GeoTIFF
- Verificare percorso file sorgente

## Riferimenti

### File Sorgente
- `tabs/gpkg_export.py` - Interfaccia export
- `gui/ui/gpkg_export.ui` - Layout UI

### Documentazione
- [GeoPackage Standard](https://www.geopackage.org/)
- [QGIS GeoPackage Support](https://docs.qgis.org/)

---

## Video Tutorial

### Export GeoPackage
`[Placeholder: video_geopackage.mp4]`

**Contenuti**:
- Selezione layer
- Export vettoriali e raster
- Verifica output
- Best practices

**Durata prevista**: 8-10 minuti

---

*Ultimo aggiornamento: Gennaio 2026*
