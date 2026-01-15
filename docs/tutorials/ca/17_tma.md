# Tutorial 17: TMA - Taula Materials Arqueològics

## Introducció

La **Fitxa TMA** (Taula Materials Arqueològics) és el mòdul avançat de PyArchInit per a la gestió dels materials d'excavació segons els estàndards ministerials italians. Permet una catalogació detallada conforme a les normatives ICCD (Istituto Centrale per il Catalogo e la Documentazione).

### Característiques Principals

- Catalogació conforme estàndard ICCD
- Gestió materials per caixa/contenidor
- Camps cronològics detallats
- Taula materials associats
- Gestió media integrada
- Export etiquetes i fitxes PDF

---

## Accés a la Fitxa

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Fitxa TMA**

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **TMA**

---

## Panoràmica de la Interfície

La fitxa presenta una interfície complexa amb molts camps.

### Àrees Principals

| # | Àrea | Descripció |
|---|------|------------|
| 1 | Toolbar DBMS | Navegació, cerca, desament |
| 2 | Camps Identificatius | Lloc, Àrea, US, Caixa |
| 3 | Camps Localització | Col·locació, Ambient, Sondeig |
| 4 | Camps Cronològics | Franja, Fracció, Cronologies |
| 5 | Taula Materials | Detall materials associats |
| 6 | Tab Media | Imatges i documents |

---

## Camps Identificatius

### Lloc

**Camp**: `comboBox_sito`
**Base de dades**: `sito`

Lloc arqueològic (SCAN - Denominació excavació ICCD).

### Àrea

**Camp**: `comboBox_area`
**Base de dades**: `area`

Àrea d'excavació.

### US (DSCU)

**Camp**: `comboBox_us`
**Base de dades**: `dscu`

Unitat Estratigràfica de procedència (DSCU = Descrizione Scavo Unità).

### Sector

**Camp**: `comboBox_settore`
**Base de dades**: `settore`

Sector d'excavació.

### Inventari

**Camp**: `lineEdit_inventario`
**Base de dades**: `inventario`

Número d'inventari.

### Caixa

**Camp**: `lineEdit_cassetta`
**Base de dades**: `cassetta`

Número de la caixa/contenidor.

---

## Camps Localització ICCD

### LDCT - Tipologia Col·locació

**Camp**: `comboBox_ldct`
**Base de dades**: `ldct`

Tipus de lloc de col·locació.

**Valors ICCD:**
- museu
- superintendència
- dipòsit
- laboratori
- altre

### LDCN - Denominació Col·locació

**Camp**: `lineEdit_ldcn`
**Base de dades**: `ldcn`

Nom específic del lloc de conservació.

### Antiga Col·locació

**Camp**: `lineEdit_vecchia_coll`
**Base de dades**: `vecchia_collocazione`

Eventual anterior col·locació.

### SCAN - Denominació Excavació

**Camp**: `lineEdit_scan`
**Base de dades**: `scan`

Nom oficial de l'excavació/recerca.

### Sondeig

**Camp**: `comboBox_saggio`
**Base de dades**: `saggio`

Sondeig/rasa de referència.

### Ambient/Locus

**Camp**: `lineEdit_vano`
**Base de dades**: `vano_locus`

Ambient o locus de procedència.

---

## Camps Cronològics

### DTZG - Franja Cronològica

**Camp**: `comboBox_dtzg`
**Base de dades**: `dtzg`

Període cronològic general.

**Exemples ICCD:**
- edat del bronze
- edat del ferro
- edat romana
- edat medieval

### DTZS - Fracció Cronològica

**Camp**: `comboBox_dtzs`
**Base de dades**: `dtzs`

Subdivisió del període.

**Exemples:**
- antic/a
- mitjà/ana
- tardà/ana
- final

### Cronologies

**Camp**: `tableWidget_cronologie`
**Base de dades**: `cronologie`

Taula per cronologies múltiples o detallades.

---

## Camps Adquisició

### AINT - Tipus Adquisició

**Camp**: `comboBox_aint`
**Base de dades**: `aint`

Modalitat d'adquisició dels materials.

**Valors ICCD:**
- excavació
- prospecció
- compra
- donació
- segrest

### AIND - Data Adquisició

**Camp**: `dateEdit_aind`
**Base de dades**: `aind`

Data de l'adquisició.

### RCGD - Data Prospecció

**Camp**: `dateEdit_rcgd`
**Base de dades**: `rcgd`

Data de la prospecció (si aplicable).

### RCGZ - Especificacions Prospecció

**Camp**: `textEdit_rcgz`
**Base de dades**: `rcgz`

Notes sobre la prospecció.

---

## Camps Materials

### OGTM - Material

**Camp**: `comboBox_ogtm`
**Base de dades**: `ogtm`

Material principal (Objecte Tipus Material).

**Valors ICCD:**
- ceràmica
- vidre
- metall
- os
- pedra
- material ceràmic de construcció

### N. Troballes

**Camp**: `spinBox_n_reperti`
**Base de dades**: `n_reperti`

Nombre total de troballes.

### Pes

