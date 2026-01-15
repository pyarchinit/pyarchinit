# Tutorial 20: Publicación Web con Lizmap

## Introducción

PyArchInit soporta la **publicación web** de los datos arqueológicos a través de **Lizmap**, una aplicación que permite transformar proyectos QGIS en aplicaciones web interactivas.

### ¿Qué es Lizmap?

Lizmap está compuesto por:
- **Plugin QGIS**: Para configurar la publicación
- **Lizmap Web Client**: Aplicación web para visualizar los mapas
- **QGIS Server**: Backend para servir los mapas

### Ventajas de la Publicación Web

| Aspecto | Descripción |
|---------|-------------|
| Accesibilidad | Datos consultables desde navegador |
| Compartición | Fácil distribución a stakeholders |
| Interactividad | Zoom, pan, consultas, popups |
| Actualización | Sincronización con la base de datos |
| Móvil | Acceso desde smartphone/tablet |

## Prerrequisitos

### Servidor

1. **QGIS Server** instalado
2. **Lizmap Web Client** configurado
3. Servidor web (Apache/Nginx)
4. PHP 7.4+
5. PostgreSQL/PostGIS (recomendado)

### Cliente

1. **QGIS Desktop** con plugin Lizmap
2. **PyArchInit** configurado
3. Proyecto QGIS guardado

## Instalación del Plugin Lizmap

### Desde QGIS

1. **Complementos** → **Administrar complementos**
2. Buscar "Lizmap"
3. Instalar **Lizmap**
4. Reiniciar QGIS

## Preparación del Proyecto

### 1. Organización de Capas

Estructura recomendada:
```
Proyecto QGIS
├── Grupo: Base
│   ├── Ortofoto
│   └── CTR/Catastral
├── Grupo: Excavación
│   ├── pyunitastratigrafiche
│   ├── pyunitastratigrafiche_usm
│   └── pyarchinit_quote
├── Grupo: Documentación
│   ├── Fotos georreferenciadas
│   └── Levantamientos
└── Grupo: Análisis
    └── Matrix de Harris (imagen)
```

### 2. Estilizado de Capas

Para cada capa:
1. Aplicar estilo apropiado
2. Configurar etiquetas
3. Establecer escala de visibilidad

### 3. Popups y Atributos

Configurar los popups para cada capa:
1. Clic derecho en la capa → **Propiedades**
2. Pestaña **Visualización**
3. Configurar **HTML Map Tip**

Ejemplo de popup para UE:
```html
<h3>UE [% "us_s" %]</h3>
<p><b>Área:</b> [% "area_s" %]</p>
<p><b>Tipo:</b> [% "tipo_us_s" %]</p>
<p><b>Definición:</b> [% "definizione" %]</p>
```

### 4. Guardado del Proyecto

1. Guardar el proyecto (.qgz) en la carpeta Lizmap
2. Usar rutas relativas para los datos
3. Verificar que todas las capas sean accesibles

## Configuración de Lizmap

### Apertura del Plugin

1. **Web** → **Lizmap** → **Lizmap**

### Pestaña General

| Campo | Descripción | Valor |
|-------|-------------|-------|
| Título del mapa | Nombre mostrado | "Excavación Via Roma" |
| Abstract | Descripción | "Documentación arqueológica..." |
| Imagen | Thumbnail del proyecto | project_thumb.png |
| Repositorio | Carpeta del servidor | /var/www/lizmap/projects |

### Pestaña Capas

Para cada capa configurar:

| Opción | Descripción |
|--------|-------------|
| Activado | Capa visible en Lizmap |
| Base layer | Capa de fondo (ortofoto, etc.) |
| Popup | Habilita popup al clic |
| Editing | Permite modificación online |
| Filtro | Filtros de usuario |

### Pestaña Basemap

Configurar fondos:
- OpenStreetMap
- Google Maps (requiere API key)
- Bing Maps
- Ortofoto personalizada

### Pestaña Locate

Búsqueda por localidad:
- Configurar capa para búsqueda
- Campos a buscar
- Formato de visualización

### Pestaña Editing (Opcional)

Para permitir edición online:
1. Seleccionar capas modificables
2. Configurar campos editables
3. Establecer permisos

### Pestaña Herramientas

Activar/desactivar:
- Impresión
- Medidas
- Selección
- Permalink
- etc.

### Guardado de Configuración

Hacer clic en **Guardar** para generar el archivo `.qgs.cfg`

## Publicación

### Subida al Servidor

1. Copiar archivos `.qgz` y `.qgz.cfg` al servidor
2. Verificar permisos de archivos
3. Configurar QGIS Server

### Estructura del Servidor

```
/var/www/lizmap/
├── lizmap/           # Aplicación Lizmap
├── projects/         # Proyectos QGIS
│   ├── excavacion_roma.qgz
│   └── excavacion_roma.qgz.cfg
└── var/              # Datos de la aplicación
```

### Configuración de QGIS Server

Archivo `/etc/apache2/sites-available/lizmap.conf`:
```apache
<VirtualHost *:80>
    ServerName lizmap.example.com
    DocumentRoot /var/www/lizmap/lizmap/www

    <Directory /var/www/lizmap/lizmap/www>
        AllowOverride All
        Require all granted
    </Directory>

    # QGIS Server
    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
        AllowOverride All
        Require all granted
    </Directory>

    FcgidInitialEnv QGIS_SERVER_LOG_FILE /var/log/qgis/qgis_server.log
    FcgidInitialEnv QGIS_SERVER_LOG_LEVEL 0
</VirtualHost>
```

