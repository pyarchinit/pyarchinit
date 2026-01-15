# Tutorial 28: GeoPackage-Export

## Einführung

Die Funktion **GeoPackage-Export** ermöglicht das Verpacken von Vektor- und Raster-Layern aus PyArchInit in eine einzelne GeoPackage-Datei (.gpkg). Dieses Format ist ideal für das Teilen, Archivieren und die Portabilität von GIS-Daten.

### Vorteile des GeoPackage

| Aspekt | Vorteil |
|--------|---------|
| Einzelne Datei | Alle Daten in einer Datei |
| Portabilität | Einfaches Teilen |
| OGC-Standard | Universelle Kompatibilität |
| Multi-Layer | Vektor und Raster zusammen |
| SQLite-basiert | Leicht und schnell |

## Zugriff

### Über Menü
**PyArchInit** → **In GeoPackage verpacken**

## Oberfläche

### Export-Panel

```
+--------------------------------------------------+
|        GeoPackage-Import                          |
+--------------------------------------------------+
| Ziel:                                             |
|   [____________________________] [Durchsuchen]   |
+--------------------------------------------------+
| [Vektorlayer exportieren]                        |
| [Rasterlayer exportieren]                        |
+--------------------------------------------------+
```

## Vorgehensweise

### Vektorlayer exportieren

1. Zu exportierende Layer im QGIS-Layer-Panel auswählen
2. GeoPackage-Export-Werkzeug öffnen
3. Zielpfad und Dateinamen angeben
4. Auf **"Vektorlayer exportieren"** klicken

### Rasterlayer exportieren

1. Rasterlayer im Layer-Panel auswählen
2. Ziel angeben (dieselbe oder neue Datei)
3. Auf **"Rasterlayer exportieren"** klicken

### Kombinierter Export

Um Vektor und Raster in dasselbe GeoPackage einzuschließen:
1. Zuerst die Vektorlayer exportieren
2. Dann die Rasterlayer in dieselbe Datei exportieren
3. Das System fügt die Layer zum bestehenden GeoPackage hinzu

## Layer-Auswahl

### Methode

1. Im QGIS-Layer-Panel die gewünschten Layer auswählen
   - Strg+Klick für Mehrfachauswahl
   - Umschalt+Klick für Bereich
2. GeoPackage-Export öffnen
3. Die ausgewählten Layer werden exportiert

### Empfohlene Layer

| Layer | Typ | Hinweise |
|-------|-----|----------|
| pyunitastratigrafiche | Vektor | Ablagerungs-SE |
| pyunitastratigrafiche_usm | Vektor | Mauerwerks-SE |
| pyarchinit_quote | Vektor | Höhenpunkte |
| pyarchinit_siti | Vektor | Fundorte |
| Orthofoto | Raster | Grabungs-Orthofoto |

## Ausgabe

### GeoPackage-Struktur

```
ausgabe.gpkg
├── pyunitastratigrafiche (Vektor)
├── pyunitastratigrafiche_usm (Vektor)
├── pyarchinit_quote (Vektor)
└── orthofoto (Raster)
```

### Standardpfad

```
~/pyarchinit/pyarchinit_DB_folder/
```

## Exportoptionen

### Vektorlayer

- Erhält Originalgeometrien
- Bewahrt alle Attribute
- Konvertiert automatisch Namen mit Leerzeichen (verwendet Unterstriche)

### Rasterlayer

- Unterstützt gängige Formate (GeoTIFF, etc.)
- Behält Georeferenzierung bei
- Bewahrt Bezugssystem

## Typische Verwendungen

### Projektfreigabe

```
1. Alle Projektlayer auswählen
2. In GeoPackage exportieren
3. Die .gpkg-Datei teilen
4. Empfänger öffnet direkt in QGIS
```

### Kampagnenarchivierung

```
1. Am Ende der Kampagne finale Layer auswählen
2. In datiertes GeoPackage exportieren
3. Mit Dokumentation archivieren
```

### GIS-Backup

```
1. Periodisch aktuellen Stand exportieren
2. Datierte Versionen behalten
3. Für Notfallwiederherstellung verwenden
```

## Best Practices

### 1. Vor dem Export

- Vollständigkeit der Layer überprüfen
- Bezugssystem kontrollieren
- QGIS-Projekt speichern

### 2. Benennung

- Beschreibende Dateinamen verwenden
- Datum im Namen einschließen
- Sonderzeichen vermeiden

### 3. Überprüfung

- Erstelltes GeoPackage öffnen
- Alle Layer überprüfen
- Attribute kontrollieren

## Fehlerbehebung

### Export fehlgeschlagen

**Ursachen**:
- Ungültiger Layer
- Nicht beschreibbarer Pfad
- Unzureichender Speicherplatz

**Lösungen**:
- Layer-Gültigkeit überprüfen
- Ordnerberechtigungen kontrollieren
- Speicherplatz freigeben

### Fehlende Layer

**Ursache**: Layer nicht ausgewählt

**Lösung**: Auswahl im Layer-Panel überprüfen

### Raster nicht exportiert

**Ursachen**:
- Format nicht unterstützt
- Quelldatei nicht zugänglich

**Lösungen**:
- Raster in GeoTIFF konvertieren
- Quelldateipfad überprüfen

## Referenzen

### Quelldateien
- `tabs/gpkg_export.py` - Export-Oberfläche
- `gui/ui/gpkg_export.ui` - UI-Layout

### Dokumentation
- [GeoPackage Standard](https://www.geopackage.org/)
- [QGIS GeoPackage Support](https://docs.qgis.org/)

---

## Video-Tutorial

### GeoPackage-Export
`[Platzhalter: video_geopackage.mp4]`

**Inhalte**:
- Layer-Auswahl
- Export von Vektor und Raster
- Ausgabeüberprüfung
- Best Practices

**Voraussichtliche Dauer**: 8-10 Minuten

---

*Letzte Aktualisierung: Januar 2026*
