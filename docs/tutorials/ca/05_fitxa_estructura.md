# Tutorial 05: Fitxa d'Estructura

## Introducció

La **Fitxa d'Estructura** és el mòdul de PyArchInit dedicat a la documentació de les estructures arqueològiques. Una estructura és un conjunt organitzat d'Unitats Estratigràfiques (US/USM) que formen una entitat constructiva o funcional recognoscible, com ara un mur, una pavimentació, una tomba, un forn, o qualsevol altre element construït.

### Conceptes Bàsics

**Estructura vs Unitat Estratigràfica:**
- Una **US** és la unitat singular (estrat, tall, rebliment)
- Una **Estructura** agrupa diverses US correlacionades funcionalment
- Exemple: un mur (estructura) està compost per fonamentació, alçat, morter (diverses US)

**Jerarquies:**
- Les estructures poden tenir relacions entre elles
- Cada estructura pertany a un o més períodes/fases cronològiques
- Les estructures estan connectades a les US que les componen

---

## Accés a la Fitxa

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Gestió Estructures** (o **Structure form**)

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Estructura** (edifici estilitzat)

---

## Panoràmica de la Interfície

La fitxa presenta un disseny organitzat en seccions funcionals:

### Àrees Principals

| # | Àrea | Descripció |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegació, cerca, desament |
| 2 | DB Info | Estat registre, ordenació, comptador |
| 3 | Camps Identificatius | Lloc, Sigla, Número estructura |
| 4 | Camps Classificació | Categoria, Tipologia, Definició |
| 5 | Àrea Tab | Pestanyes temàtiques per a dades específiques |

---

## Barra d'Eines DBMS

La barra d'eines principal proporciona tots els instruments per a la gestió dels registres.

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
| New | New record | Crea un nou registre estructura |
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
| Map Preview | Map preview | Activa/desactiva previsualització mapa |
| Media Preview | Media preview | Activa/desactiva previsualització media |
| Draw Structure | Draw structure | Dibuixa estructura al mapa |
| GIS | Load to GIS | Carrega estructura al mapa |
| Layers | Load all | Carrega totes les estructures |
| PDF | PDF export | Exporta en PDF |
| Directory | Open directory | Obre carpeta export |

---

## Camps Identificatius

Els camps identificatius defineixen unívocament l'estructura a la base de dades.

### Lloc

**Camp**: `comboBox_sito`
**Base de dades**: `sito`

Selecciona el lloc arqueològic de pertinença. El menú desplegable mostra tots els llocs registrats a la base de dades.

**Notes:**
- Camp obligatori
- La combinació Lloc + Sigla + Número ha de ser única
- Bloquejat després de la creació del registre

### Sigla Estructura

**Camp**: `comboBox_sigla_struttura`
**Base de dades**: `sigla_struttura`

Codi alfanumèric que identifica el tipus d'estructura. Convencions comunes:

| Sigla | Significat | Exemple |
|-------|------------|---------|
| MR | Mur | MR 1 |
| ST | Estructura | ST 5 |
| PV | Pavimentació | PV 2 |
| FO | Forn | FO 1 |
| VA | Bassa | VA 3 |
| TM | Tomba | TM 10 |
| PT | Pou | PT 2 |
| CN | Canal | CN 1 |

**Notes:**
- Editable amb inserció lliure
- Bloquejat després de la creació

### Número Estructura

**Camp**: `numero_struttura`
**Base de dades**: `numero_struttura`

Número progressiu de l'estructura dins de la sigla.

**Notes:**
- Camp numèric
- Ha de ser únic per combinació Lloc + Sigla
- Bloquejat després de la creació

---

## Camps de Classificació

Els camps de classificació defineixen la naturalesa de l'estructura.

### Categoria Estructura

**Camp**: `comboBox_categoria_struttura`
**Base de dades**: `categoria_struttura`

Macro-categoria funcional de l'estructura.

