# Tutorial 37: Palimpsest-Analyse (palimpsestr / SEF)

## Einführung

PyArchInit integriert **palimpsestr**, eine R-Bibliothek, die das Modell
**SEF — Stratigraphic Entanglement Field** für die *probabilistische
Zerlegung von Palimpsesten* anwendet: Sie trennt die Funde einer komplexen
Ablagerung auf statistischer Basis in latente **Phasen** und schätzt für jede
stratigraphische Einheit (US) deren Phasenzugehörigkeit, die Residualität und
etwaige **Intrusionen**.

Der Dialog **palimpsestr** (Symbol mit farbigen Schichten in der pyArchInit-
Werkzeugleiste) ermöglicht es:

- **Fit SEF**: die Phasen zu schätzen und Vektorlayer (Phasen, Verbindungen)
  sowie eine Diagnosetabelle zu erzeugen;
- **Intrusionen**: chronologisch fehlplatzierte Funde/US zu ermitteln;
- **Erzählender Bericht (PDF/DOCX)**: ein interpretativer Bericht mit Text,
  Diagnosegrafiken und Tabellen;
- **KI-Bericht**: ein beschreibender Bericht, der von spezialisierten KI-Agenten
  in jeder Sprache von pyArchInit erstellt wird;
- sowohl mit **SQLite/Spatialite** als auch mit **PostgreSQL/PostGIS** zu
  arbeiten;
- eine **absolute Chronologie** (mit OxCal kalibrierte Daten) anstelle der
  freitextlichen Datierung zu verwenden.

> Erfordert palimpsestr **≥ 0.22.0**, installiert in der R-Bibliothek, die vom
> *Processing R Provider* von QGIS verwendet wird.

---

## 1. Voraussetzungen

- **R** installiert und das Plugin **Processing R Provider** in QGIS aktiviert.
- R-Paket **palimpsestr ≥ 0.22.0** (und Abhängigkeiten: `sf`, `DBI`, `RSQLite`;
  `RPostgres` für PostgreSQL).
- Für den **PDF/DOCX-Bericht**: **pandoc** und eine **LaTeX**-Engine (z. B.
  TinyTeX). Fehlen diese, werden dennoch die Markdown-Erzählung `.md` + die
  PNG-Abbildungen erzeugt.
- Für die **OxCal-Chronologie**: R-Paket **oxcAAR** und **Java** (die
  OxCal-Engine wird beim ersten Gebrauch automatisch von
  `oxcAAR::quickSetupOxcal()` heruntergeladen).
- Für den **KI-Bericht**: ein konfigurierter LLM-Provider (OpenAI, Anthropic,
  Ollama oder LM Studio) über die Auswahl des KI-Providers.

Die R-Skripte (`.rsx`) sind **im Plugin enthalten** und werden beim Öffnen des
Dialogs automatisch installiert; die Schaltfläche *Install/update R scripts*
installiert sie manuell neu.

---

## 2. Den Dialog öffnen

1. pyArchInit-Werkzeugleiste → Analysemenü → **palimpsestr - Analisi
   palinsesti**.
2. Der Dialog zeigt die aktive Datenbank (SQLite oder PostgreSQL) und die
   Parameter an.

---

## 3. Analyseparameter

| Parameter | Bedeutung |
|---|---|
| **Anzahl der Phasen (K)** | wie viele latente Phasen geschätzt werden (2–12) |
| **Klassenmodell** | `multinomial` (empfohlen) oder `gaussian` (Legacy) |
| **Rausch-/Ausreißerkomponente** | aktiviert die Schätzung von Intrusionen/Residualität |
| **Intrusionsschwelle** | minimaler Posterior, um einen Fund als Intrusion zu markieren |
| **Funde (source)** | **Beide** / **Materialien** / **Keramik** |
| **Standort (Filter)** | beschränkt die Analyse auf einen Standort (leer = alle) |

Die Auswahl **Funde** wird von Fit, Intrusionen und Bericht gemeinsam genutzt:
Alle berücksichtigen dieselbe Fundauswahl.

---

## 4. Fit SEF und Intrusionen

- **Fit SEF model**: führt die Zerlegung aus und lädt die Layer *SEF phases*
  (nach Phase eingefärbte Punkte) und *SEF links* sowie die Diagnosetabelle in
  das Projekt.
- **Detect intrusions**: lädt einen Punktlayer mit `intrusion_prob`,
  `direction` und `intrusion_type`.

---

## 5. Erzählender Bericht (PDF/DOCX)

1. Lege **Berichtssprache** (Italienisch/Englisch) und **Format** (PDF+DOCX /
   PDF / DOCX) fest.
2. Drücke **Genera report (PDF/DOCX)**.
3. Das **Ergebnisfeld** zeigt die Erzählung an, indem es die `.md`-Datei liest,
   die **immer** neben der Ausgabe geschrieben wird.
4. Die Schaltflächen **Apri PDF / Apri DOCX / Apri cartella** werden je nach den
   tatsächlich erzeugten Dateien aktiviert.

> Erscheinen nur die `.md`-Erzählung und die Abbildungen (kein PDF/DOCX), fehlen
> pandoc/LaTeX: Der Dialog versucht, sie automatisch zum `PATH` hinzuzufügen;
> andernfalls installiere sie (in R: `tinytex::install_tinytex()`).

---

## 6. PostgreSQL / PostGIS

Die Analysen funktionieren auch mit der aktiven **PostgreSQL**-Verbindung von
pyArchInit, nicht nur mit SQLite. Der Dialog wandelt die Verbindungs-URL
automatisch in eine libpq-DSN um und übergibt sie an die Algorithmen (Parameter
`PG_connection`); bei aktivem PostgreSQL wird keine SQLite-Datei angefordert.

