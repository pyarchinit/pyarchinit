# Tutorial 13: Gestión del Tesauro

## Introducción

El **Tesauro** de PyArchInit es el sistema centralizado para la gestión de los vocabularios controlados. Permite definir y mantener las listas de valores utilizadas en todas las fichas del plugin, garantizando coherencia terminológica y facilitando la búsqueda.

### Funciones Principales

- Gestión de vocabularios para cada ficha
- Soporte multilingüe
- Siglas y descripciones extendidas
- Integración con GPT para sugerencias
- Importación/exportación desde archivo CSV

---

## Acceso al Tesauro

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Tesauro** (o **Thesaurus form**)

### Vía Toolbar
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Tesauro** (libro/diccionario)

---

## Vista General de la Interfaz

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegación, búsqueda, guardado |
| 2 | Selección de Tabla | Elección de la ficha a configurar |
| 3 | Campos de Sigla | Código, extensión, tipología |
| 4 | Descripción | Descripción detallada del término |
| 5 | Idioma | Selección de idioma |
| 6 | Herramientas | Importar CSV, sugerencias GPT |

---

## Campos del Tesauro

### Nombre de Tabla

**Campo**: `comboBox_nome_tabella`
**Base de datos**: `nome_tabella`

Selecciona la ficha para la cual definir los valores.

**Tablas disponibles:**
| Tabla | Descripción |
|-------|-------------|
| `us_table` | Ficha UE/UEM |
| `site_table` | Ficha de Sitio |
| `periodizzazione_table` | Periodización |
| `inventario_materiali_table` | Inventario de Materiales |
| `pottery_table` | Ficha Pottery |
| `campioni_table` | Ficha de Muestras |
| `documentazione_table` | Documentación |
| `tomba_table` | Ficha de Tumba |
| `individui_table` | Ficha de Individuos |
| `fauna_table` | Arqueozoología |
| `ut_table` | Ficha UT |

### Sigla

**Campo**: `comboBox_sigla`
**Base de datos**: `sigla`

Código breve/abreviatura del término.

**Ejemplos:**
- `MR` para Muro
- `UE` para Unidad Estratigráfica
- `CR` para Cerámica

### Sigla Extendida

**Campo**: `comboBox_sigla_estesa`
**Base de datos**: `sigla_estesa`

Forma completa del término.

**Ejemplos:**
- `Muro perimetral`
- `Unidad Estratigráfica`
- `Cerámica común`

### Descripción

**Campo**: `textEdit_descrizione_sigla`
**Base de datos**: `descrizione`

Descripción detallada del término, definición, notas de uso.

### Tipología de Sigla

**Campo**: `comboBox_tipologia_sigla`
**Base de datos**: `tipologia_sigla`

Código numérico que identifica el campo de destino.

**Estructura de códigos:**
```
X.Y donde:
X = número de ficha (1 Sitio, 2 UE/UEM, 3 Inventario de materiales, 4 Muestras, 6 Estructura,
    7 Tumba, 8 Individuos, 9 Documentación, 10 TMA, 11 Pottery, 12 UT, 13 Fauna)
Y = número de campo
```

**Ejemplos para us_table:**
| Código | Campo |
|--------|-------|
| 2.1 | Sector |
| 2.3 | Definición estratigráfica |
| 2.4 | Definición interpretada |

### Idioma

**Campo**: `comboBox_lingua`
**Base de datos**: `lingua`

Idioma del término.

**Idiomas soportados:**
- IT (Italiano)
- EN_US (Inglés)
- DE (Alemán)
- FR (Francés)
- ES (Español)
- AR (Árabe)
- CA (Catalán)

---

## Campos de Jerarquía

### ID Parent

**Campo**: `comboBox_id_parent`
**Base de datos**: `id_parent`

ID del término padre (para estructuras jerárquicas).

### Parent Sigla

**Campo**: `comboBox_parent_sigla`
**Base de datos**: `parent_sigla`

Sigla del término padre.

### Hierarchy Level

**Campo**: `spinBox_hierarchy`
**Base de datos**: `hierarchy_level`

Nivel en la jerarquía (0=raíz, 1=primer nivel, etc.).

---

## Funcionalidades Especiales

### Sugerencias GPT

El botón "Sugerencias" utiliza OpenAI GPT para:
- Generar descripciones automáticas
- Proporcionar enlaces de Wikipedia de referencia
- Sugerir definiciones en contexto arqueológico

**Uso:**
1. Seleccionar o introducir un término en "Sigla extendida"
2. Clic en "Sugerencias"
3. Seleccionar el modelo GPT
4. Esperar la generación
5. Revisión y guardado