**Valors típics:**
- Residencial
- Productiva
- Funerària
- Religiosa
- Defensiva
- Hidràulica
- Viària
- Artesanal

### Tipologia Estructura

**Camp**: `comboBox_tipologia_struttura`
**Base de dades**: `tipologia_struttura`

Tipologia específica dins de la categoria.

**Exemples per categoria:**
| Categoria | Tipologies |
|-----------|-----------|
| Residencial | Casa, Vil·la, Palau, Cabana |
| Productiva | Forns, Molí, Trull |
| Funerària | Tomba de fossa, Tomba de cambra, Sarcòfag |
| Hidràulica | Pou, Cisterna, Aqüeducte, Canal |

### Definició Estructura

**Camp**: `comboBox_definizione_struttura`
**Base de dades**: `definizione_struttura`

Definició sintètica i específica de l'element estructural.

**Exemples:**
- Mur perimetral
- Pavimentació en opus signinum
- Llindar de pedra
- Escalinata
- Base de columna

---

## Pestanya Dades Descriptives

La primera pestanya conté els camps textuals per a la descripció detallada.

### Descripció

**Camp**: `textEdit_descrizione_struttura`
**Base de dades**: `descrizione`

Camp textual lliure per a la descripció física de l'estructura.

**Continguts recomanats:**
- Tècnica constructiva
- Materials utilitzats
- Estat de conservació
- Dimensions generals
- Orientació
- Característiques peculiars

**Exemple:**
```
Mur en opus incertum realitzat amb blocs de calcària local
de dimensions variables (cm 15-30). Lligant en morter de calç
de color blanquinós. Conservat per una alçada màxima d'1,20 m.
Amplada mitjana 50 cm. Orientació NE-SW. Presenta restes
d'enguixat al costat intern.
```

### Interpretació

**Camp**: `textEdit_interpretazione_struttura`
**Base de dades**: `interpretazione`

Interpretació funcional i històrica de l'estructura.

**Continguts recomanats:**
- Funció original hipotètica
- Fases d'utilització/reutilització
- Comparacions tipològiques
- Enquadrament cronològic
- Relacions amb altres estructures

**Exemple:**
```
Mur perimetral nord d'un edifici residencial d'època romana
imperial. La tècnica constructiva i els materials suggereixen
una datació al segle II dC. En una fase posterior (segles III-IV)
el mur fou parcialment espoliat i incorporat en una
estructura productiva.
```

---

## Pestanya Periodització

Aquesta pestanya gestiona l'enquadrament cronològic de l'estructura.

### Període i Fase Inicial

| Camp | Base de dades | Descripció |
|------|---------------|-------------|
| Període Inicial | `periodo_iniziale` | Període de construcció/inici ús |
| Fase Inicial | `fase_iniziale` | Fase dins del període |

Els valors es poblen automàticament segons els períodes definits a la Fitxa Periodització per al lloc seleccionat.

### Període i Fase Final

| Camp | Base de dades | Descripció |
|------|---------------|-------------|
| Període Final | `periodo_finale` | Període d'abandó/amortització |
| Fase Final | `fase_finale` | Fase dins del període |

### Datació Estesa

**Camp**: `comboBox_datazione_estesa`
**Base de dades**: `datazione_estesa`

Datació literal calculada automàticament o inserida manualment.

**Formats:**
- "Segle I aC - Segle II dC"
- "100 aC - 200 dC"
- "Època romana imperial"

**Notes:**
- Es proposa automàticament segons període/fase
- Modificable manualment per a casos particulars

---

## Pestanya Relacions

Aquesta pestanya gestiona les relacions entre estructures.

### Taula Relacions Estructura

**Widget**: `tableWidget_rapporti`
**Base de dades**: `rapporti_struttura`

Registra les relacions entre l'estructura actual i altres estructures.

