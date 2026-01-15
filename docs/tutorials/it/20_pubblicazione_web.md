# Tutorial 20: Pubblicazione Web con Lizmap

## Introduzione

PyArchInit supporta la **pubblicazione web** dei dati archeologici attraverso **Lizmap**, un'applicazione che permette di trasformare progetti QGIS in applicazioni web interattive.

### Cos'e Lizmap?

Lizmap e composto da:
- **Plugin QGIS**: Per configurare la pubblicazione
- **Lizmap Web Client**: Applicazione web per visualizzare le mappe
- **QGIS Server**: Backend per servire le mappe

### Vantaggi della Pubblicazione Web

| Aspetto | Descrizione |
|---------|-------------|
| Accessibilita | Dati consultabili da browser |
| Condivisione | Facile distribuzione a stakeholder |
| Interattivita | Zoom, pan, query, popup |
| Aggiornamento | Sincronizzazione con database |
| Mobile | Accesso da smartphone/tablet |

## Prerequisiti

### Server

1. **QGIS Server** installato
2. **Lizmap Web Client** configurato
3. Server web (Apache/Nginx)
4. PHP 7.4+
5. PostgreSQL/PostGIS (consigliato)

### Client

1. **QGIS Desktop** con plugin Lizmap
2. **PyArchInit** configurato
3. Progetto QGIS salvato

## Installazione Plugin Lizmap

### Da QGIS

1. **Plugin** → **Gestione plugin**
2. Cercare "Lizmap"
3. Installare **Lizmap**
4. Riavviare QGIS

## Preparazione Progetto

### 1. Organizzazione Layer

Struttura consigliata:
```
Progetto QGIS
├── Gruppo: Base
│   ├── Ortofoto
│   └── CTR/Catastale
├── Gruppo: Scavo
│   ├── pyunitastratigrafiche
│   ├── pyunitastratigrafiche_usm
│   └── pyarchinit_quote
├── Gruppo: Documentazione
│   ├── Foto georeferenziate
│   └── Rilievi
└── Gruppo: Analisi
    └── Matrix Harris (immagine)
```

### 2. Styling Layer

Per ogni layer:
1. Applicare stile appropriato
2. Configurare etichette
3. Impostare scala visibilita

### 3. Popup e Attributi

Configurare i popup per ogni layer:
1. Tasto destro sul layer → **Proprieta**
2. Tab **Display**
3. Configurare **HTML Map Tip**

Esempio popup US:
```html
<h3>US [% "us_s" %]</h3>
<p><b>Area:</b> [% "area_s" %]</p>
<p><b>Tipo:</b> [% "tipo_us_s" %]</p>
<p><b>Definizione:</b> [% "definizione" %]</p>
```

### 4. Salvataggio Progetto

1. Salvare il progetto (.qgz) nella cartella Lizmap
2. Usare percorsi relativi per i dati
3. Verificare che tutti i layer siano accessibili

## Configurazione Lizmap

### Apertura Plugin

1. **Web** → **Lizmap** → **Lizmap**

### Tab Generale

| Campo | Descrizione | Valore |
|-------|-------------|--------|
| Titolo mappa | Nome visualizzato | "Scavo Via Roma" |
| Abstract | Descrizione | "Documentazione archeologica..." |
| Immagine | Thumbnail progetto | project_thumb.png |
| Repository | Cartella server | /var/www/lizmap/projects |

### Tab Layer

Per ogni layer configurare:

| Opzione | Descrizione |
|---------|-------------|
| Attivato | Layer visibile in Lizmap |
| Base layer | Layer di sfondo (ortofoto, etc.) |
| Popup | Abilita popup al click |
| Editing | Permette modifica online |
| Filtro | Filtri utente |

### Tab Basemap

Configurare sfondi:
- OpenStreetMap
- Google Maps (richiede API key)
- Bing Maps
- Ortofoto custom

### Tab Locate

Ricerca per localita:
- Configurare layer per ricerca
- Campi da cercare
- Formato visualizzazione

### Tab Editing (Opzionale)

Per permettere editing online:
1. Selezionare layer modificabili
2. Configurare campi editabili
3. Impostare permessi

### Tab Strumenti

Attivare/disattivare:
- Stampa
- Misure
- Selezione
- Permalink
- etc.

### Salvataggio Configurazione

Cliccare **Salva** per generare il file `.qgs.cfg`

## Pubblicazione

### Upload su Server

1. Copiare file `.qgz` e `.qgz.cfg` sul server
2. Verificare permessi file
3. Configurare QGIS Server

### Struttura Server

```
/var/www/lizmap/
├── lizmap/           # Applicazione Lizmap
├── projects/         # Progetti QGIS
│   ├── scavo_roma.qgz
│   └── scavo_roma.qgz.cfg
└── var/              # Dati applicazione
```

### Configurazione QGIS Server

File `/etc/apache2/sites-available/lizmap.conf`:
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

## Accesso Web

### URL Applicazione

```
http://lizmap.example.com/
```

### Navigazione

1. Selezione progetto dalla home
2. Visualizzazione mappa interattiva
3. Strumenti nella toolbar

