# Tutorial 27: TOPS - Total Open Station

## Introducere

**TOPS** (Total Open Station) este integrarea PyArchInit cu software-ul open source pentru descarcarea si convertirea datelor din statii totale. Permite importul direct al ridicarilor topografice in sistemul PyArchInit.

### Ce este Total Open Station?

Total Open Station este un software liber pentru:
- Descarcarea datelor din statii totale
- Conversia formatelor
- Exportul in formate compatibile GIS

PyArchInit integreaza TOPS pentru a simplifica importul datelor de excavare.

## Acces

### Din meniu
**PyArchInit** > **TOPS (Total Open Station)**

## Interfata

### Panoul principal

```
+--------------------------------------------------+
|         Total Open Station catre PyArchInit       |
+--------------------------------------------------+
| Intrare:                                          |
|   Fisier: [___________________] [Navigare]       |
|   Format intrare: [ComboBox formate]             |
+--------------------------------------------------+
| Iesire:                                           |
|   Fisier: [___________________] [Navigare]       |
|   Format iesire: [csv | dxf | ...]               |
+--------------------------------------------------+
| [ ] Convertire coordonate                        |
+--------------------------------------------------+
| [Previzualizare date - TableView]                |
+--------------------------------------------------+
|              [Export]                             |
+--------------------------------------------------+
```

## Formate suportate

### Formate de intrare (Statii totale)

| Format | Producator | Extensie |
|--------|------------|----------|
| Leica GSI | Leica | .gsi |
| Topcon GTS | Topcon | .raw |
| Sokkia SDR | Sokkia | .sdr |
| Trimble DC | Trimble | .dc |
| Nikon RAW | Nikon | .raw |
| Zeiss R5 | Zeiss | .r5 |
| CSV generic | - | .csv |

### Formate de iesire

| Format | Utilizare |
|--------|-----------|
| CSV | Import in Cote PyArchInit |
| DXF | Import in CAD/GIS |
| GeoJSON | Import direct GIS |
| Shapefile | Standard GIS |

## Flux de lucru

### 1. Importul datelor din statia totala

```
1. Conectati statia totala la PC
2. Descarcati fisierul de date (format nativ)
3. Salvati in folderul de lucru
```

### 2. Conversia cu TOPS

```
1. Deschideti TOPS in PyArchInit
2. Selectati fisierul de intrare (Navigare)
3. Alegeti formatul corect de intrare
4. Setati fisierul de iesire
5. Alegeti formatul de iesire (CSV recomandat)
6. Faceti clic pe Export
```

### 3. Importul in PyArchInit

Dupa exportul CSV:
1. Sistemul solicita automat:
   - Numele **sitului** arheologic
   - **Unitatea de masura** (metri)
   - **Numele topografului**
2. Punctele sunt incarcate ca strat QGIS
3. Optional: copiere in stratul Cote US

### 4. Conversia coordonatelor (Optional)

Daca caseta de bifare **"Convertire coordonate"** este activata:
- Introduceti deplasamentul X, Y, Z
- Aplicati translatia coordonatelor
- Util pentru sisteme de referinta locale

## Previzualizarea datelor

### TableView

Afiseaza previzualizarea datelor importate:
| point_name | area_q | x | y | z |
|------------|--------|---|---|---|
| P001 | 1000 | 100.234 | 200.456 | 10.50 |
| P002 | 1000 | 100.567 | 200.789 | 10.45 |

### Editarea datelor

- Selectati randurile de sters
- Butonul **Stergere** elimina randurile selectate
- Util pentru filtrarea punctelor inutile

## Integrarea cu Cotele US

### Copiere automata

Dupa import, TOPS poate copia punctele in stratul **"Desen Cote US"**:
1. Se solicita numele sitului
2. Se solicita unitatea de masura
3. Se solicita numele topografului
4. Punctele sunt copiate cu atributele corecte

### Atribute completate

| Atribut | Valoare |
|---------|---------|
| sito_q | Numele sitului introdus |
| area_q | Extras din point_name |
| unita_misu_q | Unitatea introdusa (metri) |
| disegnatore | Numele introdus |
| data | Data curenta |

## Conventii de denumire

### Formatul point_name

Pentru extractia automata a ariei:
```
[ARIE]-[NUME_PUNCT]
Exemplu: 1000-P001
```

Sistemul separa automat:
- `area_q` = 1000
- `point_name` = P001

## Bune practici

### 1. Pe teren

- Utilizati denumire consistenta pentru puncte
- Includeti codul ariei in numele punctului
- Notati sistemul de referinta utilizat

### 2. Import

- Verificati formatul corect de intrare
- Verificati previzualizarea inainte de export
- Stergeti punctele eronate/duplicate

### 3. Post-import

- Verificati coordonatele in QGIS
- Verificati stratul Cote US
- Legati punctele de US corecta

## Depanare

### Format nerecunoscut

**Cauza**: Formatul statiei nu este suportat

**Solutie**:
- Exportati din statie in format generic (CSV)
- Verificati documentatia statiei

### Coordonate gresite

**Cauze**:
- Sistem de referinta diferit
- Deplasament neaplicat

**Solutii**:
- Verificati sistemul de referinta al proiectului
- Aplicati conversia coordonatelor

### Stratul nu este creat

**Cauza**: Eroare in timpul importului

**Solutie**:
- Verificati jurnalul de erori
- Verificati formatul fisierului de iesire
- Repetati conversia

## Referinte

### Fisiere sursa
- `tabs/tops_pyarchinit.py` - Interfata principala
- `gui/ui/Tops2pyarchinit.ui` - Macheta UI

### Software extern
- [Total Open Station](https://tops.iosa.it/) - Software principal
- Documentatia formatelor statiilor

---

## Tutorial video

### Import TOPS
`[Placeholder: video_tops.mp4]`

**Continut**:
- Descarcarea din statia totala
- Conversia formatelor
- Importul in PyArchInit
- Integrarea cu Cotele US

**Durata estimata**: 12-15 minute

---

*Ultima actualizare: ianuarie 2026*