**Columnes:**
| Columna | Descripció |
|---------|-------------|
| Tipus de relació | Relació estratigràfica/funcional |
| Lloc | Lloc de l'estructura correlacionada |
| Sigla | Sigla de l'estructura correlacionada |
| Número | Número de l'estructura correlacionada |

**Tipus de relació:**

| Relació | Invers | Descripció |
|---------|--------|-------------|
| Es lliga a | Es lliga a | Connexió física contemporània |
| Cobreix | Cobert per | Relació de superposició |
| Talla | Tallat per | Relació de tall |
| Rebleix | Reblert per | Relació de rebliment |
| S'apoia a | Se li apoia | Relació d'assentament |
| Igual a | Igual a | Mateixa estructura amb nom diferent |

### Gestió de Files

| Botó | Funció |
|------|--------|
| + | Afegeix nova fila |
| - | Elimina fila seleccionada |

---

## Pestanya Elements Constructius

Aquesta pestanya documenta els materials i els elements que componen l'estructura.

### Materials Emprats

**Widget**: `tableWidget_materiali_impiegati`
**Base de dades**: `materiali_impiegati`

Llista dels materials utilitzats en la construcció.

**Columna:**
- Materials: descripció del material

**Exemples de materials:**
- Blocs de calcària
- Maons
- Morter de calç
- Còdols de riu
- Teules
- Marbre
- Tova

### Elements Estructurals

**Widget**: `tableWidget_elementi_strutturali`
**Base de dades**: `elementi_strutturali`

Llista dels elements constructius amb quantitat.

**Columnes:**
| Columna | Descripció |
|---------|-------------|
| Tipologia element | Tipus d'element |
| Quantitat | Nombre d'elements |

**Exemples d'elements:**
| Element | Quantitat |
|---------|-----------|
| Base de columna | 4 |
| Capitell | 2 |
| Llindar | 1 |
| Bloc escairat | 45 |

### Gestió de Files

Per a ambdues taules:
| Botó | Funció |
|------|--------|
| + | Afegeix nova fila |
| - | Elimina fila seleccionada |

---

## Pestanya Mesures

Aquesta pestanya registra les dimensions de l'estructura.

### Taula Mesuraments

**Widget**: `tableWidget_misurazioni`
**Base de dades**: `misure_struttura`

**Columnes:**
| Columna | Descripció |
|---------|-------------|
| Tipus mesura | Tipus de dimensió |
| Unitat de mesura | m, cm, m², etc. |
| Valor | Valor numèric |

### Tipus de Mesura Comuns

| Tipus | Descripció |
|-------|-------------|
| Longitud | Dimensió major |
| Amplada | Dimensió menor |
| Alçada conservada | Alçat conservat |
| Alçada original | Alçat estimat original |
| Profunditat | Per estructures enterrades |
| Diàmetre | Per estructures circulars |
| Gruix | Per murs, paviments |
| Superfície | Àrea en m² |

### Exemple de Compilació

| Tipus mesura | Unitat de mesura | Valor |
|--------------|------------------|-------|
| Longitud | m | 8,50 |
| Amplada | cm | 55 |
| Alçada conservada | m | 1,20 |
| Superfície | m² | 4,68 |

---

## Pestanya Media

Gestió d'imatges, vídeos i models 3D associats a l'estructura.

### Funcionalitats

**Widget**: `iconListWidget`

Visualitza les miniatures dels media associats.

### Botons

| Icona | Funció | Descripció |
|-------|--------|-------------|
| All Images | All images | Mostra totes les imatges |
| Remove Tags | Remove tags | Elimina associació media |
| Search | Search images | Cerca imatges a la base de dades |

### Arrossega i Deixa

És possible arrossegar fitxers directament sobre la fitxa:

**Formats suportats:**
- Imatges: JPG, JPEG, PNG, TIFF, TIF, BMP
- Vídeo: MP4, AVI, MOV, MKV, FLV
- 3D: OBJ, STL, PLY, FBX, 3DS