## Acceso Web

### URL de la Aplicación

```
http://lizmap.example.com/
```

### Navegación

1. Selección del proyecto desde la página principal
2. Visualización del mapa interactivo
3. Herramientas en la barra de herramientas

### Funcionalidades para el Usuario

| Función | Descripción |
|---------|-------------|
| Zoom | Rueda del ratón, botones +/- |
| Pan | Arrastrar el mapa |
| Popup | Clic en elementos |
| Búsqueda | Barra de búsqueda |
| Impresión | Exportar a PDF |
| Permalink | URL compartible |

## Integración con PyArchInit

### Datos en Tiempo Real

Con PostgreSQL:
- Los datos están siempre actualizados
- Modificaciones en PyArchInit visibles inmediatamente
- Sin sincronización manual

### Capas Recomendadas

| Capa PyArchInit | Publicación |
|-----------------|-------------|
| pyunitastratigrafiche | Sí, con popup |
| pyunitastratigrafiche_usm | Sí, con popup |
| pyarchinit_quote | Sí |
| pyarchinit_siti | Sí, como overview |
| Matrix de Harris | Como imagen estática |

### Configuración de Popup para UE

Plantilla HTML avanzada:
```html
<div class="us-popup">
    <h3 style="color:#2c3e50;">UE [% "us_s" %]</h3>
    <table>
        <tr><td><b>Sitio:</b></td><td>[% "scavo_s" %]</td></tr>
        <tr><td><b>Área:</b></td><td>[% "area_s" %]</td></tr>
        <tr><td><b>Tipo:</b></td><td>[% "tipo_us_s" %]</td></tr>
        <tr><td><b>Definición:</b></td><td>[% "definizione" %]</td></tr>
        <tr><td><b>Período:</b></td><td>[% "periodo" %]</td></tr>
    </table>
    [% if "foto_url" %]
    <img src="[% "foto_url" %]" style="max-width:200px;"/>
    [% end %]
</div>
```

## Seguridad

### Autenticación

Lizmap soporta:
- Usuarios locales
- LDAP
- OAuth2

### Configuración de Usuarios

En el admin de Lizmap:
1. Crear grupos (admin, arqueólogo, público)
2. Crear usuarios
3. Asignar permisos por proyecto

### Permisos de Capas

| Grupo | Visualiza | Edita | Imprime |
|-------|-----------|-------|---------|
| Admin | Todas | Todas | Sí |
| Arqueólogo | Todas | Algunas | Sí |
| Público | Solo base | No | No |

## Mantenimiento

### Actualización de Proyectos

1. Modificar proyecto en QGIS Desktop
2. Regenerar configuración Lizmap
3. Subir al servidor

### Caché

Gestión de caché de tiles:
```bash
# Limpiar caché
lizmap-cache-clearer.php -project excavacion_roma

# Regenerar tiles
lizmap-tiles-seeder.php -project excavacion_roma -bbox xmin,ymin,xmax,ymax
```

### Log y Debug

```bash
# Log QGIS Server
tail -f /var/log/qgis/qgis_server.log

# Log Lizmap
tail -f /var/www/lizmap/var/log/messages.log
```

## Buenas Prácticas

### 1. Optimización del Rendimiento

- Usar capas raster pre-tilizadas
- Limitar número de elementos por capa
- Configurar escalas de visibilidad
- Usar índices espaciales

### 2. Experiencia de Usuario

- Popups informativos pero concisos
- Estilos claros y legibles
- Organización lógica de capas
- Documentación para usuarios

### 3. Seguridad

- HTTPS obligatorio
- Actualizaciones regulares
- Backup de configuraciones
- Monitorización de accesos

### 4. Backup

- Backup de archivos `.qgz` y `.cfg`
- Backup de base de datos PostgreSQL
- Versionado de configuraciones

## Resolución de Problemas

### Mapa No Visualizado

**Causas**:
- QGIS Server no configurado
- Rutas de archivo incorrectas
- Permisos insuficientes

**Soluciones**:
- Verificar log de QGIS Server
- Comprobar rutas en el proyecto
- Verificar permisos de archivos

### Popups No Funcionan

**Causas**:
- Capa no configurada para popup
- HTML incorrecto en la plantilla

**Soluciones**:
- Habilitar popup en Lizmap
- Verificar sintaxis HTML

### Rendimiento Lento

**Causas**:
- Demasiados datos
- Caché no configurada
- Servidor subdimensionado

**Soluciones**:
- Reducir datos visibles
- Configurar caché de tiles
- Aumentar recursos del servidor

## Referencias

### Software
- [Lizmap](https://www.lizmap.com/)
- [QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

### Documentación
- [Lizmap Documentation](https://docs.lizmap.com/)
- [QGIS Server Documentation](https://docs.qgis.org/latest/en/docs/server_manual/)

---

## Video Tutorial

### Setup de Lizmap
`[Placeholder: video_lizmap_setup.mp4]`

**Contenidos**:
- Instalación del plugin
- Configuración del proyecto
- Publicación

**Duración prevista**: 20-25 minutos

### Personalización Web
`[Placeholder: video_lizmap_custom.mp4]`

**Contenidos**:
- Popups avanzados
- Estilos personalizados
- Gestión de usuarios

**Duración prevista**: 15-18 minutos

---

*Última actualización: Enero 2026*
