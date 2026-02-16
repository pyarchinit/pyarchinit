# Tutorial 20: Publicarea pe web cu Lizmap

## Introducere

PyArchInit suporta **publicarea pe web** a datelor arheologice prin **Lizmap**, o aplicatie care permite transformarea proiectelor QGIS in aplicatii web interactive.

### Ce este Lizmap?

Lizmap consta din:
- **Plugin QGIS**: Pentru configurarea publicarii
- **Lizmap Web Client**: Aplicatie web pentru vizualizarea hartilor
- **QGIS Server**: Backend pentru servirea hartilor

### Avantajele publicarii pe web

| Aspect | Descriere |
|--------|-----------|
| Accesibilitate | Date accesibile din browser |
| Partajare | Distribuire usoara catre parti interesate |
| Interactivitate | Zoom, deplasare, interogare, popup |
| Actualizare | Sincronizare cu baza de date |
| Mobil | Acces de pe smartphone/tableta |

## Cerinte prealabile

### Server

1. **QGIS Server** instalat
2. **Lizmap Web Client** configurat
3. Server web (Apache/Nginx)
4. PHP 7.4+
5. PostgreSQL/PostGIS (recomandat)

### Client

1. **QGIS Desktop** cu pluginul Lizmap
2. **PyArchInit** configurat
3. Proiect QGIS salvat

## Instalarea pluginului Lizmap

### Din QGIS

1. **Pluginuri** > **Gestionare pluginuri**
2. Cautati "Lizmap"
3. Instalati **Lizmap**
4. Reporniti QGIS

## Pregatirea proiectului

### 1. Organizarea straturilor

Structura recomandata:
```
Proiect QGIS
+-- Grup: Baza
|   +-- Ortofoto
|   +-- CTR/Cadastral
+-- Grup: Excavare
|   +-- pyunitastratigrafiche
|   +-- pyunitastratigrafiche_usm
|   +-- pyarchinit_quote
+-- Grup: Documentatie
|   +-- Fotografii georeferentiate
|   +-- Relevee
+-- Grup: Analiza
    +-- Harris Matrix (imagine)
```

### 2. Stilizarea straturilor

Pentru fiecare strat:
1. Aplicati stilul corespunzator
2. Configurati etichetele
3. Setati vizibilitatea la scara

### 3. Popup-uri si atribute

Configurati popup-urile pentru fiecare strat:
1. Clic dreapta pe strat > **Proprietati**
2. Fila **Afisare**
3. Configurati **Indicatie harta HTML**

Exemplu popup US:
```html
<h3>US [% "us_s" %]</h3>
<p><b>Arie:</b> [% "area_s" %]</p>
<p><b>Tip:</b> [% "tipo_us_s" %]</p>
<p><b>Definitie:</b> [% "definizione" %]</p>
```

### 4. Salvarea proiectului

1. Salvati proiectul (.qgz) in folderul Lizmap
2. Utilizati cai relative pentru date
3. Verificati ca toate straturile sunt accesibile

## Configurarea Lizmap

### Deschiderea pluginului

1. **Web** > **Lizmap** > **Lizmap**

### Fila Generala

| Camp | Descriere | Valoare |
|------|-----------|---------|
| Titlul hartii | Numele afisat | "Excavarea Via Roma" |
| Rezumat | Descriere | "Documentatie arheologica..." |
| Imagine | Miniatura proiectului | project_thumb.png |
| Depozit | Folderul serverului | /var/www/lizmap/projects |

### Fila Straturi

Pentru fiecare strat configurati:

| Optiune | Descriere |
|---------|-----------|
| Activat | Strat vizibil in Lizmap |
| Strat de baza | Strat de fundal (ortofoto, etc.) |
| Popup | Activare popup la clic |
| Editare | Permitere editare online |
| Filtru | Filtre utilizator |

### Fila Harta de baza

Configurati fundalurile:
- OpenStreetMap
- Google Maps (necesita cheie API)
- Bing Maps
- Ortofoto personalizata

### Fila Localizare

Cautare locatie:
- Configurati straturile pentru cautare
- Campuri de cautat
- Format de afisare

### Fila Editare (Optional)

Pentru a permite editarea online:
1. Selectati straturile editabile
2. Configurati campurile editabile
3. Setati permisiunile

### Fila Instrumente

Activati/dezactivati:
- Tiparire
- Masuratori
- Selectie
- Permalink
- etc.

### Salvarea configuratiei

Faceti clic pe **Salvare** pentru a genera fisierul `.qgs.cfg`

## Publicare

### Incarcarea pe server

1. Copiati fisierele `.qgz` si `.qgz.cfg` pe server
2. Verificati permisiunile fisierelor
3. Configurati QGIS Server

### Structura serverului

```
/var/www/lizmap/
+-- lizmap/           # Aplicatia Lizmap
+-- projects/         # Proiecte QGIS
|   +-- scavo_roma.qgz
|   +-- scavo_roma.qgz.cfg
+-- var/              # Date aplicatie
```

### Configurarea QGIS Server

Fisier `/etc/apache2/sites-available/lizmap.conf`:
```apache
<VirtualHost *:80>
    ServerName lizmap.example.com
    DocumentRoot /var/www/lizmap/lizmap/www

    <Directory /var/www/lizmap/lizmap/www>
        AllowOverride All
        Require all granted
    </Directory>

    # QGIS Server
    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
        AllowOverride All
        Require all granted
    </Directory>

    FcgidInitialEnv QGIS_SERVER_LOG_FILE /var/log/qgis/qgis_server.log
    FcgidInitialEnv QGIS_SERVER_LOG_LEVEL 0
</VirtualHost>
```

