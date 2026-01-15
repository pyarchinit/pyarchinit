# Tutorial 30: KI-Datenbankabfrage (Text2SQL)

## Einführung

**KI-Datenbankabfrage** ist eine fortgeschrittene PyArchInit-Funktion, die das Abfragen der archäologischen Datenbank in **natürlicher Sprache** ermöglicht. Das System konvertiert Fragen automatisch in SQL-Abfragen mithilfe künstlicher Intelligenz.

### Funktionsweise

1. Der Benutzer stellt eine Frage auf Deutsch/Englisch
2. Die KI analysiert die Anfrage
3. Generiert die entsprechende SQL-Abfrage
4. Führt die Abfrage auf der Datenbank aus
5. Gibt die Ergebnisse zurück

### Beispielfragen

- *"Finde alle Keramikfunde vom Fundort Römische Villa"*
- *"Zeige die SE der römischen Periode im Areal 1000"*
- *"Wie viele Individuen wurden in den Gräbern gefunden?"*
- *"Liste die Strukturen mit mittelalterlicher Datierung"*

## Zugriff

### Vom SE-/Fund-Formular
Eigener Tab **"KI-Abfrage"** oder **"Text2SQL"**

### Über Menü
**PyArchInit** → **AI Query Database**

## Oberfläche

### Abfrage-Panel

```
+--------------------------------------------------+
|         SQL-Generierung mit KI                    |
+--------------------------------------------------+
| Generierungsmodus:                                |
|   (o) OpenAI GPT-4 (API bereits konfiguriert)    |
|   ( ) Ollama (lokales Modell)                    |
|   ( ) Kostenlose API (falls verfügbar)           |
+--------------------------------------------------+
| Ollama-Modell: [llama3.2 v] [Ollama überprüfen]  |
+--------------------------------------------------+
| Eingabe:                                          |
|   Datenbanktyp: [sqlite | postgresql]            |
|                                                   |
|   Abfrage beschreiben:                           |
|   +--------------------------------------------+ |
|   | Finde alle Keramikfunde vom Fundort        | |
|   | Römische Villa mit Datierung 1.-2. Jh.     | |
|   +--------------------------------------------+ |
+--------------------------------------------------+
| [SQL generieren]  [Zurücksetzen]                 |
+--------------------------------------------------+
| Generierte SQL-Abfrage:                           |
|   +--------------------------------------------+ |
|   | SELECT * FROM inventario_materiali_table   | |
|   | WHERE sito = 'Römische Villa'              | |
|   | AND tipo_reperto LIKE '%keramik%'          | |
|   +--------------------------------------------+ |
| [Abfrage erklären] [Kopieren] [Ausführen]        |
+--------------------------------------------------+
| Erklärung:                                        |
|   Die Abfrage wählt alle Felder aus der...       |
+--------------------------------------------------+
```

## Generierungsmodi

### 1. OpenAI GPT-4

- **Voraussetzungen**: OpenAI-API-Key konfiguriert
- **Qualität**: Ausgezeichnet
- **Kosten**: Nach Verbrauch (API)
- **Geschwindigkeit**: Schnell

### 2. Ollama (Lokal)

- **Voraussetzungen**: Ollama installiert und gestartet
- **Qualität**: Gut-Ausgezeichnet (modellabhängig)
- **Kosten**: Kostenlos
- **Geschwindigkeit**: Hardware-abhängig

### 3. Kostenlose API

- **Voraussetzungen**: Internetverbindung
- **Qualität**: Variabel
- **Kosten**: Kostenlos
- **Einschränkungen**: Mögliches Rate-Limiting

## Konfiguration

### OpenAI

