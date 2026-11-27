# PyArchInit - StratiGraph: Panell de Sincronitzacio

> El tauler i la finestra de la sala segueixen la llengua de la interficie de QGIS; aqui els botons es citen tal com apareixen en catala.

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

> **Des de la versió 5.18.1 el tauler només mostra «Envia el jaciment a una sala…» i el registre.** Estat, connexió, cua, «Exporta el paquet», «Sincronitza ara» i «Cua…» estan amagats: pertanyen a la sincronització per paquets (bundle) de la Fase 2, mentre que el node StratiGraph intercanvia **sales i operacions**, no paquets. Les seccions següents, fins a «Enviar un jaciment a una sala StratiGraph», descriuen aquest mecanisme: tornarà, o es traurà, quan es decideixi la sincronització entre nodes.

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
| **Exporta el paquet** | Crea un bundle des de les vostres dades locals, el valida i l'afegeix a la cua de sincronitzacio |
| **Sincronitza ara** | Forca un intent immediat de sincronitzacio (nomes disponible quan esta online) |
| **Cua...** | Obre el dialeg de gestio de cua mostrant totes les entrades |
| **Envia el jaciment a una sala...** | Inicia sessio en un node StratiGraph i porta un jaciment a una sala (vegeu mes avall) |

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
3. Feu clic al boto **Exporta el paquet**
4. El sistema realitza automaticament tres operacions:
   - **Exportacio**: Les dades locals s'empaqueten en un fitxer bundle
   - **Validacio**: El bundle es comprova per completesa i integritat de dades
   - **Encuament**: El bundle validat s'afegeix a la cua de sincronitzacio
5. Observeu l'**indicador d'estat** que passa per: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. El **registre d'activitat** enregistra cada pas amb una marca de temps

### Que conte un bundle

Un bundle conte totes les entitats arqueologiques que tenen UUID (vegeu el Tutorial 31 per a detalls sobre UUID). Cada entitat s'identifica pel seu `entity_uuid`, assegurant que el mateix registre sempre sigui reconegut al servidor.

<!-- IMAGE: Boto Exporta el paquet i transicio d'estat -->
> **Fig. 4**: Clic a "Exporta el paquet" i observacio dels canvis d'estat al panell

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
2. Feu clic al boto **Sincronitza ara**
3. El sistema intenta immediatament pujar tots els bundles pendents

El boto **Sincronitza ara** nomes es efectiu quan el sistema esta online.

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

<!-- IMAGE: Boto Sincronitza ara i indicador de connexio -->
> **Fig. 5**: El boto "Sincronitza ara" i l'indicador d'estat de connexio

---

## Gestio de la cua

El boto **Cua...** obre un dialeg detallat on podeu inspeccionar tots els bundles a la cua de sincronitzacio.

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

Des de la versio **5.14.0-alpha** el boto **Envia el jaciment a una sala...** porta un jaciment a una *sala* d'un node StratiGraph (StratiGraph Server). El graf del jaciment es converteix en el contingut de la sala, on EMStudio, EM Tools i les altres eines del projecte el veuen i hi treballen.

![Panell StratiGraph Sync](images/32_stratigraph_sync/06_sync_panel_send_button.png)

> **Fig. 7**: El panell StratiGraph Sync amb el boto **Envia el jaciment a una sala...**

### Procediment pas a pas

1. Al panell **StratiGraph Sync**, premeu **Envia el jaciment a una sala...**
2. **Node**: l'adreca del node, per exemple `https://node.example.org/em`. Es recorda entre sessions.
3. **Jaciment**: trieu el jaciment. **Id de la sala** i **Títol de la sala** s'omplen amb el nom del jaciment i es poden canviar; l'id de la sala es una sola paraula, sense espais.
4. Premeu **Inicia sessió...**: la pagina d'acces del node s'obre al navegador. Accediu amb el vostre compte i torneu a QGIS: la linia **Identitat** mostra el nom i si podeu crear sales. Si el node té un client Keycloak dedicat a pyArchInit, el seu nom va al paràmetre de QGIS `pyArchInit/stratigraph/client_id`; si no, s'utilitza el client que indica el node.
5. Opcional: **Només pla** mostra el que s'enviaria sense escriure res al node.
6. Premeu **Envia el jaciment**: el registre indica els nodes i les arestes exportats i el resultat.

![Finestra Envia el jaciment a una sala](images/32_stratigraph_sync/07_send_site_dialog.png)

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

