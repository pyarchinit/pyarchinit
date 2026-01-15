# Tutorial 07: Fitxa d'Individus

## Introducció

La **Fitxa d'Individus** és el mòdul de PyArchInit dedicat a la documentació antropològica de les restes humanes trobades durant l'excavació. Aquesta fitxa registra informació sobre el sexe, l'edat, la posició del cos i l'estat de conservació de l'esquelet.

### Conceptes Bàsics

**Individu a PyArchInit:**
- Un individu és un conjunt de restes òssies atribuïbles a una sola persona
- Està connectat a la Fitxa Tomba (context sepulcral)
- Està connectat a la Fitxa Estructura (estructura física)
- Pot estar connectat a l'Arqueozoologia per a anàlisis específiques

**Dades Antropològiques:**
- Estimació del sexe biològic
- Estimació de l'edat a la mort
- Posició i orientació del cos
- Estat de conservació i completesa

---

## Accés a la Fitxa

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Fitxa Individus** (o **Individual form**)

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Individus** (figura humana)

---

## Panoràmica de la Interfície

La fitxa presenta un disseny organitzat en seccions funcionals:

### Àrees Principals

| # | Àrea | Descripció |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegació, cerca, desament |
| 2 | DB Info | Estat registre, ordenació, comptador |
| 3 | Camps Identificatius | Lloc, Àrea, US, Nr. Individu |
| 4 | Connexió Estructura | Sigla i número estructura |
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
| New | New record | Crea un nou registre individu |
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
| PDF | PDF export | Exporta en PDF |
| Directory | Open directory | Obre carpeta export |

---

## Camps Identificatius

Els camps identificatius defineixen unívocament l'individu a la base de dades.

### Lloc

**Camp**: `comboBox_sito`
**Base de dades**: `sito`

Selecciona el lloc arqueològic de pertinença.

### Àrea

**Camp**: `comboBox_area`
**Base de dades**: `area`

Àrea d'excavació dins del lloc. Els valors provenen del tesaurus.

### US

**Camp**: `comboBox_us`
**Base de dades**: `us`

Unitat Estratigràfica de referència.

### Número Individu

**Camp**: `lineEdit_individuo`
**Base de dades**: `nr_individuo`

Número progressiu de l'individu. Es proposa automàticament el proper número disponible.

**Notes:**
- La combinació Lloc + Àrea + US + Nr. Individu ha de ser única
- El número s'assigna automàticament en la creació

### Connexió Estructura

| Camp | Base de dades | Descripció |
|------|---------------|-------------|
| Sigla estructura | `sigla_struttura` | Sigla de l'estructura (ex. TM) |
| Nr estructura | `nr_struttura` | Número de l'estructura |

Aquests camps connecten l'individu a l'estructura funerària.

---

## Dades de Fitxatge

### Data Fitxatge

**Camp**: `dateEdit_schedatura`
**Base de dades**: `data_schedatura`

Data de compilació de la fitxa.

### Fitxador

**Camp**: `comboBox_schedatore`
**Base de dades**: `schedatore`

Nom de l'operador que compila la fitxa.

---

## Pestanya Dades Descriptives

La primera pestanya conté les dades antropològiques fonamentals.

### Estimació del Sexe

**Camp**: `comboBox_sesso`
**Base de dades**: `sesso`

Estimació del sexe biològic basada en caràcters morfològics.

**Valors:**
| Valor | Descripció |
|-------|-------------|
| Masculí | Caràcters masculins evidents |
| Femení | Caràcters femenins evidents |
| Masculí probable | Prevalença caràcters masculins |
| Femení probable | Prevalença caràcters femenins |
| Indeterminat | No determinable |

**Criteris de determinació:**
- Morfologia del pelvis
- Morfologia del crani
- Robustesa general de l'esquelet
- Dimensions dels ossos

### Estimació de l'Edat a la Mort

| Camp | Base de dades | Descripció |
|------|---------------|-------------|
| Edat mínima | `eta_min` | Límit inferior de l'estimació |
| Edat màxima | `eta_max` | Límit superior de l'estimació |

**Mètodes d'estimació:**
- Símfisi púbica
- Superfície auricular
- Sutures cranials
- Desenvolupament dental (per a subadults)
- Epífisis òssies (per a subadults)

### Classes d'Edat

**Camp**: `comboBox_classi_eta`
**Base de dades**: `classi_eta`

Classificació per franges d'edat.

