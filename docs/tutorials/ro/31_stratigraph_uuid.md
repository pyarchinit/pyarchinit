# PyArchInit - StratiGraph: Identificatori UUID

## Cuprins
1. [Introducere](#introducere)
2. [Ce sunt UUID-urile](#ce-sunt-uuid-urile)
3. [De ce sunt necesare UUID-urile in StratiGraph](#de-ce-sunt-necesare-uuid-urile-in-stratigraph)
4. [Cum functioneaza in PyArchInit](#cum-functioneaza-in-pyarchinit)
5. [Tabele cu UUID](#tabele-cu-uuid)
6. [Intrebari frecvente](#intrebari-frecvente)

---

## Introducere

Incepand cu versiunea **5.0.1-alpha**, PyArchInit integreaza un sistem de **Identificatori Unici Universali (UUID)** pentru toate entitatile arheologice. Aceasta functionalitate face parte din proiectul european **StratiGraph** (Horizon Europe) si asigura ca fiecare inregistrare din baza de date are un identificator stabil si unic la nivel global.

<!-- VIDEO: Introducere in UUID-urile din StratiGraph -->
> **Tutorial video**: [Inserati linkul video introducere UUID]

---

## Ce sunt UUID-urile

Un **UUID** (Universally Unique Identifier) este un cod alfanumeric de 128 de biti care identifica in mod unic o entitate. PyArchInit utilizeaza versiunea 4 (UUID v4), care este generata aleatoriu.

### Exemplu de UUID

```
a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### Caracteristicile UUID

| Caracteristica | Descriere |
|----------------|-----------|
| **Format** | 32 de caractere hexazecimale separate prin cratime (8-4-4-4-12) |
| **Unicitate** | Probabilitatea de coliziune este statistic neglijabila (~1 din 2^122) |
| **Independenta** | Nu depinde de baza de date, server sau momentul crearii |
| **Persistenta** | Odata atribuit, nu se schimba niciodata |
| **Versiune** | UUID v4 (generat aleatoriu) |

### Diferenta fata de ID-urile traditionale

| Tip ID | Exemplu | Stabil intre BD? | Unic la nivel global? |
|--------|---------|-------------------|-----------------------|
| Auto-incrementare (id_us) | `1`, `2`, `3`... | Nu | Nu |
| Constrangere compozita | `Sit1-Arie1-US100` | Da (semantic) | Depinde |
| **UUID** | `a3f7b2c1-8d4e-...` | **Da** | **Da** |

ID-urile auto-incrementale (`id_us`, `id_invmat`, etc.) se schimba cand copiati o baza de date sau importati date. UUID-urile insa raman **intotdeauna aceleasi**, indiferent de locul unde se afla datele.

---

## De ce sunt necesare UUID-urile in StratiGraph

Proiectul StratiGraph cere ca datele arheologice sa poata fi:

### 1. Exportate in Knowledge Graph

Datele PyArchInit sunt exportate ca **pachete** (bundle-uri structurate) intr-un Knowledge Graph central. Fiecare entitate trebuie sa aiba un identificator stabil pentru a fi recunoscuta in graf.

```
Entitate locala (PyArchInit)  -->  UUID  -->  Knowledge Graph (StratiGraph)
     US 100                   a3f7b2c1...        E18 Physical Thing
```

### 2. Sincronizate intre dispozitive

Cand lucrati pe teren fara conexiune la internet, datele sunt salvate local. La revenirea conectivitatii, datele sunt sincronizate. UUID-urile asigura ca aceeasi inregistrare este recunoscuta si actualizata (nu duplicata).

### 3. Mapate la CIDOC-CRM

Ontologia CIDOC-CRM necesita **URI-uri persistente** pentru fiecare entitate. UUID-urile sunt utilizate pentru a construi aceste URI-uri:

```
http://pyarchinit.org/entity/a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### 4. Urmarite in timp

Fiecare modificare, export sau sincronizare se refera la acelasi UUID. Acest lucru permite:
- Reconstituirea istoricului unei inregistrari
- Verificarea provenientei datelor
- Legarea datelor intre proiecte diferite

---

## Cum functioneaza in PyArchInit

### Generare automata

UUID-urile sunt generate **automat** in doua momente:

| Moment | Descriere |
|--------|-----------|
| **Crearea unei inregistrari noi** | Cand inserati o inregistrare noua (de ex., un US nou), un UUID v4 este generat automat |
| **Migrarea bazei de date existente** | La prima pornire dupa actualizare, toate inregistrarile existente fara UUID primesc un UUID generat |

Utilizatorul **nu trebuie sa faca nimic**: UUID-urile sunt gestionate in intregime de sistem.

### Unde se gaseste UUID-ul

Fiecare tabel principal al bazei de date are o coloana `entity_uuid` de tip TEXT. Campul este vizibil in baza de date dar nu apare in formularele de introducere a datelor, deoarece este gestionat intern.

### Migrare automata

La actualizarea PyArchInit la versiunea 5.0.1-alpha (sau ulterioara):

1. **La prima pornire**, sistemul verifica daca tabelele au coloana `entity_uuid`
2. Daca lipseste, coloana este **adaugata automat**
3. Inregistrarile existente fara UUID primesc un **UUID generat**
4. Aceasta operatiune are loc **o singura data** per sesiune QGIS

Procesul este transparent si nu necesita interventie manuala. Functioneaza atat cu **PostgreSQL** cat si cu **SQLite**.

---

## Tabele cu UUID

Coloana `entity_uuid` este prezenta in urmatoarele 19 tabele:

| Tabel | Continut |
|-------|----------|
| `site_table` | Situri arheologice |
| `us_table` | Unitati Stratigrafice (US/USM) |
| `inventario_materiali_table` | Inventar descoperiri |
| `tomba_table` | Inhumari |
| `periodizzazione_table` | Periodizare si faze |
| `struttura_table` | Structuri |
| `campioni_table` | Esantioane |
| `individui_table` | Indivizi antropologici |
| `pottery_table` | Ceramica |
| `media_table` | Fisiere media |
| `media_thumb_table` | Miniaturi media |
| `media_to_entity_table` | Relatii media-entitate |
| `fauna_table` | Date arheozoologice (Fauna) |
| `ut_table` | Unitati Topografice |
| `tma_materiali_archeologici` | TMA Materiale Arheologice |
| `tma_materiali_ripetibili` | TMA Materiale Repetabile |
| `archeozoology_table` | Arheozoologie |
| `documentazione_table` | Documentatie |
| `inventario_lapidei_table` | Inventar Piatra |

---

## Intrebari frecvente

### Trebuie sa inserez manual UUID-urile?

**Nu.** UUID-urile sunt generate automat de sistem. Nu este necesar (si nici recomandat) sa le modificati manual.

### Ce se intampla daca copiez baza de date?

UUID-urile sunt copiate impreuna cu baza de date. Acesta este comportamentul dorit: aceeasi inregistrare mentine acelasi UUID chiar si pe copii diferite ale bazei de date.

### Pot vedea UUID-urile in formulare?

In prezent, UUID-urile nu sunt vizibile in formularele de introducere a datelor. Sunt vizibile direct in baza de date (de ex., prin DB Manager in QGIS) in coloana `entity_uuid` a fiecarui tabel.

### UUID-urile incetinesc baza de date?

Nu. UUID-ul este un camp simplu de tip TEXT si nu are un impact semnificativ asupra performantei bazei de date.

### Ce se intampla cu bazele de date existente?

Bazele de date existente sunt actualizate automat la prima pornire: coloana `entity_uuid` este adaugata si toate inregistrarile existente primesc un UUID generat.

### UUID-urile functioneaza atat cu PostgreSQL cat si cu SQLite?

Da. Sistemul este compatibil cu ambele tipuri de baze de date suportate de PyArchInit.

---

*Documentatie PyArchInit - StratiGraph UUID*
*Versiune: 5.0.1-alpha*
*Ultima actualizare: februarie 2026*
