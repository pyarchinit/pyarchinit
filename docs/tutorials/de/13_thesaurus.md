# Tutorial 13: Thesaurus-Verwaltung

## Einführung

Der **Thesaurus** von PyArchInit ist das zentralisierte System zur Verwaltung kontrollierter Vokabulare. Er ermöglicht die Definition und Pflege von Wertelisten, die in allen Formularen des Plugins verwendet werden, und gewährleistet terminologische Konsistenz und erleichtert die Suche.

### Hauptfunktionen

- Vokabularverwaltung für jedes Formular
- Mehrsprachige Unterstützung
- Kürzel und erweiterte Beschreibungen
- Integration mit GPT für Vorschläge
- Import/Export aus CSV-Dateien

---

## Zugriff auf den Thesaurus

### Über Menü
1. Menü **PyArchInit** in der QGIS-Menüleiste
2. **Thesaurus** (oder **Thesaurus form**) auswählen

### Über Toolbar
1. PyArchInit-Toolbar finden
2. Auf das **Thesaurus**-Symbol (Buch/Wörterbuch) klicken

---

## Oberflächenübersicht

### Hauptbereiche

| # | Bereich | Beschreibung |
|---|---------|-------------|
| 1 | DBMS-Toolbar | Navigation, Suche, Speichern |
| 2 | Tabellenauswahl | Auswahl des zu konfigurierenden Formulars |
| 3 | Kürzelfelder | Code, Erweiterung, Typologie |
| 4 | Beschreibung | Detaillierte Beschreibung des Begriffs |
| 5 | Sprache | Sprachauswahl |
| 6 | Werkzeuge | CSV-Import, GPT-Vorschläge |

---

## Thesaurus-Felder

### Tabellenname

**Feld**: `comboBox_nome_tabella`
**Datenbank**: `nome_tabella`

Wählt das Formular, für das Werte definiert werden sollen.

**Verfügbare Tabellen:**
| Tabelle | Beschreibung |
|---------|-------------|
| `us_table` | SE/USM-Formular |
| `site_table` | Fundort-Formular |
| `periodizzazione_table` | Periodisierung |
| `inventario_materiali_table` | Materialinventar |
| `pottery_table` | Keramik-Formular |
| `campioni_table` | Proben-Formular |
| `documentazione_table` | Dokumentation |
| `tomba_table` | Grab-Formular |
| `individui_table` | Individuen-Formular |
| `fauna_table` | Archäozoologie |
| `ut_table` | UT-Formular |

### Kürzel

**Feld**: `comboBox_sigla`
**Datenbank**: `sigla`

Kurzcode/Abkürzung des Begriffs.

**Beispiele:**
- `MR` für Mauer
- `SE` für Stratigraphische Einheit
- `KR` für Keramik

### Erweitertes Kürzel

**Feld**: `comboBox_sigla_estesa`
**Datenbank**: `sigla_estesa`

Vollständige Form des Begriffs.

**Beispiele:**
- `Perimetrale Mauer`
- `Stratigraphische Einheit`
- `Gebrauchskeramik`

### Beschreibung

**Feld**: `textEdit_descrizione_sigla`
**Datenbank**: `descrizione`

Detaillierte Beschreibung des Begriffs, Definition, Verwendungshinweise.

### Kürzeltypologie

**Feld**: `comboBox_tipologia_sigla`
**Datenbank**: `tipologia_sigla`

Numerischer Code, der das Zielfeld identifiziert.

**Code-Struktur:**
```
X.Y wobei:
X = Tabellennummer
Y = Feldnummer
```

**Beispiele für us_table:**
| Code | Feld |
|------|------|
| 1.1 | Stratigraphische Definition |
| 1.2 | Entstehungsweise |
| 1.3 | SE-Typ |

### Sprache

**Feld**: `comboBox_lingua`
**Datenbank**: `lingua`

Sprache des Begriffs.

**Unterstützte Sprachen:**
- IT (Italienisch)
- EN_US (Englisch)
- DE (Deutsch)
- FR (Französisch)
- ES (Spanisch)
- AR (Arabisch)
- CA (Katalanisch)

---

## Hierarchie-Felder

### Parent-ID

**Feld**: `comboBox_id_parent`
**Datenbank**: `id_parent`

ID des übergeordneten Begriffs (für hierarchische Strukturen).

### Parent-Kürzel

**Feld**: `comboBox_parent_sigla`
**Datenbank**: `parent_sigla`

Kürzel des übergeordneten Begriffs.

### Hierarchie-Ebene

**Feld**: `spinBox_hierarchy`
**Datenbank**: `hierarchy_level`

Ebene in der Hierarchie (0=Wurzel, 1=erste Ebene, usw.).

---

## Spezielle Funktionen

### GPT-Vorschläge

Die Schaltfläche "Vorschläge" verwendet OpenAI GPT für:
- Automatische Beschreibungsgenerierung
- Bereitstellung von Wikipedia-Referenzlinks
- Definitionsvorschläge im archäologischen Kontext

**Verwendung:**
1. Einen Begriff unter "Erweitertes Kürzel" auswählen oder eingeben
2. Auf "Vorschläge" klicken
3. GPT-Modell auswählen
4. Auf Generierung warten
5. Überprüfung und Speicherung

**Hinweis:** Erfordert konfigurierte OpenAI API-Key.

### CSV-Import

