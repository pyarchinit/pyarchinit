# Tutorial 06: Fitxa de Tomba

## Introducció

La **Fitxa de Tomba** és el mòdul de PyArchInit dedicat a la documentació de les sepultures arqueològiques. Aquesta eina permet registrar tots els aspectes d'una tomba: des de l'estructura funerària al ritu, des del parament als individus enterrats.

### Conceptes Bàsics

**Tomba a PyArchInit:**
- Una tomba és una estructura funerària que conté un o més individus
- Està connectada a la Fitxa Estructura (l'estructura física de la sepultura)
- Està connectada a la Fitxa Individus (per a les dades antropològiques)
- Documenta ritu, parament i característiques de la deposició

**Relacions:**
```
Tomba → Estructura (contenidor físic)
     → Individu/s (restes humans)
     → Parament (objectes d'acompanyament)
     → Inventari Materials (troballes associades)
```

---

## Accés a la Fitxa

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Fitxa Tomba** (o **Grave form**)

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Tomba** (símbol sepultura)

---

## Panoràmica de la Interfície

La fitxa presenta un disseny organitzat en seccions funcionals:

### Àrees Principals

| # | Àrea | Descripció |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegació, cerca, desament |
| 2 | DB Info | Estat registre, ordenació, comptador |
| 3 | Camps Identificatius | Lloc, Àrea, N. Fitxa, Estructura |
| 4 | Camps Individu | Connexió a l'individu |
| 5 | Àrea Tab | Pestanyes temàtiques per a dades específiques |

---

## Barra d'Eines DBMS

La barra d'eines principal proporciona els instruments per a la gestió dels registres.

### Botons de Navegació

| Icona | Funció | Descripció |
|-------|--------|-------------|
| |< | First rec | Vés al primer registre |
| < | Prev rec | Vés al registre anterior |
| > | Next rec | Vés al registre següent |
| >| | Last rec | Vés a l'últim registre |

### Botons CRUD

| Icona | Funció | Descripció |
|-------|--------|-------------|
| New | New record | Crea un nou registre tomba |
| Save | Save | Desa les modificacions |
| Delete | Delete | Elimina el registre actual |

### Botons de Cerca

| Icona | Funció | Descripció |
|-------|--------|-------------|
| New Search | New search | Inicia nova cerca |
| Search | Search!!! | Executa cerca |
| Sort | Order by | Ordena resultats |
| View All | View all | Visualitza tots els registres |

### Botons Especials

| Icona | Funció | Descripció |
|-------|--------|-------------|
| GIS | GIS | Carrega tomba al mapa |
| PDF | PDF export | Exporta en PDF |
| Directory | Open directory | Obre carpeta export |

---

## Camps Identificatius

Els camps identificatius defineixen unívocament la tomba a la base de dades.

### Lloc

**Camp**: `comboBox_sito`
**Base de dades**: `sito`

Selecciona el lloc arqueològic de pertinença.

### Àrea

**Camp**: `comboBox_area`
**Base de dades**: `area`

Àrea d'excavació dins del lloc.

### Número Fitxa

**Camp**: `lineEdit_nr_scheda`
**Base de dades**: `nr_scheda_taf`

Número progressiu de la fitxa tomba. Es proposa automàticament el proper número disponible.

### Sigla i Número Estructura

| Camp | Base de dades | Descripció |
|------|---------------|-------------|
| Sigla estructura | `sigla_struttura` | Sigla de l'estructura (ex. TM, TB) |
| Nr estructura | `nr_struttura` | Número de l'estructura |

Aquests camps connecten la tomba a la corresponent Fitxa Estructura.

### Número Individu

**Camp**: `comboBox_nr_individuo`
**Base de dades**: `nr_individuo`

Número de l'individu enterrat. Connecta la tomba a la Fitxa Individus.

**Notes:**
- Una tomba pot contenir més individus (sepultura múltiple)
- El menú mostra els individus disponibles per a l'estructura seleccionada

---

## Pestanya Dades Descriptives

La primera pestanya conté els camps fonamentals per descriure la sepultura.

### Ritu

**Camp**: `comboBox_rito`
**Base de dades**: `rito`

Tipus de ritual funerari practicat.

**Valors típics:**
| Ritu | Descripció |
|------|-------------|
| Inhumació | Deposició del cos sencer |
| Cremació | Incineració de les restes |
| Incineració primària | Cremació al lloc |
| Incineració secundària | Cremació en altre lloc i deposició |
| Mixt | Combinació de ritus |
| Indeterminat | No determinable |

### Tipus Sepultura

**Camp**: `comboBox_tipo_sepoltura`
**Base de dades**: `tipo_sepoltura`

Classificació tipològica de la sepultura.

**Exemples:**
- Tomba de fossa simple
- Tomba de caixa
- Tomba de cambra
- Tomba a la cappuccina
- Tomba d'enchytrismos
- Sarcòfag
- Ossari

### Tipus Deposició

**Camp**: `comboBox_tipo_deposizione`
**Base de dades**: `tipo_deposizione`

Modalitat de deposició del cos.

**Valors:**
- Primària (deposició directa)
- Secundària (reducció/desplaçament)
- Múltiple simultània
- Múltiple successiva

### Estat de Conservació

**Camp**: `comboBox_stato_conservazione`
**Base de dades**: `stato_di_conservazione`

Avaluació de l'estat conservatiu.

**Escala:**
- Òptim
- Bo
- Mediocre
- Dolent
- Pèssim

### Descripció

**Camp**: `textEdit_descrizione`
**Base de dades**: `descrizione_taf`

Descripció detallada de la tomba.

**Continguts recomanats:**
- Forma i dimensions de la fossa
- Orientació
- Profunditat
- Característiques del rebliment
- Estat al moment de l'excavació

### Interpretació

**Camp**: `textEdit_interpretazione`
**Base de dades**: `interpretazione_taf`

Interpretació historico-arqueològica de la sepultura.

---

## Característiques de la Tomba

### Senyalitzadors

**Camp**: `comboBox_segnacoli`
**Base de dades**: `segnacoli`

Presència i tipus de senyalitzadors funeraris.

**Valors:**
- Absent
- Estela
- Cip
- Túmul
- Recinte
- Altre

### Canal Libatori

**Camp**: `comboBox_canale_libatorio`
**Base de dades**: `canale_libatorio_si_no`

Presència de canal per a libacions rituals.

**Valors:** Sí / No

### Coberta

**Camp**: `comboBox_copertura_tipo`
**Base de dades**: `copertura_tipo`

Tipus de coberta de la tomba.

**Exemples:**
- Teules
- Lloses de pedra
- Taules de fusta
- Terra
- Absent

### Contenidor Restes

**Camp**: `comboBox_tipo_contenitore`
**Base de dades**: `tipo_contenitore_resti`

Tipus de contenidor per a les restes.

**Exemples:**
- Fossa terrosa
- Caixa de fusta
- Caixa lítica
- Àmfora
- Urna
- Sarcòfag

### Objectes Externs

**Camp**: `comboBox_oggetti_esterno`
**Base de dades**: `oggetti_rinvenuti_esterno`

Objectes trobats a l'exterior de la tomba però associats a ella.

---

## Pestanya Parament

Aquesta pestanya gestiona la documentació del parament funerari.

### Presència Parament

**Camp**: `comboBox_corredo_presenza`
**Base de dades**: `corredo_presenza`

Indica si la tomba contenia parament.

**Valors:**
- Sí
- No
- Probable
- Espoliat

### Tipus Parament

**Camp**: `comboBox_corredo_tipo`
**Base de dades**: `corredo_tipo`

Classificació general del parament.

**Categories:**
- Personal (joies, fíbules)
- Ritual (vasos, llànties)
- Simbòlic (monedes, amulets)
- Instrumental (eines)
- Mixt

### Descripció Parament

**Camp**: `textEdit_corredo_descrizione`
**Base de dades**: `corredo_descrizione`

Descripció detallada dels objectes del parament.

### Taula Parament

**Widget**: `tableWidget_corredo_tipo`

Taula per registrar els elements individuals del parament.

**Columnes:**
| Columna | Descripció |
|---------|-------------|
| ID Troballa | Número d'inventari de la troballa |
| ID Indv. | Individu associat |
| Material | Tipus de material |
| Posició del parament | On estava col·locat a la tomba |
| Posició en el parament | Posició respecte al cos |

**Notes:**
- Els elements estan connectats a la Fitxa Inventari Materials
- La taula es pobla automàticament amb les troballes de l'estructura

---

## Pestanya Altres Característiques

Aquesta pestanya conté informació addicional sobre la sepultura.

### Periodització

| Camp | Base de dades | Descripció |
|------|---------------|-------------|
| Període inicial | `periodo_iniziale` | Període d'inici d'ús |
| Fase inicial | `fase_iniziale` | Fase en el període |
| Període final | `periodo_finale` | Període de fi d'ús |
| Fase final | `fase_finale` | Fase en el període |
| Datació estesa | `datazione_estesa` | Datació literal |

Els valors es poblen segons la Fitxa Periodització del lloc.

---

## Pestanya Eines

La pestanya Eines conté funcionalitats addicionals.

### Gestió Media

Permet:
- Visualitzar imatges associades
- Afegir noves fotos mitjançant arrossega i deixa
- Cercar media a la base de dades

### Exportació

Opcions per a l'exportació:
- Llista Tombes (llista sintètica)
- Fitxes Tombes (fitxes completes)
- Conversió PDF a Word

---

## Integració GIS

### Visualització al Mapa

| Botó | Funció |
|------|--------|
| GIS Toggle | Activa/desactiva càrrega automàtica |
| Load to GIS | Carrega la tomba al mapa |

### Capes GIS

La fitxa utilitza capes específiques per a les tombes:
- **pyarchinit_tomba**: geometria de les tombes
- Connexió amb capes estructures i US

---

## Exportació i Impressió

### Exportació PDF

El botó PDF obre un panell amb opcions:

| Opció | Descripció |
|-------|-------------|
| Llista Tombes | Llista sintètica de les tombes |
| Fitxes Tombes | Fitxes completes detallades |
| Imprimeix | Genera el PDF |

### Contingut Fitxa PDF

La fitxa PDF inclou:
- Dades identificatives
- Ritu i tipus sepultura
- Descripció i interpretació
- Dades del parament
- Periodització
- Imatges associades

---

## Flux de Treball Operatiu

### Creació Nova Tomba

1. **Obertura fitxa**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic a "New Record"
   - El número fitxa es proposa automàticament

3. **Dades identificatives**
   ```
   Lloc: Necròpolis d'Empúries
   Àrea: 1
   N. Fitxa: 45
   Sigla estructura: TM
   Nr estructura: 45
   ```

4. **Connexió individu**
   ```
   Nr Individu: 1
   ```

5. **Dades descriptives** (Pestanya 1)
   ```
   Ritu: Inhumació
   Tipus sepultura: Tomba de fossa simple
   Tipus deposició: Primària
   Estat conservació: Bo

   Descripció: Fossa rectangular amb angles
   arrodonits, orientada E-W...

   Senyalitzadors: Cip
   Coberta: Teules a la cappuccina
   ```

6. **Parament** (Pestanya 2)
   ```
   Presència: Sí
   Tipus: Personal
   Descripció: Fíbula de bronze prop de l'espatlla
   dreta, moneda prop de la boca...
   ```

7. **Periodització**
   ```
   Període inicial: II - Fase A
   Període final: II - Fase A
   Datació: Segle II dC
   ```

8. **Desament**
   - Clic a "Save"

### Cerca de Tombes

1. Clic a "New Search"
2. Emplenar criteris:
   - Lloc
   - Ritu
   - Tipus sepultura
   - Període
3. Clic a "Search"
4. Navegar entre els resultats

---

## Relacions amb Altres Fitxes

| Fitxa | Relació |
|-------|---------|
| **Fitxa Lloc** | El lloc conté les tombes |
| **Fitxa Estructura** | L'estructura física de la tomba |
| **Fitxa Individus** | Les restes humanes a la tomba |
| **Fitxa Inventari Materials** | Les troballes del parament |
| **Fitxa Periodització** | La cronologia |

### Flux de Treball Recomanat

1. Crear la **Fitxa Lloc** (si no existeix)
2. Crear la **Fitxa Estructura** per a la tomba
3. Crear la **Fitxa Tomba** connectant-la a l'estructura
4. Crear la **Fitxa Individus** per a cada individu
5. Registrar el parament a la **Fitxa Inventari Materials**

---

## Bones Pràctiques

### Nomenclatura

- Usar sigles coherents (TM, TB, SEP)
- Numeració progressiva dins del lloc
- Documentar les convencions adoptades

### Descripció

- Descriure sistemàticament forma, dimensions, orientació
- Documentar l'estat al moment de l'excavació
- Separar observacions objectives d'interpretacions

### Parament

- Registrar posició exacta de cada objecte
- Connectar cada element a l'Inventari Materials
- Documentar associacions significatives

### Periodització

- Basar la datació en elements diagnòstics
- Indicar el grau de fiabilitat
- Comparar amb sepultures similars

---

## Resolució de Problemes

### Problema: Individu no disponible al menú

**Causa**: L'individu no s'ha creat encara o no està associat a l'estructura.

**Solució**:
1. Verificar que existeixi la Fitxa Individus
2. Controlar que l'individu estigui associat a la mateixa estructura

### Problema: Parament no visualitzat a la taula

**Causa**: Les troballes no estan connectades a l'estructura.

**Solució**:
1. Obrir la Fitxa Inventari Materials
2. Verificar que les troballes tinguin l'estructura correcta
3. Actualitzar la fitxa Tomba

### Problema: Tomba no visible al mapa

**Causa**: Geometria no associada.

**Solució**:
1. Verificar que existeixi la capa tomba
2. Controlar que l'estructura tingui geometria
3. Verificar el sistema de referència

---

## Referències

### Base de Dades

- **Taula**: `tomba_table`
- **Classe mapper**: `TOMBA`
- **ID**: `id_tomba`

### Fitxers Font

- **UI**: `gui/ui/Tomba.ui`
- **Controller**: `tabs/Tomba.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`

---

## Vídeo Tutorial

### Panoràmica Fitxa Tomba
**Durada**: 5-6 minuts
- Presentació de la interfície
- Camps principals
- Navegació entre les pestanyes

[Placeholder vídeo: video_panoramica_tomba.mp4]

### Documentació Completa d'una Tomba
**Durada**: 10-12 minuts
- Creació nou registre
- Compilació de tots els camps
- Connexió individus i parament

[Placeholder vídeo: video_schedatura_tomba.mp4]

### Gestió Parament Funerari
**Durada**: 6-8 minuts
- Registre elements del parament
- Connexió amb Inventari Materials
- Documentació posicions

[Placeholder vídeo: video_corredo_tomba.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