**Valors típics:**
| Classe | Edat aproximada |
|--------|-----------------|
| Infans I | 0-6 anys |
| Infans II | 7-12 anys |
| Juvenis | 13-20 anys |
| Adultus | 21-40 anys |
| Maturus | 41-60 anys |
| Senilis | >60 anys |

### Observacions

**Camp**: `textEdit_osservazioni`
**Base de dades**: `osservazioni`

Camp textual per a notes antropològiques específiques.

**Continguts recomanats:**
- Patologies observades
- Traumatismes
- Marcadors ocupacionals
- Anomalies esquelètiques
- Notes sobre la determinació del sexe i l'edat

---

## Pestanya Orientació i Posició

Aquesta pestanya documenta la posició i l'orientació del cos.

### Estat de Conservació

| Camp | Base de dades | Valors |
|------|---------------|--------|
| Complet | `completo_si_no` | Sí / No |
| Pertorbat | `disturbato_si_no` | Sí / No |
| En connexió | `in_connessione_si_no` | Sí / No |

**Definicions:**
- **Complet**: tots els districtes anatòmics estan representats
- **Pertorbat**: evidències de remogut post-deposicional
- **En connexió**: les articulacions estan preservades

### Longitud Esquelet

**Camp**: `lineEdit_lunghezza`
**Base de dades**: `lunghezza_scheletro`

Longitud mesurada de l'esquelet in situ (en cm o m).

### Posició de l'Esquelet

**Camp**: `comboBox_posizione_scheletro`
**Base de dades**: `posizione_scheletro`

Posició general del cos.

