# PyArchInit - Ghid de Configurare

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea Configurarii](#accesarea-configurarii)
3. [Fila Parametri de Conexiune](#fila-parametri-de-conexiune)
4. [Fila Instalare Baza de Date](#fila-instalare-baza-de-date)
5. [Fila Instrumente de Import](#fila-instrumente-de-import)
6. [Fila Graphviz](#fila-graphviz)
7. [Fila PostgreSQL](#fila-postgresql)
8. [Fila Ajutor](#fila-ajutor)
9. [Fila FTP catre Lizmap](#fila-ftp-catre-lizmap)

---

## Introducere

Fereastra de configurare PyArchInit va permite sa setati toti parametrii necesari pentru functionarea corecta a plugin-ului. Inainte de a incepe documentarea unei sapaturi arheologice, trebuie sa configurati corect conexiunea la baza de date si caile catre resurse.

> **Tutorial Video**: [Inserati link video pentru introducerea in configurare]

---

## Accesarea Configurarii

Pentru a accesa configurarea:
1. Deschideti QGIS
2. Meniu **PyArchInit** → **Config**

Sau din bara de instrumente PyArchInit faceti clic pe pictograma **Setari**.

![Accesarea configurarii](images/01_configurazione/01_menu_config.png)
*Figura 1: Accesarea ferestrei de configurare din meniul PyArchInit*

![Bara de instrumente PyArchInit](images/01_configurazione/02_toolbar_config.png)
*Figura 2: Pictograma de configurare in bara de instrumente*

---

## Fila Parametri de Conexiune

Aceasta este fila principala pentru configurarea conexiunii la baza de date.

![Fila Parametri de Conexiune](images/01_configurazione/03_tab_parametri_connessione.png)
*Figura 3: Fila Parametri de Conexiune - Vedere completa*

### Sectiunea Setari BD

| Camp | Descriere |
|------|-----------|
| **Database** | Selectati tipul de baza de date: `sqlite` (local) sau `postgres` (server) |
| **Host** | Adresa serverului PostgreSQL (de ex., `localhost` sau IP-ul serverului) |
| **DBname** | Numele bazei de date (de ex., `pyarchinit`) |
| **Port** | Portul de conexiune (implicit: `5432` pentru PostgreSQL) |
| **User** | Numele de utilizator pentru conexiune |
| **Password** | Parola utilizatorului |
| **SSL Mode** | Modul SSL pentru PostgreSQL: `allow`, `prefer`, `require`, `disable` |

![Setari BD](images/01_configurazione/04_db_settings.png)
*Figura 4: Sectiunea Setari BD*

#### Alegerea Bazei de Date

**SQLite/Spatialite** (Recomandat pentru utilizator unic):
- Baza de date locala, nu necesita server
- Ideala pentru proiecte individuale sau mici
- Fisierul `.sqlite` este salvat in folderul `pyarchinit_DB_folder`

![Configurare SQLite](images/01_configurazione/05_config_sqlite.png)
*Figura 5: Exemplu de configurare SQLite*

**PostgreSQL/PostGIS** (Recomandat pentru echipe):
- Baza de date pe server, acces multi-utilizator
- Necesita PostgreSQL cu extensia PostGIS instalata
- Suporta gestionarea utilizatorilor si permisiuni
- Ideala pentru proiecte mari cu mai multi operatori

![Configurare PostgreSQL](images/01_configurazione/06_config_postgres.png)
*Figura 6: Exemplu de configurare PostgreSQL*

> **Tutorial Video**: [Inserati link video pentru configurarea bazei de date]

### Sectiunea Setari Cai

| Camp | Descriere | Buton |
|------|-----------|-------|
| **Thumbnail path** | Calea pentru salvarea miniaturilor imaginilor | `...` pentru navigare |
| **Image resize** | Calea pentru imaginile redimensionate | `...` pentru navigare |
| **Logo path** | Calea catre logo-ul personalizat pentru rapoarte | `...` pentru navigare |

![Setari Cai](images/01_configurazione/07_path_settings.png)
*Figura 7: Sectiunea Setari Cai*

#### Cai la Distanta Suportate

PyArchInit suporta si stocare la distanta:
- **Google Drive**: `gdrive://folder/path/`
- **Dropbox**: `dropbox://folder/path/`
- **Amazon S3**: `s3://bucket/path/`
- **Cloudinary**: `cloudinary://cloud_name/folder/`
- **WebDAV**: `webdav://server/path/`
- **HTTP/HTTPS**: `https://server/path/`

![Stocare la Distanta](images/01_configurazione/08_remote_storage.png)
*Figura 8: Exemplu de configurare stocare la distanta*

### Sectiunea Setari Santier

| Camp | Descriere |
|------|-----------|
| **Site** | Numele implicit al santierului pentru inregistrari noi |
| **Experimental features** | Activare functii experimentale (Da/Nu) |

---

## Fila Instalare Baza de Date

Aceasta fila va permite sa instalati sau sa actualizati baza de date PyArchInit.

![Fila Instalare BD](images/01_configurazione/08_tab_installazione_db.png)
*Figura 8: Fila Instalare Baza de Date*

### Instalare Noua

1. Selectati **sqlite** sau **postgres** ca tip de baza de date
2. Faceti clic pe **Conectare**
3. Daca baza de date nu exista, faceti clic pe **Instalare Baza de Date**
4. Sistemul va crea toate tabelele necesare

### Actualizare Baza de Date

Pentru instalari existente:
1. Faceti clic pe **Verificare/Actualizare Baza de Date**
2. Sistemul verifica structura si aplica eventualele actualizari

> **Atentie**: Faceti intotdeauna o copie de siguranta a bazei de date inainte de actualizare!

---

## Fila Instrumente de Import

Instrumente pentru importul datelor din surse externe.

### Import CSV

1. Selectati fisierul CSV
2. Mapati coloanele la campurile bazei de date
3. Faceti clic pe **Import**

### Import Shapefile

Pentru importul datelor GIS direct in straturile PyArchInit.

---

## Fila Graphviz

Configurarea Graphviz pentru generarea diagramelor Harris Matrix.

| Camp | Descriere |
|------|-----------|
| **Graphviz Path** | Calea catre instalarea Graphviz (de ex., `/usr/bin/` pe Linux) |
| **Check Graphviz** | Verificati instalarea Graphviz |

### Instalarea Graphviz

**Windows**: Descarcati de pe [graphviz.org](https://graphviz.org/download/)

**macOS**: `brew install graphviz`

**Linux**: `sudo apt install graphviz`

---

## Fila PostgreSQL

Setari avansate ale serverului PostgreSQL.

| Camp | Descriere |
|------|-----------|
| **pg_dump path** | Calea catre pg_dump pentru copii de siguranta |
| **psql path** | Calea catre comanda psql |

---

## Fila Ajutor

Contine linkuri utile si resurse.

| Resursa | Descriere |
|---------|-----------|
| Tutorial Video | Link catre tutoriale video YouTube |
| Documentatie Online | https://pyarchinit.github.io/pyarchinit_doc/index.html |
| Facebook | Pagina UnaQuantum |

---

## Fila FTP catre Lizmap

Configurare pentru publicare web cu Lizmap.

| Camp | Descriere |
|------|-----------|
| **FTP Host** | Adresa serverului FTP |
| **FTP User** | Numele de utilizator FTP |
| **FTP Password** | Parola FTP |
| **Remote Path** | Calea de destinatie pe server |

---

## Depanare

### Conexiune Esuata

**Cauze**:
- Date de autentificare incorecte
- Serverul nu ruleaza
- Firewall-ul blocheaza conexiunea

**Solutii**:
- Verificati numele de utilizator si parola
- Verificati daca serviciul PostgreSQL ruleaza
- Verificati regulile firewall-ului

### Baza de Date Negasita

**Cauza**: Baza de date nu a fost inca instalata

**Solutie**: Mergeti la fila Instalare BD si faceti clic pe Instalare Baza de Date

---

## Bune Practici

1. **Faceti copii de siguranta regulat**: Folositi functia de Salvare si Restaurare
2. **Folositi PostgreSQL pentru echipe**: Suport mai bun pentru multi-utilizator
3. **Setati caile corecte**: Asigurati-va ca toate setarile de cai indica directoare valide
4. **Testati conexiunea**: Verificati intotdeauna conexiunea inainte de a incepe lucrul

---

*Ultima actualizare: Ianuarie 2026*

---

## Animatie Interactiva

Explorati animatia interactiva pentru a intelege mai bine procesul de instalare si configurare.

[Deschideti Animatia de Instalare](../../animations/pyarchinit_installation_animation.html)

Explorati animatia interactiva pentru gestionarea stocarii la distanta.

[Deschideti Animatia Stocare la Distanta](../../animations/pyarchinit_remote_storage_animation.html)
