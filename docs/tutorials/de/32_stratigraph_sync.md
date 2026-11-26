# PyArchInit - StratiGraph: Synchronisierungs-Panel

> Das Panel und das Raumfenster folgen der Sprache der QGIS-Oberflaeche; die Schaltflaechen sind hier so genannt, wie sie auf Deutsch erscheinen.

## Inhaltsverzeichnis
1. [Einfuehrung](#einfuehrung)
2. [Zugriff auf das Panel](#zugriff-auf-das-panel)
3. [Die Oberflaeche verstehen](#die-oberflaeche-verstehen)
4. [Bundles exportieren](#bundles-exportieren)
5. [Synchronisierung](#synchronisierung)
6. [Warteschlangen-Verwaltung](#warteschlangen-verwaltung)
7. [Eine Fundstelle in einen StratiGraph-Raum senden](#eine-fundstelle-in-einen-stratigraph-raum-senden)
8. [Konfiguration](#konfiguration)
9. [Fehlerbehebung](#fehlerbehebung)
10. [Haeufig gestellte Fragen](#haeufig-gestellte-fragen)

---

## Einfuehrung

Ab Version **5.0.2-alpha** enthaelt PyArchInit ein **StratiGraph Sync**-Panel, das die Offline-first-Datensynchronisierung mit dem StratiGraph Knowledge Graph ermoeglicht. Dieses Panel ist Teil des europaeischen **StratiGraph**-Projekts (Horizon Europe) und implementiert den Offline-first-Arbeitsablauf: Sie arbeiten lokal ohne Internet, exportieren Bundles wenn bereit, und das System synchronisiert automatisch, wenn die Konnektivitaet wiederhergestellt wird.

<!-- VIDEO: Einfuehrung in StratiGraph Sync -->
> **Video Tutorial**: [Video-Link StratiGraph Sync Einfuehrung einfuegen]

### Arbeitsablauf-Uebersicht

```
1. Offline arbeiten     2. Bundle exportieren  3. Auto-Sync
   (OFFLINE_EDITING)       (LOCAL_EXPORT)        (QUEUED_FOR_SYNC)
        |                      |                      |
   Normale Daten-        Exportieren +          Upload wenn online
   eingabe in            Validieren +           mit automatischem
   PyArchInit            Einreihen              Retry
```

---

## Zugriff auf das Panel

Das StratiGraph Sync-Panel ist standardmaessig ausgeblendet und kann ueber eine Schaltflaeche in der Werkzeugleiste umgeschaltet werden.

### Ueber die Werkzeugleiste

1. Suchen Sie die Schaltflaeche **StratiGraph Sync** in der PyArchInit-Werkzeugleiste -- sie hat ein gruenes Symbol mit Synchronisierungspfeilen und dem Buchstaben "S"
2. Klicken Sie auf die Schaltflaeche, um das Panel **anzuzeigen** (es ist eine Umschaltflaeche)
3. Klicken Sie erneut, um das Panel **auszublenden**

Das Panel erscheint als **linkes Dock-Widget** in der QGIS-Oberflaeche. Sie koennen es wie jedes andere QGIS-Dock-Panel ziehen und neu positionieren.

<!-- IMAGE: Werkzeugleisten-Schaltflaeche fuer StratiGraph Sync -->
> **Abb. 1**: Die StratiGraph Sync-Schaltflaeche in der Werkzeugleiste (gruenes Symbol mit Synchronisierungspfeilen und "S")

<!-- IMAGE: Panel angedockt auf der linken Seite von QGIS -->
> **Abb. 2**: Das StratiGraph Sync-Panel angedockt auf der linken Seite des QGIS-Fensters

---

## Die Oberflaeche verstehen

Das StratiGraph Sync-Panel ist in mehrere Abschnitte unterteilt, von oben nach unten.

### Statusanzeige

Die **Statusanzeige** am oberen Rand des Panels zeigt den aktuellen Synchronisierungszustand Ihrer Daten an. Die moeglichen Zustaende sind:

| Zustand | Symbol | Beschreibung |
|---------|--------|-------------|
| **OFFLINE_EDITING** | Stift | Sie arbeiten lokal und bearbeiten Daten normal |
| **LOCAL_EXPORT** | Paket | Ein Bundle wird aus lokalen Daten exportiert |
| **LOCAL_VALIDATION** | Haekchen | Das exportierte Bundle wird validiert |
| **QUEUED_FOR_SYNC** | Uhr | Das Bundle wurde validiert und wartet auf den Upload |
| **SYNC_SUCCESS** | Gruener Kreis | Die letzte Synchronisierung wurde erfolgreich abgeschlossen |
| **SYNC_FAILED** | Roter Kreis | Der letzte Synchronisierungsversuch ist fehlgeschlagen |

### Verbindungsanzeige

Unter der Statusanzeige zeigt die **Verbindungsanzeige**, ob das System den StratiGraph-Server erreichen kann:

| Status | Bedeutung |
|--------|-----------|
| **Online** | Der Health-Check-Endpunkt ist erreichbar; automatische Synchronisierung ist aktiv |
| **Offline** | Der Health-Check-Endpunkt ist nicht erreichbar; Bundles werden in die Warteschlange gestellt |

Das System prueft automatisch die Konnektivitaet alle **30 Sekunden** (konfigurierbar).

### Warteschlangen-Zaehler

Der **Warteschlangen-Zaehler** zeigt zwei Zahlen an:

- **Ausstehende Bundles**: Anzahl der Bundles, die auf den Upload warten
- **Fehlgeschlagene Bundles**: Anzahl der Bundles, deren Upload fehlgeschlagen ist (werden automatisch erneut versucht)

### Letzte Synchronisierung

Zeigt den **Zeitstempel** und das **Ergebnis** (Erfolg oder Fehlschlag) des letzten Synchronisierungsversuchs an.

### Aktionsschaltflaechen

| Schaltflaeche | Aktion |
|---------------|--------|
| **Paket exportieren** | Erstellt ein Bundle aus Ihren lokalen Daten, validiert es und fuegt es der Synchronisierungs-Warteschlange hinzu |
| **Jetzt synchronisieren** | Erzwingt einen sofortigen Synchronisierungsversuch (nur verfuegbar wenn online) |
| **Warteschlange...** | Oeffnet den Warteschlangen-Verwaltungsdialog mit allen Eintraegen |
| **Fundstelle an einen Raum senden...** | Meldet sich an einem StratiGraph-Knoten an und bringt eine Fundstelle in einen Raum (siehe unten) |

### Aktivitaetsprotokoll

Am unteren Rand des Panels zeigt ein scrollbares **Aktivitaetsprotokoll** zeitgestempelte Eintraege der juengsten Aktivitaeten, einschliesslich Statusaenderungen, Exporte, Validierungen und Synchronisierungsversuche.

<!-- IMAGE: Vollstaendiges Panel mit allen annotierten Abschnitten -->
> **Abb. 3**: Das vollstaendige StratiGraph Sync-Panel mit allen beschrifteten Abschnitten

---

## Bundles exportieren

Das Exportieren eines Bundles verpackt Ihre lokalen archaeologischen Daten in ein strukturiertes Format, das zum Upload in den StratiGraph Knowledge Graph bereit ist.

### Schritt-fuer-Schritt-Export

1. Stellen Sie sicher, dass Sie alle aktuelle Arbeit in PyArchInit gespeichert haben
2. Oeffnen Sie das StratiGraph Sync-Panel (falls nicht bereits sichtbar)
3. Klicken Sie auf die Schaltflaeche **Paket exportieren**
4. Das System fuehrt automatisch drei Operationen aus:
   - **Export**: Lokale Daten werden in eine Bundle-Datei verpackt
   - **Validierung**: Das Bundle wird auf Vollstaendigkeit und Datenintegritaet geprueft
   - **Einreihung**: Das validierte Bundle wird der Synchronisierungs-Warteschlange hinzugefuegt
5. Beobachten Sie die **Statusanzeige**, die durch folgende Zustaende wechselt: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. Das **Aktivitaetsprotokoll** zeichnet jeden Schritt mit einem Zeitstempel auf

### Was ein Bundle enthaelt

Ein Bundle enthaelt alle archaeologischen Entitaeten, die UUIDs haben (siehe Tutorial 31 fuer UUID-Details). Jede Entitaet wird durch ihre `entity_uuid` identifiziert, wodurch sichergestellt wird, dass derselbe Datensatz immer auf dem Server erkannt wird.

<!-- IMAGE: Paket exportieren-Schaltflaeche und Statusuebergang -->
> **Abb. 4**: Klick auf "Paket exportieren" und Beobachtung der Statusaenderungen im Panel

---

## Synchronisierung

### Automatische Synchronisierung

Wenn das System erkennt, dass Sie **online** sind (Health-Check erfolgreich), laedt es automatisch alle ausstehenden Bundles aus der Warteschlange hoch. Es ist kein manueller Eingriff erforderlich.

Der automatische Synchronisierungsprozess:

1. Die Konnektivitaetspruefung ist erfolgreich (Health-Check-Endpunkt antwortet)
2. Die Verbindungsanzeige wechselt auf **Online**
3. Ausstehende Bundles in der Warteschlange werden einzeln hochgeladen
4. Erfolgreich hochgeladene Bundles werden als `SYNC_SUCCESS` markiert
5. Der Zeitstempel und das Ergebnis der **letzten Synchronisierung** werden aktualisiert

### Manuelle Synchronisierung

Wenn Sie einen sofortigen Synchronisierungsversuch erzwingen moechten:

1. Stellen Sie sicher, dass die Verbindungsanzeige **Online** zeigt
2. Klicken Sie auf die Schaltflaeche **Jetzt synchronisieren**
3. Das System versucht sofort, alle ausstehenden Bundles hochzuladen

Die Schaltflaeche **Jetzt synchronisieren** ist nur wirksam, wenn das System online ist.

### Automatischer Retry mit exponentiellem Backoff

Wenn ein Upload fehlschlaegt, gibt das System **nicht** auf. Stattdessen versucht es automatisch erneut mit zunehmenden Verzoegerungen:

| Versuch | Verzoegerung |
|---------|-------------|
| 1. Retry | 30 Sekunden |
| 2. Retry | 60 Sekunden |
| 3. Retry | 120 Sekunden |
| 4. Retry | 5 Minuten |
| 5. Retry | 15 Minuten |

Dies verhindert eine Ueberlastung des Servers bei voruebergehender Nichtverfuegbarkeit und stellt gleichzeitig die endgueltige Zustellung sicher.

<!-- IMAGE: Jetzt synchronisieren-Schaltflaeche und Verbindungsanzeige -->
> **Abb. 5**: Die "Jetzt synchronisieren"-Schaltflaeche und die Verbindungsstatusanzeige

---

## Warteschlangen-Verwaltung

Die Schaltflaeche **Warteschlange...** oeffnet einen detaillierten Dialog, in dem Sie alle Bundles in der Synchronisierungs-Warteschlange einsehen koennen.

### Spalten des Warteschlangen-Dialogs

| Spalte | Beschreibung |
|--------|-------------|
| **ID** | Eindeutige Kennung des Warteschlangeneintrags |
| **Status** | Aktueller Status des Eintrags (pending, syncing, success, failed) |
| **Attempts** | Anzahl der bisherigen Upload-Versuche |
| **Created** | Zeitstempel, wann das Bundle der Warteschlange hinzugefuegt wurde |
| **Last Error** | Fehlermeldung des letzten fehlgeschlagenen Versuchs (leer wenn kein Fehler) |
| **Bundle path** | Dateisystem-Pfad zur Bundle-Datei |

### Warteschlangeneintraege interpretieren

- **Pending**-Eintraege warten auf den Upload
- **Success**-Eintraege wurden hochgeladen und vom Server bestaetigt
- **Failed**-Eintraege werden automatisch erneut versucht; pruefen Sie die Spalte **Last Error** fuer Details
- Die **Attempts**-Anzahl hilft zu verstehen, wie oft das System versucht hat, ein bestimmtes Bundle hochzuladen

### Warteschlangen-Speicherung

Die Warteschlangen-Datenbank wird als SQLite-Datei gespeichert unter:

```
$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite
```

Diese Datei bleibt zwischen QGIS-Sitzungen erhalten, sodass ausstehende Bundles nicht verloren gehen, wenn Sie QGIS schliessen.

<!-- IMAGE: Warteschlangen-Dialog mit mehreren Eintraegen -->
> **Abb. 6**: Der Warteschlangen-Verwaltungsdialog mit Bundle-Eintraegen

---

## Eine Fundstelle in einen StratiGraph-Raum senden

Ab Version **5.14.0-alpha** bringt die Schaltflaeche **Fundstelle an einen Raum senden...** eine Fundstelle in einen *Raum* eines StratiGraph-Knotens (StratiGraph Server). Der Graph der Fundstelle wird zum Inhalt des Raums, wo EMStudio, EM Tools und die anderen Werkzeuge des Projekts ihn sehen und bearbeiten.

![Panel StratiGraph Sync](images/32_stratigraph_sync/06_sync_panel_send_button.png)

> **Fig. 7**: Das Panel StratiGraph Sync mit der Schaltflaeche **Fundstelle an einen Raum senden...**

### Schritt-fuer-Schritt-Anleitung

1. Im Panel **StratiGraph Sync** auf **Fundstelle an einen Raum senden...** klicken.
2. **Knoten**: die Adresse des Knotens, zum Beispiel `https://knoten.example.org/em`. Sie wird zwischen den Sitzungen gespeichert.
3. **Fundstelle**: die Fundstelle waehlen. **Raum-ID** und **Raumtitel** werden aus dem Namen der Fundstelle ausgefuellt und koennen geaendert werden; die Raum-ID ist ein Wort ohne Leerzeichen.
4. Auf **Anmelden...** klicken: die Anmeldeseite des Knotens oeffnet sich im Browser. Mit dem eigenen Konto anmelden und zu QGIS zurueckkehren: die Zeile **Identität** zeigt den Namen und ob Raeume erstellt werden duerfen. Hat der Knoten einen eigenen Keycloak-Client für pyArchInit, gehört sein Name in die QGIS-Einstellung `pyArchInit/stratigraph/client_id`; sonst wird der vom Knoten genannte Client verwendet.
5. Optional: **Nur planen** zeigt, was gesendet wuerde, ohne etwas auf dem Knoten zu schreiben.
6. Auf **Fundstelle senden** klicken: das Protokoll nennt die exportierten Knoten und Kanten und das Ergebnis.

![Fenster Fundstelle an einen Raum senden](images/32_stratigraph_sync/07_send_site_dialog.png)

> **Fig. 8**: Das Fenster nach der Anmeldung und dem Senden der Beispiel-Fundstelle an einen Entwicklungsknoten: 745 Operationen angewendet, 0 abgelehnt, die Datenbank als Verweis behalten

### Was gesendet wird

- Der Graph der ganzen Fundstelle, als ein einziger Graph auch bei mehreren Sondagen: so reisen die Beziehungen zwischen Einheiten verschiedener Sondagen mit.
- Vom Graphen zitierte Dateien werden nur einmal hochgeladen. Erneutes Senden derselben Fundstelle verdoppelt nichts.
- **Datenbankdateien werden nie hochgeladen** (sqlite, spatialite, gpkg): im Raum bleibt nur ein Verweis. Die anderen Fundstellen der Datenbank bleiben auf dem eigenen Rechner.
- Das Passwort geht nie durch pyArchInit: es wird nur auf der Seite des Knotens eingegeben. Das Zugangstoken bleibt im Speicher und verfaellt beim Schliessen des Fensters.

### Ueber die Kommandozeile

Dieselbe Uebertragung ohne QGIS (ohne `--dry-run` wird wirklich geschrieben; ohne `--token` oeffnet sich der Browser zur Anmeldung):

```bash
python scripts/stratigraph_send_site.py --db ~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite \
    --site "Scavo archeologico" --node https://nodo.example.org/em --room scavo-2026 --dry-run
```

### Mit einem Raum arbeiten, der bereits Daten enthaelt

Wenn auch andere im Raum arbeiten (EMStudio, StratiField, EM Tools), nach der Anmeldung:

1. **Mit dem Raum vergleichen** vergleicht die Fundstelle mit dem Raum in beide Richtungen, ohne etwas zu schreiben: was der Raum Neues fuer pyArchInit hat (neue Einheiten, geaenderte Definitionen, Beziehungen) und was pyArchInit dem Raum hinzufuegt.
2. **Änderungen senden** sendet dem Raum die hier geleistete Arbeit: neue Einheiten und Beziehungen, hier geänderte Felder, hier entfernte Beziehungen. Was sich nur im Raum geändert hat, bleibt unberührt; ein auf beiden Seiten geändertes Feld ist ein Konflikt und wird nur angezeigt (siehe «Synchronisation mit Gedächtnis»).
3. **Aus dem Raum holen** bringt den Raum in die Datenblaetter von pyArchInit (SE, Definitionen, Periodisierung, Beziehungen) und erkennt jedes Blatt an seiner Kennung. Wuerde der Pull lokale Beziehungen entfernen, die der Raum nicht kennt, listet das Fenster sie auf und fragt nach Bestaetigung.

Mit **Aus dem Raum holen** laesst sich auch eine Fundstelle in einer Datenbank wiederherstellen, die sie nicht enthaelt: die Einheiten kommen mit Nummer, Typ, Definitionen und Periodisierung zurueck. Kontinuitaetseinheiten (CON) reisen nicht mit: pyArchInit erzeugt sie mit **Genera continuita** neu.

Der Raum erhaelt den ganzen SE-Datensatz, nicht nur die Felder des Graphen: Beschreibung, Interpretation, Farbe, Konsistenz, Hoehen, Masse, Sondage, Raum, Quadrat, Sektor, die Mauerwerksfelder (USM). Ein aus einem Raum wiederhergestellter Datensatz gleicht dem Original; die Beziehungen aendern sich nur in der Schreibweise (mit Areal und Fundstelle). Ein Raum, der mit einer frueheren pyArchInit-Version gesendet wurde, enthaelt nur die Felder des Graphen: der Vergleich zeigt viele abweichende Felder; ein neues **Fundstelle senden** vervollstaendigt ihn.

All das gilt fuer SQLite wie fuer PostgreSQL. Um eine Fundstelle wiederherzustellen, genuegt eine leere, in pyArchInit angelegte und geoeffnete Datenbank: **Aus dem Raum holen** fuellt sie (Fundstelle, Datensaetze, Periodisierung, Beziehungen, Medien). Beziehungen haben immer vier Elemente: Typ, SE, Areal, Fundstelle.

![Vergleich mit dem Raum](images/32_stratigraph_sync/08_compare_with_room.png)

> **Fig. 9**: Der Vergleich mit einem Raum, in dem auch in EMStudio gearbeitet wurde: eine neue SE und eine ueberarbeitete Definition im Raum, eine neue SE aus pyArchInit zum Senden

### Fotos und Medien im Raum

Fotos, Videos, 3D-Modelle und Dokumente, die mit SE-Datensaetzen verknuepft sind, reisen mit der Fundstelle, in beide Richtungen. Orthofotos und andere Raster bleiben aussen vor: sie sind QGIS-Layer, keine pyArchInit-Medien.

- **Fundstelle senden** und **Änderungen senden** laden jede Datei nur einmal in den Speicher des Raums: eine Datei, die der Raum schon hat (gleicher Inhalt), wird nicht erneut gesendet. Ist das Original nicht mehr auf der Festplatte, wird die Kopie im Resize-Ordner verwendet.
- **Aus dem Raum holen** laedt neue Medien in den Ordner `stratigraph_media/<Raum>` des pyArchInit-Home, erzeugt Vorschau und Kopie wie beim Laden einer Datei aus dem Formular und verknuepft sie mit ihrer SE, mit Beschreibung und Tags. Ein Medium, das die Datenbank schon hat (an seiner Kennung erkannt), wird nicht erneut geladen: nur die Verknuepfung wird geprueft.
- Medien von Funden, Keramik, Graebern und Strukturen bleiben vorerst lokal: das Fenster zaehlt sie.

![Ein neues Foto an den Raum gesendet](images/32_stratigraph_sync/09_room_media.png)

> **Fig. 10**: Ein Foto, das nach dem Senden der Fundstelle zur SE 3 hinzugefuegt wurde: der Vergleich findet es und Änderungen senden laedt Datei und Verknuepfung hoch

### Synchronisation mit Gedächtnis

Nach dem ersten **Aus dem Raum holen** (oder dem ersten **Fundstelle senden**) merkt sich pyArchInit den Raum, wie er in diesem Moment war: die gemeinsame *Basis*, gespeichert im Ordner `stratigraph_rooms` des pyArchInit-Home, eine pro Datenbank, Fundstelle und Raum. Von da an:

- liest der Vergleich aus dem Raum **nur das Neue** seit der letzten Synchronisation, nicht das ganze Dokument;
- hat jeder Unterschied einen Urheber: **hier geändert** (wird gesendet), **im Raum geändert** (das Holen bringt es), **auf beiden Seiten geändert** (Konflikt, mit beiden Werten angezeigt), **im Raum entfernt** (das Holen entfernt es auch hier), **hier entfernt** (wird gesendet);
- überschreibt **Aus dem Raum holen** nie stillschweigend noch nicht gesendete Arbeit: gibt es lokale Änderungen, Konflikte, hier hinzugefügte oder entfernte Beziehungen, listet das Fenster sie auf und empfiehlt, sie zuerst zu senden. Bei einem bestätigten Konflikt gewinnt der Wert des Raums.

Einheiten, die das Holen absichtlich auslässt (erzeugte Kontinuitätseinheiten CON und ihre Medien), bleiben im Raum und zählen nicht als Entfernungen. Es funktioniert mit SQLite und PostgreSQL gleich.

![Drei-Wege-Vergleich](images/32_stratigraph_sync/10_three_way_compare.png)

> **Fig. 11**: Der Vergleich nach einer Synchronisation: ein hier geändertes Feld zum Senden, ein im Raum geändertes zum Holen, ein Konflikt im selben Feld

### Geometrien: Fundstelle, Sondagen, Areale und Eingriffe

Mit der Fundstelle reisen auch die Zeichnungen der GIS-Layer von pyArchInit, als Footprints in ihrem eigenen Bezugssystem: das Polygon der **Fundstelle** (`pyarchinit_siti_polygonal`), die **Sondagen** (`pyarchinit_sondaggi`), **Areale und Sektoren** (`pyarchinit_ripartizioni_spaziali`) und die **Eingriffe**, also die negativen SE (`pyunitastratigrafiche`). Sie gehen von SQLite und von PostGIS aus.

**Aus dem Raum holen** schreibt sie in die Layer zurück, SpatiaLite oder PostGIS, im Bezugssystem des Layers: ein fehlendes Objekt wird ergänzt, ein gleiches bleibt unberührt, und ein **hier anders gezeichnetes Objekt bleibt, wie es ist**, und wird gemeldet: das Holen überschreibt nie eine lokale Zeichnung.

Die Polygone der positiven SE reisen nicht: für die Extended Matrix ist ihre Geometrie das 3D-Modell. Orthofotos und Raster bleiben in QGIS.

### Haeufige Probleme

| Meldung | Was tun |
|---------|---------|
| `401` oder Anmeldung abgelaufen | Die Sitzung erneuert sich waehrend der Arbeit selbst; ist sie ganz abgelaufen (viele Stunden ungenutzt), erneut **Anmelden...** druecken |
| ⚠ «Die Nummer … gehört mehreren Einheiten» | Im selben Areal haben zwei Einheiten dieselbe Nummer und verschiedene Typen: Beziehungen nennen eine Einheit nur mit Nummer, Areal und Fundstelle und erreichen im Raum daher beide. Vor dem Senden eine davon umnummerieren |
| `403` / *may create rooms: False* | Das Konto hat keine Rolle im Raum oder darf keine Raeume erstellen: den Administrator des Knotens fragen |
| `CERTIFICATE_VERIFY_FAILED` | Der Knoten nutzt ein lokales Zertifikat (Entwicklungs- oder Feldknoten): dessen CA auf dem Rechner installieren oder auf der Kommandozeile `--ca-file` verwenden |
| `409 ... already declared` | Der Raum existiert und gehoert einem anderen Benutzer: eine andere ID waehlen |

---

## Konfiguration

### Health-Check-URL

Das System verwendet eine Health-Check-URL, um die Konnektivitaet zum StratiGraph-Server zu bestimmen. Sie koennen diese in den QGIS-Einstellungen konfigurieren:

| Einstellung | Schluessel | Standard |
|-------------|-----------|----------|
| Health-Check-URL | `pyArchInit/stratigraph/health_check_url` | `http://localhost:8080/health` |

Um die Health-Check-URL zu aendern:

1. Oeffnen Sie **QGIS** -> **Einstellungen** -> **Optionen** (oder verwenden Sie die QGIS-Python-Konsole)
2. Navigieren Sie zu den PyArchInit-Einstellungen oder stellen Sie ein ueber:

```python
from qgis.core import QgsSettings
s = QgsSettings()
s.setValue("pyArchInit/stratigraph/health_check_url", "https://ihr-server.beispiel.de/health")
```

### Pruefintervall

Das Standard-Konnektivitaetspruefintervall betraegt **30 Sekunden**. Dies kann ebenfalls ueber QgsSettings konfiguriert werden.

---

## Fehlerbehebung

### Das Panel erscheint nicht

- Stellen Sie sicher, dass Sie PyArchInit Version **5.0.2-alpha** oder neuer verwenden
- Pruefen Sie, ob die StratiGraph Sync-Schaltflaeche in der Werkzeugleiste sichtbar ist
- Versuchen Sie, die Schaltflaeche aus- und wieder einzuschalten
- Pruefen Sie **Sketchy** -> **Sketchy** in QGIS, ob das Dock-Widget aufgelistet ist

### Die Verbindungsanzeige zeigt immer "Offline"

- Stellen Sie sicher, dass der StratiGraph-Server laeuft und erreichbar ist
- Pruefen Sie die Health-Check-URL in den Einstellungen (Standard: `http://localhost:8080/health`)
- Testen Sie die URL manuell im Browser oder mit `curl`:

```bash
curl http://localhost:8080/health
```

- Wenn sich der Server auf einem anderen Rechner befindet, stellen Sie sicher, dass keine Firewall-Regeln die Verbindung blockieren

### Bundle-Export schlaegt fehl

- Stellen Sie sicher, dass die Datenbank verbunden und erreichbar ist
- Pruefen Sie, ob Ihre Datensaetze gueltige UUIDs haben (Tutorial 31)
- Kontrollieren Sie das Aktivitaetsprotokoll auf spezifische Fehlermeldungen
- Stellen Sie sicher, dass genuegend Speicherplatz fuer die Bundle-Datei vorhanden ist

### Synchronisierung schlaegt wiederholt fehl

- Pruefen Sie die Spalte **Last Error** im Warteschlangen-Dialog fuer Details
- Haeufige Ursachen:
  - Server ist voruebergehend nicht verfuegbar (das System versucht es automatisch erneut)
  - Netzwerk-Konnektivitaetsprobleme
  - Server hat das Bundle abgelehnt (pruefen Sie die Server-Logs)
- Wenn ein Bundle nach vielen Versuchen konsistent fehlschlaegt, erwaegen Sie, es erneut zu exportieren

### Probleme mit der Warteschlangen-Datenbank

- Die Warteschlangen-Datenbank befindet sich unter `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite`
- Bei Beschaedigung koennen Sie sie sicher loeschen -- ausstehende Bundles gehen verloren, koennen aber erneut exportiert werden
- Sichern Sie diese Datei, wenn Sie den Warteschlangenzustand erhalten muessen

---

## Haeufig gestellte Fragen

### Brauche ich Internet, um PyArchInit zu verwenden?

**Nein.** PyArchInit ist vollstaendig offline funktionsfaehig. Das StratiGraph Sync-Panel behandelt nur die Synchronisierung mit dem StratiGraph-Server. Sie koennen vollstaendig offline arbeiten und exportieren/synchronisieren, wenn Sie bereit sind.

### Was passiert, wenn ich QGIS mit ausstehenden Bundles schliesse?

Ausstehende Bundles werden in der Warteschlangen-Datenbank gespeichert und sind beim Neustart von QGIS verfuegbar. Das System nimmt die Synchronisierung automatisch wieder auf, wenn die Konnektivitaet wiederhergestellt wird.

### Kann ich mehrere Bundles exportieren?

Ja. Jedes Mal, wenn Sie auf "Paket exportieren" klicken, wird ein neues Bundle erstellt und der Warteschlange hinzugefuegt. Mehrere Bundles koennen in die Warteschlange gestellt werden und werden nacheinander hochgeladen.

### Wie weiss ich, ob meine Daten synchronisiert wurden?

Pruefen Sie die Anzeige der **letzten Synchronisierung** im Panel fuer das juengste Ergebnis. Sie koennen auch den **Warteschlange...**-Dialog oeffnen, um den Status jedes einzelnen Bundles zu sehen.

### Funktioniert StratiGraph Sync sowohl mit PostgreSQL als auch mit SQLite?

Ja. Das Synchronisierungssystem funktioniert mit beiden von PyArchInit unterstuetzten Datenbank-Backends. Bundles werden in einem datenbankunabhaengigen Format exportiert.

### Was ist die Beziehung zwischen UUIDs und Synchronisierung?

UUIDs (Tutorial 31) stellen die stabilen Kennungen bereit, die die Synchronisierung ermoeglichen. Jede Entitaet in einem Bundle wird durch ihre UUID identifiziert, sodass der Server Datensaetze korrekt zuordnen, erstellen oder aktualisieren kann.

---

*PyArchInit Dokumentation - StratiGraph Sync*
*Version: 5.0.2-alpha*
*Letzte Aktualisierung: Februar 2026*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../../animations/stratigraph_sync_animation.html)
