# Tutorial 27: TOPS - Total Open Station

## Introducció

**TOPS** (Total Open Station) és la integració de PyArchInit amb el programari de codi obert per a la descàrrega i conversió de dades d'estacions totals. Permet importar directament els aixecaments topogràfics al sistema PyArchInit.

### Què és Total Open Station?

Total Open Station és un programari lliure per:
- Descàrrega de dades d'estacions totals
- Conversió entre formats
- Export en formats compatibles amb GIS

PyArchInit integra TOPS per simplificar la importació de les dades d'excavació.

## Accés

### Des del Menú
**PyArchInit** → **TOPS (Total Open Station)**

## Interfície

### Panell Principal

```
+--------------------------------------------------+
|         Total Open Station a PyArchInit           |
+--------------------------------------------------+
| Entrada:                                          |
|   Fitxer: [___________________] [Navega]         |
|   Format entrada: [ComboBox formats]             |
+--------------------------------------------------+
| Sortida:                                          |
|   Fitxer: [___________________] [Navega]         |
|   Format sortida: [csv | dxf | ...]              |
+--------------------------------------------------+
| [ ] Converteix coordenades                       |
+--------------------------------------------------+
| [Previsualització Dades - TableView]             |
+--------------------------------------------------+
|              [Exporta]                            |
+--------------------------------------------------+
```

## Formats Suportats

### Formats d'Entrada (Estacions Totals)

| Format | Fabricant | Extensió |
|--------|-----------|----------|
| Leica GSI | Leica | .gsi |
| Topcon GTS | Topcon | .raw |
| Sokkia SDR | Sokkia | .sdr |
| Trimble DC | Trimble | .dc |
| Nikon RAW | Nikon | .raw |
| Zeiss R5 | Zeiss | .r5 |
| CSV genèric | - | .csv |

### Formats de Sortida

| Format | Ús |
|--------|-----|
| CSV | Import a PyArchInit Cotes |
| DXF | Import a CAD/GIS |
| GeoJSON | Import directe GIS |
| Shapefile | Estàndard GIS |

## Flux de Treball

### 1. Import Dades d'Estació Total

```
1. Connectar estació total al PC
2. Descarregar fitxer dades (format natiu)
3. Desar a carpeta de treball
```

### 2. Conversió amb TOPS

```
1. Obrir TOPS a PyArchInit
2. Seleccionar fitxer entrada (Navega)
3. Escollir format entrada correcte
4. Establir fitxer sortida
5. Escollir format sortida (CSV recomanat)
6. Fer clic Exporta
```

### 3. Import a PyArchInit

Després de l'export a CSV:
1. El sistema demana automàticament:
   - **Nom lloc** arqueològic
   - **Unitat de mesura** (metres)
   - **Nom dibuixant**
2. Els punts es carreguen com a capa QGIS
3. Opcional: còpia a capa Cotes US

### 4. Conversió Coordenades (Opcional)

Si checkbox **"Converteix coordenades"** actiu:
- Inserir offset X, Y, Z
- Aplicar translació coordenades
- Útil per a sistemes de referència locals

## Previsualització Dades

### TableView

Mostra previsualització de les dades importades:
| point_name | area_q | x | y | z |
|------------|--------|---|---|---|
| P001 | 1000 | 100.234 | 200.456 | 10.50 |
| P002 | 1000 | 100.567 | 200.789 | 10.45 |

### Modificació Dades

- Seleccionar files a eliminar
- Botó **Delete** elimina files seleccionades
- Útil per filtrar punts no necessaris

## Integració Cotes US

### Còpia Automàtica

Després de l'import, TOPS pot copiar els punts a la capa **"Cotes US dibuix"**:
1. Es demana el nom del lloc
2. Es demana la unitat de mesura
3. Es demana el dibuixant
4. Els punts es copien amb atributs correctes

### Atributs Emplenats

| Atribut | Valor |
|---------|-------|
| sito_q | Nom lloc inserit |
| area_q | Extret de point_name |
| unita_misu_q | Unitat inserida (metres) |
| disegnatore | Nom inserit |
| data | Data actual |

## Convencions Naming

### Format point_name

Per a l'extracció automàtica de l'àrea:
```
[ÀREA]-[NOM_PUNT]
Exemple: 1000-P001
```

El sistema separa automàticament:
- `area_q` = 1000
- `point_name` = P001

## Bones Pràctiques

### 1. Al Camp

- Usar naming consistent per a punts
- Incloure codi àrea al nom del punt
- Anotar sistema de referència usat

### 2. Import

- Verificar format entrada correcte
- Controlar previsualització abans d'exportar
- Eliminar punts erronis/duplicats

### 3. Post-Import

- Verificar coordenades a QGIS
- Controlar capa Cotes US
- Connectar punts a US correctes

## Resolució de Problemes

### Format No Reconegut

**Causa**: Format estació no suportat

**Solució**:
- Exportar des de l'estació en format genèric (CSV)
- Verificar documentació estació

### Coordenades Errònies

**Causes**:
- Sistema referència diferent
- Offset no aplicat

**Solucions**:
- Verificar sistema referència projecte
- Aplicar conversió coordenades

### Capa No Creada

**Causa**: Error durant import

**Solució**:
- Controlar log errors
- Verificar format fitxer sortida
- Repetir conversió

## Referències

### Fitxers Font
- `tabs/tops_pyarchinit.py` - Interfície principal
- `gui/ui/Tops2pyarchinit.ui` - Layout UI

### Programari Extern
- [Total Open Station](https://tops.iosa.it/) - Programari principal
- Documentació formats estacions

---

## Vídeo Tutorial

### TOPS Import
`[Placeholder: video_tops.mp4]`

**Continguts**:
- Descàrrega d'estació total
- Conversió formats
- Import a PyArchInit
- Integració Cotes US

**Durada prevista**: 12-15 minuts

---

*Última actualització: Gener 2026*
