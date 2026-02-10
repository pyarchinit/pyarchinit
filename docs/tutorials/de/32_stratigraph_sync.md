# PyArchInit - StratiGraph: Synchronisierungs-Panel

## Inhaltsverzeichnis
1. [Einfuehrung](#einfuehrung)
2. [Zugriff auf das Panel](#zugriff-auf-das-panel)
3. [Die Oberflaeche verstehen](#die-oberflaeche-verstehen)
4. [Bundles exportieren](#bundles-exportieren)
5. [Synchronisierung](#synchronisierung)
6. [Warteschlangen-Verwaltung](#warteschlangen-verwaltung)
7. [Konfiguration](#konfiguration)
8. [Fehlerbehebung](#fehlerbehebung)
9. [Haeufig gestellte Fragen](#haeufig-gestellte-fragen)

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
| **Export Bundle** | Erstellt ein Bundle aus Ihren lokalen Daten, validiert es und fuegt es der Synchronisierungs-Warteschlange hinzu |
| **Sync Now** | Erzwingt einen sofortigen Synchronisierungsversuch (nur verfuegbar wenn online) |
| **Queue...** | Oeffnet den Warteschlangen-Verwaltungsdialog mit allen Eintraegen |

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
3. Klicken Sie auf die Schaltflaeche **Export Bundle**
4. Das System fuehrt automatisch drei Operationen aus:
   - **Export**: Lokale Daten werden in eine Bundle-Datei verpackt
   - **Validierung**: Das Bundle wird auf Vollstaendigkeit und Datenintegritaet geprueft
   - **Einreihung**: Das validierte Bundle wird der Synchronisierungs-Warteschlange hinzugefuegt
5. Beobachten Sie die **Statusanzeige**, die durch folgende Zustaende wechselt: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. Das **Aktivitaetsprotokoll** zeichnet jeden Schritt mit einem Zeitstempel auf

### Was ein Bundle enthaelt

Ein Bundle enthaelt alle archaeologischen Entitaeten, die UUIDs haben (siehe Tutorial 31 fuer UUID-Details). Jede Entitaet wird durch ihre `entity_uuid` identifiziert, wodurch sichergestellt wird, dass derselbe Datensatz immer auf dem Server erkannt wird.

<!-- IMAGE: Export Bundle-Schaltflaeche und Statusuebergang -->
> **Abb. 4**: Klick auf "Export Bundle" und Beobachtung der Statusaenderungen im Panel

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
2. Klicken Sie auf die Schaltflaeche **Sync Now**
3. Das System versucht sofort, alle ausstehenden Bundles hochzuladen

Die Schaltflaeche **Sync Now** ist nur wirksam, wenn das System online ist.

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

<!-- IMAGE: Sync Now-Schaltflaeche und Verbindungsanzeige -->
> **Abb. 5**: Die "Sync Now"-Schaltflaeche und die Verbindungsstatusanzeige

---

## Warteschlangen-Verwaltung

Die Schaltflaeche **Queue...** oeffnet einen detaillierten Dialog, in dem Sie alle Bundles in der Synchronisierungs-Warteschlange einsehen koennen.

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

Ja. Jedes Mal, wenn Sie auf "Export Bundle" klicken, wird ein neues Bundle erstellt und der Warteschlange hinzugefuegt. Mehrere Bundles koennen in die Warteschlange gestellt werden und werden nacheinander hochgeladen.

### Wie weiss ich, ob meine Daten synchronisiert wurden?

Pruefen Sie die Anzeige der **letzten Synchronisierung** im Panel fuer das juengste Ergebnis. Sie koennen auch den **Queue...**-Dialog oeffnen, um den Status jedes einzelnen Bundles zu sehen.

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
