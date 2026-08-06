# Tutorial 38: Import aus QField (GPKG)

## Einführung

Die Funktion **Import aus QField (GPKG)** überträgt die mit **QField** über das
begleitende Plugin **pyarchinit-qfield** im Feld erfassten Daten nach
pyArchInit. Der Befehl liest die GeoPackages (`.gpkg`) des QField-Projekts sowie
die im Feld aufgenommenen Fotos und **hängt** die Datensätze an die
pyArchInit-Datenbank an, ohne bereits vorhandene SE und Funde zu duplizieren:
Bei vorhandenen Datensätzen werden **nur die leeren Felder** gefüllt, bereits
vorhandene Werte werden **nie** überschrieben.

Der Ablauf ist auf **Sicherheit** ausgelegt: Zuerst führen Sie eine **Vorschau
(Probelauf)** durch, die alles simuliert, ohne etwas zu schreiben; dann — erst
nach Bestätigung — starten Sie den eigentlichen **Import** in einer einzigen
Transaktion.

> Voraussetzung: Die Daten müssen im Feld mit **QField** über das begleitende
> Plugin **pyarchinit-qfield** erfasst worden sein.

---

## 1. Voraussetzungen

- Im Feld mit **QField** über das Plugin **pyarchinit-qfield** erfasste Daten.
- Der QField-Projektordner enthält die **`.gpkg`**-Dateien und die Fotos unter
  **`DCIM/pyarchinit`**.
- Eine konfigurierte pyArchInit-Datenbank (SQLite/Spatialite oder
  PostgreSQL/PostGIS): Die DB wird **automatisch** aus der Plugin-Konfiguration
  ermittelt.

---

## 2. Dialog öffnen

Der Befehl ist auf **zwei Wegen** erreichbar:

1. **Menü**: **Plugin → pyArchInit - Archaeological GIS Tools → Importa da
   QField (GPKG)**.
2. **Werkzeugleiste** (neu): Öffnen Sie in der pyArchInit-Werkzeugleiste die
   **Dropdown-Schaltfläche der Analysewerkzeuge** — dieselbe, die auch
   GeoArchaeo, MoveCost, Palimpsest und weitere Werkzeuge enthält — und wählen
   Sie **Importa da QField (GPKG)**. Der Eintrag ist an seinem **neuen eigenen
   Symbol** zu erkennen: eine grüne, abgerundete Kachel im QField-Stil mit
   einer weißen Ortsmarke, die in eine Import-Ablage hinabführt.

In beiden Fällen öffnet sich der Dialog *Import aus QField*: QGIS **friert
nicht ein**, da das Kopieren der Fotos und der WebDAV-Zugriff in einem
separaten Thread laufen.

---

## 3. Quelle auswählen: Ordner oder ZIP-Archiv

1. Klicken Sie auf **Durchsuchen…** und wählen Sie den
   **QField-Projektordner**, oder klicken Sie auf **ZIP-Archiv…** und wählen
   Sie ein **`.zip`**-Archiv des QField-Projekts (die Dateiauswahl filtert
   auf `*.zip`). In beiden Fällen erscheint der gewählte Pfad im selben
   Quellfeld.
2. Wählen Sie einen Ordner, **durchsucht** der Dialog die GeoPackages und
   füllt das Kombinationsfeld **Fundort** automatisch mit den gefundenen
   Fundorten.
3. Wählen Sie ein ZIP-Archiv, wird es **automatisch in einen temporären
   Ordner entpackt** und das Kombinationsfeld **Fundort** setzt sich auf
   **Alle Fundorte** zurück (aus einem Zip erfolgt kein Vorab-Scan der
   Fundorte): Der Import (Vorschau/Probelauf oder Import, einschließlich
   Fotos und Thumbnails) läuft auf dem entpackten Verzeichnisbaum, und der
   temporäre Ordner wird am Ende des Vorgangs **automatisch entfernt**,
   auch im Fehlerfall.
