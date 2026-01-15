# Tutorial 09: Fitxa de Mostres

## Introducció

La **Fitxa de Mostres** és el mòdul de PyArchInit dedicat a la gestió de les mostratges arqueològics. Permet registrar i fer seguiment de tots els tipus de mostres extretes durant l'excavació: terres, carbons, llavors, ossos, morters, metalls i altre material destinat a anàlisis especialitzades.

### Tipologies de Mostres

Les mostres arqueològiques comprenen:
- **Sediments**: per a anàlisis sedimentològiques, granulomètriques
- **Carbons**: per a datacions radiomètriques (C14)
- **Llavors/Pol·lens**: per a anàlisis arqueobotàniques
- **Ossos**: per a anàlisis arqueozoològiques, isotòpiques, ADN
- **Morters/Enguixats**: per a anàlisis arqueomètriques
- **Metalls/Escòries**: per a anàlisis metal·lúrgiques
- **Ceràmiques**: per a anàlisis de pasta, procedència

---

## Accés a la Fitxa

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Fitxa Mostres** (o **Samples form**)

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Mostres**

---

## Panoràmica de la Interfície

La fitxa presenta un disseny simplificat per a la gestió ràpida de les mostres.

### Àrees Principals

| # | Àrea | Descripció |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegació, cerca, desament |
| 2 | DB Info | Estat registre, ordenació, comptador |
| 3 | Camps Identificatius | Lloc, Nr. Mostra, Tipus |
| 4 | Camps Descriptius | Descripció, notes |
| 5 | Camps de Conservació | Caixa, Lloc |

---

## Barra d'Eines DBMS

### Botons de Navegació

| Icona | Funció | Descripció |
|-------|--------|-------------|
| First rec | Vés al primer registre |
| Prev rec | Vés al registre anterior |
| Next rec | Vés al registre següent |
| Last rec | Vés a l'últim registre |

### Botons CRUD

| Icona | Funció | Descripció |
|-------|--------|-------------|
| New record | Crea un nou registre mostra |
| Save | Desa les modificacions |
| Delete | Elimina el registre actual |

### Botons de Cerca

| Icona | Funció | Descripció |
|-------|--------|-------------|
| New search | Inicia nova cerca |
| Search!!! | Executa cerca |
| Order by | Ordena resultats |
| View all | Visualitza tots els registres |

---

## Camps de la Fitxa

### Lloc

**Camp**: `comboBox_sito`
**Base de dades**: `sito`

Selecciona el lloc arqueològic de pertinença.

### Número Mostra

**Camp**: `lineEdit_nr_campione`
**Base de dades**: `nr_campione`

Número identificatiu progressiu de la mostra.

### Tipus Mostra

**Camp**: `comboBox_tipo_campione`
**Base de dades**: `tipo_campione`

Classificació tipològica de la mostra. Els valors provenen del tesaurus.

**Tipologies comunes:**
| Tipus | Descripció |
|-------|-------------|
| Sediment | Mostra de terra |
| Carbó | Per a datacions C14 |
| Llavors | Restes carpològiques |
| Ossos | Restes faunístiques |
| Morter | Lligants edilicis |
| Ceràmica | Per a anàlisi pasta |
| Metall | Per a anàlisis metal·lúrgiques |
| Pol·len | Per a anàlisis palinològiques |

### Descripció

**Camp**: `textEdit_descrizione`
**Base de dades**: `descrizione`

Descripció detallada de la mostra.

**Continguts recomanats:**
- Característiques físiques de la mostra
- Quantitat extreta
- Modalitat d'extracció
- Motiu del mostratge
- Anàlisis previstes

### Àrea

**Camp**: `comboBox_area`
**Base de dades**: `area`

Àrea d'excavació de procedència.

### US

**Camp**: `comboBox_us`
**Base de dades**: `us`

Unitat Estratigràfica de procedència.

### Número Inventari Material

**Camp**: `lineEdit_nr_inv_mat`
**Base de dades**: `numero_inventario_materiale`

Si la mostra està connectada a una troballa inventariada, indicar el número d'inventari.

### Número Caixa

**Camp**: `lineEdit_nr_cassa`
**Base de dades**: `nr_cassa`

Caixa o contenidor de conservació.

### Lloc de Conservació

**Camp**: `comboBox_luogo_conservazione`
**Base de dades**: `luogo_conservazione`

On es conserva la mostra.

**Exemples:**
- Laboratori excavació
- Dipòsit museu
- Laboratori anàlisi extern
- Universitat

---

## Flux de Treball Operatiu

### Creació Nova Mostra

1. **Obertura fitxa**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic a "New Record"

3. **Dades identificatives**
   ```
   Lloc: Vil·la Romana de Centcelles
   Nr. Mostra: C-2024-001
   Tipus mostra: Carbó
   ```

4. **Procedència**
   ```
   Àrea: 1000
   US: 150
   ```

5. **Descripció**
   ```
   Mostra de carbó extreta de la
   superfície de cuit US 150.
   Quantitat: 50 gr aproximadament.
   Extreta per a datació C14.
   ```

6. **Conservació**
   ```
   Nr. Caixa: Mos-1
   Lloc: Laboratori excavació
   ```

7. **Desament**
   - Clic a "Save"

### Cerca de Mostres

1. Clic a "New Search"
2. Emplenar criteris:
   - Lloc
   - Tipus mostra
   - US
3. Clic a "Search"
4. Navegar entre els resultats

---

## Exportació PDF

La fitxa suporta l'exportació en PDF per:
- Llista mostres
- Fitxes detallades individuals

---

## Bones Pràctiques

### Nomenclatura

- Usar codis únics i parlants
- Format recomanat: `LLOC-ANY-PROGRESSIU`
- Exemple: `VRC-2024-C001`

### Extracció

- Documentar sempre les coordenades d'extracció
- Fotografiar el punt d'extracció
- Anotar profunditat i context

### Conservació

- Usar contenidors apropiats al tipus
- Etiquetar clarament cada mostra
- Mantenir condicions idònies

### Documentació

- Connectar sempre a la US de procedència
- Indicar les anàlisis previstes
- Registrar l'enviament a laboratoris externs

---

## Resolució de Problemes

### Problema: Tipus mostra no disponible

**Causa**: Tesaurus no configurat.

**Solució**:
1. Obrir la Fitxa Tesaurus
2. Afegir el tipus que falta per a `campioni_table`
3. Desar i reobrir la Fitxa Mostres

### Problema: US no visualitzada

**Causa**: US no registrada per al lloc seleccionat.

**Solució**:
1. Verificar que la US existeixi a la Fitxa US
2. Controlar que pertanyi al mateix lloc

---

## Referències

### Base de Dades

- **Taula**: `campioni_table`
- **Classe mapper**: `CAMPIONI`
- **ID**: `id_campione`

### Fitxers Font

- **UI**: `gui/ui/Campioni.ui`
- **Controller**: `tabs/Campioni.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

---

## Vídeo Tutorial

### Gestió Mostres
**Durada**: 5-6 minuts
- Creació nova mostra
- Compilació camps
- Cerca i exportació

[Placeholder vídeo: video_campioni.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
