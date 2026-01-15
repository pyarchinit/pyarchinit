# Tutorial 15: Fitxa Arqueozoologia (Fauna)

## Introducció

La **Fitxa Arqueozoologia/Fauna** (FITXA FR - Fauna Record) és el mòdul de PyArchInit dedicat a l'anàlisi i documentació de les restes faunístiques. Permet registrar dades arqueozoològiques detallades per a l'estudi de les economies de subsistència antigues.

### Conceptes Bàsics

**Arqueozoologia:**
- Estudi de les restes animals de contextos arqueològics
- Anàlisi de les relacions home-animal en el passat
- Reconstrucció de dietes, ramaderia, caça

**Dades registrades:**
- Identificació taxonòmica (espècie)
- Parts esquelètiques presents
- NMI (Nombre Mínim d'Individus)
- Estat de conservació
- Traces tafonòmiques
- Senyals de carnisseria

---

## Accés a la Fitxa

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Fitxa Fauna** (o **Fauna form**)

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Fauna** (os estilitzat)

---

## Panoràmica de la Interfície

La fitxa està organitzada en pestanyes temàtiques:

### Pestanyes Principals

| # | Pestanya | Contingut |
|---|----------|-----------|
| 1 | Dades Identificatives | Lloc, Àrea, US, Context |
| 2 | Dades Arqueozoològiques | Espècie, NMI, Parts esquelètiques |
| 3 | Dades Tafonòmiques | Conservació, Fragmentació, Traces |
| 4 | Dades Contextuals | Context deposicional, Associacions |
| 5 | Estadístiques | Gràfics i quantificacions |

---

## Barra d'Eines

La barra d'eines proporciona les funcions estàndard:

| Icona | Funció |
|-------|--------|
| First/Prev/Next/Last | Navegació registres |
| New | Nou registre |
| Save | Desa |
| Delete | Elimina |
| Search | Cerca |
| View All | Visualitza tots |
| PDF | Export PDF |

---

## Pestanya Dades Identificatives

### Selecció US

**Camp**: `comboBox_us_select`

Selecciona la US de procedència. Mostra les US disponibles en format "Lloc - Àrea - US".

### Lloc

**Camp**: `comboBox_sito`
**Base de dades**: `sito`

Lloc arqueològic.

### Àrea

**Camp**: `comboBox_area`
**Base de dades**: `area`

Àrea d'excavació.

### Sondeig

**Camp**: `comboBox_saggio`
**Base de dades**: `saggio`

Sondeig/rasa de procedència.

### US

**Camp**: `comboBox_us`
**Base de dades**: `us`

Unitat Estratigràfica.

### Datació US

**Camp**: `lineEdit_datazione`
**Base de dades**: `datazione_us`

Enquadrament cronològic de la US.

### Responsable

**Camp**: `comboBox_responsabile`
**Base de dades**: `responsabile_scheda`

Autor de la fitxa.

### Data Compilació

**Camp**: `dateEdit_data`
**Base de dades**: `data_compilazione`

Data de compilació de la fitxa.

---

## Pestanya Dades Arqueozoològiques

### Context

**Camp**: `comboBox_contesto`
**Base de dades**: `contesto`

Tipus de context deposicional.

**Valors:**
- Habitat
- Abocador/Escombrera
- Rebliment
- Estrat de vida
- Sepultura
- Ritual

### Espècie

**Camp**: `comboBox_specie`
**Base de dades**: `specie`

Identificació taxonòmica.

**Espècies comunes en arqueozoologia:**
| Espècie | Nom científic |
|---------|---------------|
| Boví | Bos taurus |
| Oví | Ovis aries |
| Cabrum | Capra hircus |
| Porcí | Sus domesticus |
| Equí | Equus caballus |
| Cérvol | Cervus elaphus |
| Senglar | Sus scrofa |
| Llebre | Lepus europaeus |
| Gos | Canis familiaris |
| Gat | Felis catus |
| Aviram | Gallus gallus |

### Nombre Mínim d'Individus (NMI)

**Camp**: `spinBox_nmi`
**Base de dades**: `numero_minimo_individui`

Estimació del nombre mínim d'individus representats.

### Parts Esquelètiques

**Camp**: `tableWidget_parti`
**Base de dades**: `parti_scheletriche`

Taula per registrar les parts anatòmiques presents.

**Columnes:**
| Columna | Descripció |
|---------|------------|
| Element | Os/part anatòmica |
| Costat | Dret/Esq/Axial |
| Quantitat | Nombre fragments |
| NMI | Contribució al NMI |

### Mesures Ossos

**Camp**: `tableWidget_misure`
**Base de dades**: `misure_ossa`

Mesuraments osteomètrics estàndard.

---

## Pestanya Dades Tafonòmiques

### Estat Fragmentació

**Camp**: `comboBox_frammentazione`
**Base de dades**: `stato_frammentazione`

Grau de fragmentació de les restes.

**Valors:**
- Integre
- Poc fragmentat
- Fragmentat
- Molt fragmentat

### Estat Conservació

**Camp**: `comboBox_conservazione`
**Base de dades**: `stato_conservazione`

Condicions generals de conservació.

**Valors:**
- Òptim
- Bo
- Mediocre
- Dolent
- Pèssim

### Traces Combustió

**Camp**: `comboBox_combustione`
**Base de dades**: `tracce_combustione`

Presència de traces de foc.

**Valors:**
- Absents
- Ennegriment
- Carbonització
- Calcinació

### Senyals Tafonòmics

**Camp**: `comboBox_segni_tafo`
**Base de dades**: `segni_tafonomici_evidenti`

Traces d'alteració post-deposicional.

**Tipus:**
- Weathering (agents atmosfèrics)
- Root marks (arrels)
- Gnawing (rosegades)
- Trampling (trepig)

### Alteracions Morfològiques

**Camp**: `textEdit_alterazioni`
**Base de dades**: `alterazioni_morfologiche`

Descripció detallada de les alteracions observades.

---

## Pestanya Dades Contextuals

### Metodologia Recuperació

**Camp**: `comboBox_metodologia`
**Base de dades**: `metodologia_recupero`

Mètode de recollida de les restes.

**Valors:**
- A vista
- Garbell en sec
- Flotació
- Garbell humit

### Restes en Connexió Anatòmica

**Camp**: `checkBox_connessione`
**Base de dades**: `resti_connessione_anatomica`

Presència de parts en connexió.

### Classes Troballes Associació

**Camp**: `textEdit_associazioni`
**Base de dades**: `classi_reperti_associazione`

Altres materials associats a les restes faunístiques.

### Observacions

**Camp**: `textEdit_osservazioni`
**Base de dades**: `osservazioni`

Notes generals.

### Interpretació

**Camp**: `textEdit_interpretazione`
**Base de dades**: `interpretazione`

Interpretació del context faunístic.

---

## Pestanya Estadístiques

Proporciona eines per:
- Gràfics de distribució per espècie
- Càlcul NMI totals
- Comparacions entre US/fases
- Export dades estadístiques

---

## Flux de Treball Operatiu

### Fitxació Restes Faunístiques

1. **Obertura fitxa**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic a "New Record"

3. **Dades identificatives**
   ```
   Lloc: Vil·la Romana
   Àrea: 1000
   US: 150
   Responsable: J. Garcia
   Data: 20/07/2024
   ```

4. **Dades arqueozoològiques** (Pestanya 2)
   ```
   Context: Abocador/Escombrera
   Espècie: Bos taurus
   NMI: 3

   Parts esquelètiques:
   - Húmer / Dret / 2 / 1
   - Tíbia / Esq / 3 / 2
   - Metàpode / - / 5 / 1
   ```

5. **Dades tafonòmiques** (Pestanya 3)
   ```
   Fragmentació: Fragmentat
   Conservació: Bo
   Combustió: Absents
   Senyals tafonòmics: Root marks
   ```

6. **Interpretació**
   ```
   Abocador de residus alimentaris.
   Presència de traces de carnisseria
   en alguns ossos llargs.
   ```

7. **Desament**
   - Clic a "Save"

---

## Bones Pràctiques

### Identificació

- Utilitzar col·leccions de referència
- Indicar el grau de certesa de la ID
- Registrar també les restes no identificables

### NMI

- Calcular per a cada espècie separadament
- Considerar costat i edat de les troballes
- Documentar el mètode de càlcul

### Tafonomia

- Observar sistemàticament cada troballa
- Documentar les traces abans del rentat
- Fotografiar casos significatius

### Context

- Connectar sempre a la US de procedència
- Registrar el mètode de recuperació
- Anotar associacions significatives

---

## Export PDF

La fitxa permet generar:
- Fitxes singulars detallades
- Llistes per US o fase
- Informes estadístics

---

## Resolució de Problemes

### Problema: Espècie no disponible

**Causa**: Llista espècies incompleta.

**Solució**:
1. Verificar el tesaurus fauna
2. Afegir les espècies que falten
3. Contactar l'administrador

### Problema: NMI no calculat

**Causa**: Parts esquelètiques no registrades.

**Solució**:
1. Emplenar la taula parts esquelètiques
2. Indicar costat i quantitat
3. El sistema calcularà automàticament

---

## Referències

### Base de Dades

- **Taula**: `fauna_table`
- **Classe mapper**: `FAUNA`
- **ID**: `id_fauna`

### Fitxers Font

- **Controller**: `tabs/Fauna.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Faunasheet_pdf.py`

---

## Vídeo Tutorial

### Fitxació Arqueozoològica
**Durada**: 12-15 minuts
- Identificació taxonòmica
- Registre parts esquelètiques
- Anàlisi tafonòmica

[Placeholder vídeo: video_arqueozoologia.mp4]

### Estadístiques Faunístiques
**Durada**: 8-10 minuts
- Càlcul NMI
- Gràfics de distribució
- Export dades

[Placeholder vídeo: video_fauna_estadistiques.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
