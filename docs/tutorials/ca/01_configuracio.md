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