## Acces web

### URL-ul aplicatiei

```
http://lizmap.example.com/
```

### Navigare

1. Selectarea proiectului din pagina principala
2. Vizualizare harta interactiva
3. Instrumente in bara de instrumente

### Functionalitati pentru utilizatori

| Functie | Descriere |
|---------|-----------|
| Zoom | Rotita mouse-ului, butoane +/- |
| Deplasare | Tragerea hartii |
| Popup | Clic pe element |
| Cautare | Bara de cautare |
| Tiparire | Export in PDF |
| Permalink | URL care poate fi partajat |

## Integrarea PyArchInit

### Date in timp real

Cu PostgreSQL:
- Datele sunt intotdeauna actualizate
- Modificarile din PyArchInit sunt vizibile imediat
- Fara sincronizare manuala

### Straturi recomandate

| Strat PyArchInit | Publicare |
|------------------|-----------|
| pyunitastratigrafiche | Da, cu popup |
| pyunitastratigrafiche_usm | Da, cu popup |
| pyarchinit_quote | Da |
| pyarchinit_siti | Da, ca prezentare generala |
| Harris Matrix | Ca imagine statica |

### Configurare avansata popup US

Sablon HTML avansat:
```html
<div class="us-popup">
    <h3 style="color:#2c3e50;">US [% "us_s" %]</h3>
    <table>
        <tr><td><b>Sit:</b></td><td>[% "scavo_s" %]</td></tr>
        <tr><td><b>Arie:</b></td><td>[% "area_s" %]</td></tr>
        <tr><td><b>Tip:</b></td><td>[% "tipo_us_s" %]</td></tr>
        <tr><td><b>Definitie:</b></td><td>[% "definizione" %]</td></tr>
        <tr><td><b>Perioada:</b></td><td>[% "periodo" %]</td></tr>
    </table>
    [% if "foto_url" %]
    <img src="[% "foto_url" %]" style="max-width:200px;"/>
    [% end %]
</div>
```

## Securitate

### Autentificare

Lizmap suporta:
- Utilizatori locali
- LDAP
- OAuth2

### Configurarea utilizatorilor

In administratorul Lizmap:
1. Creati grupuri (administrator, arheolog, public)
2. Creati utilizatori
3. Atribuiti permisiuni per proiect

### Permisiuni pe straturi

| Grup | Vizualizare | Editare | Tiparire |
|------|-------------|---------|----------|
| Administrator | Toate | Toate | Da |
| Arheolog | Toate | Unele | Da |
| Public | Doar baza | Nu | Nu |

## Intretinere

### Actualizari proiect

1. Editati proiectul in QGIS Desktop
2. Regenerati configuratia Lizmap
3. Incarcati pe server

### Cache

Gestionarea cache-ului de dale:
```bash
# Stergere cache
lizmap-cache-clearer.php -project scavo_roma

# Regenerare dale
lizmap-tiles-seeder.php -project scavo_roma -bbox xmin,ymin,xmax,ymax
```

### Jurnalizare si depanare

```bash
# Jurnal QGIS Server
tail -f /var/log/qgis/qgis_server.log

# Jurnal Lizmap
tail -f /var/www/lizmap/var/log/messages.log
```

## Bune practici

### 1. Optimizarea performantei

- Utilizati straturi raster pre-daluite
- Limitati numarul de elemente per strat
- Configurati vizibilitatea la scara
- Utilizati indexuri spatiale

### 2. Experienta utilizatorului

- Popup-uri informative dar concise
- Stiluri clare si lizibile
- Organizare logica a straturilor
- Documentatie pentru utilizatori

### 3. Securitate

- HTTPS obligatoriu
- Actualizari regulate
- Copii de siguranta ale configuratiei
- Monitorizarea accesului

### 4. Copii de siguranta

- Copii de siguranta ale fisierelor `.qgz` si `.cfg`
- Copii de siguranta ale bazei de date PostgreSQL
- Versionarea configuratiilor

## Depanare

### Harta nu este afisata

**Cauze**:
- QGIS Server nu este configurat
- Cai de fisiere gresite
- Permisiuni insuficiente

**Solutii**:
- Verificati jurnalul QGIS Server
- Verificati caile in proiect
- Verificati permisiunile fisierelor

### Popup-urile nu functioneaza

**Cauze**:
- Stratul nu este configurat pentru popup
- HTML incorect in sablon

**Solutii**:
- Activati popup-ul in Lizmap
- Verificati sintaxa HTML

### Performanta slaba

**Cauze**:
- Prea multe date
- Cache neconfigurate
- Server subdimensionat

**Solutii**:
- Reduceti datele vizibile
- Configurati cache-ul de dale
- Cresteti resursele serverului

## Referinte

### Software
- [Lizmap](https://www.lizmap.com/)
- [QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

### Documentatie
- [Documentatie Lizmap](https://docs.lizmap.com/)
- [Documentatie QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

---

## Tutorial video

### Configurare Lizmap
`[Placeholder: video_lizmap_setup.mp4]`

**Continut**:
- Instalarea pluginului
- Configurarea proiectului
- Publicare

**Durata estimata**: 20-25 minute

### Personalizare web
`[Placeholder: video_lizmap_custom.mp4]`

**Continut**:
- Popup-uri avansate
- Stiluri personalizate
- Gestionarea utilizatorilor

**Durata estimata**: 15-18 minute

---

*Ultima actualizare: ianuarie 2026*
