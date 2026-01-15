# Tutorial 04: Fitxa de Periodització

## Índex
1. [Introducció](#introducció)
2. [Accés a la Fitxa](#accés-a-la-fitxa)
3. [Interfície d'Usuari](#interfície-dusuari)
4. [Conceptes Fonamentals](#conceptes-fonamentals)
5. [Camps de la Fitxa](#camps-de-la-fitxa)
6. [Barra d'Eines DBMS](#barra-deines-dbms)
7. [Funcionalitats GIS](#funcionalitats-gis)
8. [Exportació PDF](#exportació-pdf)
9. [Integració AI](#integració-ai)
10. [Flux de Treball Operatiu](#flux-de-treball-operatiu)

---

## Introducció

La **Fitxa de Periodització** és una eina fonamental per a la gestió de les fases cronològiques d'una excavació arqueològica. Permet definir els períodes i les fases que caracteritzen la seqüència estratigràfica del lloc, associant a cada parella període/fase una datació cronològica i una descripció.

### Propòsit de la Fitxa

- Definir la seqüència cronològica de l'excavació
- Associar períodes i fases a les unitats estratigràfiques
- Gestionar la cronologia absoluta (anys) i relativa (períodes històrics)
- Visualitzar les US per període/fase al mapa GIS
- Generar informes PDF de la periodització

### Relació amb altres Fitxes

La Fitxa de Periodització està estretament connectada a:
- **Fitxa US/USM**: Cada US s'assigna a un període i una fase
- **Fitxa Lloc**: Els períodes són específics per a cada lloc
- **Matriu de Harris**: Els períodes coloren la Matriu per fase cronològica

---

## Accés a la Fitxa

### Des del Menú

1. Obrir QGIS amb el connector PyArchInit actiu
2. Menú **PyArchInit** → **Archaeological record management** → **Excavation - Loss of use calculation** → **Period and Phase**

### Des de la Barra d'Eines

1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Periodització** (icona de lloc amb rellotge)

---

## Interfície d'Usuari

L'interfície de la Fitxa de Periodització està organitzada de manera senzilla i lineal:

### Àrees Principals

| Àrea | Descripció |
|------|------------|
| **1. DBMS Toolbar** | Barra d'eines per a navegació i gestió de registres |
| **2. Indicadors d'Estat** | DB Info, Status, Ordenació |
| **3. Dades Identificatives** | Lloc, Període, Fase, Codi de període |
| **4. Dades Descriptives** | Descripció textual del període |
| **5. Cronologia** | Anys inicial i final |
| **6. Datació Estesa** | Selecció del vocabulari d'èpoques històriques |

---

## Conceptes Fonamentals

### Període i Fase

El sistema de periodització a PyArchInit es basa en una estructura jeràrquica de dos nivells:

#### Període
El **Període** representa una macro-fase cronològica de l'excavació. S'identifica per un número enter (1, 2, 3, ...) i representa les grans subdivisions de la seqüència estratigràfica.

Exemples de períodes:
- Període 1: Edat contemporània
- Període 2: Edat medieval
- Període 3: Edat romana imperial
- Període 4: Edat romana republicana

#### Fase
La **Fase** representa una subdivisió interna del període. També s'identifica per un número enter i permet detallar més la seqüència.

Exemples de fases en el Període 3 (Edat romana imperial):
- Fase 1: Segles III-IV dC
- Fase 2: Segle II dC
- Fase 3: Segle I dC

### Codi de Període

El **Codi de Període** és un identificador numèric únic que connecta la parella període/fase a les US. Quan s'assigna un període/fase a una US a la Fitxa US, s'utilitza aquest codi.

> **Important**: El codi de període ha de ser únic per a cada combinació lloc/període/fase.

### Esquema Conceptual

```
Lloc
└── Període 1 (Edat contemporània)
│   ├── Fase 1 → Codi 101
│   └── Fase 2 → Codi 102
├── Període 2 (Edat medieval)
│   ├── Fase 1 → Codi 201
│   ├── Fase 2 → Codi 202
│   └── Fase 3 → Codi 203
└── Període 3 (Edat romana)
    ├── Fase 1 → Codi 301
    └── Fase 2 → Codi 302
```

---

## Camps de la Fitxa

### Camps Identificatius

#### Lloc
- **Tipus**: ComboBox (només lectura en mode navegació)
- **Obligatori**: Sí
- **Descripció**: Selecciona el lloc arqueològic al qual pertany la periodització

#### Període
- **Tipus**: ComboBox editable
- **Obligatori**: Sí
- **Valors**: Números enters de l'1 al 15 (predefinits) o valors personalitzats
- **Descripció**: Número del període cronològic
- **Notes**: Els números baixos indiquen períodes més recents, els números alts períodes més antics

#### Fase
- **Tipus**: ComboBox editable
- **Obligatori**: Sí
- **Valors**: Números enters de l'1 al 15 (predefinits) o valors personalitzats
- **Descripció**: Número de la fase dins del període

#### Codi de Període
- **Tipus**: LineEdit (text)
- **Obligatori**: No (però molt recomanat)
- **Descripció**: Codi numèric únic per identificar la parella període/fase
- **Suggeriment**: Usar una convenció com `[període][fase]` (ex. 101, 102, 201, 301)

### Camps Descriptius

#### Descripció
- **Tipus**: TextEdit (multilínia)
- **Obligatori**: No
- **Descripció**: Descripció textual del període/fase
- **Contingut suggerit**:
  - Característiques generals del període
  - Esdeveniments històrics correlacionats
  - Tipologies d'estructures/materials esperats
  - Referències bibliogràfiques

### Camps Cronològics

#### Cronologia Inicial
- **Tipus**: LineEdit (numèric)
- **Obligatori**: No
- **Format**: Any numèric
- **Notes**:
  - Valors positius = dC
  - Valors negatius = aC
  - Exemple: `-100` per 100 aC, `200` per 200 dC

#### Cronologia Final
- **Tipus**: LineEdit (numèric)
- **Obligatori**: No
- **Format**: Any numèric (mateixes convencions que Cronologia Inicial)

#### Datació Estesa
- **Tipus**: ComboBox
- **Obligatori**: No
- **Descripció**: Vocabolari controlat per a l'atribució cronològica

**Valors típics:**
- Edat del Bronze
- Edat del Ferro
- Època ibèrica
- Època romana republicana
- Època romana imperial
- Antiguitat tardana
- Alta Edat Mitjana
- Baixa Edat Mitjana
- Època moderna
- Època contemporània

---

## Barra d'Eines DBMS

La barra d'eines proporciona les funcions estàndard de gestió de registres:

### Navegació

| Botó | Funció |
|------|--------|
| First rec | Vés al primer registre |
| Prev rec | Vés al registre anterior |
| Next rec | Vés al registre següent |
| Last rec | Vés a l'últim registre |

### Gestió de Registres

| Botó | Funció |
|------|--------|
| New record | Crea un nou registre |
| Save | Desa les modificacions |
| Delete | Elimina el registre actual |
| View all | Visualitza tots els registres |

### Cerca

| Botó | Funció |
|------|--------|
| New search | Inicia una nova cerca |
| Search!!! | Executa la cerca |
| Order by | Ordena els resultats |

---

## Funcionalitats GIS

### Visualització per Període

La Fitxa de Periodització s'integra amb les funcionalitats GIS:

1. **Preview per període**: Mostra les US del període/fase seleccionat al mapa
2. **Coloració automàtica**: Les US es coloren segons el període assignat
3. **Filtratge**: Permet filtrar la visualització per període/fase

### Com Visualitzar

1. Seleccionar un registre de periodització
2. Fer clic al botó **GIS Preview**
3. Les US associades es ressalten al mapa

---

## Exportació PDF

### Generació d'Informes

La fitxa permet generar informes PDF:

1. Fer clic al botó **PDF Export**
2. Seleccionar les opcions de format
3. L'informe inclou:
   - Llista de períodes/fases
   - Datacions associades
   - Descripcions
   - Estadístiques d'US per període

---

## Integració AI

### Anàlisi amb GPT

La fitxa inclou integració amb AI per a:
- Suggeriments de datació basats en materials
- Anàlisi de coherència cronològica
- Generació automàtica de descripcions

---

## Flux de Treball Operatiu

### Crear una Nova Periodització

1. **Obrir la Fitxa de Periodització**
2. **Fer clic a New record**
3. **Seleccionar el Lloc** del desplegable
4. **Inserir Període** (ex. 1)
5. **Inserir Fase** (ex. 1)
6. **Inserir Codi de Període** (ex. 101)
7. **Emplenar Cronologia Inicial i Final** (ex. 1900, 2000)
8. **Seleccionar Datació Estesa** (ex. Edat Contemporània)
9. **Escriure Descripció** del període
10. **Fer clic a Save**

### Assignar Períodes a les US

1. Crear totes les perioditzacions del lloc
2. Obrir la Fitxa US
3. Per a cada US, seleccionar:
   - Període Inicial
   - Fase Inicial
   - Període Final (si diferent)
   - Fase Final (si diferent)

### Verificar la Periodització

1. Obrir la Fitxa de Periodització
2. Usar el Preview GIS per verificar les assignacions
3. Generar el Matrix de Harris colorat per períodes

---

## Bones Pràctiques

### 1. Planificació

- Definir l'estructura de períodes ABANS de començar la documentació
- Usar un sistema de numeració coherent (101, 102, 201, 202...)
- Documentar la convenció de numeració

### 2. Coherència

- Mantenir la convenció de numeració en tot el projecte
- Periòdics baixos = més recents
- Fases dins del període = subdivision temporal

### 3. Documentació

- Emplenar sempre la descripció del període
- Indicar les datacions absolutes quan sigui possible
- Referenciar evidències datants

---

## Resolució de Problemes

### El període no es desa
- Verificar que Lloc, Període i Fase estiguin emplenats
- Verificar que la combinació sigui única

### Les US no mostren el període
- Verificar que la US tingui assignat un període
- Verificar que el període existeixi a la Fitxa de Periodització

### La coloració del Matrix no funciona
- Verificar que els períodes estiguin correctament assignats
- Regenerar el Matrix després d'assignar períodes

---

## Notes Tècniques

- **Taula de base de dades**: `periodizzazione_table`
- **Camps principals**: sito, periodo, fase, cron_iniziale, cron_finale, datazione_estesa, descrizione, cont_per
- **Relació amb US**: Via camps `periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`

---

*Documentació PyArchInit - Fitxa de Periodització*
*Versió: 4.9.x*
*Última actualització: Gener 2026*