### Visualització

- **Doble clic** sobre miniatura: obre el visualitzador
- Per als vídeos: obre el reproductor de vídeo integrat
- Per als 3D: obre el visualitzador 3D PyVista

---

## Pestanya Mapa

Previsualització de la posició de l'estructura al mapa.

### Funcionalitats

- Visualitza la geometria de l'estructura
- Zoom automàtic sobre l'element
- Integració amb les capes GIS del projecte

---

## Integració GIS

### Visualització al Mapa

| Botó | Funció |
|------|--------|
| Map Preview | Toggle previsualització a la pestanya Mapa |
| Draw Structure | Ressalta estructura al mapa QGIS |
| Load to GIS | Carrega capa estructures |
| Load All | Carrega totes les estructures del lloc |

### Capes GIS

La fitxa utilitza la capa **pyarchinit_strutture** per a la visualització:
- Geometria: polígon o multipolígon
- Atributs connectats als camps de la fitxa

---

## Exportació i Impressió

### Exportació PDF

El botó PDF obre un panell amb opcions d'exportació:

| Opció | Descripció |
|-------|-------------|
| Llista Estructures | Llista sintètica de les estructures |
| Fitxes Estructures | Fitxes completes detallades |
| Imprimeix | Genera el PDF |
| Converteix a Word | Converteix PDF a format Word |

### Conversió PDF a Word

Funcionalitat avançada per convertir els PDF generats en documents Word editables:

1. Seleccionar el fitxer PDF a convertir
2. Especificar interval de pàgines (opcional)
3. Fer clic a "Convert"
4. El fitxer Word es desa a la mateixa carpeta

---

## Flux de Treball Operatiu

### Creació Nova Estructura

1. **Obertura fitxa**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic al botó "New Record"
   - Els camps identificatius es tornen editables

3. **Dades identificatives**
   ```
   Lloc: Vil·la Romana de Centcelles
   Sigla: MR
   Número: 15
   ```

4. **Classificació**
   ```
   Categoria: Residencial
   Tipologia: Mur perimetral
   Definició: Mur en opus incertum
   ```

5. **Dades descriptives** (Pestanya 1)
   ```
   Descripció: Mur realitzat en opus incertum amb
   blocs de calcària local...

   Interpretació: Límit nord de la domus, fase I
   de l'implantació residencial...
   ```

6. **Periodització** (Pestanya 2)
   ```
   Període inicial: I - Fase: A
   Període final: II - Fase: B
   Datació: Segle I aC - Segle II dC
   ```

7. **Relacions** (Pestanya 3)
   ```
   Es lliga a: MR 16, MR 17
   Tallat per: ST 5
   ```

8. **Elements constructius** (Pestanya 4)
   ```
   Materials: Blocs de calcària, Morter de calç
   Elements: Blocs escairats (52), Llindar (1)
   ```

9. **Mesures** (Pestanya 5)
   ```
   Longitud: 12,50 m
   Amplada: 0,55 m
   Alçada conservada: 1,80 m
   ```

10. **Desament**
    - Clic a "Save"
    - Verifica confirmació de desament

### Cerca d'Estructures

1. Clic a "New Search"
2. Emplenar un o més camps filtre:
   - Lloc
   - Sigla estructura
   - Categoria
   - Període
3. Clic a "Search"
4. Navegar entre els resultats

### Modificació Estructura Existent

1. Navegar al registre desitjat
2. Modificar els camps necessaris
3. Clic a "Save"

---

## Bones Pràctiques

### Nomenclatura

- Usar sigles coherents en tot el projecte
- Documentar les convencions usades
- Evitar duplicacions de numeració

### Descripció

- Ser sistemàtics en la descripció
- Seguir un esquema: tècnica > materials > dimensions > estat
- Separar descripció objectiva d'interpretació

### Periodització

- Connectar sempre a períodes definits a la Fitxa Periodització
- Indicar tant fase inicial com final
- Usar la datació estesa per síntesi