**Camp**: `doubleSpinBox_peso`
**Base de dades**: `peso`

Pes total en grams.

### DESO - Indicació Objectes

**Camp**: `textEdit_deso`
**Base de dades**: `deso`

Descripció sintètica dels objectes.

---

## Taula Materials Detall

**Widget**: `tableWidget_materiali`
**Taula associada**: `tma_materiali`

Permet registrar els materials individuals continguts a la caixa.

### Columnes

| Camp ICCD | Descripció |
|-----------|------------|
| MADI | Inventari material |
| MACC | Categoria |
| MACL | Classe |
| MACP | Precisió tipològica |
| MACD | Definició |
| Cronologia | Datació específica |
| MACQ | Quantitat |

### Gestió Files

| Botó | Funció |
|------|--------|
| + | Afegeix material |
| - | Elimina material |

---

## Camps Documentació

### FTAP - Tipus Fotografia

**Camp**: `comboBox_ftap`
**Base de dades**: `ftap`

Tipus de documentació fotogràfica.

### FTAN - Codi Foto

**Camp**: `lineEdit_ftan`
**Base de dades**: `ftan`

Codi identificatiu de la foto.

### DRAT - Tipus Dibuix

**Camp**: `comboBox_drat`
**Base de dades**: `drat`

Tipus de documentació gràfica.

### DRAN - Codi Dibuix

**Camp**: `lineEdit_dran`
**Base de dades**: `dran`

Codi identificatiu del dibuix.

### DRAA - Autor Dibuix

**Camp**: `lineEdit_draa`
**Base de dades**: `draa`

Autor del dibuix.

---

## Tab Media

Gestió d'imatges associades a la caixa/TMA.

### Funcionalitats

- Visualització miniatures
- Drag & drop per afegir imatges
- Doble clic per visualitzar
- Connexió a base de dades media

---

## Tab Table View

Vista tabular de tots els registres TMA per a una consulta ràpida.

### Funcionalitats

- Visualització a graella
- Ordenació per columna
- Filtres ràpids
- Selecció múltiple

---

## Export i Impressió

### Export PDF

| Opció | Descripció |
|-------|------------|
| Fitxa TMA | Fitxa completa |
| Etiquetes | Etiquetes per caixes |

### Etiquetes Caixes

Generació automàtica d'etiquetes per a:
- Identificació caixes
- Contingut sintètic
- Dades de procedència
- Codi de barres (opcional)

---

## Flux de Treball Operatiu

### Registre Nova TMA

1. **Obertura fitxa**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic a "New Record"

3. **Dades identificatives**
   ```
   Lloc: Vil·la Romana
   Àrea: 1000
   US: 150
   Caixa: C-001
   ```

4. **Localització**
   ```
   LDCT: dipòsit
   LDCN: Dipòsit Superintendència Barcelona
   SCAN: Excavacions Vil·la Romana 2024
   ```

5. **Cronologia**
   ```
   DTZG: edat romana
   DTZS: imperial
   ```

6. **Materials** (taula)
   ```
   | Inv | Cat | Classe | Def | Qtat |
   |-----|-----|--------|-----|------|
   | 001 | ceràmica | comuna | olla | 5 |
   | 002 | ceràmica | sigil·lata | plat | 3 |
   | 003 | vidre | - | ungüentari | 1 |
   ```

7. **Desament**
   - Clic a "Save"

---

## Bones Pràctiques

### Estàndard ICCD

- Utilitzar els vocabularis controlats ICCD
- Respectar les sigles oficials
- Mantenir coherència terminològica

### Organització Caixes

- Numeració progressiva unívoca
- Una TMA per caixa física
- Separar per US quan sigui possible

### Documentació

- Connectar sempre fotos i dibuixos
- Usar codis uníocs per als media
- Registrar autor i data

---

## Resolució de Problemes

### Problema: Vocabularis ICCD no disponibles

**Causa**: Tesaurus no configurat.

**Solució**:
1. Importar els vocabularis ICCD estàndard
2. Verificar la configuració del tesaurus

### Problema: Materials no desats

**Causa**: Taula materials no sincronitzada.

**Solució**:
1. Verificar que tots els camps obligatoris estiguin emplenats
2. Desar la fitxa principal abans d'afegir materials

---

## Referències

### Base de Dades

- **Taula principal**: `tma_materiali_archeologici`
- **Taula detall**: `tma_materiali`
- **Classe mapper**: `TMA`, `TMA_MATERIALI`
- **ID**: `id`

### Fitxers Font

- **UI**: `gui/ui/Tma.ui`
- **Controller**: `tabs/Tma.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Tmasheet_pdf.py`
- **Etiquetes**: `modules/utility/pyarchinit_tma_label_pdf.py`

---

## Vídeo Tutorial

### Catalogació TMA
**Durada**: 15-18 minuts
- Estàndard ICCD
- Compilació completa
- Gestió materials

[Placeholder vídeo: video_tma_catalogacio.mp4]

### Generació Etiquetes
**Durada**: 5-6 minuts
- Configuració etiquetes
- Impressió per lots
- Personalització

[Placeholder vídeo: video_tma_etiquetes.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
