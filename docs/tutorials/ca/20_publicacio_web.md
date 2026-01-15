# Tutorial 20: Publicació Web amb Lizmap

## Introducció

PyArchInit suporta la **publicació web** de les dades arqueològiques mitjançant **Lizmap**, una aplicació que permet transformar projectes QGIS en aplicacions web interactives.

### Què és Lizmap?

Lizmap està compost per:
- **Plugin QGIS**: Per configurar la publicació
- **Lizmap Web Client**: Aplicació web per visualitzar els mapes
- **QGIS Server**: Backend per servir els mapes

### Avantatges de la Publicació Web

| Aspecte | Descripció |
|---------|------------|
| Accessibilitat | Dades consultables des del navegador |
| Compartició | Fàcil distribució a stakeholders |
| Interactivitat | Zoom, pan, consultes, popup |
| Actualització | Sincronització amb base de dades |
| Mòbil | Accés des de smartphone/tablet |

## Prerequisits

### Servidor

1. **QGIS Server** instal·lat
2. **Lizmap Web Client** configurat
3. Servidor web (Apache/Nginx)
4. PHP 7.4+
5. PostgreSQL/PostGIS (recomanat)

### Client

1. **QGIS Desktop** amb plugin Lizmap
2. **PyArchInit** configurat
3. Projecte QGIS desat

## Instal·lació Plugin Lizmap

### Des de QGIS

1. **Plugin** → **Gestió plugins**
2. Cercar "Lizmap"
3. Instal·lar **Lizmap**
4. Reiniciar QGIS

## Preparació Projecte

### 1. Organització Capes

Estructura recomanada:
```
Projecte QGIS
├── Grup: Base
│   ├── Ortofoto
│   └── CTR/Cadastral
├── Grup: Excavació
│   ├── pyunitastratigrafiche
│   ├── pyunitastratigrafiche_usm
│   └── pyarchinit_quote
├── Grup: Documentació
│   ├── Fotos georeferenciades
│   └── Aixecaments
└── Grup: Anàlisi
    └── Matrix Harris (imatge)
```

### 2. Estilització Capes

Per a cada capa:
1. Aplicar estil apropiat
2. Configurar etiquetes
3. Establir escala visibilitat

### 3. Popup i Atributs

Configurar els popup per a cada capa:
1. Botó dret sobre la capa → **Propietats**
2. Tab **Display**
3. Configurar **HTML Map Tip**

Exemple popup US:
```html
<h3>US [% "us_s" %]</h3>
<p><b>Àrea:</b> [% "area_s" %]</p>
<p><b>Tipus:</b> [% "tipo_us_s" %]</p>
<p><b>Definició:</b> [% "definizione" %]</p>
```

### 4. Desament Projecte

1. Desar el projecte (.qgz) a la carpeta Lizmap
2. Usar rutes relatives per a les dades
3. Verificar que totes les capes siguin accessibles

## Configuració Lizmap

### Obertura Plugin

1. **Web** → **Lizmap** → **Lizmap**

### Tab General

| Camp | Descripció | Valor |
|------|------------|-------|
| Títol mapa | Nom visualitzat | "Excavació Via Roma" |
| Abstract | Descripció | "Documentació arqueològica..." |
| Imatge | Thumbnail projecte | project_thumb.png |
| Repository | Carpeta servidor | /var/www/lizmap/projects |

### Tab Layer

Per a cada capa configurar:

| Opció | Descripció |
|-------|------------|
| Activat | Capa visible a Lizmap |
| Base layer | Capa de fons (ortofoto, etc.) |
| Popup | Habilita popup al clic |
| Editing | Permet modificació online |
| Filtre | Filtres usuari |

### Tab Basemap

Configurar fons:
- OpenStreetMap
- Google Maps (requereix API key)
- Bing Maps
- Ortofoto custom

### Tab Locate

Cerca per localitat:
- Configurar capa per cerca
- Camps a cercar
- Format visualització

### Tab Editing (Opcional)

Per permetre edició online:
1. Seleccionar capes modificables
2. Configurar camps editables
3. Establir permisos

### Tab Eines

Activar/desactivar:
- Impressió
- Mesures
- Selecció
- Permalink
- etc.

### Desament Configuració

Fer clic **Desa** per generar el fitxer `.qgs.cfg`

## Publicació

### Pujada al Servidor

1. Copiar fitxers `.qgz` i `.qgz.cfg` al servidor
2. Verificar permisos fitxers
3. Configurar QGIS Server

### Estructura Servidor

```
/var/www/lizmap/
├── lizmap/           # Aplicació Lizmap
├── projects/         # Projectes QGIS
│   ├── excavacio_roma.qgz
│   └── excavacio_roma.qgz.cfg
└── var/              # Dades aplicació
```

### Configuració QGIS Server

Fitxer `/etc/apache2/sites-available/lizmap.conf`:
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

## Accés Web

### URL Aplicació

```
http://lizmap.example.com/
```

### Navegació

1. Selecció projecte des de la home
2. Visualització mapa interactiu
3. Eines a la barra d'eines

