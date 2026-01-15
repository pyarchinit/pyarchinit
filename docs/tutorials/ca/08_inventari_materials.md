# Tutorial 08: Fitxa Inventari Materials

## Índex
1. [Introducció](#introducció)
2. [Accés a la Fitxa](#accés-a-la-fitxa)
3. [Interfície d'Usuari](#interfície-dusuari)
4. [Camps Principals](#camps-principals)
5. [Pestanyes de la Fitxa](#pestanyes-de-la-fitxa)
6. [Barra d'Eines DBMS](#barra-deines-dbms)
7. [Gestió Media](#gestió-media)
8. [Funcionalitats GIS](#funcionalitats-gis)
9. [Quantificacions i Estadístiques](#quantificacions-i-estadístiques)
10. [Exportació i Informes](#exportació-i-informes)
11. [Integració AI](#integració-ai)
12. [Flux de Treball Operatiu](#flux-de-treball-operatiu)
13. [Bones Pràctiques](#bones-pràctiques)
14. [Resolució de Problemes](#resolució-de-problemes)

---

## Introducció

La **Fitxa Inventari Materials** és l'eina principal per a la gestió de les troballes arqueològiques a PyArchInit. Permet catalogar, descriure i quantificar tots els materials trobats durant l'excavació, des de la ceràmica als metalls, des dels vidres als ossos animals.

### Propòsit de la Fitxa

- Inventariar totes les troballes trobades
- Associar les troballes a les US de procedència
- Gestionar la classificació tipològica
- Documentar les característiques físiques i tecnològiques
- Calcular quantificacions (formes mínimes, EVE, pes)
- Connectar fotos i dibuixos a les troballes
- Generar informes i estadístiques

### Tipus de Materials Gestionables

La fitxa suporta diversos tipus de materials:
- **Ceràmica**: Vaixella, terracotes, maons
- **Metalls**: Bronze, ferro, plom, or, plata
- **Vidre**: Contenidors, vidre de finestra
- **Os/Ivori**: Manufactures en matèria dura animal
- **Pedra**: Eines lítiques, escultures
- **Monedes**: Numismàtica
- **Orgànics**: Fusta, teixits, cuir

---

## Accés a la Fitxa

### Des del Menú

1. Obrir QGIS amb el connector PyArchInit actiu
2. Menú **PyArchInit** → **Archaeological record management** → **Artefact** → **Artefact form**

### Des de la Barra d'Eines

1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Troballes** (icona àmfora/vas)

### Drecera de Teclat

- **Ctrl+G**: Activa/desactiva visualització GIS de la troballa actual

---

## Interfície d'Usuari

La interfície està organitzada en tres àrees principals:

### Àrees Principals

| Àrea | Descripció |
|------|-------------|
| **1. Capçalera** | DBMS Toolbar, indicadors estat, botons GIS i export |
| **2. Camps Identificatius** | Lloc, Àrea, US, Número inventari, RA, Tipus troballa |
| **3. Camps Descriptius** | Classe, Definició, Estat conservació, Datació |
| **4. Pestanyes Detall** | 6 pestanyes per a dades específiques |

### Pestanyes Disponibles

| Pestanya | Contingut |
|----------|-----------|
| **Descripció** | Text descriptiu, visor media, datació |
| **Diapositives** | Gestió diapositives i negatius fotogràfics |
| **Dades quantitatives** | Elements troballa, formes, mesures ceràmiques |
| **Tecnologies** | Tècniques productives i decoratives |
| **Ref Biblio** | Referències bibliogràfiques |
| **Quantificacions** | Gràfics i estadístiques |

---

## Camps Principals

### Camps Identificatius

#### Lloc
- **Tipus**: ComboBox (només lectura després del desament)
- **Obligatori**: Sí
- **Descripció**: Lloc arqueològic de procedència

#### Número Inventari
- **Tipus**: LineEdit numèric
- **Obligatori**: Sí
- **Descripció**: Número progressiu únic de la troballa dins del lloc
- **Restricció**: Únic per lloc

#### Àrea
- **Tipus**: ComboBox editable
- **Obligatori**: No
- **Descripció**: Àrea d'excavació de procedència

#### US (Unitat Estratigràfica)
- **Tipus**: LineEdit
- **Obligatori**: No (però molt recomanat)
- **Descripció**: Número de la US de troballa
- **Connexió**: Connecta la troballa a la fitxa US corresponent

#### Estructura
- **Tipus**: ComboBox editable
- **Obligatori**: No
- **Descripció**: Estructura de pertinença (si aplicable)

#### RA (Troballa Arqueològica)
- **Tipus**: LineEdit numèric
- **Obligatori**: No
- **Descripció**: Número de troballa arqueològica (numeració alternativa)

### Camps Classificació

#### Tipus Troballa
- **Tipus**: ComboBox editable
- **Obligatori**: Sí
- **Valors típics**: Ceràmica, Metall, Vidre, Os, Pedra, Moneda, etc.

#### Classe Material (Criteri Fitxatge)
- **Tipus**: ComboBox editable
- **Obligatori**: No
- **Descripció**: Classe de pertinença del material
- **Exemples per ceràmica**:
  - Ceràmica comuna
  - Sigil·lata itàlica
  - Sigil·lata africana
  - Ceràmica de vernís negre
  - Ceràmica de parets fines
  - Àmfores
  - Llànties

#### Definició
- **Tipus**: ComboBox editable
- **Obligatori**: No
- **Descripció**: Definició tipològica específica
- **Exemples**: Plat, Copa, Olla, Gerra, Tapadora, etc.

### Camps Estat i Conservació

#### Rentat
- **Tipus**: ComboBox
- **Valors**: Sí, No
- **Descripció**: Indica si la troballa ha estat rentada

#### Repertoriat
- **Tipus**: ComboBox
- **Valors**: Sí, No
- **Descripció**: Indica si la troballa ha estat seleccionada per a l'estudi

#### Diagnòstic
- **Tipus**: ComboBox
- **Valors**: Sí, No
- **Descripció**: Indica si la troballa és diagnòstica (útil per a classificació)

#### Estat Conservació
- **Tipus**: ComboBox editable
- **Obligatori**: No
- **Valors típics**: Integre, Fragmentari, Lacunós, Restaurat

### Camps Dipòsit

#### Nr. Caixa
- **Tipus**: LineEdit
- **Descripció**: Número de la caixa de dipòsit

#### Lloc de Conservació
- **Tipus**: ComboBox editable
- **Descripció**: Magatzem o dipòsit de conservació

---

## Pestanyes de la Fitxa

### Pestanya 1: Descripció

La pestanya principal conté la descripció textual de la troballa i la gestió dels media.

#### Camp Descripció
- **Tipus**: TextEdit multilínia
- **Contingut suggerit**:
  - Forma general
  - Parts conservades
  - Característiques tècniques
  - Decoracions
  - Confronts tipològics

#### Datació Troballa
- **Tipus**: ComboBox editable
- **Descripció**: Enquadrament cronològic de la troballa
- **Format**: Textual (ex. "Segle I aC", "Segles II-III dC")

#### Visor Media
Àrea per visualitzar les imatges associades a la troballa:
- **Visualitza totes les imatges**: Carrega totes les fotos connectades
- **Cerca imatges**: Cerca a les imatges
- **Elimina tag**: Elimina associació imatge-troballa
- **SketchGPT**: Genera descripció AI des d'imatge

### Pestanya 2: Diapositives

Gestió de la documentació fotogràfica tradicional.

#### Taula Diapositives
| Columna | Descripció |
|---------|-------------|
| Codi | Codi identificatiu de la diapositiva |
| N. | Número progressiu |

#### Taula Negatius
| Columna | Descripció |
|---------|-------------|
| Codi | Codi del rotllo negatiu |
| N. | Número del fotograma |

### Pestanya 3: Dades Quantitatives

Pestanya fonamental per a l'anàlisi quantitativa, especialment per a la ceràmica.

#### Taula Elements Troballa
Permet registrar els elements individuals que componen la troballa:

| Columna | Descripció | Exemple |
|---------|-------------|---------|
| Element trobat | Part anatòmica del vas | Vora, Paret, Fons, Nansa |
| Tipus de quantitat | Estat del fragment | Fragment, Sencer |
| Quantitat | Nombre de peces | 5 |

#### Camps Quantificació Ceràmica

| Camp | Descripció |
|------|-------------|
| **Formes mínimes** | Nombre Mínim d'Individus (NMI) |
| **Formes màximes** | Nombre Màxim d'Individus |
| **Total fragments** | Comptatge automàtic des de la taula elements |
| **Pes** | Pes en grams |
| **Diàmetre vora** | Diàmetre de la vora en cm |
| **EVE vora** | Estimated Vessel Equivalent (percentatge vora conservada) |

### Pestanya 4: Tecnologies

Registre de les tècniques productives i decoratives.

#### Taula Tecnologies

| Columna | Descripció | Exemple |
|---------|-------------|---------|
| Tipus tecnologia | Categoria tècnica | Producció, Decoració |
| Posició | On es troba | Intern, Extern, Cos |
| Quantitat | Si aplicable | - |

#### Camps Específics Ceràmica

| Camp | Descripció |
|------|-------------|
| **Cos ceràmic** | Tipus de pasta (Depurat, Semidepurat, Groller) |
| **Revestiment** | Tipus de revestiment (Vernís, Engalba, Vidrat) |

### Pestanya 5: Referències Bibliogràfiques

Gestió de la bibliografia de confrontació.

#### Taula Referències

| Columna | Descripció |
|---------|-------------|
| Autor | Cognom autor/s |
| Any | Any publicació |
| Títol | Títol abreujat |
| Pàgina | Referència pàgina |
| Figura | Referència figura/làmina |

### Pestanya 6: Quantificacions

Pestanya per generar gràfics i estadístiques sobre les dades.

#### Tipus de Quantificació Disponibles

| Tipus | Descripció |
|-------|-------------|
| **Formes mínimes** | Gràfic per NMI |
| **Formes màximes** | Gràfic per nombre màxim |
| **Total fragments** | Gràfic per comptatge fragments |
| **Pes** | Gràfic per pes |
| **EVE vora** | Gràfic per EVE |

---

## Barra d'Eines DBMS

La barra d'eines ofereix tots els instruments per a la gestió dels registres.

### Botons Estàndard

| Icona | Funció | Descripció |
|-------|--------|-------------|
| Connection test | Test connexió | Verifica connexió a la base de dades |
| First/Prev/Next/Last | Navegació | Navegació entre els registres |
| New record | Nou | Crea nova troballa |
| Save | Desa | Desa modificacions |
| Delete | Elimina | Elimina troballa actual |
| View all | Tots | Visualitza tots els registres |
| New search | Cerca | Activa modalitat cerca |
| Search!!! | Executa | Executa la cerca |
| Order by | Ordena | Ordena els registres |

### Botons Específics

| Icona | Funció | Descripció |
|-------|--------|-------------|
| GIS | Visualitza GIS | Mostra troballa al mapa |
| PDF | Export PDF | Genera fitxa PDF |
| Sheet | Export llista | Genera llista PDF |
| Excel | Export Excel | Exporta en format Excel/CSV |
| A5 | Export A5 | Genera etiqueta format A5 |
| Quant | Quantificacions | Obre panell quantificacions |

---

## Gestió Media

### Associació Imatges

#### Arrossega i Deixa
És possible arrossegar imatges directament a la llista per associar-les a la troballa.

#### Botons Media

| Botó | Funció |
|------|--------|
| **Totes les imatges** | Carrega totes les imatges associades |
| **Cerca imatges** | Obre cerca a les imatges |
| **Elimina tag** | Elimina associació actual |

### Visualitzador Imatges

Doble clic sobre una imatge a la llista obre el visualitzador complet amb:
- Zoom
- Panoràmica
- Rotació
- Informació EXIF

---

## Funcionalitats GIS

### Visualització al Mapa

#### Botó GIS (Toggle)
- **Actiu**: La troballa es ressalta al mapa QGIS
- **Desactiu**: Cap visualització
- **Drecera**: Ctrl+G

#### Requisits
- La troballa ha de tenir la US de procedència especificada
- La US ha de tenir una geometria a la capa GIS

---

## Quantificacions i Estadístiques

### Accés a les Quantificacions

1. Fer clic al botó **Quant** a la barra d'eines
2. Seleccionar el tipus de quantificació
3. Seleccionar els paràmetres d'agrupament
4. Fer clic OK

### Tipus de Gràfics

#### Gràfic de Barres
Visualitza la distribució per categoria seleccionada.

### Exportació Quantificacions

Les dades de les quantificacions s'exporten automàticament en:
- Fitxer CSV a la carpeta `pyarchinit_Quantificazioni_folder`
- Gràfic visualitzat a pantalla

---

## Exportació i Informes

### Exportació PDF Fitxa Individual

Genera una fitxa PDF completa de la troballa actual amb:
- Totes les dades identificatives
- Descripció
- Dades quantitatives
- Referències bibliogràfiques
- Imatges associades (si disponibles)

### Exportació PDF Llista

Genera una llista PDF de totes les troballes visualitzades (resultat cerca actual):
- Taula recapitulativa
- Dades essencials per a cada troballa

### Exportació A5 (Etiquetes)

Genera etiquetes format A5 per:
- Identificació caixes
- Etiquetatge troballes
- Fitxes mòbils

### Exportació Excel/CSV

Exporta les dades en format tabular per:
- Elaboracions estadístiques externes
- Import en altres programaris
- Arxivament

---

## Integració AI

### SketchGPT

Funcionalitat AI per generar automàticament descripcions de les troballes a partir d'imatges.

#### Ús

1. Associar una imatge a la troballa
2. Fer clic al botó **SketchGPT**
3. Seleccionar la imatge a analitzar
4. Seleccionar el model GPT (gpt-4-vision, gpt-4o)
5. El sistema genera una descripció arqueològica

#### Sortida

La descripció generada inclou:
- Identificació del tipus de troballa
- Descripció de les característiques visibles
- Possibles confronts tipològics
- Suggeriments de datació

> **Nota**: Requereix API Key OpenAI configurada.

---

## Flux de Treball Operatiu

### Creació d'una Nova Troballa

#### Pas 1: Obertura Fitxa
1. Obrir la Fitxa Inventari Materials
2. Verificar la connexió a la base de dades

#### Pas 2: Nou Registre
1. Fer clic **New record**
2. L'Status canvia a "Nou Registre"

#### Pas 3: Dades Identificatives
1. Verificar/seleccionar el **Lloc**
2. Inserir el **Número inventari** (progressiu)
3. Inserir **Àrea** i **US** de procedència

#### Pas 4: Classificació
1. Seleccionar el **Tipus troballa**
2. Seleccionar la **Classe material**
3. Seleccionar/inserir la **Definició**

#### Pas 5: Descripció
1. Compilar el camp **Descripció** a la pestanya Descripció
2. Seleccionar la **Datació**
3. Associar eventuals imatges

#### Pas 6: Dades Quantitatives (si ceràmica)
1. Obrir la pestanya **Dades quantitatives**
2. Inserir els elements a la taula
3. Compilar formes mínimes/màximes
4. Inserir pes i mesures

#### Pas 7: Dipòsit
1. Inserir **Nr. caixa**
2. Seleccionar **Lloc conservació**
3. Indicar **Estat conservació**

#### Pas 8: Desament
1. Fer clic **Save**
2. Verificar el missatge de confirmació

### Cerca Troballes

#### Cerca Simple
1. Fer clic **New search**
2. Emplenar els camps de cerca desitjats
3. Fer clic **Search!!!**

#### Cerca per US
1. Activar cerca
2. Inserir només el número US al camp US
3. Executar cerca

---

## Bones Pràctiques

### Numeració Inventari

- Usar numeració progressiva sense interrupcions
- Un número = una troballa (o grup homogeni)
- Documentar el criteri d'inventariació

### Classificació

- Utilitzar vocabularis controlats per a les classes
- Mantenir coherència en la definició dels tipus
- Actualitzar el tesaurus quan sigui necessari

### Quantificació Ceràmica

Per a una correcta quantificació:
1. **Formes mínimes (NMI)**: Comptar només elements diagnòstics (vores, fons distintius)
2. **EVE**: Mesurar el percentatge de circumferència conservada
3. **Pes**: Pesar tots els fragments del grup

### Documentació Fotogràfica

- Fotografiar totes les troballes diagnòstiques
- Usar escala mètrica a les fotos
- Associar les fotos mitjançant el gestor media

### Connexió US

- Verificar sempre que la US existeixi abans d'associar-la
- Per a troballes de neteja/superfície, usar US apropiades
- Documentar els casos de troballes fora de context

---

## Resolució de Problemes

### Problemes Comuns

#### Número inventari duplicat
- **Error**: "Ja existeix un registre amb aquest número inventari"
- **Causa**: El número ja està utilitzat per al lloc
- **Solució**: Verificar el proper número disponible amb "View all"

#### Imatges no visualitzades
- **Causa**: Ruta de les imatges no correcta
- **Solució**:
  1. Verificar configuració ruta a Settings
  2. Verificar que les imatges siguin a la carpeta correcta
  3. Reassociar les imatges

#### Quantificacions buides
- **Causa**: Camps quantitatius no emplenats
- **Solució**: Emplenar formes mínimes/màximes o total fragments

#### Exportació PDF buida
- **Causa**: Cap registre seleccionat
- **Solució**: Verificar de tenir almenys un registre visualitzat

#### GIS no funciona
- **Causa**: US no té geometria o capa no carregada
- **Solució**:
  1. Verificar que la capa US estigui carregada a QGIS
  2. Verificar que la US tingui una geometria associada

---

## Vídeo Tutorial

### Vídeo 1: Panoràmica Fitxa Inventari
*Durada: 5-6 minuts*

**Continguts:**
- Interfície general
- Navegació entre les pestanyes
- Funcionalitats principals

### Vídeo 2: Fitxatge Ceràmica Complet
*Durada: 8-10 minuts*

**Continguts:**
- Compilació de tots els camps
- Quantificació ceràmica
- Elements de la troballa
- Tecnologies

### Vídeo 3: Gestió Media i Fotos
*Durada: 4-5 minuts*

**Continguts:**
- Associació imatges
- Visualitzador
- SketchGPT

### Vídeo 4: Exportació i Quantificacions
*Durada: 5-6 minuts*

**Continguts:**
- Exportació PDF
- Exportació Excel
- Gràfics quantificacions

---

*Última actualització: Gener 2026*
*PyArchInit - Gestió de Dades Arqueològiques*
