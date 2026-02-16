# PyArchInit - Fitxa de Lloc

## Índex
1. [Introducció](#introducció)
2. [Accés a la Fitxa](#accés-a-la-fitxa)
3. [Interfície d'Usuari](#interfície-dusuari)
4. [Dades Descriptives del Lloc](#dades-descriptives-del-lloc)
5. [Barra d'Eines DBMS](#barra-deines-dbms)
6. [Funcionalitats GIS](#funcionalitats-gis)
7. [Generació de Fitxes US](#generació-de-fitxes-us)
8. [Eines d'Anàlisi](#eines-danàlisi)
9. [Exportació d'Informes](#exportació-dinformes)
10. [Flux de Treball Operatiu](#flux-de-treball-operatiu)

---

## Introducció

La **Fitxa de Lloc** és el punt de partida per a la documentació d'una excavació arqueològica a PyArchInit. Cada projecte arqueològic comença amb la creació d'un lloc, que funciona com a contenidor principal per a totes les altres informacions (Unitats Estratigràfiques, Estructures, Troballes, etc.).

Un **lloc arqueològic** a PyArchInit representa una àrea geogràfica definida on es desenvolupen les activitats de recerca arqueològica. Pot ser una excavació, una àrea de prospecció, un monument, etc.

---

## Accés a la Fitxa

Per accedir a la Fitxa de Lloc:

1. Menú **PyArchInit** → **Archaeological record management** → **Site**
2. O des de la barra d'eines PyArchInit, fer clic a la icona **Lloc**

---

## Interfície d'Usuari

La Fitxa de Lloc es divideix en diverses àrees funcionals:

### Àrees Principals

| # | Àrea | Descripció |
|---|------|------------|
| 1 | **DBMS Toolbar** | Barra d'eines per a navegació i gestió de registres |
| 2 | **Dades Descriptives** | Camps per inserir la informació del lloc |
| 3 | **Generador US** | Eina per crear fitxes US en lot |
| 4 | **GIS Viewer** | Controls per a visualització cartogràfica |
| 5 | **Eines d'Anàlisi** | Accessibles des de la barra d'eines (MoveCost, GeoArchaeo, SAM, etc.) |
| 6 | **Ajuda** | Documentació i tutorials en vídeo |

---

## Dades Descriptives del Lloc

### Pestanya Dades Descriptives

#### Camps Obligatoris

| Camp | Descripció | Notes |
|------|------------|-------|
| **Lloc** | Nom identificatiu del lloc | Camp obligatori, ha de ser únic |

#### Camps Geogràfics

| Camp | Descripció | Exemple |
|------|------------|---------|
| **Nació** | Estat on es troba el lloc | Espanya |
| **Regió** | Comunitat autònoma | Catalunya |
| **Província** | Província | Barcelona |
| **Municipi** | Municipi | Barcelona |

#### Camps Descriptius

| Camp | Descripció |
|------|------------|
| **Nom** | Nom extens/descriptiu del lloc |
| **Definició** | Tipologia del lloc (del tesaurus) |
| **Descripció** | Camp textual lliure per a descripció detallada |
| **Carpeta** | Ruta a la carpeta local del projecte |

### Definició de Lloc (Tesaurus)

El camp **Definició** utilitza un vocabulari controlat (tesaurus). Les opcions disponibles inclouen:

| Definició | Descripció |
|-----------|------------|
| Àrea d'excavació | Zona sotmesa a investigació estratigràfica |
| Àrea de prospecció | Àrea de reconeixement superficial |
| Lloc arqueològic | Localitat amb evidències arqueològiques |
| Monument | Estructura monumental singular |
| Necròpolis | Àrea sepulcral |
| Assentament | Àrea habitacional |
| Santuari | Àrea sagrada/cultual |
| ... | Altres definicions del tesaurus |

### Carpeta del Projecte

El camp **Carpeta** permet associar un directori local al lloc per organitzar els fitxers del projecte.

| Botó | Funció |
|------|--------|
| **...** | Explora per seleccionar la carpeta |
| **Obre** | Obre la carpeta al gestor de fitxers |

---

## Barra d'Eines DBMS

La barra d'eines DBMS proporciona tots els controls per a la gestió dels registres.

### Indicadors d'Estat

| Indicador | Descripció |
|-----------|------------|
| **DB Info** | Mostra el tipus de base de dades connectada (SQLite/PostgreSQL) |
| **Status** | Estat actual: `Usa` (navegar), `Cerca` (cercar), `Nou Registre` |
| **Ordenació** | Indica si els registres estan ordenats |
| **registre n.** | Número del registre actual |
| **registre tot.** | Total de registres |

### Navegació de Registres

| Botó | Icona | Funció | Drecera |
|------|-------|--------|---------|
| **First rec** | |< | Vés al primer registre | - |
| **Prev rec** | < | Vés al registre anterior | - |
| **Next rec** | > | Vés al registre següent | - |
| **Last rec** | >| | Vés a l'últim registre | - |

### Gestió de Registres

| Botó | Funció | Descripció |
|------|--------|------------|
| **New record** | Crea nou | Prepara el formulari per inserir un nou lloc |
| **Save** | Desa | Desa les modificacions o el nou registre |
| **Delete record** | Elimina | Elimina el registre actual (amb confirmació) |
| **View all records** | Visualitza tots | Mostra tots els registres de la base de dades |

### Cerca i Ordenació

| Botó | Funció | Descripció |
|------|--------|------------|
| **new search** | Nova cerca | Inicia mode de cerca |
| **search !!!** | Executa cerca | Executa la cerca amb els criteris inserits |
| **Order by** | Ordena | Obre panell d'ordenació |

#### Com Fer una Cerca

1. Fer clic a **new search** - l'estat canvia a "Cerca"
2. Emplenar els camps amb els criteris de cerca
3. Fer clic a **search !!!** per executar
4. Els resultats es mostren i es pot navegar entre ells

#### Panell d'Ordenació

Fent clic a **Order by** s'obre un panell per ordenar els registres:

| Opció | Descripció |
|-------|------------|
| **Camp** | Selecciona el camp per a l'ordenació |
| **Ascendent** | Ordre A-Z, 0-9 |
| **Descendent** | Ordre Z-A, 9-0 |

---

## Funcionalitats GIS

La Fitxa de Lloc ofereix diverses funcionalitats d'integració GIS.

### Càrrega de Capes

| Botó | Funció |
|------|--------|
| **GIS viewer** | Carrega totes les capes per inserir geometries |
| **Carrega capa lloc** (icona globus) | Carrega només les capes del lloc actual |
| **Carrega tots els llocs** (icona globus múltiple) | Carrega les capes de tots els llocs |

### Geocoding - Cerca d'Adreça

La funció de geocoding permet localitzar una adreça al mapa.

1. Inserir l'adreça al camp de text
2. Fer clic a **Zoom on**
3. El mapa es centra a la posició trobada

| Camp | Descripció |
|------|------------|
| **Adreça** | Inserir carrer, ciutat, país |
| **Zoom on** | Centra el mapa a l'adreça |

### Mode GIS Actiu

El toggle **Habilita la càrrega de les cerques** activa/desactiva la visualització automàtica dels resultats de cerca al mapa.

- **Actiu**: Les cerques es visualitzen automàticament al mapa
- **Desactiu**: Les cerques no modifiquen la visualització del mapa

### WMS Vincles Arqueològics

El botó WMS carrega la capa de vincles arqueològics del Ministeri de Cultura.

### Base Maps

El botó Base Maps permet carregar mapes base (Google Maps, OpenStreetMap, etc.).

---

## Generació de Fitxes US

Aquesta funcionalitat permet crear automàticament un nombre arbitrari de fitxes US per al lloc actual.

### Paràmetres

| Camp | Descripció | Exemple |
|------|------------|---------|
| **Número Àrea** | Número de l'àrea d'excavació | 1 |
| **Número de fitxa US des d'on partir** | Número inicial US | 1 |
| **Número de fitxes a crear** | Quantes US generar | 100 |
| **Tipus** | US o USM | US |

### Procediment

1. Assegurar-se d'estar al lloc correcte
2. Inserir el número de l'àrea
3. Inserir el número US de partida
4. Inserir quantes fitxes crear
5. Seleccionar el tipus (US o USM)
6. Fer clic a **Genera US**

---

## Eines d'Anàlisi

Les eines d'anàlisi avançada estan ara disponibles com a diàlegs independents, accessibles des del botó **Eines d'Anàlisi** a la barra d'eines de PyArchInit:

- **MoveCost** - Anàlisi de camins de menor cost (vegeu [Tutorial MoveCost](34_movecost.md))
- **GeoArchaeo** - Anàlisi geoestadística per a la recerca arqueològica (vegeu [Tutorial GeoArchaeo](33_geoarchaeo.md))
- **SAM Segmentation** - Segmentació d'imatges amb IA
- **Pottery Tools** - Eines d'anàlisi ceràmica
- **TOPS** - Importació de dades d'estació total
- **Image Search** - Cerca d'imatges

---

## Exportació d'Informes

### Exporta Memòria d'Excavació

El botó **Exporta** genera un PDF amb la memòria d'excavació per al lloc actual.

**Nota**: Aquesta funció és en versió de desenvolupament i pot contenir errors.

L'informe inclou:
- Dades identificatives del lloc
- Llistat de les US
- Seqüència estratigràfica
- Matriu de Harris (si disponible)

---

## Flux de Treball Operatiu

### Crear un Nou Lloc

#### Pas 1: Obrir la Fitxa de Lloc

#### Pas 2: Fer clic a "New record"
L'estat canvia a "Nou Registre" i els camps es buiden.

#### Pas 3: Emplenar les Dades Obligatòries
Inserir almenys el nom del lloc (camp obligatori).

#### Pas 4: Emplenar les Dades Geogràfiques
Inserir nació, regió, província, municipi.

#### Pas 5: Seleccionar la Definició
Escollir la tipologia del lloc del tesaurus.

#### Pas 6: Afegir Descripció
Emplenar el camp descripció amb informació detallada.

#### Pas 7: Desar
Fer clic a **Save** per desar el nou lloc.

#### Pas 8: Verificar
El lloc ha estat creat, l'estat torna a "Usa".

### Modificar un Lloc Existent

1. Navegar al lloc a modificar
2. Modificar els camps desitjats
3. Fer clic a **Save**
4. Confirmar el desament de les modificacions

### Eliminar un Lloc

**Atenció**: L'eliminació d'un lloc NO elimina automàticament les US, estructures i troballes associades.

1. Navegar al lloc a eliminar
2. Fer clic a **Delete record**
3. Confirmar l'eliminació

---

## Pestanya Ajuda

La pestanya Ajuda proporciona accés ràpid a la documentació.

| Recurs | Enllaç |
|--------|--------|
| Tutorials en Vídeo | YouTube |
| Documentació | pyarchinit.github.io |
| Comunitat | Facebook UnaQuantum |

---

## Gestió de Concurrència (PostgreSQL)

Quan s'usa PostgreSQL en entorn multiusuari, el sistema gestiona automàticament els conflictes de modificació:

- **Indicador de bloqueig**: Mostra si el registre està en modificació per un altre usuari
- **Control de versió**: Detecta modificacions concurrents
- **Resolució de conflictes**: Permet escollir quina versió mantenir

---

## Resolució de Problemes

### El lloc no es desa
- Verificar que el camp "Lloc" estigui emplenat
- Verificar que el nom no existeixi ja a la base de dades

### Les capes GIS no es carreguen
- Verificar la connexió a la base de dades
- Verificar que existeixin geometries associades al lloc

### Error en el geocoding
- Verificar la connexió a internet
- Comprovar que l'adreça estigui escrita correctament

### Eines d'anàlisi
- Per a problemes amb MoveCost, GeoArchaeo i altres eines d'anàlisi, consulteu els tutorials dedicats corresponents.

---

## Notes Tècniques

- **Taula de base de dades**: `site_table`
- **Camps de la base de dades**: sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path
- **Capes GIS associades**: PYSITO_POLYGON, PYSITO_POINT
- **Tesaurus**: tipologia_sigla = '1.1'

---

*Documentació PyArchInit - Fitxa de Lloc*
*Versió: 4.9.x*
*Última actualització: Gener 2026*