### Funcionalitats Usuari

| Funció | Descripció |
|--------|------------|
| Zoom | Rodeta ratolí, botons +/- |
| Pan | Arrossegament mapa |
| Popup | Clic sobre feature |
| Cerca | Barra de cerca |
| Impressió | Exporta a PDF |
| Permalink | URL compartible |

## Integració PyArchInit

### Dades Real-time

Amb PostgreSQL:
- Les dades estan sempre actualitzades
- Modificacions a PyArchInit visibles immediatament
- Cap sincronització manual

### Capes Recomanades

| Capa PyArchInit | Publicació |
|-----------------|------------|
| pyunitastratigrafiche | Sí, amb popup |
| pyunitastratigrafiche_usm | Sí, amb popup |
| pyarchinit_quote | Sí |
| pyarchinit_siti | Sí, com a overview |
| Matrix Harris | Com a imatge estàtica |

### Configuració Popup US

Template HTML avançat:
```html
<div class="us-popup">
    <h3 style="color:#2c3e50;">US [% "us_s" %]</h3>
    <table>
        <tr><td><b>Lloc:</b></td><td>[% "scavo_s" %]</td></tr>
        <tr><td><b>Àrea:</b></td><td>[% "area_s" %]</td></tr>
        <tr><td><b>Tipus:</b></td><td>[% "tipo_us_s" %]</td></tr>
        <tr><td><b>Definició:</b></td><td>[% "definizione" %]</td></tr>
        <tr><td><b>Període:</b></td><td>[% "periodo" %]</td></tr>
    </table>
    [% if "foto_url" %]
    <img src="[% "foto_url" %]" style="max-width:200px;"/>
    [% end %]
</div>
```

## Seguretat

### Autenticació

Lizmap suporta:
- Usuaris locals
- LDAP
- OAuth2

### Configuració Usuaris

A l'admin de Lizmap:
1. Crear grups (admin, arqueòleg, públic)
2. Crear usuaris
3. Assignar permisos per projecte

### Permisos Capa

| Grup | Visualitza | Edita | Imprimeix |
|------|------------|-------|-----------|
| Admin | Tots | Tots | Sí |
| Arqueòleg | Tots | Alguns | Sí |
| Públic | Només base | No | No |

## Manteniment

### Actualització Projectes

1. Modificar projecte a QGIS Desktop
2. Regenerar configuració Lizmap
3. Pujar al servidor

### Cache

Gestió cache tiles:
```bash
# Netejar cache
lizmap-cache-clearer.php -project excavacio_roma

# Regenerar tiles
lizmap-tiles-seeder.php -project excavacio_roma -bbox xmin,ymin,xmax,ymax
```

### Log i Debug

```bash
# Log QGIS Server
tail -f /var/log/qgis/qgis_server.log

# Log Lizmap
tail -f /var/www/lizmap/var/log/messages.log
```

## Bones Pràctiques

### 1. Optimització Rendiment

- Usar capes ràster pre-tilitzades
- Limitar nombre features per capa
- Configurar escales de visibilitat
- Usar índexs espacials

### 2. User Experience

- Popup informatius però concisos
- Estils clars i llegibles
- Organització lògica capes
- Documentació per usuaris

### 3. Seguretat

- HTTPS obligatori
- Actualitzacions regulars
- Còpia de seguretat configuracions
- Monitorització accessos

### 4. Còpia de Seguretat

- Còpia de seguretat fitxers `.qgz` i `.cfg`
- Còpia de seguretat base de dades PostgreSQL
- Versionat configuracions

## Resolució de Problemes

### Mapa No Visualitzat

**Causes**:
- QGIS Server no configurat
- Rutes fitxers errònies
- Permisos insuficients

**Solucions**:
- Verificar log QGIS Server
- Controlar rutes al projecte
- Verificar permisos fitxers

### Popup No Funcionen

**Causes**:
- Capa no configurada per popup
- HTML erroni al template

**Solucions**:
- Habilitar popup a Lizmap
- Verificar sintaxi HTML

### Rendiment Lent

**Causes**:
- Massa dades
- Cache no configurada
- Servidor subdimensionat

**Solucions**:
- Reduir dades visibles
- Configurar cache tiles
- Augmentar recursos servidor

## Referències

### Software
- [Lizmap](https://www.lizmap.com/)
- [QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

### Documentació
- [Lizmap Documentation](https://docs.lizmap.com/)
- [QGIS Server Documentation](https://docs.qgis.org/latest/en/docs/server_manual/)

---

## Vídeo Tutorial

### Setup Lizmap
`[Placeholder: video_lizmap_setup.mp4]`

**Continguts**:
- Instal·lació plugin
- Configuració projecte
- Publicació

**Durada prevista**: 20-25 minuts

### Personalització Web
`[Placeholder: video_lizmap_custom.mp4]`

**Continguts**:
- Popup avançats
- Estils personalitzats
- Gestió usuaris

**Durada prevista**: 15-18 minuts

---

*Última actualització: Gener 2026*
