# Tutorial 28: Export GeoPackage

## Introducere

Functia **Export GeoPackage** permite impachetarea straturilor vectoriale si raster PyArchInit intr-un singur fisier GeoPackage (.gpkg). Acest format este ideal pentru partajare, arhivare si portabilitatea datelor.

### Avantajele GeoPackage

| Aspect | Avantaj |
|--------|---------|
| Fisier unic | Toate datele intr-un singur fisier |
| Portabilitate | Partajare usoara |
| Standard OGC | Compatibilitate universala |
| Multi-strat | Vectori si rasteri impreuna |
| Bazat pe SQLite | Usor si rapid |

## Acces

### Din meniu
**PyArchInit** > **Impachetare pentru GeoPackage**

## Interfata

### Panoul de export

```
+--------------------------------------------------+
|        Import in GeoPackage                       |
+--------------------------------------------------+
| Destinatie:                                       |
|   [____________________________] [Navigare]      |
+--------------------------------------------------+
| [Export straturi vectoriale]                      |
| [Export straturi raster]                          |
+--------------------------------------------------+
```

## Procedura

### Exportul straturilor vectoriale

1. Selectati straturile de exportat in panoul Straturi QGIS
2. Deschideti instrumentul Export GeoPackage
3. Specificati calea si numele fisierului de destinatie
4. Faceti clic pe **"Export straturi vectoriale"**

### Exportul straturilor raster

1. Selectati straturile raster in panoul Straturi
2. Specificati destinatia (acelasi fisier sau unul nou)
3. Faceti clic pe **"Export straturi raster"**

### Export combinat

Pentru a include vectori si rasteri in acelasi GeoPackage:
1. Mai intai exportati vectorii
2. Apoi exportati rasterii in acelasi fisier
3. Sistemul adauga straturile in GeoPackage-ul existent

## Selectarea straturilor

### Metoda

1. In panoul Straturi QGIS, selectati straturile dorite
   - Ctrl+clic pentru selectie multipla
   - Shift+clic pentru interval
2. Deschideti Export GeoPackage
3. Straturile selectate vor fi exportate

### Straturi recomandate

| Strat | Tip | Note |
|-------|-----|------|
| pyunitastratigrafiche | Vector | US de depozit |
| pyunitastratigrafiche_usm | Vector | US de zid |
| pyarchinit_quote | Vector | Puncte de cota |
| pyarchinit_siti | Vector | Situri |
| Ortofoto | Raster | Ortofotografie excavare |

## Iesire

### Structura GeoPackage

```
output.gpkg
+-- pyunitastratigrafiche (vector)
+-- pyunitastratigrafiche_usm (vector)
+-- pyarchinit_quote (vector)
+-- ortofoto (raster)
```

### Calea implicita

```
~/pyarchinit/pyarchinit_DB_folder/
```

## Optiuni de export

### Straturi vectoriale

- Mentine geometriile originale
- Pastreaza toate atributele
- Converteste automat numele cu spatii (utilizeaza underscore)

### Straturi raster

- Suporta formate comune (GeoTIFF, etc.)
- Mentine georeferentierea
- Pastreaza sistemul de referinta al coordonatelor

## Utilizari tipice

### Partajarea proiectului

```
1. Selectati toate straturile proiectului
2. Exportati in GeoPackage
3. Partajati fisierul .gpkg
4. Destinatarul deschide direct in QGIS
```

### Arhivarea campaniei

```
1. La sfarsitul campaniei, selectati straturile finale
2. Exportati in GeoPackage datat
3. Arhivati impreuna cu documentatia
```

### Copie de siguranta GIS

```
1. Exportati periodic starea curenta
2. Mentineti versiuni datate
3. Utilizati pentru recuperare in caz de dezastru
```

## Bune practici

### 1. Inainte de export

- Verificati completitudinea straturilor
- Verificati sistemul de referinta al coordonatelor
- Salvati proiectul QGIS

### 2. Denumire

- Utilizati nume descriptive pentru fisiere
- Includeti data in nume
- Evitati caracterele speciale

### 3. Verificare

- Deschideti GeoPackage-ul creat
- Verificati ca toate straturile sunt prezente
- Verificati atributele

## Depanare

### Exportul a esuat

**Cauze**:
- Strat invalid
- Calea nu permite scriere
- Spatiu pe disc insuficient

**Solutii**:
- Verificati validitatea stratului
- Verificati permisiunile folderului
- Eliberati spatiu pe disc

### Straturi lipsa

**Cauza**: Strat neselectat

**Solutie**: Verificati selectia in panoul Straturi

### Rasterul nu este exportat

**Cauze**:
- Format nesuportat
- Fisier sursa inaccesibil

**Solutii**:
- Convertiti rasterul in GeoTIFF
- Verificati calea fisierului sursa

## Referinte

### Fisiere sursa
- `tabs/gpkg_export.py` - Interfata de export
- `gui/ui/gpkg_export.ui` - Macheta UI

### Documentatie
- [Standard GeoPackage](https://www.geopackage.org/)
- [Suport GeoPackage QGIS](https://docs.qgis.org/)

---

## Tutorial video

### Export GeoPackage
`[Placeholder: video_geopackage.mp4]`

**Continut**:
- Selectarea straturilor
- Export vectorial si raster
- Verificarea iesirii
- Bune practici

**Durata estimata**: 8-10 minute

---

*Ultima actualizare: ianuarie 2026*