1. **Compara amb la sala** compara el jaciment amb la sala en els dos sentits, sense escriure res: que te de nou la sala per a pyArchInit (unitats noves, definicions canviades, relacions) i que hi afegeix pyArchInit.
2. **Envia els canvis** envia a la sala la feina feta aquí: unitats i relacions noves, camps canviats aquí, relacions tretes aquí. El que només ha canviat a la sala no es toca; un camp canviat a les dues bandes és un conflicte i només es mostra (vegeu «Sincronització amb memòria»).
3. **Porta de la sala** porta la sala a les fitxes de pyArchInit (UE, definicions, perioditzacio, relacions), reconeixent cada fitxa pel seu identificador. Si el pull tragues relacions locals que la sala no coneix, la finestra les enumera i demana confirmacio.

Amb **Porta de la sala** tambe es pot reconstruir un jaciment en una base de dades que no el te: les unitats tornen amb numero, tipus, definicions i perioditzacio. Les unitats de continuitat (CON) no viatgen: pyArchInit les regenera amb **Genera continuita**.

La sala rep la fitxa UE sencera, no nomes els camps del graf: descripcio, interpretacio, color, consistencia, cotes, mesures, sondeig, ambient, quadre, sector, els camps de parament (USM). Una fitxa reconstruida des d'una sala es igual a l'original; les relacions nomes canvien en l'escriptura (amb area i jaciment). Una sala enviada amb una versio anterior de pyArchInit nomes te els camps del graf: la comparacio mostra molts camps diferents; n'hi ha prou amb un nou **Envia el jaciment** per completar-la.

Tot aixo val tant per a SQLite com per a PostgreSQL. Per reconstruir un jaciment n'hi ha prou amb una base de dades de pyArchInit creada i buida, oberta a pyArchInit: **Porta de la sala** l'omple (jaciment, fitxes, perioditzacio, relacions, mitjans). Les relacions tenen sempre quatre elements: tipus, UE, area, jaciment.

![Comparacio amb la sala](images/32_stratigraph_sync/08_compare_with_room.png)

> **Fig. 9**: La comparacio amb una sala on tambe s'ha treballat a EMStudio: una UE nova i una definicio revisada a la sala, una UE nova de pyArchInit per enviar

### Fotos i mitjans a la sala

Les fotos, els videos, els models 3D i els documents vinculats a les fitxes UE viatgen amb el jaciment, en tots dos sentits. Les ortofotos i els altres raster en queden fora: son capes de QGIS, no mitjans de pyArchInit.

- **Envia el jaciment** i **Envia els canvis** pugen cada fitxer al diposit de la sala una sola vegada: un fitxer que la sala ja te (mateix contingut) no es torna a enviar. Si l'original ja no es al disc s'utilitza la copia de la carpeta Resize.
- **Porta de la sala** descarrega els mitjans nous a la carpeta `stratigraph_media/<sala>` del home de pyArchInit, crea miniatura i copia com quan es carrega un fitxer des de la fitxa i els vincula a la seva UE, amb descripcio i etiquetes. Un mitja que la base de dades ja te (reconegut pel seu identificador) no es torna a descarregar: nomes se'n comprova el vincle.
- Els mitjans de troballes, ceramica, tombes i estructures de moment queden en local: la finestra els compta.

![Una foto nova enviada a la sala](images/32_stratigraph_sync/09_room_media.png)

> **Fig. 10**: Una foto afegida a la UE 3 despres d'enviar el jaciment: la comparacio la troba i Envia els canvis puja el fitxer i el seu vincle

### Sincronització amb memòria

Després del primer **Porta de la sala** (o del primer **Envia el jaciment**) pyArchInit recorda la sala tal com era en aquell moment: la *base* comuna, desada a la carpeta `stratigraph_rooms` del home de pyArchInit, una per base de dades, jaciment i sala. A partir d'aleshores:

- la comparació llegeix de la sala **només les novetats** des de la darrera sincronització, no tot el document;
- cada diferència té un autor: **canviat aquí** (s'envia), **canviat a la sala** (el porta «Porta»), **canviat a les dues bandes** (conflicte, mostrat amb els dos valors), **tret a la sala** (es treu també aquí), **tret aquí** (s'envia);
- **Porta de la sala** mai no sobreescriu en silenci feina encara no enviada: si hi ha canvis locals, conflictes, relacions tretes aquí, la finestra els llista i aconsella enviar-los abans. En un conflicte confirmat guanya el valor de la sala.
- els camps que pyArchInit **calcula** (ordre estratigràfic, codi de període, datació) no són mai canvis ni conflictes: al final del portar pyArchInit els recalcula sol, com els botons de la fitxa UE;
- **les relacions són un conjunt**: les afegides aquí i encara no enviades es mantenen després del portar, juntament amb les que altres han afegit a la sala;
- si confirmes un portar que substitueix valors locals, aquests valors **no es perden**: **Restaura els valors substituïts** els torna a posar, i tornen a ser canvis per enviar.

Les unitats que el portar deixa fora a propòsit (les continuïtats CON generades i els seus mitjans) queden a la sala i no compten com a eliminacions. Funciona igual amb SQLite i PostgreSQL.

![Comparació a tres vies](images/32_stratigraph_sync/10_three_way_compare.png)

> **Fig. 11**: La comparació després d'una sincronització: un camp canviat aquí per enviar, un canviat a la sala per portar, un conflicte en el mateix camp

### Geometries: jaciment, sondejos, àrees i retalls

Amb el jaciment viatgen també els dibuixos de les capes SIG de pyArchInit, com a empremtes en el seu propi sistema de referència: el polígon del **jaciment** (`pyarchinit_siti_polygonal`), els **sondejos** (`pyarchinit_sondaggi`), **àrees i sectors** (`pyarchinit_ripartizioni_spaziali`) i els **retalls**, és a dir les UE negatives (`pyunitastratigrafiche`). Surten de SQLite i de PostGIS.

**Porta de la sala** els torna a escriure a les capes, SpatiaLite o PostGIS, en el sistema de referència de la capa: un element que falta s'afegeix, un d'igual no es toca, i un element **dibuixat aquí d'una altra manera es queda com està** i se senyala: el portar mai no sobreescriu un dibuix local.

Ortofotos i ràsters es queden a QGIS.

### Plantes d'excavació: els polígons de les UE positives

Els polígons de les UE positives no són la geometria de la unitat (per a l'Extended Matrix és el model 3D) sinó la seva **documentació**: viatgen com a **plantes d'excavació**, en la forma acordada amb l'equip de s3dgraphy.

- El jaciment té **un sol document**, «Piante di scavo · *jaciment*», que roman obert mentre l'excavació continua.
- Cada **planta** és el conjunt de polígons dibuixats per a una UE en una data, a la capa de les UE o a la de les USM. A la sala és un model de representació documental (RMDoc) del document, vinculat a la seva UE.
- La geometria és un **fitxer GeoJSON** amb el seu sistema de referència, un per planta, pujat al magatzem de la sala com les fotos. El graf només porta el node, els seus vincles i l'adreça del fitxer.

**Envia el jaciment** envia les plantes amb les fitxes. **Porta de la sala** baixa les que falten aquí i les escriu a les capes `pyunitastratigrafiche` i `pyunitastratigrafiche_usm`, amb les seves columnes (tipus, dibuixant, data…). Una planta que ja existeix aquí, igual o diferent, no es toca mai: la diferent s'assenyala al registre. Un polígon dibuixat sobre una UE que les fitxes no tenen es queda fora, i el registre ho diu.

Les plantes són documentació, no fitxes: no apareixen mai entre els canvis per enviar. Una planta nova dibuixada aquí arriba a la sala amb un nou **Envia el jaciment**.

### Problemes frequents

| Missatge | Que cal fer |
|----------|-------------|
| `401` o acces caducat | La sessio es renova sola mentre es treballa; si ha caducat del tot (moltes hores sense fer-la servir) premeu de nou **Inicia sessió...** |
| ⚠ «El número … és de diverses unitats» | A la mateixa àrea dues unitats tenen el mateix número i tipus diferent: les relacions indiquen la unitat només amb número, àrea i jaciment, així que a la sala arriben a totes dues. Renumerar-ne una abans d'enviar |
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

Si. Cada vegada que feu clic a "Exporta el paquet", es crea un nou bundle i s'afegeix a la cua. Es poden encuar multiples bundles i es pujaran sequencialment.

### Com se si les meves dades s'han sincronitzat?

Comproveu l'indicador d'**ultima sincronitzacio** al panell per al resultat mes recent. Tambe podeu obrir el dialeg **Cua...** per veure l'estat de cada bundle individual.

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