**Nota:** Requiere API key de OpenAI configurada.

### Importar CSV

Para bases de datos SQLite es posible importar vocabularios desde archivo CSV.

**Formato CSV requerido:**
```text
nome_tabella,sigla,sigla_estesa,descrizione,tipologia_sigla,lingua
us_table,MR,Muro,Estructura muraria,2.4,IT
us_table,PV,Pavimento,Superficie de tránsito,2.4,IT
```

**Procedimiento:**
1. Clic en "Importar CSV"
2. Seleccionar el archivo
3. Confirmar la importación
4. Verificar los datos importados

---

## Workflow Operativo

### Añadir Nuevo Término

1. **Apertura del Tesauro**
   - Vía menú o barra de herramientas

2. **Nuevo registro**
   - Clic en "New Record"

3. **Selección de tabla**
   ```
   Nombre tabla: us_table
   ```

4. **Definición del término**
   ```
   Sigla: PZ
   Sigla extendida: Pozo
   Tipología sigla: 2.4
   Idioma: ES
   ```

5. **Descripción**
   ```
   Estructura excavada en el terreno para
   el abastecimiento de agua.
   Generalmente de forma circular
   con revestimiento de piedra o ladrillo.
   ```

6. **Guardado**
   - Clic en "Save"

### Búsqueda de Términos

1. Clic en "New Search"
2. Completar criterios:
   - Nombre de tabla
   - Sigla o sigla extendida
   - Idioma
3. Clic en "Search"
4. Navegar entre los resultados

### Modificación de Término Existente

1. Buscar el término a modificar
2. Modificar los campos necesarios
3. Clic en "Save"

---

## Organización de Códigos de Tipología

### Los Códigos de las Fichas

Los códigos no se eligen: cada lista desplegable de una ficha lee su propio código, fijo. Algunos ejemplos — la lista completa, ficha por ficha, se abre desde la ventana del Tesauro con el botón **Ver lista de códigos**:

**site_table (1.x):**
| Código | Campo |
|--------|-------|
| 1.1 | Definición del sitio |

**us_table (2.x):**
| Código | Campo |
|--------|-------|
| 2.1 | Sector |
| 2.3 | Definición estratigráfica |
| 2.4 | Definición interpretada |
| 2.8 | Método de excavación |

**inventario_materiali_table (3.x):**
| Código | Campo |
|--------|-------|
| 3.1 | Tipo de hallazgo |
| 3.2 | Clase de material |
| 3.3 | Definición |

**pottery_table (11.x):**
| Código | Campo |
|--------|-------|
| 11.1 | Fabric |
| 11.4 | Forma |
| 11.6 | Ware |

---

## Buenas Prácticas

### Coherencia Terminológica

- Usar siempre los mismos términos para los mismos conceptos
- Evitar sinónimos no documentados
- Documentar las convenciones adoptadas

### Multilingüe

- Crear los términos en todos los idiomas necesarios
- Mantener las correspondencias entre idiomas
- Usar traducciones oficiales cuando estén disponibles

### Jerarquía

- Utilizar la estructura jerárquica para términos relacionados
- Definir claramente los niveles
- Documentar las relaciones

### Mantenimiento

- Revisar periódicamente los vocabularios
- Eliminar términos obsoletos
- Actualizar las descripciones

---

## Resolución de Problemas

### Problema: Término no visible en los ComboBox

**Causa:** Código de tipología erróneo o idioma no correspondiente.

**Solución:**
1. Verificar el código tipologia_sigla
2. Comprobar el idioma configurado
3. Verificar que el registro esté guardado

### Problema: Importar CSV fallido

**Causa:** Formato de archivo incorrecto.

**Solución:**
1. Verificar la estructura del CSV
2. Comprobar los delimitadores (coma)
3. Verificar la codificación (UTF-8)

### Problema: Sugerencias GPT no funcionan

**Causa:** API key faltante o no válida.

**Solución:**
1. Verificar la configuración de API key
2. Comprobar la conexión a internet
3. Verificar el crédito de OpenAI

---

## Referencias

### Base de Datos

- **Tabla**: `pyarchinit_thesaurus_sigle`
- **Clase mapper**: `PYARCHINIT_THESAURUS_SIGLE`
- **ID**: `id_thesaurus_sigle`

### Archivos Fuente

- **UI**: `gui/ui/Thesaurus.ui`
- **Controlador**: `tabs/Thesaurus.py`

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../animations/pyarchinit_thesaurus_animation.html)