Für SQLite-Datenbanken können Vokabulare aus CSV-Dateien importiert werden.

**Erforderliches CSV-Format:**
```csv
nome_tabella,sigla,sigla_estesa,descrizione,tipologia_sigla,lingua
us_table,MR,Mauer,Mauerstruktur,1.3,DE
us_table,BO,Boden,Begehungsfläche,1.3,DE
```

**Vorgehensweise:**
1. Auf "CSV importieren" klicken
2. Datei auswählen
3. Import bestätigen
4. Importierte Daten überprüfen

---

## Operativer Arbeitsablauf

### Neuen Begriff hinzufügen

1. **Thesaurus öffnen**
   - Über Menü oder Toolbar

2. **Neuer Datensatz**
   - Auf "New Record" klicken

3. **Tabelle auswählen**
   ```
   Tabellenname: us_table
   ```

4. **Begriff definieren**
   ```
   Kürzel: BR
   Erweitertes Kürzel: Brunnen
   Kürzeltypologie: 1.3
   Sprache: DE
   ```

5. **Beschreibung**
   ```
   In den Boden gegrabene Struktur zur
   Wasserversorgung. Gewöhnlich runde Form
   mit Auskleidung aus Stein oder Ziegeln.
   ```

6. **Speichern**
   - Auf "Save" klicken

### Begriffe suchen

1. Auf "New Search" klicken
2. Kriterien ausfüllen:
   - Tabellenname
   - Kürzel oder erweitertes Kürzel
   - Sprache
3. Auf "Search" klicken
4. Zwischen Ergebnissen navigieren

### Bestehenden Begriff bearbeiten

1. Zu ändernden Begriff suchen
2. Erforderliche Felder bearbeiten
3. Auf "Save" klicken

---

## Organisation der Typologie-Codes

### Empfohlene Struktur

Für jede Tabelle die Codes systematisch organisieren:

**us_table (1.x):**
| Code | Feld |
|------|------|
| 1.1 | Stratigraphische Definition |
| 1.2 | Entstehungsweise |
| 1.3 | SE-Typ |
| 1.4 | Konsistenz |
| 1.5 | Farbe |

**inventario_materiali_table (2.x):**
| Code | Feld |
|------|------|
| 2.1 | Fundtyp |
| 2.2 | Materialklasse |
| 2.3 | Definition |
| 2.4 | Erhaltungszustand |

**pottery_table (3.x):**
| Code | Feld |
|------|------|
| 3.1 | Form |
| 3.2 | Ware |
| 3.3 | Ton |
| 3.4 | Oberflächenbehandlung |

---

## Best Practices

### Terminologische Konsistenz

- Immer dieselben Begriffe für dieselben Konzepte verwenden
- Undokumentierte Synonyme vermeiden
- Angenommene Konventionen dokumentieren

### Mehrsprachigkeit

- Begriffe in allen erforderlichen Sprachen erstellen
- Entsprechungen zwischen Sprachen beibehalten
- Offizielle Übersetzungen verwenden, wenn verfügbar

### Hierarchie

- Hierarchische Struktur für verwandte Begriffe verwenden
- Ebenen klar definieren
- Beziehungen dokumentieren

### Wartung

- Vokabulare regelmäßig überprüfen
- Veraltete Begriffe löschen
- Beschreibungen aktualisieren

---

## Fehlerbehebung

### Problem: Begriff nicht in ComboBox sichtbar

**Ursache:** Falscher Typologie-Code oder nicht übereinstimmende Sprache.

**Lösung:**
1. tipologia_sigla-Code überprüfen
2. Eingestellte Sprache kontrollieren
3. Überprüfen, dass der Datensatz gespeichert ist

### Problem: CSV-Import fehlgeschlagen

**Ursache:** Falsches Dateiformat.

**Lösung:**
1. CSV-Struktur überprüfen
2. Trennzeichen kontrollieren (Komma)
3. Kodierung überprüfen (UTF-8)

### Problem: GPT-Vorschläge funktionieren nicht

**Ursache:** API-Key fehlt oder ungültig.

**Lösung:**
1. API-Key-Konfiguration überprüfen
2. Internetverbindung kontrollieren
3. OpenAI-Guthaben überprüfen

---

## Referenzen

### Datenbank

- **Tabelle**: `pyarchinit_thesaurus_sigle`
- **Mapper-Klasse**: `PYARCHINIT_THESAURUS_SIGLE`
- **ID**: `id_thesaurus_sigle`

### Quelldateien

- **UI**: `gui/ui/Thesaurus.ui`
- **Controller**: `tabs/Thesaurus.py`

---

## Video-Tutorial

### Vokabularverwaltung
**Dauer**: 10-12 Minuten
- Thesaurus-Struktur
- Begriffe hinzufügen
- Code-Organisation

[Platzhalter Video: video_thesaurus_verwaltung.mp4]

### Mehrsprachigkeit und Import
**Dauer**: 8-10 Minuten
- Sprachkonfiguration
- Import aus CSV
- GPT-Vorschläge

[Platzhalter Video: video_thesaurus_erweitert.mp4]

---

*Letzte Aktualisierung: Januar 2026*
*PyArchInit - Archäologisches Datenverwaltungssystem*

---

## Interaktive Animation

Erkunden Sie die interaktive Animation, um mehr über dieses Thema zu erfahren.

[Interaktive Animation öffnen](../animations/pyarchinit_thesaurus_animation.html)