1. API-Key von [OpenAI](https://platform.openai.com/) erhalten
2. In **PyArchInit** → **Konfiguration** → **API-Keys** konfigurieren
3. "OpenAI GPT-4" im Modus auswählen

### Ollama

1. Ollama von [ollama.ai](https://ollama.ai/) installieren
2. Ollama starten: `ollama serve`
3. Modell herunterladen: `ollama pull llama3.2`
4. "Ollama" auswählen und Verbindung überprüfen

### Empfohlene Ollama-Modelle

| Modell | Größe | SQL-Qualität |
|--------|-------|--------------|
| llama3.2 | 2GB | Gut |
| mistral | 4GB | Ausgezeichnet |
| codellama | 7GB | Hervorragend für SQL |
| qwen2.5-coder | 4GB | Ausgezeichnet für Code |

## Verwendung

### 1. Frage formulieren

Im Eingabefeld beschreiben, was gesucht werden soll:
- Natürliche Sprache verwenden
- Möglichst spezifisch sein
- Tabellen/Felder erwähnen wenn bekannt

### 2. SQL generieren

1. Auf **"SQL generieren"** klicken
2. Verarbeitung abwarten
3. Generierte Abfrage anzeigen

### 3. Abfrage überprüfen

- Generierte SQL-Abfrage lesen
- Auf **"Abfrage erklären"** für Verständnis klicken
- Logische Korrektheit überprüfen

### 4. Abfrage ausführen

- **"Kopieren"**: In Zwischenablage kopieren
- **"Ausführen"**: Direkt im System ausführen

## Datenbankschema

### Haupttabellen

Das System kennt das PyArchInit-Schema:

| Tabelle | Beschreibung |
|---------|-------------|
| site_table | Archäologische Fundorte |
| us_table | Stratigraphische Einheiten |
| inventario_materiali_table | Funde |
| pottery_table | Keramik |
| tomba_table | Gräber |
| individui_table | Individuen |
| struttura_table | Strukturen |
| periodizzazione_table | Periodisierung |
| campioni_table | Proben |
| documentazione_table | Dokumentation |

### Gängige Felder

Die KI kennt die Hauptfelder:
- `sito` - Fundortname
- `area` - Arealnummer
- `us` - SE-Nummer
- `periodo_iniziale` / `fase_iniziale`
- `datazione_estesa`
- `descrizione` / `interpretazione`

## Abfragebeispiele

### Fundsuche

**Frage**: *"Finde alle Bronzefunde vom Fundort Antikes Rom"*

```sql
SELECT * FROM inventario_materiali_table
WHERE sito = 'Antikes Rom'
AND (tipo_reperto LIKE '%bronzo%' OR definizione LIKE '%bronzo%')
```

### SE-Zählung

**Frage**: *"Wie viele SE gibt es pro Periode im Fundort Villa Adriana?"*

```sql
SELECT periodo_iniziale, COUNT(*) as num_us
FROM us_table
WHERE sito = 'Villa Adriana'
GROUP BY periodo_iniziale
```

### Räumliche Suche

**Frage**: *"Zeige die SE im Areal 1000 mit Höhen unter 10 Metern"*

```sql
SELECT * FROM us_table
WHERE area = '1000'
AND quota_min_usm < 10
```

## Best Practices

### 1. Effektive Fragen

- Spezifisch sein: Fundortnamen, Nummern, Daten
- Angeben, was gewünscht ist: Liste, Anzahl, Details
- Gewünschte Filter erwähnen

### 2. Ergebnisüberprüfung

- Generierte Abfrage immer kontrollieren
- "Abfrage erklären" nutzen wenn unklar
- Bei komplexen Abfragen erst an Teilmenge testen

### 3. Iteration

- Bei falschem Ergebnis Frage umformulieren
- Details hinzufügen wenn Abfrage zu breit
- Vereinfachen wenn Abfrage zu komplex

## Fehlerbehebung

### Abfrage nicht generiert

**Ursachen**:
- API nicht konfiguriert
- Verbindung fehlt
- Frage unverständlich

**Lösungen**:
- API-Konfiguration überprüfen
- Verbindung prüfen
- Frage umformulieren

### Falsche Ergebnisse

**Ursachen**:
- Mehrdeutige Frage
- Feld/Tabelle existiert nicht

**Lösungen**:
- Spezifischer sein
- Tabellen-/Feldnamen überprüfen

### Ollama antwortet nicht

**Ursachen**:
- Ollama läuft nicht
- Modell nicht heruntergeladen

**Lösungen**:
- `ollama serve` starten
- Benötigtes Modell herunterladen

## Referenzen

### Quelldateien
- `modules/utility/textTosql.py` - Klasse MakeSQL
- `modules/utility/database_schema.py` - Datenbankschema

### Externe APIs
- [OpenAI API](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

## Video-Tutorial

### KI-Datenbankabfrage
`[Platzhalter: video_ki_abfrage.mp4]`

**Inhalte**:
- API-Konfiguration
- Effektive Fragenformulierung
- Ergebnisinterpretation
- Best Practices

**Voraussichtliche Dauer**: 15-18 Minuten

---

*Letzte Aktualisierung: Januar 2026*