### Relacions

- Registrar totes les relacions significatives
- Verificar la reciprocitat de les relacions
- Connectar a les US que componen l'estructura

### Media

- Associar fotos representatives
- Incloure fotos de detall constructius
- Documentar les fases d'excavació

---

## Resolució de Problemes

### Problema: Estructura no visible al mapa

**Causa**: Geometria no associada o capa no carregada.

**Solució**:
1. Verificar que existeixi la capa `pyarchinit_strutture`
2. Controlar que l'estructura tingui una geometria associada
3. Verificar el sistema de referència

### Problema: Períodes no disponibles

**Causa**: Períodes no definits per al lloc.

**Solució**:
1. Obrir la Fitxa Periodització
2. Definir els períodes per al lloc actual
3. Tornar a la Fitxa Estructura

### Problema: Error desament "registre existent"

**Causa**: Combinació Lloc + Sigla + Número ja existent.

**Solució**:
1. Verificar la numeració existent
2. Usar un número progressiu lliure
3. Controlar que no hi hagi duplicats

### Problema: Media no visualitzats

**Causa**: Ruta de les imatges no correcta.

**Solució**:
1. Verificar la ruta a la configuració
2. Controlar que els fitxers existeixin
3. Regenerar les miniatures si cal

---

## Sincronització amb la Fitxa US

Quan es crea una estructura a la Fitxa Estructura, apareix automàticament a la llista desplegable del camp **Estructura** de la Fitxa US.

### Camps Requerits per a la Sincronització

Perquè una estructura aparegui a la llista desplegable d'US:
1. **Lloc**: Ha de coincidir amb el lloc de l'US
2. **Sigla Estructura**: Ha d'estar emplenat (ex. MR, ST, PV)
3. **Número Estructura**: Ha d'estar emplenat

### Flux de Treball

1. **Crear l'estructura**: Emplenar lloc, sigla i número
2. **Desar**: El registre s'ha de desar
3. **A la Fitxa US**: L'estructura ara apareix al desplegable del camp Estructura
4. **Assignar**: Seleccioneu l'estructura/es per a l'US
5. **Sincronització**: Les dades queden vinculades entre les fitxes

### Eliminar Estructures d'una US

Per eliminar totes les estructures d'una US:
1. Obriu la Fitxa US
2. **Clic dret** al camp Estructura
3. Seleccioneu **"Clear Structure field"**
4. Deseu el registre

---

## Relacions amb Altres Fitxes

| Fitxa | Relació |
|-------|---------|
| **Fitxa Lloc** | El lloc conté les estructures |
| **Fitxa US** | Les US componen les estructures |
| **Fitxa Periodització** | Proporciona la cronologia |
| **Fitxa Inventari Materials** | Troballes associades a les estructures |
| **Fitxa Tomba** | Tombes com a tipus especial d'estructura |

---

## Referències

### Base de Dades

- **Taula**: `struttura_table`
- **Classe mapper**: `STRUTTURA`
- **ID**: `id_struttura`

### Fitxers Font

- **UI**: `gui/ui/Struttura.ui`
- **Controller**: `tabs/Struttura.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`

---

## Vídeo Tutorial

### Panoràmica Fitxa Estructura
**Durada**: 5-6 minuts
- Presentació general de la interfície
- Navegació entre les pestanyes
- Funcionalitats principals

[Placeholder vídeo: video_panoramica_struttura.mp4]

### Documentació Completa d'una Estructura
**Durada**: 10-12 minuts
- Creació nou registre
- Compilació de tots els camps
- Gestió relacions i mesures

[Placeholder vídeo: video_schedatura_struttura.mp4]

### Integració GIS i Exportació
**Durada**: 6-8 minuts
- Visualització al mapa
- Càrrega de capes
- Exportació PDF i Word

[Placeholder vídeo: video_gis_export_struttura.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
