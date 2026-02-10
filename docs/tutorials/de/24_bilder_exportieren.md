# Tutorial 24: Bilder exportieren

## Einführung

Die Funktion **Bilder exportieren** ermöglicht den Massenexport von Bildern, die mit archäologischen Datensätzen verknüpft sind, mit automatischer Organisation in Ordnern nach Periode, Phase und Entitätstyp.

## Zugriff

### Über Menü
**PyArchInit** → **Bilder exportieren**

## Oberfläche

### Export-Panel

```
+--------------------------------------------------+
|           Bilder exportieren                      |
+--------------------------------------------------+
| Fundort: [ComboBox Fundortauswahl]               |
| Jahr: [ComboBox Grabungsjahr]                    |
+--------------------------------------------------+
| Exporttyp:                                        |
|   (o) Alle Bilder                                |
|   ( ) Nur SE                                     |
|   ( ) Nur Funde                                  |
|   ( ) Nur Keramik                                |
+--------------------------------------------------+
| [Ordner öffnen]           [Exportieren]          |
+--------------------------------------------------+
```

### Exportoptionen

| Option | Beschreibung |
|--------|-------------|
| Alle Bilder | Gesamtes Fotomaterial exportieren |
| Nur SE | Nur mit SE verknüpfte Bilder exportieren |
| Nur Funde | Nur Fundbilder exportieren |
| Nur Keramik | Nur Keramikbilder exportieren |

## Ausgabestruktur

### Ordnerorganisation

Der Export erstellt eine hierarchische Struktur:

```
pyarchinit_image_export/
└── [Fundortname] - Alle Bilder/
    ├── Periode - 1/
    │   ├── Phase - 1/
    │   │   ├── SE_001/
    │   │   │   ├── foto_001.jpg
    │   │   │   └── foto_002.jpg
    │   │   └── SE_002/
    │   │       └── foto_003.jpg
    │   └── Phase - 2/
    │       └── SE_003/
    │           └── foto_004.jpg
    └── Periode - 2/
        └── ...
```

### Namenskonvention

Die Dateien behalten den Originalnamen, organisiert nach:
1. **Periode** - Anfangsperiode
2. **Phase** - Anfangsphase
3. **Entität** - SE, Fund, etc.

## Exportprozess

### Schritt 1: Parameter auswählen

1. **Fundort** aus ComboBox auswählen
2. **Jahr** auswählen (optional)
3. **Exporttyp** wählen

### Schritt 2: Ausführung

1. Auf **"Exportieren"** klicken
2. Auf Abschluss warten
3. Bestätigungsmeldung

### Schritt 3: Überprüfung

1. Auf **"Ordner öffnen"** klicken
2. Erstellte Struktur überprüfen
3. Vollständigkeit kontrollieren

## Ausgabeordner

### Standardpfad

```
~/pyarchinit/pyarchinit_image_export/
```

### Inhalt

- Nach Fundort organisierte Ordner
- Unterordner nach Periode/Phase
- Originalbilder (nicht skaliert)

## Filter nach Jahr

Die ComboBox **Jahr** ermöglicht:
- Export nur von Bildern einer bestimmten Kampagne
- Organisation des Exports nach Grabungsjahr
- Reduzierung der Exportgröße

## Best Practices

### 1. Vor dem Export

- Bild-Entitäts-Verknüpfungen überprüfen
- SE-Periodisierung kontrollieren
- Ausreichend Speicherplatz sicherstellen

### 2. Während des Exports

- Prozess nicht unterbrechen
- Auf Abschlussmeldung warten

### 3. Nach dem Export

- Ordnerstruktur überprüfen
- Bildvollständigkeit kontrollieren
- Bei Bedarf Backup erstellen

## Typische Verwendungen

### Berichtsvorbereitung

```
1. Fundort auswählen
2. Alle Bilder exportieren
3. Struktur für Berichtskapitel verwenden
```

### Abgabe an Denkmalamt

```
1. Fundort und Jahr auswählen
2. Nach angefordertem Typ exportieren
3. Gemäß ministeriellen Standards organisieren
```

### Kampagnen-Backup

```
1. Am Ende der Kampagne alles exportieren
2. Auf externem Speicher archivieren
3. Integrität überprüfen
```

## Fehlerbehebung

### Unvollständiger Export

**Ursachen**:
- Nicht verknüpfte Bilder
- Falsche Dateipfade

**Lösungen**:
- Verknüpfungen im Medien-Manager überprüfen
- Existenz der Quelldateien kontrollieren

### Falsche Struktur

**Ursachen**:
- Fehlende Periodisierung
- SE ohne Periode/Phase

**Lösungen**:
- SE-Periodisierung ausfüllen
- Allen SE Periode/Phase zuweisen

## Referenzen

### Quelldateien
- `tabs/Images_directory_export.py` - Export-Oberfläche
- `gui/ui/Images_directory_export.ui` - UI-Layout

### Ordner
- `~/pyarchinit/pyarchinit_image_export/` - Export-Ausgabe

---

## Video-Tutorial

### Bilder exportieren
`[Platzhalter: video_bilder_exportieren.mp4]`

**Inhalte**:
- Exportkonfiguration
- Ausgabestruktur
- Archivorganisation

**Voraussichtliche Dauer**: 10-12 Minuten

---

*Letzte Aktualisierung: Januar 2026*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../../pyarchinit_image_export_animation.html)