**Valors:**
- Supí (d'esquena)
- Pron (cara avall)
- Lateral dret
- Lateral esquerre
- Encongit
- Irregular

### Posició del Crani

**Camp**: `comboBox_posizione_cranio`
**Base de dades**: `posizione_cranio`

Orientació del cap.

**Valors:**
- Girat a la dreta
- Girat a l'esquerra
- Girat amunt
- Girat avall
- No determinable

### Posició Extremitats Superiors

**Camp**: `comboBox_arti_superiori`
**Base de dades**: `posizione_arti_superiori`

Posició dels braços.

**Valors:**
- Estesos al llarg dels flancs
- Sobre el pelvis
- Sobre el tòrax
- Creuats sobre el tòrax
- Mixtos
- No determinable

### Posició Extremitats Inferiors

**Camp**: `comboBox_arti_inferiori`
**Base de dades**: `posizione_arti_inferiori`

Posició de les cames.

**Valors:**
- Esteses
- Flexionades
- Creuades
- Separades
- No determinable

### Orientació Eix

**Camp**: `comboBox_orientamento_asse`
**Base de dades**: `orientamento_asse`

Orientació de l'eix longitudinal del cos.

**Valors:**
- N-S (cap al Nord)
- S-N (cap al Sud)
- E-W (cap a l'Est)
- W-E (cap a l'Oest)
- NE-SW, NW-SE, etc.

### Orientació Azimut

**Camp**: `lineEdit_azimut`
**Base de dades**: `orientamento_azimut`

Valor numèric de l'azimut en graus (0-360).

---

## Pestanya Restes Osteològiques

Aquesta pestanya està dedicada a la documentació dels districtes anatòmics.

### Documentació dels Districtes

Permet registrar:
- Presència/absència dels elements ossis individuals
- Estat de conservació per districte
- Costat (dret/esquerre) per a elements parells

**Districtes principals:**
| Districte | Elements |
|-----------|----------|
| Crani | Calvària, mandíbula, dents |
| Raquis | Vèrtebres cervicals, toràciques, lumbars, sacre |
| Tòrax | Costelles, estern |
| Extremitats superiors | Clavícules, escàpules, húmers, radi, cúbit, mans |
| Pelvis | Coxals |
| Extremitats inferiors | Fèmurs, tíbia, peroné, peus |

---

## Pestanya Altres Característiques

Aquesta pestanya conté informació addicional.

### Continguts

- Característiques mètriques específiques
- Índexs antropomètrics
- Patologies detallades
- Relacions amb altres individus

---

## Exportació i Impressió

### Exportació PDF

El botó PDF obre un panell amb opcions:

| Opció | Descripció |
|-------|-------------|
| Llista Individus | Llista sintètica |
| Fitxes Individus | Fitxes completes detallades |
| Imprimeix | Genera el PDF |

### Contingut Fitxa PDF

La fitxa PDF inclou:
- Dades identificatives
- Dades antropològiques (sexe, edat)
- Posició i orientació
- Estat de conservació
- Observacions

---

## Flux de Treball Operatiu

### Creació Nou Individu

1. **Obertura fitxa**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic a "New Record"
   - El número individu es proposa automàticament

3. **Dades identificatives**
   ```
   Lloc: Necròpolis d'Empúries
   Àrea: 1
   US: 150
   Nr. Individu: 1
   Sigla estructura: TM
   Nr estructura: 45
   ```

4. **Dades fitxatge**
   ```
   Data: 15/03/2024
   Fitxador: M. Garcia
   ```

5. **Dades antropològiques** (Pestanya 1)
   ```
   Sexe: Masculí
   Edat min: 35
   Edat max: 45
   Classe edat: Adultus

   Observacions: Estatura estimada 170 cm.
   Artrosi lumbar. Càries múltiples.
   ```

6. **Orientació i Posició** (Pestanya 2)
   ```
   Complet: Sí
   Pertorbat: No
   En connexió: Sí
   Longitud: 165 cm
   Posició: Supí
   Crani: Girat a la dreta
   Extremitats superiors: Estesos al llarg dels flancs
   Extremitats inferiors: Esteses
   Orientació: E-W
   Azimut: 90
   ```

7. **Restes osteològiques** (Pestanya 3)
   - Documentar els districtes presents

8. **Desament**
   - Clic a "Save"

### Cerca d'Individus

1. Clic a "New Search"
2. Emplenar criteris:
   - Lloc
   - Sexe
   - Classe edat
   - Posició
3. Clic a "Search"
4. Navegar entre els resultats

---

## Relacions amb Altres Fitxes

| Fitxa | Relació |
|-------|---------|
| **Fitxa Lloc** | El lloc conté els individus |
| **Fitxa Estructura** | L'estructura conté l'individu |
| **Fitxa Tomba** | La tomba documenta el context |
| **Arqueozoologia** | Per a anàlisis osteològiques específiques |

### Flux de Treball Recomanat

1. Crear la **Fitxa Estructura** per a la tomba
2. Crear la **Fitxa Tomba**
3. Crear la **Fitxa Individus** per a cada esquelet
4. Connectar individu a la tomba i estructura

---

## Bones Pràctiques

### Determinació del Sexe

- Utilitzar diversos indicadors morfològics
- Indicar el grau de fiabilitat
- Especificar els criteris utilitzats a les observacions

### Estimació de l'Edat

- Proporcionar sempre un rang (min-max)
- Indicar els mètodes utilitzats
- Per a subadults, especificar desenvolupament dental i epifisiari

### Posició i Orientació

- Documentar amb fotos abans de l'extracció
- Usar referències cardinals
- Mesurar l'azimut amb brúixola

### Conservació

- Distingir pèrdues tafonòmiques d'extraccions antigues
- Documentar les pertorbacions post-deposicionals
- Registrar condicions de recuperació

---

## Resolució de Problemes

### Problema: Número individu duplicat

**Causa**: Ja existeix un individu amb el mateix número.

**Solució**:
1. Verificar la numeració existent
2. Usar el número proposat automàticament
3. Controlar àrea i US

### Problema: Estructura no trobada

**Causa**: L'estructura no existeix o té sigla diferent.

**Solució**:
1. Verificar l'existència de la Fitxa Estructura
2. Controlar sigla i número
3. Crear primer l'estructura si cal

### Problema: Classes edat no disponibles

**Causa**: Tesaurus no configurat.

**Solució**:
1. Verificar la configuració del tesaurus
2. Controlar la llengua establerta
3. Contactar l'administrador

---

## Referències

### Base de Dades

- **Taula**: `individui_table`
- **Classe mapper**: `SCHEDAIND`
- **ID**: `id_scheda_ind`

### Fitxers Font

- **UI**: `gui/ui/Schedaind.ui`
- **Controller**: `tabs/Schedaind.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Individui_pdf.py`

---

## Vídeo Tutorial

### Panoràmica Fitxa Individus
**Durada**: 5-6 minuts
- Presentació de la interfície
- Camps principals
- Navegació entre les pestanyes

[Placeholder vídeo: video_panoramica_individui.mp4]

### Fitxatge Antropològic Complet
**Durada**: 12-15 minuts
- Creació nou registre
- Determinació sexe i edat
- Documentació posició
- Registre restes osteològiques

[Placeholder vídeo: video_schedatura_individui.mp4]

### Connexió Tomba-Individu
**Durada**: 5-6 minuts
- Relació entre fitxes
- Flux de treball correcte
- Bones pràctiques

[Placeholder vídeo: video_collegamento_tomba_individuo.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