### Funzionalita Utente

| Funzione | Descrizione |
|----------|-------------|
| Zoom | Rotella mouse, pulsanti +/- |
| Pan | Trascinamento mappa |
| Popup | Click su feature |
| Ricerca | Barra di ricerca |
| Stampa | Esporta in PDF |
| Permalink | URL condivisibile |

## Integrazione PyArchInit

### Dati Real-time

Con PostgreSQL:
- I dati sono sempre aggiornati
- Modifiche in PyArchInit visibili immediatamente
- Nessuna sincronizzazione manuale

### Layer Consigliati

| Layer PyArchInit | Pubblicazione |
|------------------|---------------|
| pyunitastratigrafiche | Si, con popup |
| pyunitastratigrafiche_usm | Si, con popup |
| pyarchinit_quote | Si |
| pyarchinit_siti | Si, come overview |
| Matrix Harris | Come immagine statica |

### Configurazione Popup US

Template HTML avanzato:
```html
<div class="us-popup">
    <h3 style="color:#2c3e50;">US [% "us_s" %]</h3>
    <table>
        <tr><td><b>Sito:</b></td><td>[% "scavo_s" %]</td></tr>
        <tr><td><b>Area:</b></td><td>[% "area_s" %]</td></tr>
        <tr><td><b>Tipo:</b></td><td>[% "tipo_us_s" %]</td></tr>
        <tr><td><b>Definizione:</b></td><td>[% "definizione" %]</td></tr>
        <tr><td><b>Periodo:</b></td><td>[% "periodo" %]</td></tr>
    </table>
    [% if "foto_url" %]
    <img src="[% "foto_url" %]" style="max-width:200px;"/>
    [% end %]
</div>
```

## Sicurezza

### Autenticazione

Lizmap supporta:
- Utenti locali
- LDAP
- OAuth2

### Configurazione Utenti

In Lizmap admin:
1. Creare gruppi (admin, archeologo, pubblico)
2. Creare utenti
3. Assegnare permessi per progetto

### Permessi Layer

| Gruppo | Visualizza | Edita | Stampa |
|--------|------------|-------|--------|
| Admin | Tutti | Tutti | Si |
| Archeologo | Tutti | Alcuni | Si |
| Pubblico | Solo base | No | No |

## Manutenzione

### Aggiornamento Progetti

1. Modificare progetto in QGIS Desktop
2. Rigenerare configurazione Lizmap
3. Upload su server

### Cache

Gestione cache tiles:
```bash
# Pulire cache
lizmap-cache-clearer.php -project scavo_roma

# Rigenerare tiles
lizmap-tiles-seeder.php -project scavo_roma -bbox xmin,ymin,xmax,ymax
```

### Log e Debug

```bash
# Log QGIS Server
tail -f /var/log/qgis/qgis_server.log

# Log Lizmap
tail -f /var/www/lizmap/var/log/messages.log
```

## Best Practices

### 1. Ottimizzazione Prestazioni

- Usare layer raster pre-tilizzati
- Limitare numero feature per layer
- Configurare scale di visibilita
- Usare indici spaziali

### 2. User Experience

- Popup informativi ma concisi
- Stili chiari e leggibili
- Organizzazione logica layer
- Documentazione per utenti

### 3. Sicurezza

- HTTPS obbligatorio
- Aggiornamenti regolari
- Backup configurazioni
- Monitoraggio accessi

### 4. Backup

- Backup file `.qgz` e `.cfg`
- Backup database PostgreSQL
- Versionamento configurazioni

## Risoluzione Problemi

### Mappa Non Visualizzata

**Cause**:
- QGIS Server non configurato
- Percorsi file errati
- Permessi insufficienti

**Soluzioni**:
- Verificare log QGIS Server
- Controllare percorsi in progetto
- Verificare permessi file

### Popup Non Funzionanti

**Cause**:
- Layer non configurato per popup
- HTML errato nel template

**Soluzioni**:
- Abilitare popup in Lizmap
- Verificare sintassi HTML

### Prestazioni Lente

**Cause**:
- Troppi dati
- Cache non configurata
- Server sottodimensionato

**Soluzioni**:
- Ridurre dati visibili
- Configurare cache tiles
- Aumentare risorse server

## Riferimenti

### Software
- [Lizmap](https://www.lizmap.com/)
- [QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

### Documentazione
- [Lizmap Documentation](https://docs.lizmap.com/)
- [QGIS Server Documentation](https://docs.qgis.org/latest/en/docs/server_manual/)

---

## Video Tutorial

### Setup Lizmap
`[Placeholder: video_lizmap_setup.mp4]`

**Contenuti**:
- Installazione plugin
- Configurazione progetto
- Pubblicazione

**Durata prevista**: 20-25 minuti

### Customizzazione Web
`[Placeholder: video_lizmap_custom.mp4]`

**Contenuti**:
- Popup avanzati
- Stili personalizzati
- Gestione utenti

**Durata prevista**: 15-18 minuti

---

*Ultimo aggiornamento: Gennaio 2026*
