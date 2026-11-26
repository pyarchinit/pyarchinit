# PyArchInit - StratiGraph: Panell de Sincronitzacio

## Index
1. [Introduccio](#introduccio)
2. [Acces al panell](#acces-al-panell)
3. [Comprensio de la interficie](#comprensio-de-la-interficie)
4. [Exportacio de bundles](#exportacio-de-bundles)
5. [Sincronitzacio](#sincronitzacio)
6. [Gestio de la cua](#gestio-de-la-cua)
7. [Enviar un jaciment a una sala StratiGraph](#enviar-un-jaciment-a-una-sala-stratigraph)
8. [Configuracio](#configuracio)
9. [Resolucio de problemes](#resolucio-de-problemes)
10. [Preguntes Frequents](#preguntes-frequents)

---

## Introduccio

A partir de la versio **5.0.2-alpha**, PyArchInit inclou un panell **StratiGraph Sync** que permet la sincronitzacio offline-first de dades amb el Knowledge Graph d'StratiGraph. Aquest panell forma part del projecte europeu **StratiGraph** (Horizon Europe) i implementa el flux de treball offline-first: treballeu localment sense internet, exporteu bundles quan estigueu a punt, i el sistema es sincronitza automaticament quan es restableix la connectivitat.

<!-- VIDEO: Introduccio a StratiGraph Sync -->
> **Video Tutorial**: [Inserir enllac de video introduccio StratiGraph Sync]

### Visio general del flux de treball

```
1. Treball offline      2. Exportar Bundle     3. Sincronitzacio
   (OFFLINE_EDITING)       (LOCAL_EXPORT)        (QUEUED_FOR_SYNC)
        |                      |                      |
   Entrada de dades      Exportar + Validar     Pujar quan online
   normal a              + Encuar               amb reintent
   PyArchInit                                   automatic
```

---

## Acces al panell

El panell StratiGraph Sync esta ocult per defecte i es pot activar mitjancant un boto a la barra d'eines.

### Des de la barra d'eines

1. Cerqueu el boto **StratiGraph Sync** a la barra d'eines de PyArchInit -- te una icona verda amb fletxes de sincronitzacio i la lletra "S"
2. Feu clic al boto per **mostrar** el panell (es un boto de commutacio)
3. Feu clic de nou per **amagar** el panell

El panell apareix com un **dock widget a l'esquerra** a la interficie de QGIS. Podeu arrossegar-lo i reposicionar-lo com qualsevol altre panell de QGIS.

<!-- IMAGE: Boto de la barra d'eines per a StratiGraph Sync -->
> **Fig. 1**: El boto StratiGraph Sync a la barra d'eines (icona verda amb fletxes de sincronitzacio i "S")

<!-- IMAGE: Panell ancorat al costat esquerre de QGIS -->
> **Fig. 2**: El panell StratiGraph Sync ancorat al costat esquerre de la finestra QGIS

---

## Comprensio de la interficie

El panell StratiGraph Sync es divideix en diverses seccions, de dalt a baix.

### Indicador d'estat

L'**indicador d'estat** a la part superior del panell mostra l'estat actual de sincronitzacio de les vostres dades. Els estats possibles son:

| Estat | Icona | Descripcio |
|-------|-------|------------|
| **OFFLINE_EDITING** | Llapis | Esteu treballant localment, editant dades normalment |
| **LOCAL_EXPORT** | Paquet | S'esta exportant un bundle des de les dades locals |
| **LOCAL_VALIDATION** | Marca de verificacio | El bundle exportat s'esta validant |
| **QUEUED_FOR_SYNC** | Rellotge | El bundle ha estat validat i espera per ser pujat |
| **SYNC_SUCCESS** | Cercle verd | L'ultima sincronitzacio s'ha completat amb exit |
| **SYNC_FAILED** | Cercle vermell | L'ultim intent de sincronitzacio ha fallat |

### Indicador de connexio

Sota l'indicador d'estat, l'**indicador de connexio** mostra si el sistema pot arribar al servidor StratiGraph:

| Estat | Significat |
|-------|------------|
| **Online** | L'endpoint de health check es accessible; la sincronitzacio automatica esta activa |
| **Offline** | L'endpoint de health check no es accessible; els bundles s'encuaran |

El sistema comprova automaticament la connectivitat cada **30 segons** (configurable).

### Comptador de cua

El **comptador de cua** mostra dos numeros:

- **Bundles pendents**: Nombre de bundles esperant per ser pujats
- **Bundles fallits**: Nombre de bundles la pujada dels quals ha fallat (es reintentaran automaticament)

### Ultima sincronitzacio

Mostra la **marca de temps** i el **resultat** (exit o fallada) de l'ultim intent de sincronitzacio.

### Botons d'accio

| Boto | Accio |
|------|-------|
| **Export Bundle** | Crea un bundle des de les vostres dades locals, el valida i l'afegeix a la cua de sincronitzacio |
| **Sync Now** | Forca un intent immediat de sincronitzacio (nomes disponible quan esta online) |
| **Queue...** | Obre el dialeg de gestio de cua mostrant totes les entrades |
| **Send site to a room...** | Inicia sessio en un node StratiGraph i porta un jaciment a una sala (vegeu mes avall) |

### Registre d'activitat

A la part inferior del panell, un **registre d'activitat** desplacable mostra entrades amb marca de temps de l'activitat recent, incloent canvis d'estat, exportacions, validacions i intents de sincronitzacio.

<!-- IMAGE: Panell complet amb totes les seccions anotades -->
> **Fig. 3**: El panell StratiGraph Sync complet amb totes les seccions etiquetades

---

## Exportacio de bundles

L'exportacio d'un bundle empaqueta les vostres dades arqueologiques locals en un format estructurat llest per pujar al Knowledge Graph d'StratiGraph.

### Procediment pas a pas

1. Assegureu-vos d'haver desat tot el treball actual a PyArchInit
2. Obriu el panell StratiGraph Sync (si no es ja visible)
3. Feu clic al boto **Export Bundle**
4. El sistema realitza automaticament tres operacions:
   - **Exportacio**: Les dades locals s'empaqueten en un fitxer bundle
   - **Validacio**: El bundle es comprova per completesa i integritat de dades
   - **Encuament**: El bundle validat s'afegeix a la cua de sincronitzacio
5. Observeu l'**indicador d'estat** que passa per: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. El **registre d'activitat** enregistra cada pas amb una marca de temps

### Que conte un bundle

Un bundle conte totes les entitats arqueologiques que tenen UUID (vegeu el Tutorial 31 per a detalls sobre UUID). Cada entitat s'identifica pel seu `entity_uuid`, assegurant que el mateix registre sempre sigui reconegut al servidor.

<!-- IMAGE: Boto Export Bundle i transicio d'estat -->
> **Fig. 4**: Clic a "Export Bundle" i observacio dels canvis d'estat al panell

---

## Sincronitzacio

### Sincronitzacio automatica

Quan el sistema detecta que esteu **online** (el health check te exit), puja automaticament tots els bundles pendents de la cua. No es requereix cap intervencio manual.

El proces de sincronitzacio automatica:

1. La comprovacio de connectivitat te exit (l'endpoint de health check respon)
2. L'indicador de connexio canvia a **Online**
3. Els bundles pendents a la cua es pugen un per un
4. Els bundles pujats amb exit es marquen com a `SYNC_SUCCESS`
5. La marca de temps i el resultat de l'**ultima sincronitzacio** s'actualitzen

### Sincronitzacio manual

Si voleu forcar un intent immediat de sincronitzacio:

1. Assegureu-vos que l'indicador de connexio mostri **Online**
2. Feu clic al boto **Sync Now**
3. El sistema intenta immediatament pujar tots els bundles pendents

El boto **Sync Now** nomes es efectiu quan el sistema esta online.

### Reintent automatic amb backoff exponencial

Si una pujada falla, el sistema **no** es rendeix. En lloc d'aixo, reintenta automaticament amb retards creixents:

| Intent | Retard |
|--------|--------|
| 1r reintent | 30 segons |
| 2n reintent | 60 segons |
| 3r reintent | 120 segons |
| 4t reintent | 5 minuts |
| 5e reintent | 15 minuts |

Aixo evita sobrecarregar el servidor quan no esta disponible temporalment, assegurant alhora el lliurament final.

<!-- IMAGE: Boto Sync Now i indicador de connexio -->
> **Fig. 5**: El boto "Sync Now" i l'indicador d'estat de connexio

---

## Gestio de la cua

El boto **Queue...** obre un dialeg detallat on podeu inspeccionar tots els bundles a la cua de sincronitzacio.

### Columnes del dialeg de cua

| Columna | Descripcio |
|---------|------------|
| **ID** | Identificador unic de l'entrada a la cua |
| **Status** | Estat actual de l'entrada (pending, syncing, success, failed) |
| **Attempts** | Nombre d'intents de pujada realitzats fins ara |
| **Created** | Marca de temps de quan el bundle va ser afegit a la cua |
| **Last Error** | Missatge d'error de l'ultim intent fallit (buit si no hi ha error) |
| **Bundle path** | Ruta del fitxer bundle al sistema de fitxers |

### Interpretar les entrades de la cua

- Les entrades **Pending** estan esperant per ser pujades
- Les entrades **Success** han estat pujades i confirmades pel servidor
- Les entrades **Failed** es reintentaran automaticament; consulteu la columna **Last Error** per a detalls
- El recompte d'**Attempts** ajuda a entendre quantes vegades el sistema ha intentat pujar un bundle particular

### Emmagatzematge de la cua

La base de dades de la cua s'emmagatzema com un fitxer SQLite a:

```
$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite
```

Aquest fitxer persisteix entre sessions de QGIS, de manera que els bundles pendents no es perden si tanqueu QGIS.

<!-- IMAGE: Dialeg de cua mostrant diverses entrades -->
> **Fig. 6**: El dialeg de gestio de cua amb entrades de bundles

---

## Enviar un jaciment a una sala StratiGraph

Des de la versio **5.14.0-alpha** el boto **Send site to a room...** porta un jaciment a una *sala* d'un node StratiGraph (StratiGraph Server). El graf del jaciment es converteix en el contingut de la sala, on EMStudio, EM Tools i les altres eines del projecte el veuen i hi treballen.

![Panell StratiGraph Sync](images/32_stratigraph_sync/06_sync_panel_send_button.png)

> **Fig. 7**: El panell StratiGraph Sync amb el boto **Send site to a room...**

### Procediment pas a pas

1. Al panell **StratiGraph Sync**, premeu **Send site to a room...**
2. **Node**: l'adreca del node, per exemple `https://node.example.org/em`. Es recorda entre sessions.
3. **Site**: trieu el jaciment. **Room id** i **Room title** s'omplen amb el nom del jaciment i es poden canviar; l'id de la sala es una sola paraula, sense espais.
4. Premeu **Sign in...**: la pagina d'acces del node s'obre al navegador. Accediu amb el vostre compte i torneu a QGIS: la linia **Identity** mostra el nom i si podeu crear sales.
5. Opcional: **Plan only** mostra el que s'enviaria sense escriure res al node.
6. Premeu **Send site**: el registre indica els nodes i les arestes exportats i el resultat.

![Finestra Send site to a room](images/32_stratigraph_sync/07_send_site_dialog.png)

> **Fig. 8**: La finestra despres de l'acces i l'enviament del jaciment d'exemple a un node de desenvolupament: 745 operacions aplicades, 0 rebutjades, la base de dades conservada com a referencia

### Que s'envia

- El graf del jaciment sencer, com un sol graf encara que el jaciment tingui diversos sondeigs: aixi les relacions entre unitats de sondeigs diferents viatgen amb la resta.
- Els fitxers citats pel graf es pugen una sola vegada. Tornar a enviar el mateix jaciment no duplica res.
- **Els fitxers de base de dades no es pugen mai** (sqlite, spatialite, gpkg): a la sala nomes en queda una referencia. Els altres jaciments de la base de dades es queden al vostre ordinador.
- La contrasenya no passa mai per pyArchInit: nomes s'escriu a la pagina del node. El token d'acces queda en memoria i es perd en tancar la finestra.

### Des de la linia d'ordres

El mateix enviament sense QGIS (sense `--dry-run` escriu de debo; sense `--token` obre el navegador per accedir):

```bash
python scripts/stratigraph_send_site.py --db ~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite \
    --site "Scavo archeologico" --node https://nodo.example.org/em --room scavo-2026 --dry-run
```

### Treballar amb una sala que ja te dades

Quan a la sala hi treballen tambe altres (EMStudio, StratiField, EM Tools), despres d'accedir:

1. **Compare with room** compara el jaciment amb la sala en els dos sentits, sense escriure res: que te de nou la sala per a pyArchInit (unitats noves, definicions canviades, relacions) i que hi afegeix pyArchInit.
2. **Send additions** envia nomes les addicions del jaciment: unitats i relacions noves. Un camp diferent es mostra pero no s'envia, perque a la sala pot ser la modificacio mes recent d'un company; el que nomes es a la sala no es toca mai.
3. **Pull from room** porta la sala a les fitxes de pyArchInit (UE, definicions, perioditzacio, relacions), reconeixent cada fitxa pel seu identificador. Si el pull tragues relacions locals que la sala no coneix, la finestra les enumera i demana confirmacio.

Amb **Pull from room** tambe es pot reconstruir un jaciment en una base de dades que no el te: les unitats tornen amb numero, tipus, definicions i perioditzacio. Les unitats de continuitat (CON) no viatgen: pyArchInit les regenera amb **Genera continuita**.

![Comparacio amb la sala](images/32_stratigraph_sync/08_compare_with_room.png)

> **Fig. 9**: La comparacio amb una sala on tambe s'ha treballat a EMStudio: una UE nova i una definicio revisada a la sala, una UE nova de pyArchInit per enviar

### Fotos i mitjans a la sala

Les fotos, els videos, els models 3D i els documents vinculats a les fitxes UE viatgen amb el jaciment, en tots dos sentits. Les ortofotos i els altres raster en queden fora: son capes de QGIS, no mitjans de pyArchInit.

- **Send site** i **Send additions** pugen cada fitxer al diposit de la sala una sola vegada: un fitxer que la sala ja te (mateix contingut) no es torna a enviar. Si l'original ja no es al disc s'utilitza la copia de la carpeta Resize.
- **Pull from room** descarrega els mitjans nous a la carpeta `stratigraph_media/<sala>` del home de pyArchInit, crea miniatura i copia com quan es carrega un fitxer des de la fitxa i els vincula a la seva UE, amb descripcio i etiquetes. Un mitja que la base de dades ja te (reconegut pel seu identificador) no es torna a descarregar: nomes se'n comprova el vincle.
- Els mitjans de troballes, ceramica, tombes i estructures de moment queden en local: la finestra els compta.

![Una foto nova enviada a la sala](images/32_stratigraph_sync/09_room_media.png)

> **Fig. 10**: Una foto afegida a la UE 3 despres d'enviar el jaciment: la comparacio la troba i Send additions puja el fitxer i el seu vincle

### Problemes frequents

| Missatge | Que cal fer |
|----------|-------------|
| `401` o acces caducat | Premeu de nou **Sign in...**: el token dura pocs minuts |
| `403` / *may create rooms: False* | El compte no te cap rol a la sala o no pot crear sales: pregunteu a l'administrador del node |
| `CERTIFICATE_VERIFY_FAILED` | El node fa servir un certificat local (node de desenvolupament o de camp): instal·leu-ne la CA a l'ordinador, o feu servir `--ca-file` a la linia d'ordres |
| `409 ... already declared` | La sala existeix i pertany a un altre usuari: trieu un altre id |

---

## Configuracio

### URL de Health Check

El sistema utilitza una URL de health check per determinar la connectivitat amb el servidor StratiGraph. Podeu configurar-la a les opcions de QGIS:

| Configuracio | Clau | Per defecte |
|-------------|------|-------------|
| URL Health check | `pyArchInit/stratigraph/health_check_url` | `http://localhost:8080/health` |

Per canviar la URL de health check:

1. Obriu **QGIS** -> **Configuracio** -> **Opcions** (o utilitzeu la consola Python de QGIS)
2. Navegueu a la configuracio de PyArchInit o establiu mitjancant:

```python
from qgis.core import QgsSettings
s = QgsSettings()
s.setValue("pyArchInit/stratigraph/health_check_url", "https://el-vostre-servidor.exemple.cat/health")
```

### Interval de comprovacio

L'interval de comprovacio de connectivitat per defecte es de **30 segons**. Aixo tambe es pot configurar a traves de QgsSettings.

---

## Resolucio de problemes

### El panell no apareix

- Assegureu-vos d'utilitzar PyArchInit versio **5.0.2-alpha** o posterior
- Comproveu que el boto StratiGraph Sync sigui visible a la barra d'eines
- Proveu de desactivar i reactivar el boto
- Comproveu **Vista** -> **Panells** a QGIS per veure si el dock widget esta llistat

### L'indicador de connexio mostra sempre "Offline"

- Comproveu que el servidor StratiGraph s'estigui executant i sigui accessible
- Comproveu la URL de health check a la configuracio (per defecte: `http://localhost:8080/health`)
- Proveu la URL manualment al navegador o amb `curl`:

```bash
curl http://localhost:8080/health
```

- Si el servidor es en una altra maquina, assegureu-vos que no hi hagi regles de tallafocs bloquejant la connexio

### L'exportacio del bundle falla

- Assegureu-vos que la base de dades estigui connectada i sigui accessible
- Comproveu que els vostres registres tinguin UUID valids (Tutorial 31)
- Consulteu el registre d'activitat per a missatges d'error especifics
- Assegureu-vos que hi hagi prou espai de disc per al fitxer bundle

### La sincronitzacio falla repetidament

- Comproveu la columna **Last Error** al dialeg de cua per a detalls
- Causes comunes:
  - El servidor no esta disponible temporalment (el sistema reintentara automaticament)
  - Problemes de connectivitat de xarxa
  - El servidor ha rebutjat el bundle (comproveu els registres del servidor)
- Si un bundle falla consistentment despres de molts intents, considereu reexportar-lo

### Problemes amb la base de dades de la cua

- La base de dades de la cua es a `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite`
- Si esta corrompuda, podeu eliminar-la de forma segura -- els bundles pendents es perdran, pero es poden reexportar
- Feu una copia de seguretat d'aquest fitxer si necessiteu preservar l'estat de la cua

---

## Preguntes Frequents

### Necessito internet per utilitzar PyArchInit?

**No.** PyArchInit funciona completament sense connexio. El panell StratiGraph Sync nomes gestiona la sincronitzacio amb el servidor StratiGraph. Podeu treballar completament offline i exportar/sincronitzar quan estigueu a punt.

### Que passa si tanco QGIS amb bundles pendents?

Els bundles pendents es desen a la base de dades de la cua i estaran disponibles en reiniciar QGIS. El sistema reprendra la sincronitzacio automaticament quan es restableixi la connectivitat.

### Puc exportar multiples bundles?

Si. Cada vegada que feu clic a "Export Bundle", es crea un nou bundle i s'afegeix a la cua. Es poden encuar multiples bundles i es pujaran sequencialment.

### Com se si les meves dades s'han sincronitzat?

Comproveu l'indicador d'**ultima sincronitzacio** al panell per al resultat mes recent. Tambe podeu obrir el dialeg **Queue...** per veure l'estat de cada bundle individual.

### StratiGraph Sync funciona tant amb PostgreSQL com amb SQLite?

Si. El sistema de sincronitzacio funciona amb tots dos backends de base de dades compatibles amb PyArchInit. Els bundles s'exporten en un format independent de la base de dades.

### Quina es la relacio entre UUID i sincronitzacio?

Els UUID (Tutorial 31) proporcionen els identificadors estables que fan possible la sincronitzacio. Cada entitat en un bundle s'identifica pel seu UUID, permetent al servidor associar, crear o actualitzar registres correctament.

---

*Documentacio PyArchInit - StratiGraph Sync*
*Versio: 5.0.2-alpha*
*Ultima actualitzacio: Febrer 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../animations/stratigraph_sync_animation.html)
