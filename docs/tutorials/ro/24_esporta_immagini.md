# Tutorial 24: Exportul imaginilor

## Introducere

Functia **Export imagini** permite exportul in lot al imaginilor asociate cu inregistrarile arheologice, organizandu-le automat in foldere dupa perioada, faza si tipul entitatii.

## Acces

### Din meniu
**PyArchInit** > **Export imagini**

## Interfata

### Panoul de export

```
+--------------------------------------------------+
|           Export imagini                          |
+--------------------------------------------------+
| Sit: [ComboBox selectie sit]                     |
| An: [ComboBox an excavare]                       |
+--------------------------------------------------+
| Tipul exportului:                                 |
|   [o] Toate imaginile                            |
|   [ ] Doar US                                    |
|   [ ] Doar descoperiri                           |
|   [ ] Doar ceramica                              |
+--------------------------------------------------+
| [Deschide folder]           [Export]              |
+--------------------------------------------------+
```

### Optiuni de export

| Optiune | Descriere |
|---------|-----------|
| Toate imaginile | Export tot materialul fotografic |
| Doar US | Export doar imagini legate de US |
| Doar descoperiri | Export doar imagini de descoperiri |
| Doar ceramica | Export doar imagini de ceramica |

## Structura iesirii

### Organizarea folderelor

Exportul creeaza o structura ierarhica:

```
pyarchinit_image_export/
+-- [Numele sitului] - Toate imaginile/
    +-- Perioada - 1/
    |   +-- Faza - 1/
    |   |   +-- US_001/
    |   |   |   +-- foto_001.jpg
    |   |   |   +-- foto_002.jpg
    |   |   +-- US_002/
    |   |       +-- foto_003.jpg
    |   +-- Faza - 2/
    |       +-- US_003/
    |           +-- foto_004.jpg
    +-- Perioada - 2/
        +-- ...
```

### Conventie de denumire

Fisierele isi pastreaza numele original, organizate dupa:
1. **Perioada** - Perioada cronologica initiala
2. **Faza** - Faza cronologica initiala
3. **Entitate** - US, Descoperire, etc.

## Procesul de export

### Pasul 1: Selectarea parametrilor

1. Selectati **Situl** din ComboBox
2. Selectati **Anul** (optional)
3. Alegeti **Tipul exportului**

### Pasul 2: Executie

1. Faceti clic pe **"Export"**
2. Asteptati finalizarea
3. Mesaj de confirmare

### Pasul 3: Verificare

1. Faceti clic pe **"Deschide folder"**
2. Verificati structura creata
3. Verificati completitudinea

## Folderul de iesire

### Calea standard

```
~/pyarchinit/pyarchinit_image_export/
```

### Continut

- Foldere organizate pe sit
- Subfoldere pe perioada/faza
- Imagini originale (neredimensionate)

## Filtrul pe an

**ComboBox-ul An** permite:
- Exportul doar al imaginilor dintr-o campanie specifica
- Organizarea exportului dupa anul de excavare
- Reducerea dimensiunii exportului

## Bune practici

### 1. Inainte de export

- Verificati legaturile imagine-entitate
- Verificati periodizarea US
- Asigurati-va ca aveti suficient spatiu pe disc

### 2. In timpul exportului

- Nu intrerupeti procesul
- Asteptati mesajul de finalizare

### 3. Dupa export

- Verificati structura folderelor
- Verificati completitudinea imaginilor
- Creati o copie de siguranta daca este necesar

## Utilizari tipice

### Pregatirea rapoartelor

```
1. Selectati situl
2. Exportati toate imaginile
3. Utilizati structura pentru capitolele raportului
```

### Livrare catre superintendenta

```
1. Selectati situl si anul
2. Exportati dupa tipul solicitat
3. Organizati conform standardelor ministeriale
```

### Copia de siguranta a campaniei

```
1. La sfarsitul campaniei, exportati totul
2. Arhivati pe stocare externa
3. Verificati integritatea
```

## Depanare

### Export incomplet

**Cauze**:
- Imagini nelegate
- Cai de fisiere gresite

**Solutii**:
- Verificati legaturile in Manager Media
- Verificati existenta fisierelor sursa

### Structura incorecta

**Cauze**:
- Periodizare lipsa
- US fara perioada/faza

**Solutii**:
- Completati periodizarea US
- Atribuiti perioada/faza tuturor US

## Referinte

### Fisiere sursa
- `tabs/Images_directory_export.py` - Interfata de export
- `gui/ui/Images_directory_export.ui` - Macheta UI

### Foldere
- `~/pyarchinit/pyarchinit_image_export/` - Iesire export

---

## Tutorial video

### Exportul imaginilor
`[Placeholder: video_export_immagini.mp4]`

**Continut**:
- Configurarea exportului
- Structura iesirii
- Organizarea arhivei

**Durata estimata**: 10-12 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animatie interactiva

Explorati animatia interactiva pentru a afla mai multe despre acest subiect.

[Deschideti animatia interactiva](../../animations/pyarchinit_image_export_animation.html)
