# Tutorial 28: Export GeoPackage

## Introducció

La funció **Export GeoPackage** permet empaquetar les capes vectorials i ràster de PyArchInit en un únic fitxer GeoPackage (.gpkg). Aquest format és ideal per a la compartició, l'arxivament i la portabilitat de les dades GIS.

### Avantatges del GeoPackage

| Aspecte | Avantatge |
|---------|-----------|
| Fitxer únic | Totes les dades en un sol fitxer |
| Portabilitat | Fàcil compartició |
| Estàndard OGC | Compatibilitat universal |
| Multi-capa | Vectorials i ràster junts |
| Basat en SQLite | Lleuger i ràpid |

## Accés

### Des del Menú
**PyArchInit** → **Empaqueta per GeoPackage**

## Interfície

### Panell Export

```
+--------------------------------------------------+
|        Importa a GeoPackage                       |
+--------------------------------------------------+
| Destinació:                                       |
|   [____________________________] [Navega]        |
+--------------------------------------------------+
| [Exporta Capes Vectorials]                       |
| [Exporta Capes Ràster]                           |
+--------------------------------------------------+
```

## Procediment

### Export Capes Vectorials

1. Seleccionar les capes a exportar al panell Capes QGIS
2. Obrir l'eina GeoPackage Export
3. Especificar ruta i nom del fitxer de destinació
4. Fer clic **"Exporta Capes Vectorials"**

### Export Capes Ràster

1. Seleccionar capa ràster al panell Capes
2. Especificar destinació (mateix fitxer o nou)
3. Fer clic **"Exporta Capes Ràster"**

### Export Combinat

Per incloure vectorials i ràster al mateix GeoPackage:
1. Primer exportar els vectorials
2. Després exportar els ràster al mateix fitxer
3. El sistema afegeix les capes al GeoPackage existent

## Selecció Capes

### Mètode

1. Al panell Capes de QGIS, seleccionar les capes desitjades
   - Ctrl+clic per selecció múltiple
   - Shift+clic per rang
2. Obrir Export GeoPackage
3. Les capes seleccionades seran exportades

### Capes Recomanades

| Capa | Tipus | Notes |
|------|-------|-------|
| pyunitastratigrafiche | Vectorial | US dipòsit |
| pyunitastratigrafiche_usm | Vectorial | US muràries |
| pyarchinit_quote | Vectorial | Punts cota |
| pyarchinit_siti | Vectorial | Llocs |
| Ortofoto | Ràster | Ortofoto d'excavació |

## Sortida

### Estructura GeoPackage

```
output.gpkg
├── pyunitastratigrafiche (vector)
├── pyunitastratigrafiche_usm (vector)
├── pyarchinit_quote (vector)
└── ortofoto (raster)
```

### Ruta per Defecte

```
~/pyarchinit/pyarchinit_DB_folder/
```

## Opcions Export

### Capes Vectorials

- Manté geometries originals
- Preserva tots els atributs
- Converteix automàticament noms amb espais (usa guions baixos)

### Capes Ràster

- Suporta formats comuns (GeoTIFF, etc.)
- Manté georeferenciació
- Preserva sistema de referència

## Usos Típics

### Compartició Projecte

```
1. Seleccionar totes les capes del projecte
2. Exportar a GeoPackage
3. Compartir el fitxer .gpkg
4. El destinatari obre directament a QGIS
```

### Arxivament Campanya

```
1. A fi de campanya, seleccionar capes finals
2. Exportar a GeoPackage datat
3. Arxivar amb documentació
```

### Còpia de Seguretat GIS

```
1. Periòdicament exportar estat actual
2. Mantenir versions datades
3. Usar per recuperació de desastres
```

## Bones Pràctiques

### 1. Abans de l'Export

- Verificar completesa capes
- Controlar sistema de referència
- Desar projecte QGIS

### 2. Naming

- Usar noms descriptius per al fitxer
- Incloure data al nom
- Evitar caràcters especials

### 3. Verificació

- Obrir GeoPackage creat
- Verificar totes les capes presents
- Controlar atributs

## Resolució de Problemes

### Export Fallit

**Causes**:
- Capa no vàlida
- Ruta no escrivible
- Espai en disc insuficient

**Solucions**:
- Verificar validesa capa
- Controlar permisos carpeta
- Alliberar espai en disc

### Capes Absents

**Causa**: Capa no seleccionada

**Solució**: Verificar selecció al panell Capes

### Ràster No Exportat

**Causes**:
- Format no suportat
- Fitxer font no accessible

**Solucions**:
- Convertir ràster a GeoTIFF
- Verificar ruta fitxer font

## Referències

### Fitxers Font
- `tabs/gpkg_export.py` - Interfície export
- `gui/ui/gpkg_export.ui` - Layout UI

### Documentació
- [GeoPackage Standard](https://www.geopackage.org/)
- [QGIS GeoPackage Support](https://docs.qgis.org/)

---

## Vídeo Tutorial

### Export GeoPackage
`[Placeholder: video_geopackage.mp4]`

**Continguts**:
- Selecció capes
- Export vectorials i ràster
- Verificació sortida
- Bones pràctiques

**Durada prevista**: 8-10 minuts

---

*Última actualització: Gener 2026*
