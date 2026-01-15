# Tutorial 10: Fitxa de Documentació

## Introducció

La **Fitxa de Documentació** és el mòdul de PyArchInit per a la gestió de la documentació gràfica d'excavació: plantes, seccions, alçats, aixecaments i qualsevol altre elaborat gràfic produït durant les activitats arqueològiques.

### Tipologies de Documentació

- **Plantes**: plantes d'estrat, de fase, generals
- **Seccions**: seccions estratigràfiques
- **Alçats**: alçats muraris, fronts d'excavació
- **Aixecaments**: aixecaments topogràfics, fotogramètrics
- **Ortofotos**: elaboracions des de dron/fotogrametria
- **Dibuixos de troballes**: ceràmica, metalls, etc.

---

## Accés a la Fitxa

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Fitxa Documentació** (o **Documentation form**)

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Documentació**

---

## Panoràmica de la Interfície

### Àrees Principals

| # | Àrea | Descripció |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegació, cerca, desament |
| 2 | DB Info | Estat registre, ordenació, comptador |
| 3 | Camps Identificatius | Lloc, Nom, Data |
| 4 | Camps Tipològics | Tipus, Font, Escala |
| 5 | Camps Descriptius | Dibuixant, Notes |

---

## Barra d'Eines DBMS

### Botons Estàndard

| Funció | Descripció |
|--------|-------------|
| First/Prev/Next/Last rec | Navegació entre els registres |
| New record | Crea nou registre |
| Save | Desa les modificacions |
| Delete | Elimina el registre |
| New search / Search | Funcions de cerca |
| Order by | Ordena resultats |
| View all | Visualitza tots els registres |

---

## Camps de la Fitxa

### Lloc

**Camp**: `comboBox_sito_doc`
**Base de dades**: `sito`

Lloc arqueològic de referència.

### Nom Documentació

**Camp**: `lineEdit_nome_doc`
**Base de dades**: `nome_doc`

Nom identificatiu del document.

**Convencions de nomenclatura:**
- `P` = Planta (ex. P001)
- `S` = Secció (ex. S001)
- `AL` = Alçat (ex. AL001)
- `A` = Aixecament (ex. A001)

### Data

**Camp**: `dateEdit_data`
**Base de dades**: `data`

Data d'execució del dibuix/aixecament.

### Tipus Documentació

**Camp**: `comboBox_tipo_doc`
**Base de dades**: `tipo_documentazione`

Tipologia del document.

**Valors típics:**
| Tipus | Descripció |
|-------|-------------|
| Planta d'estrat | US singular |
| Planta de fase | Diverses US coetànies |
| Planta general | Vista de conjunt |
| Secció estratigràfica | Perfil vertical |
| Alçat | Alçat murari |
| Aixecament topogràfic | Planimetria general |
| Ortofoto | Des de fotogrametria |
| Dibuix troballa | Ceràmica, metall, etc. |

### Font

**Camp**: `comboBox_sorgente`
**Base de dades**: `sorgente`

Font/mètode de producció.

**Valors:**
- Aixecament directe
- Fotogrametria
- Escàner làser
- GPS/Estació total
- Digitalització CAD
- Ortofoto dron

### Escala

**Camp**: `comboBox_scala`
**Base de dades**: `scala`

Escala de representació.

**Escales comunes:**
| Escala | Ús típic |
|--------|----------|
| 1:1 | Dibuixos troballes |
| 1:5 | Detalls |
| 1:10 | Seccions, detalls |
| 1:20 | Plantes d'estrat |
| 1:50 | Plantes generals |
| 1:100 | Planimetries |
| 1:200+ | Cartes topogràfiques |

### Dibuixant

**Camp**: `comboBox_disegnatore`
**Base de dades**: `disegnatore`

Autor del dibuix/aixecament.

### Notes

**Camp**: `textEdit_note`
**Base de dades**: `note`

Notes addicionals sobre el document.

---

## Flux de Treball Operatiu

### Registre Nova Documentació

1. **Obertura fitxa**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic a "New Record"

3. **Dades identificatives**
   ```
   Lloc: Vil·la Romana de Centcelles
   Nom: P025
   Data: 15/06/2024
   ```

4. **Classificació**
   ```
   Tipus: Planta d'estrat
   Font: Aixecament directe
   Escala: 1:20
   ```

5. **Autor i notes**
   ```
   Dibuixant: M. Garcia
   Notes: Planta US 150. Evidencia
   límits del paviment de formigó.
   ```

6. **Desament**
   - Clic a "Save"

### Cerca Documentació

1. Clic a "New Search"
2. Emplenar criteris:
   - Lloc
   - Tipus documentació
   - Escala
   - Dibuixant
3. Clic a "Search"
4. Navegar entre els resultats

---

## Exportació PDF

La fitxa suporta l'exportació en PDF per:
- Llista documentació
- Fitxes detallades

---

## Bones Pràctiques

### Nomenclatura

- Usar codis coherents en tot el projecte
- Numeració progressiva per tipus
- Documentar les convencions adoptades

### Organització

- Connectar sempre al lloc de referència
- Indicar l'escala efectiva
- Registrar data i autor

### Arxiu

- Connectar els fitxers digitals mitjançant la gestió media
- Mantenir còpies de seguretat
- Usar formats estàndard (PDF, TIFF)

---

## Resolució de Problemes

### Problema: Tipus documentació no disponible

**Causa**: Tesaurus no configurat.

**Solució**:
1. Obrir la Fitxa Tesaurus
2. Afegir els tipus que falten per a `documentazione_table`

### Problema: Fitxer no visualitzat

**Causa**: Ruta no correcta o fitxer absent.

**Solució**:
1. Verificar que el fitxer existeixi
2. Controlar la ruta a la configuració media

---

## Referències

### Base de Dades

- **Taula**: `documentazione_table`
- **Classe mapper**: `DOCUMENTAZIONE`
- **ID**: `id_documentazione`

### Fitxers Font

- **UI**: `gui/ui/Documentazione.ui`
- **Controller**: `tabs/Documentazione.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py`

---

## Vídeo Tutorial

### Gestió Documentació Gràfica
**Durada**: 6-8 minuts
- Registre nova documentació
- Classificació i metadades
- Cerca i consulta

[Placeholder vídeo: video_documentazione.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
