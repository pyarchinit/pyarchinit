# PyArchInit - Guia de Configuració

## Índex
1. [Introducció](#introducció)
2. [Accés a la Configuració](#accés-a-la-configuració)
3. [Pestanya Paràmetres de Connexió](#pestanya-paràmetres-de-connexió)
4. [Pestanya Instal·lació BD](#pestanya-installació-bd)
5. [Pestanya Eines d'Importació](#pestanya-eines-dimportació)
6. [Pestanya Graphviz](#pestanya-graphviz)
7. [Pestanya PostgreSQL](#pestanya-postgresql)
8. [Pestanya Ajuda](#pestanya-ajuda)
9. [Pestanya FTP a Lizmap](#pestanya-ftp-a-lizmap)
10. [Espai de treball Paradata (només PostgreSQL)](#espai-de-treball-paradata-només-postgresql)

---

## Introducció

La finestra de configuració de PyArchInit permet establir tots els paràmetres necessaris per al correcte funcionament del connector. Abans de començar a documentar una excavació arqueològica, cal configurar correctament la connexió a la base de dades i les rutes dels recursos.

> **Tutorial en Vídeo**: [Inserir enllaç vídeo introducció configuració]

---

## Accés a la Configuració

Per accedir a la configuració:
1. Obrir QGIS
2. Menú **PyArchInit** → **Config**

O des de la barra d'eines de PyArchInit, fer clic a la icona **Configuració**.

---

## Pestanya Paràmetres de Connexió

Aquesta és la pestanya principal per configurar la connexió a la base de dades.

### Secció DB Settings

| Camp | Descripció |
|------|------------|
| **Database** | Seleccionar el tipus de base de dades: `sqlite` (local) o `postgres` (servidor) |
| **Host** | Adreça del servidor PostgreSQL (ex. `localhost` o IP del servidor) |
| **DBname** | Nom de la base de dades (ex. `pyarchinit`) |
| **Port** | Port de connexió (per defecte: `5432` per PostgreSQL) |
| **User** | Nom d'usuari per a la connexió |
| **Password** | Contrasenya de l'usuari |
| **SSL Mode** | Mode SSL per PostgreSQL: `allow`, `prefer`, `require`, `disable` |

#### Elecció de la Base de Dades

**SQLite/Spatialite** (Recomanat per a ús individual):
- Base de dades local, sense servidor requerit
- Ideal per a projectes individuals o de petites dimensions
- El fitxer `.sqlite` es desa a la carpeta `pyarchinit_DB_folder`

**PostgreSQL/PostGIS** (Recomanat per a equips):
- Base de dades en servidor, accés multiusuari
- Necessari tenir PostgreSQL amb extensió PostGIS instal·lat
- Suporta gestió d'usuaris i permisos
- Ideal per a projectes grans amb múltiples operadors

### Secció Path Settings

| Camp | Descripció | Botó |
|------|------------|------|
| **Thumbnail path** | Ruta per desar les miniatures de les imatges | `...` per explorar |
| **Image resize** | Ruta per a les imatges redimensionades | `...` per explorar |
| **Logo path** | Ruta del logotip personalitzat per als informes | `...` per explorar |

#### Rutes Remotes Suportades

PyArchInit suporta també emmagatzematge remot:
- **Google Drive**: `gdrive://folder/path/`
- **Dropbox**: `dropbox://folder/path/`
- **Amazon S3**: `s3://bucket/path/`
- **Cloudinary**: `cloudinary://cloud_name/folder/`
- **WebDAV**: `webdav://server/path/`
- **HTTP/HTTPS**: `https://server/path/`

> **Configuració de mèdia a WebDAV.** Per utilitzar un servidor WebDAV com a emmagatzematge d'imatges:
>
> 1. **Credencials** — diàleg **Remote Storage Config**, pestanya **WebDAV**: introdueix el *Nom d'usuari* i la *Contrasenya*.
> 2. **Verify SSL** (mateixa pestanya) — si el servidor utilitza un **certificat autofirmat** (típic dels servidors amb una adreça IP directa o un port HTTPS no estàndard), estableix **"Verify SSL" → No (Self-signed certificates)**: amb la verificació activada contra un servidor autofirmat la connexió falla silenciosament. Per als servidors amb un certificat vàlid (p. ex. Nextcloud/ownCloud) deixa-la a **Yes (Verify certificates)**, que és el valor per defecte.
> 3. **Rutes** — als camps **Thumbnail path** i **Thumbnail resize** utilitza el format `webdav://server:port/folder/` (p. ex. `webdav://192.0.2.10:5006/pyarchinit_media/thumb_resize/`).
> 4. **Reinicia QGIS** després de desar perquè la nova configuració d'emmagatzematge tingui efecte.

### Carpeta de dades de pyArchInit 5 (`~/pyarchinit_5`)

pyArchInit 5 desa totes les seves dades de treball — `config.cfg`, bases de dades, exportacions, còpies de seguretat, paradata i la carpeta `bin/` amb les eines d'IA — en una carpeta dedicada al directori d'inici: **`~/pyarchinit_5/`**.

Aquesta carpeta és independent del pyArchInit clàssic, que continua usant **`~/pyarchinit/`**. Les dues versions per tant **no** comparteixen dades, de manera que és possible executar pyArchInit 5 mentre la instal·lació anterior i les seves bases de dades romanen intactes.

**Primer inici — còpia de les dades existents.** La primera vegada que pyArchInit 5 s'inicia, si `~/pyarchinit_5` encara no existeix però es troba una instal·lació prèvia de `~/pyarchinit`, apareix un diàleg que pregunta si es vol copiar la configuració i les bases de dades a la nova carpeta:

- Tria **Sí** per copiar `pyarchinit_DB_folder` (és a dir, `config.cfg` i les bases de dades SQLite) a `~/pyarchinit_5`, de manera que puguis continuar treballant immediatament amb les dades existents.
- La **carpeta `bin/` no es copia**, perquè conté assets d'IA de gran mida (entorns virtuals de SAM i ceràmica, models CLIP, índexs FAISS, fitxers de claus API). Torna a crear-los executant de nou les funcions d'IA corresponents, o copia manualment `~/pyarchinit/bin` a `~/pyarchinit_5/bin`.
- Si tries **No**, pyArchInit 5 simplement crea una nova estructura de carpetes buida, com en una instal·lació nova.

> **Novetat 5.13.16-alpha — primer inici més clar.**
> - La pregunta "copiar la configuració i les bases de dades a la nova carpeta `~/pyarchinit_5`?" ara apareix sempre en primer pla, davant de qualsevol finestra. Abans, sobretot a Windows, podia quedar amagada darrere de QGIS o de la pantalla d'inici (splash) i l'inici semblava bloquejat. Respon **Sí** o **No** per continuar.
> - Mentre s'instal·len els paquets de Python que falten, la pantalla d'inici de pyArchInit roman en primer pla amb una barra de progrés que mostra el paquet n de N, el percentatge i el temps transcorregut. La instal·lació pot trigar diversos minuts: no tanquis QGIS. A Windows no s'obre cap finestra de consola durant la instal·lació.

> **Novetat 5.13.17-alpha — QGIS 4 i diverses versions de QGIS al mateix ordinador.**
> - Els paquets de Python de pyArchInit s'instal·len amb el Python del QGIS que estàs fent servir (per exemple Python 3.12 a QGIS 4). Abans, amb QGIS 3 i QGIS 4 instal·lats alhora a macOS, s'instal·laven per al Python de QGIS 3 i QGIS 4 s'aturava amb l'error `No module named 'psycopg2._psycopg'`.
> - Si la carpeta del connector conté paquets instal·lats per a un altre Python (per exemple un perfil de QGIS 3 copiat a QGIS 4), en iniciar-se pyArchInit els mou a la carpeta `ext_libs_cp39` (el nom indica la versió de Python) i reinstal·la els que calen: la primera vegada pot trigar uns minuts, amb el progrés a la pantalla d'inici (splash). El missatge apareix al tauler de registre de QGIS, pestanya "PyArchInit".
> - Les carpetes `ext_libs_cp…` es poden eliminar. Si fas servir el mateix connector des de dues versions de QGIS, pyArchInit torna a posar al seu lloc la carpeta correcta en lloc de reinstal·lar.

**Ubicació personalitzada (avançat).** Per usar una carpeta de dades diferent, defineix la variable d'entorn `PYARCHINIT_HOME` abans d'iniciar QGIS; quan s'estableix, substitueix la ubicació predeterminada `~/pyarchinit_5`.

### Secció Experimental

| Camp | Descripció |
|------|------------|
| **Experimental** | Activa funcionalitats experimentals (`Sí`/`No`) |

### Secció Activació Lloc

| Camp | Descripció |
|------|------------|
| **Activa query lloc** | Selecciona el lloc actiu per filtrar les dades a les fitxes |

Aquesta opció és fonamental quan es treballa amb múltiples llocs arqueològics a la mateixa base de dades. Seleccionant un lloc, totes les fitxes mostraran només les dades relatives a aquest lloc.

### Botons d'Acció

| Botó | Funció |
|------|--------|
| **Desa els paràmetres** | Desa totes les configuracions |
| **Actualitza BD** | Actualitza l'esquema de la base de dades existent sense perdre dades |

### Funcions d'Alineament de Base de Dades

| Botó | Descripció |
|------|------------|
| **Alinea Postgres** | Alinea i actualitza l'estructura de la base de dades PostgreSQL |
| **Alinea Spatialite** | Alinea i actualitza l'estructura de la base de dades SQLite |
| **EPSG code** | Inserir el codi EPSG del sistema de referència de la base de dades |

### Summary (Resum)

La secció Summary mostra un resum de les configuracions actuals en format HTML.

---

## Pestanya Instal·lació BD

Aquesta pestanya permet crear una nova base de dades des de zero.

### Instal·la la base de dades (PostgreSQL/PostGIS)

| Camp | Descripció |
|------|------------|
| **host** | Adreça del servidor (per defecte: `localhost`) |
| **port (5432)** | Port del servidor PostgreSQL |
| **user** | Usuari amb permisos de creació de base de dades (ex. `postgres`) |
| **password** | Contrasenya de l'usuari |
| **db name** | Nom de la nova base de dades (per defecte: `pyarchinit`) |
| **Selecciona SRID** | Sistema de referència espacial (ex. `4326` per WGS84, `32632` per UTM 32N) |

**Botó Instal·la**: Crea la base de dades amb totes les taules necessàries.

### Instal·la la base de dades (SpatiaLite)

| Camp | Descripció |
|------|------------|
| **db name** | Nom del fitxer de base de dades (per defecte: `pyarchinit`) |
| **Selecciona SRID** | Sistema de referència espacial |

**Botó Instal·la**: Crea la base de dades SQLite local.

### SRID Comuns

| SRID | Descripció |
|------|------------|
| 4326 | WGS 84 (coordenades geogràfiques) |
| 32632 | WGS 84 / UTM zone 32N (Nord Itàlia) |
| 32633 | WGS 84 / UTM zone 33N (Centre-Sud Itàlia) |
| 25831 | ETRS89 / UTM zone 31N (Catalunya) |
| 3003 | Monte Mario / Italy zone 1 (Gauss-Boaga Oest) |
| 3004 | Monte Mario / Italy zone 2 (Gauss-Boaga Est) |

---

## Pestanya Eines d'Importació

Aquesta pestanya permet importar dades d'altres bases de dades o fitxers CSV.

### Secció Importació de Dades

#### Base de Dades Origen (Recurs)

| Camp | Descripció |
|------|------------|
| **Database** | Tipus base de dades origen (`sqlite` o `postgres`) |
| **Host/Port/Username/Password** | Credencials per PostgreSQL origen |
| **...** | Selecciona fitxer SQLite origen |

#### Base de Dades Destinació

| Camp | Descripció |
|------|------------|
| **Database** | Tipus base de dades destinació |
| **Host/Port/Username/Password** | Credencials per PostgreSQL destinació |
| **...** | Selecciona fitxer SQLite destinació |

### Taules Disponibles per Importació

| Taula | Descripció |
|-------|------------|
| SITE | Llocs arqueològics |
| US | Unitats Estratigràfiques |
| PERIODIZZAZIONE | Periodització i fases |
| INVENTARIO_MATERIALI | Inventari de troballes |
| TMA | Taules Materials Arqueològics |
| TMA_MATERIALI | Materials TMA |
| POTTERY | Ceràmica |
| STRUTTURA | Estructures |
| TOMBA | Tombes |
| PYARCHINIT_THESAURUS_SIGLE | Tesaurus de sigles |
| SCHEDAIND | Fitxes d'individus antropològics |
| DETSESSO | Determinació del sexe |
| DETETA | Determinació de l'edat |
| ARCHEOZOOLOGY | Dades arqueozoològiques |
| CAMPIONI | Mostres |
| DOCUMENTAZIONE | Documentació |
| MEDIA | Fitxers multimèdia |
| MEDIA_THUMB | Miniatures |
| MEDIATOENTITY | Relacions media-entitat |
| UT | Unitats Topogràfiques |
| ALL | Totes les taules |

### Opcions d'Importació

| Opció | Descripció |
|-------|------------|
| **Replace** | Substitueix els registres existents |
| **Ignore** | Ignora els duplicats |
| **Abort** | Interromp en cas d'error |
| **Apply Constraints** | Aplica restriccions d'unicitat al tesaurus |

### Importació de Geometries

| Capa | Descripció |
|------|------------|
| PYSITO_POLYGON | Polígons dels llocs |
| PYSITO_POINT | Punts dels llocs |
| PYUS | Unitats Estratigràfiques |
| PYUSM | Unitats Estratigràfiques Muràries |
| PYQUOTE | Cotes |
| PYQUOTEUSM | Cotes USM |
| PYUS_NEGATIVE | US negatives |
| PYSTRUTTURE | Estructures |
| PYREPERTI | Troballes |
| PYINDIVIDUI | Individus |
| PYCAMPIONI | Mostres |
| PYTOMBA | Tombes |
| PYSEZIONI | Seccions |
| PYDOCUMENTAZIONE | Documentació |
| PYLINEERIFERIMENTO | Línies de referència |
| PYRIPARTIZIONI_SPAZIALI | Reparticions espacials |

### Botons

| Botó | Funció |
|------|--------|
| **Import Table** | Importa les dades de la taula seleccionada |
| **Import Geometry** | Importa les geometries seleccionades |
| **Converteix db a spatialite** | Converteix de PostgreSQL a SQLite |
| **Converteix db a postgres** | Converteix de SQLite a PostgreSQL |

---

### Exportar un lloc a em.json (Extended Matrix)

Des del menú **pyArchInit → Extended Matrix → Esporta sito in em.json…** (Exportar lloc a em.json) un lloc sencer passa al format de treball de l'Extended Matrix, el que **EMStudio** obre de manera nativa.

Què esperar:

- pyArchInit llista els llocs de la base de dades: se'n tria **un**;
- el fitxer neix a `pyarchinit_EM_folder`, dins la carpeta de dades del connector, amb el nom del lloc (qualsevol alfabet: `Al-Khutm.em.json`, `Scavo_archeologico.em.json`);
- abans de lliurar-lo, pyArchInit **rellegeix el fitxer**: una exportació que no es rellegeix igual no es lliura;
- al final pregunta si es vol **obrir de seguida a EMStudio**; si EMStudio no està instal·lat, pyArchInit indica on és el fitxer i **ofereix instal·lar-lo ara** (vegeu l'apartat següent).

Al fitxer només hi ha el lloc triat, i cada unitat hi arriba per allò que és:

- **només les files d'aquell lloc**: en una base de dades amb diversos llocs, la documentació i els períodes dels altres llocs ja no entren a l'exportació;
- **cada unitat amb el tipus que declara**: les unitats virtuals continuen essent virtuals, els special finds i les continuïtats continuen essent ells mateixos, de manera que EMStudio dibuixa el símbol correcte en lloc de convertir-ho tot en un estrat;
- **les paradades viatgen com a paradades**, no com a unitats estratigràfiques;
- una **columna buida** de la fitxa ja no esdevé una propietat buida al graf.

El que dibuixa el panell **«Vedi la matrice»** és exactament el que hi ha dins el fitxer: fer-hi un cop d'ull és la manera més ràpida de comprovar l'exportació abans d'enviar-la a EMStudio o a una sala.

> **Nota**: el GraphML sobreviu només com a **importació puntual des de yEd**; el format per mirar i validar la matriu és em.json.

### Instal·lar EMStudio des del menú

**EMStudio** és el visor de l'Extended Matrix: un programa a part del projecte Extended Matrix (llicència GPL-3). pyArchInit no el conté — el **descarrega i l'engega**, quan se li demana.

Amb **pyArchInit → Extended Matrix → Installa EMStudio…** (Instal·lar EMStudio):

1. pyArchInit llegeix les releases oficials d'EMStudio i **tria el paquet per a aquest ordinador** (macOS Apple Silicon, Windows, Linux);
2. abans de descarregar mostra una finestra amb **versió, nom del fitxer, mida, adreça de descàrrega i carpeta de destinació** — `<carpeta de dades de pyArchInit>/tools/EMStudio` — i espera un sí;
3. acabada la descàrrega **verifica l'empremta sha256** declarada per la release: un fitxer que no coincideix no s'instal·la;
4. a macOS **treure la quarantena** forma part de la instal·lació: la compilació no està signada per Apple i sense aquest pas el sistema diria que l'aplicació està "malmesa";
5. al final indica on s'ha instal·lat. Si EMStudio ja hi era, pregunta si es vol tornar a descarregar l'última versió.

Si l'exportació a em.json no troba EMStudio, **proposa instal·lar-lo a l'instant** i després obre el fitxer.

> **Límit conegut**: la release d'avui no publica cap paquet per als **Mac Intel**. En aquest cas pyArchInit ho diu i indica la pàgina de les releases (github.com/ExtendedMatrix/EMStudio/releases), des d'on es descarrega a mà.

### Veure la matriu dins el QGIS

Des del menú **pyArchInit → Extended Matrix → Vedi la matrice…** (Veure la matriu) la matriu d'un lloc es dibuixa en un **panell acoblat a la dreta** de la finestra del QGIS. No cal EMStudio, ni un node StratiGraph, ni iniciar sessió, ni internet: pyArchInit exporta l'em.json del lloc a una carpeta temporal i el dibuixa.

Què esperar:

- es tria el **lloc** d'una llista; el panell s'obre amb la matriu ja ajustada a la finestra i, a dalt, una línia que diu **quantes unitats, quantes èpoques i quantes relacions** s'han dibuixat;
- el dibuix té **una franja horitzontal per cada període/fase**, la **més recent a dalt**, cadascuna amb el seu nom, els seus anys i el seu color;
- cada unitat és a la franja del període en què va néixer, i dins la franja és l'estratigrafia la que decideix el nivell: **el que cobreix es dibuixa damunt del que és cobert**;
- cada unitat es dibuixa amb la **simbologia de l'Extended Matrix**, la de les regles de s3dgraphy (vegeu la taula);
- la **roda del ratolí** acosta i allunya, un **doble clic** torna tota la matriu a la finestra (com el botó **Adatta** / Ajustar), un **clic sobre una unitat** mostra la seva fitxa al requadre de la dreta: definició, interpretació, període i fase, datació, àrea, estructura;
- sota la fitxa apareixen els **mitjans vinculats a aquesta UE**: les miniatures de les fotos, amb el seu nom. Si les imatges són en un magatzem remot, les miniatures no es descarreguen soles — un botó **Carica le anteprime** (carregar miniatures) les demana, perquè cadascuna és una petició de xarxa;
- el botó **Zoom sulla geometria** enquadra al mapa la planta de la unitat. Només s'activa per a les unitats que són files de la fitxa UE (un node de continuïtat o un document no té geometria), i cerca entre les **capes ja carregades**, en l'ordre de la llegenda, sense afegir-ne cap. Si cap capa carregada porta els camps per reconèixer la unitat, o si la planta mai es va dibuixar, el plafó ho diu en lloc de no fer res.

| Unitat | Símbol |
|---|---|
| US — unitat estratigràfica | rectangle |
| USVs — unitat virtual estructural | paral·lelogram blau |
| USVn — unitat virtual no estructural | hexàgon verd |
| SF — troballa singular (special find) | octàgon oliva |
| BR / CON — continuïtat | rombe negre |
| Extractor | pentàgon |
| Combinador | hexàgon discontinu |
| Document | el·lipse |
| Propietat | cercle discontinu |

**Salva SVG…** (Desar SVG) i **Salva PNG…** (Desar PNG) desen el dibuix on es vulgui. L'**SVG és vectorial**: s'obre en un navegador o a l'Inkscape, s'amplia tant com calgui sense perdre nitidesa i s'imprimeix a qualsevol mida, pòsters inclosos.

La mateixa matriu s'obre també des de la finestra **«Export Extended Matrix»** de la fitxa US: el botó **«Vedi la matrice»**, al costat d'**«Apri in EMStudio»**, s'encén després d'una exportació em.json correcta i dibuixa el fitxer tot just exportat.

> **Nota**: en un lloc molt gran el panell ho diu ell mateix, amb un avís a la barra de missatges del QGIS, i aconsella **desar l'SVG i mirar-lo fora del QGIS**: recórrer per pantalla un dibuix de milers d'unitats és lent.

> **Nota**: la matriu es dibuixa també quan l'excavació no està endreçada. Les relacions que apunten a un element de paradata continuen al dibuix, i les unitats el nivell de les quals no es pot decidir perquè les relacions contenen un bucle es dibuixen igualment: el panell no rebutja una excavació real.

### Lliurar un lloc a una sala StratiGraph

Des de **pyArchInit → Extended Matrix → Consegna sito alla stanza…** (Lliurar lloc a la sala) les unitats estratigràfiques d'un lloc viatgen cap a una **sala** d'un node StratiGraph (REST, un lliurament cada vegada — no cal quedar-se connectat).

Què esperar:

- es tria el **lloc**, després la finestra demana el **node** (p. ex. `http://127.0.0.1:8020`; per a un node institucional `https://node.org/em` — escriure l'arrel també funciona, `/em` es troba sol), la **sala** i, només si el node ho exigeix, un **token** (millor a la variable d'entorn `STRATIGRAPH_TOKEN`: no es desa mai);
- el resultat és una frase: *"129 aplicades de 129"* al primer lliurament; al segon *"44 aplicades de 129, 85 ja presents"* — **les repeticions no dupliquen res**: els nodes es fusionen, les arestes ja conegudes tornen com a "ja presents";
- les files que no poden esdevenir unitats de la sala (documents, extractors, propietats) s'enumeren a *Mostra els detalls*, mai no s'inventen;
- **qui signa és qui lliura**: l'autor l'escriu el node a partir de la identitat verificada, no el payload.

Amb **Extended Matrix → Apri il nodo (stanze)…** (Obrir el node (sales)) la sala s'obre **dins de pyArchInit** (plafó lateral): s'usa Qt WebEngine si el perfil de QGIS el té, si no Qt WebKit, que QGIS 3 encara inclou — així el plafó es queda dins de QGIS fins i tot on falta WebEngine, i el navegador extern queda només com a darrer recurs. Amb una sala configurada s'obre directament la seva pàgina; sense sala s'obre la porta del node amb totes les sales.

---

## Pestanya Graphviz

Graphviz és necessari per generar els diagrames de la Matriu de Harris.

### Configuració

| Camp | Descripció |
|------|------------|
| **Ruta bin** | Ruta a la carpeta `/bin` de Graphviz |
| **...** | Explora per seleccionar la carpeta |
| **Desa** | Desa la ruta a la variable d'entorn PATH |

### Instal·lació de Graphviz

**Windows**: Descarregar des de https://graphviz.org/download/ i instal·lar

**macOS**:
```bash
brew install graphviz
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install graphviz
```

Si Graphviz ja està correctament instal·lat al PATH del sistema, els camps es desactivaran automàticament.

---

## Pestanya PostgreSQL

Configuració de la ruta de PostgreSQL per a operacions avançades.

| Camp | Descripció |
|------|------------|
| **Ruta bin** | Ruta a la carpeta `/bin` de PostgreSQL |
| **...** | Explora per seleccionar la carpeta |
| **Desa** | Desa la ruta a la variable d'entorn PATH |

Necessari per a operacions com dump/restore de la base de dades.

---

## Pestanya Ajuda

Conté recursos d'ajuda i documentació.

### Enllaços Útils

| Recurs | Descripció |
|--------|------------|
| **Tutorials en Vídeo** | Enllaç als tutorials de YouTube |
| **Documentació en Línia** | https://pyarchinit.github.io/pyarchinit_doc/index.html |
| **Facebook** | Pàgina UnaQuantum |

### WebView

Àrea per visualitzar continguts d'ajuda directament al connector.

---

## Pestanya FTP a Lizmap

Permet publicar les dades en un servidor Lizmap per a la visualització web.

### Paràmetres de Connexió FTP

| Camp | Descripció |
|------|------------|
| **ip address** | Adreça IP del servidor FTP |
| **Port** | Port FTP (per defecte: 21) |
| **User** | Nom d'usuari FTP |
| **Password** | Contrasenya FTP |

### Operacions Disponibles

| Botó | Funció |
|------|--------|
| **Connect** | Connecta al servidor FTP |
| **Disconnect** | Desconnecta del servidor |
| **Change directory** | Canvia el directori actual |
| **Create Directory** | Crea un nou directori |
| **Upload file** | Puja un fitxer al servidor |
| **Download file** | Descarrega un fitxer del servidor |
| **Delete file** | Elimina un fitxer |
| **Delete directory** | Elimina un directori |

### Status

| Camp | Descripció |
|------|------------|
| **Status connection** | Estat de la connexió actual |
| **Dialog List** | Llista de fitxers/directoris a la ubicació actual |
| **Input** | Camp per inserir noms de fitxers/directoris |

---

## Espai de treball Paradata (només PostgreSQL)

A la **Pestanya DB Sync** de la finestra de configuració hi ha la secció **Paradata Workspace**, que permet personalitzar el directori on es desen els fitxers `paradata_<lloc>.graphml` i `groups_<lloc>.graphml` quan es treballa amb una base de dades PostgreSQL.

> **Només PostgreSQL**: els usuaris de SQLite no es veuen afectats per aquesta opció. Amb SQLite, els fitxers de paradata es continuen guardant al costat del fitxer `.sqlite` (comportament heretat byte-idèntic).

### Ruta per defecte

Sense override, la ruta resolta és:

```
~/pyarchinit/pyarchinit_DB_folder/<host>_<port>_<dbname>/<lloc>/
```

Exemple: `~/pyarchinit/pyarchinit_DB_folder/localhost_5432_pyarchinit/Volterra/`

### Personalitzar la ruta

- **Examinar...** obre un diàleg de fitxers per triar un directori. La ruta es desa immediatament a les QSettings de QGIS.
- També es pot **escriure** la ruta directament al camp de text: el valor es persisteix en sortir del camp (senyal `editingFinished`). Deixar-lo buit elimina l'override.
- **Restablir** buida el camp, elimina la clau de QSettings i restaura la ruta per defecte.

### Cadena de resolució (qui guanya)

La ruta efectiva segueix una cadena de fallback de 3 nivells:

1. **Variable d'entorn `PYARCHINIT_WORKSPACE_DIR`** (prioritat màxima — útil per a scripts de CI/test).
2. **QSettings `pyarchinit/paradata_workspace`** (override de la UI — aquesta secció).
3. **Per defecte** `~/pyarchinit/pyarchinit_DB_folder/`.

Els valors buits se salten: si `PYARCHINIT_WORKSPACE_DIR=""`, la resolució passa al nivell 2; si les QSettings també són buides, s'utilitza el valor per defecte.

### Quan té efecte

Els canvis són **immediats**: el següent accés a ParadataStore / GroupStore (per exemple, desar paradata en una fitxa US o exportar una Matrix) fa servir la nova ruta. **No cal reiniciar QGIS.**

### Casos d'ús

- **Unitat de xarxa compartida**: apuntar el workspace a una ruta de xarxa (p. ex. `/Volumes/team/pyarchinit_workspace`) per compartir paradata entre usuaris sobre un PostgreSQL centralitzat.
- **Còpia de seguretat separada**: mantenir els fitxers de paradata fora del directori d'usuari per facilitar còpies dedicades.
- **Tests aïllats**: usar `PYARCHINIT_WORKSPACE_DIR` en scripts de test per no contaminar el workspace per defecte.

---

## Funcions d'Administrador (Només PostgreSQL)

Si connectats com a administrador, apareix una secció addicional:

### Gestió d'Usuaris i Permisos
Permet crear, modificar i eliminar usuaris amb diferents nivells d'accés.

### Monitor d'Activitat en Temps Real
Visualitza en temps real les activitats a la base de dades i els usuaris connectats.

### Actualitza Esquema de Base de Dades
Aplica actualitzacions a l'esquema sense perdre dades.

### Aplica Sistema de Concurrència
Afegeix el sistema de control de concurrència per evitar conflictes de modificació.

---

## Advance Setting (Comparació de Bases de Dades)

A la part superior de la pestanya principal, hi ha una secció per comparar bases de dades SQLite:

| Opció | Descripció |
|-------|------------|
| **--schema** | Compara només l'esquema |
| **--summary** | Mostra un resum |
| **--changeset FILE** | Genera un fitxer amb els canvis |

| Botó | Funció |
|------|--------|
| **Convert** | Converteix a Spatialite v5 |
| **Converteix a Spatialite v5** | Actualitza format de la base de dades |
| **Compara db** | Compara dues bases de dades |

---

## Flux de Treball Recomanat per a Nou Projecte

1. **Obrir la Configuració** des del menú PyArchInit
2. **Escollir el tipus de base de dades** (SQLite per a ús individual, PostgreSQL per a equips)
3. **Pestanya Instal·lació BD**: Crear una nova base de dades amb l'SRID apropiat
4. **Pestanya Paràmetres de Connexió**: Configurar els paràmetres de connexió
5. **Establir les rutes** per a thumbnail, resize i logotip
6. **Desar els paràmetres**
7. **Provar la connexió** obrint qualsevol fitxa (ex. Lloc)

---

## Resolució de Problemes Comuns

### Error de connexió PostgreSQL

- Verificar que el servidor PostgreSQL estigui iniciat
- Comprovar host, port i credencials
- Verificar que l'extensió PostGIS estigui instal·lada

### Base de dades SQLite no trobada
- Verificar que el fitxer existeixi a la carpeta `pyarchinit_DB_folder`
- Comprovar els permisos de lectura/escriptura

### Graphviz no funciona
- Verificar la instal·lació de Graphviz
- Establir manualment la ruta a la pestanya Graphviz
- Reiniciar QGIS després de la configuració

### Imatges no visualitzades
- Verificar les rutes Thumbnail path i Image resize
- Comprovar que les carpetes existeixin i siguin accessibles

---

## Notes Tècniques

- Les configuracions es desen a les QgsSettings de QGIS
- La base de dades per defecte és `Home/pyarchint/pyarchinit_DB_folder/pyarchinit_db.sqlite`
- Els logs de depuració es desen a `[TEMP]/pyarchinit_debug.log`
- La variable d'entorn `PYARCHINIT_HOME` apunta a la carpeta `pyarchinit` instal·lada a la Home de l'usuari

---

*Documentació PyArchInit - Fitxa Configuració*
*Versió: 4.9.x*
*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per comprendre millor el procés d'instal·lació i configuració.

[Obre Animació d'Instal·lació](../../animations/pyarchinit_installation_animation.html)

Explora l'animació interactiva per a la gestió de l'emmagatzematge remot.

[Obre Animació d'Emmagatzematge Remot](../../animations/pyarchinit_remote_storage_animation.html)