4. Wählen Sie einen bestimmten Fundort oder belassen Sie **Alle Fundorte**, um
   alles zu importieren.

> Während ein Import läuft, sind sowohl **Durchsuchen…** als auch
> **ZIP-Archiv…** **deaktiviert**, wie alle anderen Dialogelemente auch.

> Ist das gewählte Archiv **beschädigt oder ungültig**, wird ein eindeutiger
> Fehler angezeigt: **„Archivio ZIP non valido o corrotto: …“**. Enthält das
> Zip keine **`.gpkg`**-Datei, erscheint stattdessen die übliche Meldung
> „keine Layer gefunden“.

---

## 4. Import-Optionen

| Option | Bedeutung |
|---|---|
| **SRID (leer = aus GPKG)** | Referenzsystem; leer lassen, um es aus dem GeoPackage zu lesen |
| **Foto-Ziel** | vorbelegt mit dem konfigurierten Medienordner (lokal oder WebDAV) |
| **Geometrien deduplizieren** | verhindert das erneute Einfügen bereits vorhandener identischer Geometrien |
| **Fotos kopieren** | kopiert die Fotos in das Medien-Backend |
| **Thumbnails erzeugen** | erstellt automatisch Vorschaubilder der Fotos |

Die drei Kontrollkästchen sind **standardmäßig aktiviert**.

---

## 5. Vorschau (Probelauf)

Klicken Sie auf **Vorschau (Probelauf)**: Der gesamte Import wird als
**Simulation** ausgeführt und **schreibt nichts** in die Datenbank. Das Protokoll
zeigt:

- wie viele **SE**, **Funde**, **Geometrien**, **Höhenpunkte**, **Fotos** und
  **Verknüpfungen** importiert würden;
- genau **welche leeren Felder** vorhandener Datensätze gefüllt würden.

Dies ist der Schritt, mit dem Sie stets das Ergebnis prüfen sollten, bevor Sie
schreiben.

---

## 6. Importieren

Klicken Sie auf **Importieren** (es wird eine **Bestätigung** verlangt). Der
Vorgang:

- **hängt** die Datensätze in **einer einzigen Transaktion** an;
- **dupliziert** vorhandene SE und Funde **nicht**: Er füllt **nur deren leere
  Felder** und überschreibt bereits vorhandene Werte nie;
- **kopiert die Fotos** in das Medien-Backend und **erzeugt automatisch deren
  Thumbnails**;
- weist den importierten Datensätzen eine **`node_uuid`** zu und markiert sie mit
  **`created_by = 'qfield_import'`**.

---

## 7. Nach dem Import

Prüfen Sie die **stratigraphischen Beziehungen** der importierten SE: Sie werden
**nicht automatisch abgeleitet** und müssen im SE-Formular von Hand ergänzt
werden.

---

## 8. Alternative über die Kommandozeile (CLI)

Für fortgeschrittene oder Headless-Anwendungen steht ein CLI-Skript zur
Verfügung. Der **Probelauf ist das Standardverhalten**; fügen Sie `--apply`
hinzu, um tatsächlich zu schreiben. Der Parameter `--qfield-dir` akzeptiert
sowohl den **Projektordner** als auch ein **`.zip`**-Archiv: Verweist er auf
ein Zip, wird es automatisch in einen temporären Ordner entpackt, der am Ende
des Laufs entfernt wird. Eine nicht existierende Quelle beendet das Skript mit
dem Fehler **„Sorgente non trovata (cartella o archivio .zip): …“**.

```bash
# Vorschau (Probelauf, Standard) aus einem Ordner
python3 scripts/import_qfield.py --qfield-dir <Ordner>

# Vorschau (Probelauf, Standard) aus einem ZIP-Archiv
python3 scripts/import_qfield.py --qfield-dir <Archiv.zip>

# Echter Import
python3 scripts/import_qfield.py --qfield-dir <Ordner> --apply
```

---

*PyArchInit-Dokumentation — Juli 2026*