---

## 7. Absolute Chronologie (OxCal)

Die optionale Tabelle **`palimpsest_chronology`** liefert **pro US kalibrierte
Daten** (Kalenderjahre, v. Chr. negativ), die palimpsestr **anstelle** der
freitextlichen `datazione` verwendet.

1. Drücke **Cronologia assoluta (OxCal)…**.
2. **Crea/aggiorna tabella**: erstellt `palimpsest_chronology` auf dem aktiven
   Backend (SQLite oder PostgreSQL), idempotent.
3. **Live-Kalibrierung**: Gib für jede US die Radiokarbondaten ein
   (BP ± Fehler, Laborcode) und drücke **Calibra e salva (OxCal)**: Ein
   R-Treiber (`oxcAAR::oxcalCalibrate` + `palimpsestr::chronology_from_oxcal`)
   berechnet die Kalenderintervalle und speichert sie als `start`/`end`.
4. **CSV-Import**: Importiere alternativ eine bereits kalibrierte CSV mit den
   Spalten `sito, area, us, start, end, lab_code, source`.

Die Beispieldaten liegen in `docs/examples/`:
`palimpsest_oxcal_samples_villa_romana.csv` (C14-Proben für die Kalibrierung) und
`palimpsest_chronology_villa_romana.csv` (bereits kalibrierte Intervalle).

> Sobald die Tabelle befüllt ist, wird sie **automatisch** erkannt — an den
> Algorithmen muss nichts geändert werden.

---

## 8. KI-Bericht (beschreibende Analyse)

Die Schaltfläche **Report AI (analisi descrittiva)…** erzeugt einen
**beschreibenden, didaktischen** Bericht mit einer Pipeline aus
**spezialisierten KI-Agenten**:

1. **Methodologe** — erläutert die Entscheidungen: das Modell (multinomial vs.
   gaussian), den Wert von **K** und die ihn stützenden diagnostischen Belege,
   die Rauschkomponente und die **Schwelle**, die Fundauswahl und die Nutzung
   der OxCal-Chronologie; benennt Grenzen und Vorbehalte.
2. **Analyst** — interpretiert Phasen, Chronologie (mit den absoluten Daten,
   sofern vorhanden), Residualität/Intrusionen und das räumliche Muster.
3. **Redakteur** — verfasst einen einzigen kohärenten Bericht und verweist auf
   die Abbildungen.

Vorgehen:

1. Wähle den **KI-Provider** und das Modell in der Auswahl.
2. Wähle die **Berichtssprache** (alle Sprachen von pyArchInit:
   it, en, de, es, fr, pt, ca, ro, el, ar).
3. Drücke **Genera report AI**: Der Text erscheint in Echtzeit.
4. Speichere als **DOCX** (mit eingebetteten Abbildungen) oder **Markdown**.

Der Bericht erläutert ausdrücklich, **warum** das Modell, das K und die Schwelle
gewählt wurden, und interpretiert die Ergebnisse verständlich — ideal für den
Grabungsbericht.

---

## 9. Daten bearbeiten, OxCal-Grafik, PDF und ein Hinweis zu taf

- **Gespeicherte Daten sind bearbeitbar**: Der Dialog *Cronologia assoluta*
  **lädt beim Öffnen** die bereits in `palimpsest_chronology` vorhandenen Daten
  (Schaltfläche *Ricarica dal DB*). Du kannst die Spalten **start/end** von Hand
  bearbeiten und **Salva modifiche (start/end)** drücken oder neue C14-Daten
  eingeben und *Calibra e salva* drücken. Die Daten **bleiben** in der Datenbank
  erhalten — sie müssen nicht jedes Mal neu eingegeben werden.
- **Kalibrierungsgrafik**: Nach *Calibra e salva* zeigen die Schaltflächen
  **Mostra grafico OxCal** / **Esporta grafico (PNG)** ein Feld pro US mit der
  Wahrscheinlichkeitskurve, dem 95%-HPD-Band und dem Kalenderintervall.
- **KI-Bericht als PDF**: Neben DOCX und Markdown kann der KI-Bericht auch als
  **PDF** gespeichert werden (Schaltfläche *Salva PDF…*), mit eingebetteten
  Tabellen und Abbildungen.
- **Taphonomischer Wert (taf)**: ein **interpretativer** Wert in `[0,1]`
  (0 = vollständig gestörter/umgelagerter Fund, 1 = unversehrt in situ), der die
  Funde bei der Schätzung gewichtet. Er wird **nicht automatisch berechnet**: Der
  Archäologe vergibt ihn anhand des Ablagerungskontexts (z. B. 1.0 In-situ-
  Ablagerungen; 0.5–0.7 Akkumulations-/Planierungsschichten; 0.3 eindeutig
  umgelagerte Verfüllungen).
- **Zu beachtende Grenzen** (der KI-Bericht nennt sie automatisch): Das Modell
  setzt eine **horizontale Stratigraphie** voraus (z als chronologischer Proxy;
  Vorsicht bei Grubenverfüllungen, Einstürzen, Terrassierungen); die **Auflösung
  ist durch die Daten begrenzt**: Bei US-Zentroid-Koordinaten und an die US
  gebundenen Daten spiegeln ein PDI≈1 und eine Entropie≈0 die **Erfassung**
  wider, nicht eine perfekt aufgelöste Sequenz.

---

*PyArchInit-Dokumentation — Juni 2026*
