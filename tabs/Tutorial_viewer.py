# -*- coding: utf-8 -*-
"""
Tutorial Viewer Dialog for PyArchInit
Displays built-in tutorials and documentation with multilingual support
"""

import os
import re
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextBrowser, QSplitter, QLineEdit, QPushButton, QLabel, QFrame,
    QComboBox, QStackedWidget
)
from qgis.PyQt.QtCore import Qt, QSize, QUrl
from qgis.PyQt.QtGui import QIcon, QFont

from qgis.core import QgsMessageLog, Qgis

def _log_info(msg):
    QgsMessageLog.logMessage(str(msg), 'TutorialViewer', Qgis.MessageLevel.Info)

# Web view import for animation playback — prefer QtWebKit (bundled with QGIS),
# fall back to QtWebEngine, then graceful degradation to system browser.
HAS_WEB_VIEW = False
_WebViewClass = None
_USE_WEBKIT = False
_QWebSettings = None

# Try QtWebKit first (available in most QGIS installations via qgis.PyQt)
try:
    from qgis.PyQt.QtWebKitWidgets import QWebView as _WebViewClass
    from qgis.PyQt.QtWebKit import QWebSettings as _QWebSettings
    HAS_WEB_VIEW = True
    _USE_WEBKIT = True
    _log_info("QWebView (QtWebKit) available — animation embedding enabled")
except (ImportError, AttributeError, RuntimeError):
    pass

# Fall back to QtWebEngine if QtWebKit not available
if not HAS_WEB_VIEW:
    try:
        from qgis.PyQt.QtWebEngineWidgets import QWebEngineView as _WebViewClass
        HAS_WEB_VIEW = True
        _log_info("QWebEngineView available — animation embedding enabled")
    except (ImportError, AttributeError, RuntimeError):
        pass

if not HAS_WEB_VIEW:
    _log_info("No web view available (QtWebKit/QtWebEngine) — animations will open in system browser")

from qgis.core import QgsSettings
from modules.utility.pyarchinit_theme_manager import ThemeManager


class TutorialViewerDialog(QDialog):
    """Dialog for viewing PyArchInit tutorials with multilingual support"""

    # Supported languages
    SUPPORTED_LANGUAGES = {
        'it': 'Italiano',
        'en': 'English',
        'de': 'Deutsch',
        'fr': 'Français',
        'es': 'Español',
        'ar': 'العربية',
        'ca': 'Català'
    }

    # Tutorial metadata per language - (filename, title, description)
    TUTORIALS_METADATA = {
        'it': [
            ("01_configurazione.md", "Configurazione", "Setup iniziale, connessione database, percorsi"),
            ("02_scheda_sito.md", "Scheda Sito", "Gestione siti archeologici"),
            ("03_scheda_us.md", "Scheda US/USM", "Unita Stratigrafiche e Murarie"),
            ("04_scheda_periodizzazione.md", "Periodizzazione", "Fasi e periodi cronologici"),
            ("05_scheda_struttura.md", "Scheda Struttura", "Documentazione strutture"),
            ("06_scheda_tomba.md", "Scheda Tomba", "Sepolture e corredi"),
            ("07_scheda_individui.md", "Scheda Individui", "Antropologia fisica"),
            ("08_scheda_inventario_materiali.md", "Inventario Materiali", "Gestione reperti"),
            ("09_scheda_campioni.md", "Scheda Campioni", "Campionature"),
            ("10_scheda_documentazione.md", "Documentazione", "Foto, disegni, rilievi"),
            ("11_matrix_harris.md", "Matrix di Harris", "Generazione diagrammi stratigrafici"),
            ("12_report_stampe.md", "Report e Stampe", "Generazione documentazione PDF"),
            ("13_thesaurus.md", "Thesaurus", "Gestione vocabolari controllati"),
            ("14_gis_cartografia.md", "GIS e Cartografia", "Integrazione QGIS e SAM Segmentation"),
            ("15_archeozoologia.md", "Archeozoologia", "Analisi faunistiche"),
            ("16_scheda_pottery.md", "Ceramica/Pottery", "Schedatura ceramica specialistica"),
            ("17_tma.md", "TMA", "Tabelle Materiali Archeologici"),
            ("18_backup.md", "Backup e Restore", "Gestione backup database"),
            ("19_multiutente.md", "Multi-utente", "Lavoro collaborativo PostgreSQL"),
            ("20_pubblicazione_web.md", "Pubblicazione Web", "Export e Lizmap"),
            ("21_scheda_ut.md", "Scheda UT", "Unita Topografiche / Survey"),
            ("22_media_manager.md", "Media Manager", "Gestione multimedia e allegati"),
            ("23_ricerca_immagini.md", "Ricerca Immagini", "Ricerca globale immagini"),
            ("24_esporta_immagini.md", "Esporta Immagini", "Export immagini per Periodo/Fase/US"),
            ("25_time_manager.md", "Time Manager", "Navigazione temporale stratigrafica"),
            ("26_pottery_tools.md", "Pottery Tools", "Strumenti elaborazione ceramica"),
            ("27_tops.md", "TOPS", "Total Open Station integration"),
            ("28_geopackage_export.md", "GeoPackage Export", "Export dati in GeoPackage"),
            ("29_make_your_map.md", "Make Your Map", "Generazione mappe e stampe"),
            ("30_ai_query_database.md", "AI Query Database", "Query database con AI (Text2SQL)"),
            ("31_stratigraph_uuid.md", "StratiGraph UUID", "Identificatori persistenti per il Knowledge Graph"),
            ("32_stratigraph_sync.md", "StratiGraph Sync", "Sincronizzazione offline-first con il Knowledge Graph"),
        ],
        'en': [
            ("01_configurazione.md", "Configuration", "Initial setup, database connection, paths"),
            ("02_scheda_sito.md", "Site Form", "Archaeological site management"),
            ("03_scheda_us.md", "SU/WSU Form", "Stratigraphic and Wall Units"),
            ("04_scheda_periodizzazione.md", "Periodization", "Chronological phases and periods"),
            ("05_scheda_struttura.md", "Structure Form", "Structure documentation"),
            ("06_scheda_tomba.md", "Burial Form", "Burials and grave goods"),
            ("07_scheda_individui.md", "Individuals Form", "Physical anthropology"),
            ("08_scheda_inventario_materiali.md", "Finds Inventory", "Artefact management"),
            ("09_scheda_campioni.md", "Samples Form", "Sampling"),
            ("10_scheda_documentazione.md", "Documentation", "Photos, drawings, surveys"),
            ("11_matrix_harris.md", "Harris Matrix", "Stratigraphic diagram generation"),
            ("12_report_stampe.md", "Reports & Printing", "PDF documentation generation"),
            ("13_thesaurus.md", "Thesaurus", "Controlled vocabulary management"),
            ("14_gis_cartografia.md", "GIS & Cartography", "QGIS integration and SAM Segmentation"),
            ("15_archeozoologia.md", "Archaeozoology", "Faunal analysis"),
            ("16_scheda_pottery.md", "Pottery", "Specialist ceramic recording"),
            ("17_tma.md", "TMA", "Archaeological Materials Tables"),
            ("18_backup.md", "Backup & Restore", "Database backup management"),
            ("19_multiutente.md", "Multi-user", "Collaborative work with PostgreSQL"),
            ("20_pubblicazione_web.md", "Web Publishing", "Export and Lizmap"),
            ("21_scheda_ut.md", "TU Form", "Topographic Units / Survey"),
            ("22_media_manager.md", "Media Manager", "Multimedia and attachments management"),
            ("23_ricerca_immagini.md", "Image Search", "Global image search"),
            ("24_esporta_immagini.md", "Export Images", "Image export by Period/Phase/SU"),
            ("25_time_manager.md", "Time Manager", "Stratigraphic temporal navigation"),
            ("26_pottery_tools.md", "Pottery Tools", "Ceramic processing tools"),
            ("27_tops.md", "TOPS", "Total Open Station integration"),
            ("28_geopackage_export.md", "GeoPackage Export", "Data export to GeoPackage"),
            ("29_make_your_map.md", "Make Your Map", "Map and print generation"),
            ("30_ai_query_database.md", "AI Query Database", "Database query with AI (Text2SQL)"),
            ("31_stratigraph_uuid.md", "StratiGraph UUID", "Persistent identifiers for the Knowledge Graph"),
            ("32_stratigraph_sync.md", "StratiGraph Sync", "Offline-first sync with the Knowledge Graph"),
        ],
        'de': [
            ("01_konfiguration.md", "Konfiguration", "Ersteinrichtung, Datenbankverbindung, Pfade"),
            ("02_fundort_formular.md", "Fundstelle", "Verwaltung archäologischer Fundstellen"),
            ("03_se_formular.md", "SE/MSE Formular", "Stratigraphische und Mauereinheiten"),
            ("04_periodisierung.md", "Periodisierung", "Chronologische Phasen und Perioden"),
            ("05_struktur_formular.md", "Struktur Formular", "Strukturdokumentation"),
            ("06_grab_formular.md", "Grab Formular", "Bestattungen und Grabbeigaben"),
            ("07_individuen_formular.md", "Individuen Formular", "Physische Anthropologie"),
            ("08_fundinventar_formular.md", "Fundinventar", "Artefaktverwaltung"),
            ("09_proben_formular.md", "Proben Formular", "Probenentnahme"),
            ("10_dokumentation_formular.md", "Dokumentation", "Fotos, Zeichnungen, Vermessungen"),
            ("11_harris_matrix.md", "Harris-Matrix", "Stratigraphische Diagrammerstellung"),
            ("12_berichte_pdf.md", "Berichte & Druck", "PDF-Dokumentationserstellung"),
            ("13_thesaurus.md", "Thesaurus", "Verwaltung kontrollierter Vokabulare"),
            ("14_gis_kartographie.md", "GIS & Kartographie", "QGIS-Integration und SAM-Segmentierung"),
            ("15_archaeozoologie.md", "Archäozoologie", "Faunistische Analyse"),
            ("16_keramik_formular.md", "Keramik", "Spezialisierte Keramikerfassung"),
            ("17_tma.md", "TMA", "Archäologische Materialtabellen"),
            ("18_backup.md", "Backup & Wiederherstellung", "Datenbank-Backup-Verwaltung"),
            ("19_mehrbenutzerbetrieb.md", "Mehrbenutzerbetrieb", "Kollaboratives Arbeiten mit PostgreSQL"),
            ("20_webveroeffentlichung.md", "Web-Veröffentlichung", "Export und Lizmap"),
            ("21_ut_formular.md", "TE Formular", "Topographische Einheiten / Survey"),
            ("22_medien_manager.md", "Medien-Manager", "Multimedia- und Anhangsverwaltung"),
            ("23_bildersuche.md", "Bildsuche", "Globale Bildsuche"),
            ("24_bilder_exportieren.md", "Bilder exportieren", "Bildexport nach Periode/Phase/SE"),
            ("25_time_manager.md", "Zeit-Manager", "Stratigraphische Zeitnavigation"),
            ("26_keramik_werkzeuge.md", "Keramik-Werkzeuge", "Keramikverarbeitungswerkzeuge"),
            ("27_tops.md", "TOPS", "Total Open Station Integration"),
            ("28_geopackage_export.md", "GeoPackage-Export", "Datenexport nach GeoPackage"),
            ("29_karte_erstellen.md", "Karte erstellen", "Karten- und Druckerstellung"),
            ("30_ki_datenbankabfrage.md", "KI-Datenbankabfrage", "Datenbankabfrage mit KI (Text2SQL)"),
            ("31_stratigraph_uuid.md", "StratiGraph UUID", "Persistente Identifikatoren für den Knowledge Graph"),
            ("32_stratigraph_sync.md", "StratiGraph Sync", "Offline-first Synchronisation mit dem Knowledge Graph"),
        ],
        'fr': [
            ("01_configuration.md", "Configuration", "Configuration initiale, connexion base de données, chemins"),
            ("02_fiche_site.md", "Fiche Site", "Gestion des sites archéologiques"),
            ("03_fiche_us.md", "Fiche US/USM", "Unités Stratigraphiques et Murales"),
            ("04_fiche_periodisation.md", "Périodisation", "Phases et périodes chronologiques"),
            ("05_fiche_structure.md", "Fiche Structure", "Documentation des structures"),
            ("06_fiche_tombe.md", "Fiche Sépulture", "Sépultures et mobilier funéraire"),
            ("07_fiche_individus.md", "Fiche Individus", "Anthropologie physique"),
            ("08_fiche_inventaire_materiaux.md", "Inventaire Mobilier", "Gestion des artefacts"),
            ("09_fiche_echantillons.md", "Fiche Échantillons", "Échantillonnage"),
            ("10_fiche_documentation.md", "Documentation", "Photos, dessins, relevés"),
            ("11_matrice_harris.md", "Matrice de Harris", "Génération de diagrammes stratigraphiques"),
            ("12_rapports_impressions.md", "Rapports & Impression", "Génération de documentation PDF"),
            ("13_thesaurus.md", "Thésaurus", "Gestion des vocabulaires contrôlés"),
            ("14_gis_cartographie.md", "SIG & Cartographie", "Intégration QGIS et Segmentation SAM"),
            ("15_archeozoologie.md", "Archéozoologie", "Analyse faunique"),
            ("16_fiche_pottery.md", "Céramique", "Enregistrement céramique spécialisé"),
            ("17_tma.md", "TMA", "Tables des Matériaux Archéologiques"),
            ("18_sauvegarde.md", "Sauvegarde & Restauration", "Gestion des sauvegardes de base de données"),
            ("19_multi_utilisateur.md", "Multi-utilisateur", "Travail collaboratif avec PostgreSQL"),
            ("20_publication_web.md", "Publication Web", "Export et Lizmap"),
            ("21_fiche_ut.md", "Fiche UT", "Unités Topographiques / Prospection"),
            ("22_gestionnaire_medias.md", "Gestionnaire Médias", "Gestion multimédia et pièces jointes"),
            ("23_recherche_images.md", "Recherche Images", "Recherche globale d'images"),
            ("24_export_images.md", "Exporter Images", "Export d'images par Période/Phase/US"),
            ("25_time_manager.md", "Gestionnaire Temps", "Navigation temporelle stratigraphique"),
            ("26_pottery_tools.md", "Outils Céramique", "Outils de traitement céramique"),
            ("27_tops.md", "TOPS", "Intégration Total Open Station"),
            ("28_export_geopackage.md", "Export GeoPackage", "Export de données vers GeoPackage"),
            ("29_creer_votre_carte.md", "Créer une Carte", "Génération de cartes et impressions"),
            ("30_requete_ia_base_donnees.md", "Requête IA Base de Données", "Requête de base de données avec IA (Text2SQL)"),
            ("31_stratigraph_uuid.md", "StratiGraph UUID", "Identifiants persistants pour le Knowledge Graph"),
            ("32_stratigraph_sync.md", "StratiGraph Sync", "Synchronisation offline-first avec le Knowledge Graph"),
        ],
        'es': [
            ("01_configuracion.md", "Configuración", "Configuración inicial, conexión de base de datos, rutas"),
            ("02_ficha_sitio.md", "Ficha Yacimiento", "Gestión de yacimientos arqueológicos"),
            ("03_ficha_ue.md", "Ficha UE/UEM", "Unidades Estratigráficas y Murarias"),
            ("04_ficha_periodizacion.md", "Periodización", "Fases y periodos cronológicos"),
            ("05_ficha_estructura.md", "Ficha Estructura", "Documentación de estructuras"),
            ("06_ficha_tumba.md", "Ficha Tumba", "Enterramientos y ajuares"),
            ("07_ficha_individuos.md", "Ficha Individuos", "Antropología física"),
            ("08_ficha_inventario_materiales.md", "Inventario Materiales", "Gestión de artefactos"),
            ("09_ficha_muestras.md", "Ficha Muestras", "Muestreo"),
            ("10_ficha_documentacion.md", "Documentación", "Fotos, dibujos, levantamientos"),
            ("11_matrix_harris.md", "Matriz de Harris", "Generación de diagramas estratigráficos"),
            ("12_informes_impresiones_pdf.md", "Informes e Impresión", "Generación de documentación PDF"),
            ("13_tesauro.md", "Tesauro", "Gestión de vocabularios controlados"),
            ("14_gis_cartografia.md", "SIG y Cartografía", "Integración QGIS y Segmentación SAM"),
            ("15_arqueozoologia.md", "Arqueozoología", "Análisis faunístico"),
            ("16_ficha_pottery.md", "Cerámica", "Registro cerámico especializado"),
            ("17_tma.md", "TMA", "Tablas de Materiales Arqueológicos"),
            ("18_backup_restauracion.md", "Copia de Seguridad", "Gestión de copias de seguridad de base de datos"),
            ("19_multiusuario.md", "Multiusuario", "Trabajo colaborativo con PostgreSQL"),
            ("20_publicacion_web.md", "Publicación Web", "Exportación y Lizmap"),
            ("21_ficha_ut.md", "Ficha UT", "Unidades Topográficas / Prospección"),
            ("22_media_manager.md", "Gestor de Medios", "Gestión multimedia y adjuntos"),
            ("23_busqueda_imagenes.md", "Búsqueda de Imágenes", "Búsqueda global de imágenes"),
            ("24_exportar_imagenes.md", "Exportar Imágenes", "Exportación de imágenes por Periodo/Fase/UE"),
            ("25_time_manager.md", "Gestor de Tiempo", "Navegación temporal estratigráfica"),
            ("26_pottery_tools.md", "Herramientas Cerámica", "Herramientas de procesamiento cerámico"),
            ("27_tops.md", "TOPS", "Integración Total Open Station"),
            ("28_geopackage_export.md", "Exportar GeoPackage", "Exportación de datos a GeoPackage"),
            ("29_crear_mapa.md", "Crear tu Mapa", "Generación de mapas e impresiones"),
            ("30_consulta_ai_database.md", "Consulta IA Base de Datos", "Consulta de base de datos con IA (Text2SQL)"),
            ("31_stratigraph_uuid.md", "StratiGraph UUID", "Identificadores persistentes para el Knowledge Graph"),
            ("32_stratigraph_sync.md", "StratiGraph Sync", "Sincronización offline-first con el Knowledge Graph"),
        ],
        'ar': [
            ("01_التكوين.md", "التكوين", "الإعداد الأولي، اتصال قاعدة البيانات، المسارات"),
            ("02_بطاقة_الموقع.md", "بطاقة الموقع", "إدارة المواقع الأثرية"),
            ("03_بطاقة_الوحدة_الطبقية.md", "بطاقة الوحدات", "الوحدات الطبقية والجدارية"),
            ("04_بطاقة_التأريخ.md", "التأريخ", "المراحل والفترات الزمنية"),
            ("05_بطاقة_الهيكل.md", "بطاقة الهيكل", "توثيق الهياكل"),
            ("06_بطاقة_القبر.md", "بطاقة القبر", "المدافن والمرفقات الجنائزية"),
            ("07_بطاقة_الأفراد.md", "بطاقة الأفراد", "الأنثروبولوجيا الفيزيائية"),
            ("08_بطاقة_جرد_المواد.md", "جرد المواد", "إدارة القطع الأثرية"),
            ("09_بطاقة_العينات.md", "بطاقة العينات", "أخذ العينات"),
            ("10_بطاقة_التوثيق.md", "التوثيق", "الصور والرسومات والمسوحات"),
            ("11_مصفوفة_هاريس.md", "مصفوفة هاريس", "إنشاء المخططات الطبقية"),
            ("12_التقارير_والطباعة.md", "التقارير والطباعة", "إنشاء وثائق PDF"),
            ("13_القاموس.md", "المكنز", "إدارة المفردات المنضبطة"),
            ("14_نظم_المعلومات_الجغرافية.md", "نظم المعلومات الجغرافية", "تكامل QGIS وتجزئة SAM"),
            ("15_علم_آثار_الحيوان.md", "علم الآثار الحيوانية", "التحليل الحيواني"),
            ("16_بطاقة_الفخار.md", "الفخار", "تسجيل الفخار المتخصص"),
            ("17_جدول_المواد_الأثرية.md", "TMA", "جداول المواد الأثرية"),
            ("18_النسخ_الاحتياطي.md", "النسخ الاحتياطي", "إدارة النسخ الاحتياطي لقاعدة البيانات"),
            ("19_العمل_متعدد_المستخدمين.md", "متعدد المستخدمين", "العمل التعاوني مع PostgreSQL"),
            ("20_النشر_على_الويب.md", "النشر على الويب", "التصدير و Lizmap"),
            ("21_بطاقة_الوحدة_الطبوغرافية.md", "بطاقة الوحدات الطبوغرافية", "الوحدات الطبوغرافية / المسح"),
            ("22_مدير_الوسائط.md", "مدير الوسائط", "إدارة الوسائط المتعددة والمرفقات"),
            ("23_البحث_عن_الصور.md", "البحث عن الصور", "البحث الشامل عن الصور"),
            ("24_تصدير_الصور.md", "تصدير الصور", "تصدير الصور حسب الفترة/المرحلة/الوحدة"),
            ("25_مدير_الزمن.md", "مدير الوقت", "التنقل الزمني الطبقي"),
            ("26_أدوات_الفخار.md", "أدوات الفخار", "أدوات معالجة الفخار"),
            ("27_المحطة_المساحية.md", "TOPS", "تكامل محطة المسح الكلية"),
            ("28_تصدير_جيوباكج.md", "تصدير GeoPackage", "تصدير البيانات إلى GeoPackage"),
            ("29_إنشاء_خريطتك.md", "إنشاء خريطتك", "إنشاء الخرائط والطباعة"),
            ("30_استعلام_قاعدة_البيانات_بالذكاء_الاصطناعي.md", "استعلام قاعدة البيانات بالذكاء الاصطناعي", "استعلام قاعدة البيانات بالذكاء الاصطناعي"),
            ("31_stratigraph_uuid.md", "StratiGraph UUID", "معرفات دائمة لرسم المعرفة"),
            ("32_stratigraph_sync.md", "StratiGraph Sync", "مزامنة دون اتصال أولاً مع رسم المعرفة"),
        ],
        'ca': [
            ("01_configuracio.md", "Configuració", "Configuració inicial, connexió de base de dades, camins"),
            ("02_fitxa_lloc.md", "Fitxa Jaciment", "Gestió de jaciments arqueològics"),
            ("03_fitxa_us.md", "Fitxa UE/UEM", "Unitats Estratigràfiques i Murals"),
            ("04_fitxa_perioditzacio.md", "Periodització", "Fases i períodes cronològics"),
            ("05_fitxa_estructura.md", "Fitxa Estructura", "Documentació d'estructures"),
            ("06_fitxa_tomba.md", "Fitxa Tomba", "Enterraments i aixovars"),
            ("07_fitxa_individus.md", "Fitxa Individus", "Antropologia física"),
            ("08_inventari_materials.md", "Inventari Materials", "Gestió d'artefactes"),
            ("09_fitxa_mostres.md", "Fitxa Mostres", "Mostreig"),
            ("10_fitxa_documentacio.md", "Documentació", "Fotos, dibuixos, aixecaments"),
            ("11_matriu_harris.md", "Matriu de Harris", "Generació de diagrames estratigràfics"),
            ("12_informes_impressions.md", "Informes i Impressió", "Generació de documentació PDF"),
            ("13_tesaurus.md", "Tesaurus", "Gestió de vocabularis controlats"),
            ("14_gis_cartografia.md", "SIG i Cartografia", "Integració QGIS i Segmentació SAM"),
            ("15_arqueozoologia.md", "Arqueozoologia", "Anàlisi faunística"),
            ("16_fitxa_pottery.md", "Ceràmica", "Registre ceràmic especialitzat"),
            ("17_tma.md", "TMA", "Taules de Materials Arqueològics"),
            ("18_copia_seguretat.md", "Còpia de Seguretat", "Gestió de còpies de seguretat de base de dades"),
            ("19_multiusuari.md", "Multiusuari", "Treball col·laboratiu amb PostgreSQL"),
            ("20_publicacio_web.md", "Publicació Web", "Exportació i Lizmap"),
            ("21_fitxa_ut.md", "Fitxa UT", "Unitats Topogràfiques / Prospecció"),
            ("22_gestor_media.md", "Gestor de Mitjans", "Gestió multimèdia i adjunts"),
            ("23_cerca_imatges.md", "Cerca d'Imatges", "Cerca global d'imatges"),
            ("24_exporta_imatges.md", "Exportar Imatges", "Exportació d'imatges per Període/Fase/UE"),
            ("25_gestor_temps.md", "Gestor de Temps", "Navegació temporal estratigràfica"),
            ("26_eines_ceramica.md", "Eines Ceràmica", "Eines de processament ceràmic"),
            ("27_tops.md", "TOPS", "Integració Total Open Station"),
            ("28_exportacio_geopackage.md", "Exportar GeoPackage", "Exportació de dades a GeoPackage"),
            ("29_crea_mapa.md", "Crear el teu Mapa", "Generació de mapes i impressions"),
            ("30_consulta_ai_bd.md", "Consulta IA Base de Dades", "Consulta de base de dades amb IA (Text2SQL)"),
            ("31_stratigraph_uuid.md", "StratiGraph UUID", "Identificadors persistents per al Knowledge Graph"),
            ("32_stratigraph_sync.md", "StratiGraph Sync", "Sincronització offline-first amb el Knowledge Graph"),
        ],
    }

    # UI Labels per language
    UI_LABELS = {
        'it': {
            'window_title': 'PyArchInit - Tutorial e Documentazione',
            'search': 'Cerca:',
            'search_placeholder': 'Cerca nei tutorial...',
            'available': 'Tutorial Disponibili:',
            'content': 'Contenuto:',
            'close': 'Chiudi',
            'back': 'Indietro',
            'language': 'Lingua:',
            'not_available': 'Tutorial non disponibile',
            'file_not_found': 'Il file non è stato trovato.',
            'path': 'Percorso',
            'load_error': 'Errore nel caricamento',
            'error_loading': 'Si è verificato un errore nel caricamento del tutorial:',
        },
        'en': {
            'window_title': 'PyArchInit - Tutorials & Documentation',
            'search': 'Search:',
            'search_placeholder': 'Search tutorials...',
            'available': 'Available Tutorials:',
            'content': 'Content:',
            'close': 'Close',
            'back': 'Back',
            'language': 'Language:',
            'not_available': 'Tutorial not available',
            'file_not_found': 'The file was not found.',
            'path': 'Path',
            'load_error': 'Loading error',
            'error_loading': 'An error occurred while loading the tutorial:',
        },
        'de': {
            'window_title': 'PyArchInit - Tutorials & Dokumentation',
            'search': 'Suchen:',
            'search_placeholder': 'Tutorials durchsuchen...',
            'available': 'Verfügbare Tutorials:',
            'content': 'Inhalt:',
            'close': 'Schließen',
            'back': 'Zurück',
            'language': 'Sprache:',
            'not_available': 'Tutorial nicht verfügbar',
            'file_not_found': 'Die Datei wurde nicht gefunden.',
            'path': 'Pfad',
            'load_error': 'Ladefehler',
            'error_loading': 'Beim Laden des Tutorials ist ein Fehler aufgetreten:',
        },
        'fr': {
            'window_title': 'PyArchInit - Tutoriels & Documentation',
            'search': 'Rechercher:',
            'search_placeholder': 'Rechercher dans les tutoriels...',
            'available': 'Tutoriels Disponibles:',
            'content': 'Contenu:',
            'close': 'Fermer',
            'back': 'Retour',
            'language': 'Langue:',
            'not_available': 'Tutoriel non disponible',
            'file_not_found': 'Le fichier n\'a pas été trouvé.',
            'path': 'Chemin',
            'load_error': 'Erreur de chargement',
            'error_loading': 'Une erreur s\'est produite lors du chargement du tutoriel:',
        },
        'es': {
            'window_title': 'PyArchInit - Tutoriales y Documentación',
            'search': 'Buscar:',
            'search_placeholder': 'Buscar en tutoriales...',
            'available': 'Tutoriales Disponibles:',
            'content': 'Contenido:',
            'close': 'Cerrar',
            'back': 'Atrás',
            'language': 'Idioma:',
            'not_available': 'Tutorial no disponible',
            'file_not_found': 'El archivo no fue encontrado.',
            'path': 'Ruta',
            'load_error': 'Error de carga',
            'error_loading': 'Se produjo un error al cargar el tutorial:',
        },
        'ar': {
            'window_title': 'PyArchInit - الدروس والتوثيق',
            'search': 'بحث:',
            'search_placeholder': 'البحث في الدروس...',
            'available': 'الدروس المتاحة:',
            'content': 'المحتوى:',
            'close': 'إغلاق',
            'back': 'رجوع',
            'language': 'اللغة:',
            'not_available': 'الدرس غير متاح',
            'file_not_found': 'لم يتم العثور على الملف.',
            'path': 'المسار',
            'load_error': 'خطأ في التحميل',
            'error_loading': 'حدث خطأ أثناء تحميل الدرس:',
        },
        'ca': {
            'window_title': 'PyArchInit - Tutorials i Documentació',
            'search': 'Cercar:',
            'search_placeholder': 'Cercar en tutorials...',
            'available': 'Tutorials Disponibles:',
            'content': 'Contingut:',
            'close': 'Tancar',
            'back': 'Enrere',
            'language': 'Idioma:',
            'not_available': 'Tutorial no disponible',
            'file_not_found': 'El fitxer no s\'ha trobat.',
            'path': 'Camí',
            'load_error': 'Error de càrrega',
            'error_loading': 'S\'ha produït un error en carregar el tutorial:',
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # Detect QGIS language
        self.current_lang = self.detect_language()
        self.labels = self.UI_LABELS.get(self.current_lang, self.UI_LABELS['it'])

        self.setWindowTitle(self.labels['window_title'])
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Get tutorials path
        self.plugin_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tutorials_base_path = os.path.join(self.plugin_path, "docs", "tutorials")

        self.setup_ui()
        self.load_tutorial_list()

        # Theme support
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)
        # Also reload HTML content on theme toggle to update inner CSS
        self.theme_toggle_btn.clicked.connect(self._on_theme_toggled)
        ThemeManager.apply_theme(self)

        # Select first tutorial by default
        if self.tutorial_list.count() > 0:
            self.tutorial_list.setCurrentRow(0)

    def detect_language(self):
        """Detect QGIS locale and return language code"""
        locale = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if locale in self.SUPPORTED_LANGUAGES:
            return locale
        return 'it'  # Default to Italian

    def _on_theme_toggled(self):
        """Reload current tutorial content to apply new theme CSS"""
        current = self.tutorial_list.currentItem()
        if current:
            self.on_tutorial_selected(current, None)

    def get_tutorials_path(self, lang=None):
        """Get the tutorials path for a specific language"""
        if lang is None:
            lang = self.current_lang
        return os.path.join(self.tutorials_base_path, lang)

    def setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Top bar with search and language selector
        top_layout = QHBoxLayout()

        # Search bar
        search_label = QLabel(self.labels['search'])
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.labels['search_placeholder'])
        self.search_edit.textChanged.connect(self.filter_tutorials)
        top_layout.addWidget(search_label)
        top_layout.addWidget(self.search_edit, 1)

        top_layout.addSpacing(20)

        # Language selector
        lang_label = QLabel(self.labels['language'])
        self.lang_combo = QComboBox()
        for code, name in self.SUPPORTED_LANGUAGES.items():
            self.lang_combo.addItem(name, code)
        # Set current language
        index = self.lang_combo.findData(self.current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        top_layout.addWidget(lang_label)
        top_layout.addWidget(self.lang_combo)

        main_layout.addLayout(top_layout)

        # Splitter for list and content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Tutorial list
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.list_label = QLabel(self.labels['available'])
        self.list_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        left_layout.addWidget(self.list_label)

        self.tutorial_list = QListWidget()
        self.tutorial_list.setMinimumWidth(280)
        self.tutorial_list.currentItemChanged.connect(self.on_tutorial_selected)
        left_layout.addWidget(self.tutorial_list)

        splitter.addWidget(left_frame)

        # Right panel - Content viewer
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.content_label = QLabel(self.labels['content'])
        self.content_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        right_layout.addWidget(self.content_label)

        # Back button (hidden by default, shown when viewing an animation)
        self.back_button = QPushButton(self.labels.get('back', 'Back'))
        self.back_button.setVisible(False)
        self.back_button.clicked.connect(self._on_back_clicked)
        right_layout.addWidget(self.back_button)

        # QStackedWidget: page 0 = QTextBrowser (markdown), page 1 = QWebEngineView (animations)
        self.content_stack = QStackedWidget()

        # Page 0: QTextBrowser — always used for markdown rendering
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(False)
        self.content_browser.setOpenLinks(False)
        self.content_browser.anchorClicked.connect(self._on_link_clicked)
        self.content_browser.setMouseTracking(True)
        self.content_browser.viewport().setMouseTracking(True)
        self.content_browser.viewport().installEventFilter(self)
        self.content_browser.setStyleSheet("")
        self.use_webengine = False  # markdown always via QTextBrowser
        self._hover_popup = None
        self._image_cache = {}
        self._figure_images = []
        self._thumb_to_full = {}
        self.current_tutorial_dir = None
        self._last_hover_path = None
        self._hover_timer = None
        self.content_stack.addWidget(self.content_browser)  # index 0

        # Page 1: QWebEngineView — for HTML5 animation files (if available)
        self.animation_viewer = None
        if HAS_WEB_VIEW:
            self.animation_viewer = _WebViewClass()
            # Enable JavaScript and local file access for HTML5 animations
            if _USE_WEBKIT and _QWebSettings:
                ws = self.animation_viewer.settings()
                ws.setAttribute(_QWebSettings.JavascriptEnabled, True)
                ws.setAttribute(_QWebSettings.LocalContentCanAccessFileUrls, True)
                ws.setAttribute(_QWebSettings.DeveloperExtrasEnabled, True)
            self.content_stack.addWidget(self.animation_viewer)  # index 1
            self.animation_viewer.installEventFilter(self)
            _log_info("Animation viewer ready as stack page 1")
        else:
            _log_info("No QWebEngineView — animation links will fall back to system browser")

        self.content_stack.setCurrentIndex(0)
        right_layout.addWidget(self.content_stack)

        splitter.addWidget(right_frame)

        # Set splitter sizes (30% list, 70% content)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter)

        # Footer with buttons
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        close_button = QPushButton(self.labels['close'])
        close_button.clicked.connect(self.close)
        footer_layout.addWidget(close_button)

        main_layout.addLayout(footer_layout)

    def eventFilter(self, obj, event):
        """Handle mouse events for image hover popup"""
        from qgis.PyQt.QtCore import QEvent

        if obj == self.content_browser.viewport():
            if event.type() == QEvent.Type.MouseMove:
                self.handle_mouse_move(event)
            elif event.type() == QEvent.Type.Leave:
                self.hide_hover_popup()
            elif event.type() == QEvent.Type.MouseButtonPress:
                # Handle click on figure thumbnail
                img_path = self.get_figure_at_position(event.pos())
                if img_path:
                    self.hide_hover_popup()  # Hide hover popup before showing dialog
                    self.show_image_dialog(img_path)
                    return True  # Consume the event

        return super().eventFilter(obj, event)

    def _on_link_clicked(self, url):
        """Handle link clicks in QTextBrowser — resolve relative paths,
        load .html animations in embedded viewer or open in browser."""
        url_str = url.toString()

        # Resolve relative paths using current tutorial directory
        if not url.scheme() or url.scheme() == 'file':
            if hasattr(self, 'current_tutorial_dir') and self.current_tutorial_dir:
                relative_path = url.toLocalFile() or url_str
                abs_path = os.path.normpath(os.path.join(self.current_tutorial_dir, relative_path))
                if os.path.isfile(abs_path):
                    # If it's an HTML file, try to load in embedded animation viewer
                    if abs_path.lower().endswith('.html') and self.animation_viewer is not None:
                        self._load_animation(abs_path)
                        return
                    # Otherwise open in system browser
                    import webbrowser
                    webbrowser.open(f'file://{abs_path}')
                    return

        # External URLs
        import webbrowser
        webbrowser.open(url_str)

    def _load_animation(self, file_path):
        """Load a local HTML animation file into the embedded QWebView."""
        _log_info("Loading animation: {}".format(file_path))
        self.back_button.setVisible(True)
        self._current_animation_path = file_path
        self.animation_viewer.setUrl(QUrl.fromLocalFile(file_path))
        self.content_stack.setCurrentIndex(1)

    def _on_back_clicked(self):
        """Go back to the current tutorial from an animation view."""
        self.back_button.setVisible(False)
        self.content_stack.setCurrentIndex(0)
        self._current_animation_path = None
        if self.animation_viewer is not None:
            self.animation_viewer.setUrl(QUrl('about:blank'))

    def get_figure_at_position(self, pos):
        """Check if position is over a figure thumbnail and return image path"""
        cursor = self.content_browser.cursorForPosition(pos)
        char_format = cursor.charFormat()

        # Check if we're over an image (thumbnail)
        if char_format.isImageFormat():
            img_name = char_format.toImageFormat().name()
            # Check if this is one of our figure thumbnails (data URI)
            if img_name.startswith('data:image') and self._thumb_to_full:
                # Use hash of first 100 chars of data URI as key
                thumb_key = hash(img_name[:100])
                if thumb_key in self._thumb_to_full:
                    return self._thumb_to_full[thumb_key]
        return None

    def handle_mouse_move(self, event):
        """Check if mouse is over a figure and show popup with debounce"""
        from qgis.PyQt.QtCore import QTimer

        img_path = self.get_figure_at_position(event.pos())

        # Debounce: only update if path changed
        if img_path == self._last_hover_path:
            return

        self._last_hover_path = img_path

        # Cancel pending timer
        if self._hover_timer:
            self._hover_timer.stop()

        if img_path:
            # Delay showing popup slightly to prevent flicker
            self._hover_timer = QTimer()
            self._hover_timer.setSingleShot(True)
            self._hover_timer.timeout.connect(lambda: self.show_hover_popup(img_path))
            self._hover_timer.start(150)  # 150ms delay
        else:
            self.hide_hover_popup()

    def show_hover_popup(self, img_path):
        """Show hover popup with full-size image centered in dialog"""
        if not hasattr(self, '_image_cache') or img_path not in self._image_cache:
            return

        # Don't recreate if already showing same image
        if self._hover_popup and self._hover_popup.isVisible():
            if hasattr(self._hover_popup, '_img_path') and self._hover_popup._img_path == img_path:
                return

        from qgis.PyQt.QtWidgets import QLabel
        from qgis.PyQt.QtGui import QPixmap
        from qgis.PyQt.QtCore import Qt
        import base64

        # Create or reuse popup
        if not self._hover_popup:
            self._hover_popup = QLabel(None, Qt.WindowType.ToolTip)
            if ThemeManager.is_dark_theme():
                self._hover_popup.setStyleSheet("background: #2b2b2b; border: 2px solid #555; padding: 5px;")
            else:
                self._hover_popup.setStyleSheet("background: white; border: 2px solid #333; padding: 5px;")

        # Load image
        img_data = base64.b64decode(self._image_cache[img_path])
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)

        # Scale if too large for screen
        screen_size = self.screen().availableGeometry()
        max_w = int(screen_size.width() * 0.7)
        max_h = int(screen_size.height() * 0.7)
        if pixmap.width() > max_w or pixmap.height() > max_h:
            pixmap = pixmap.scaled(max_w, max_h, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)

        self._hover_popup.setPixmap(pixmap)
        self._hover_popup._img_path = img_path

        # Position popup in the center of the dialog window
        dialog_geometry = self.geometry()
        dialog_center = self.mapToGlobal(dialog_geometry.center() - dialog_geometry.topLeft())
        x = dialog_center.x() - pixmap.width() // 2
        y = dialog_center.y() - pixmap.height() // 2

        self._hover_popup.move(x, y)
        self._hover_popup.show()

    def hide_hover_popup(self):
        """Hide the hover popup"""
        if self._hover_popup and self._hover_popup.isVisible():
            self._hover_popup.hide()

    def show_image_dialog(self, img_path):
        """Show image in a dialog with close button"""
        if not hasattr(self, '_image_cache') or img_path not in self._image_cache:
            return

        from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea
        from qgis.PyQt.QtGui import QPixmap
        from qgis.PyQt.QtCore import Qt
        import base64

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Figura")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        # Scroll area for large images
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Image label
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Load image
        img_data = base64.b64decode(self._image_cache[img_path])
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)

        # Scale if too large for screen
        screen_size = self.screen().availableGeometry()
        max_w = int(screen_size.width() * 0.85)
        max_h = int(screen_size.height() * 0.85)
        if pixmap.width() > max_w or pixmap.height() > max_h:
            pixmap = pixmap.scaled(max_w, max_h, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)

        img_label.setPixmap(pixmap)
        scroll.setWidget(img_label)
        layout.addWidget(scroll)

        # Close button
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        # Size dialog to image
        dialog.resize(min(pixmap.width() + 50, max_w), min(pixmap.height() + 80, max_h))

        dialog.exec()

    def on_language_changed(self, index):
        """Handle language change"""
        new_lang = self.lang_combo.itemData(index)
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            self.labels = self.UI_LABELS.get(self.current_lang, self.UI_LABELS['it'])
            self.update_ui_labels()
            self.load_tutorial_list()
            if self.tutorial_list.count() > 0:
                self.tutorial_list.setCurrentRow(0)

    def update_ui_labels(self):
        """Update UI labels after language change"""
        self.setWindowTitle(self.labels['window_title'])
        self.search_edit.setPlaceholderText(self.labels['search_placeholder'])
        self.list_label.setText(self.labels['available'])
        self.content_label.setText(self.labels['content'])

    def load_tutorial_list(self):
        """Load the list of available tutorials for current language"""
        self.tutorial_list.clear()

        tutorials = self.TUTORIALS_METADATA.get(self.current_lang, self.TUTORIALS_METADATA['it'])
        tutorials_path = self.get_tutorials_path()
        fallback_path = self.get_tutorials_path('it')

        for filename, title, description in tutorials:
            filepath = os.path.join(tutorials_path, filename)
            fallback_filepath = os.path.join(fallback_path, filename)

            item = QListWidgetItem()
            item.setText(f"{title}\n{description}")
            item.setData(Qt.ItemDataRole.UserRole, filename)
            item.setSizeHint(QSize(250, 50))

            # Check if file exists in current language or fallback
            if not os.path.exists(filepath) and not os.path.exists(fallback_filepath):
                item.setForeground(Qt.GlobalColor.gray)
                item.setToolTip(self.labels['not_available'])

            self.tutorial_list.addItem(item)

    def filter_tutorials(self, text):
        """Filter tutorials based on search text"""
        search_text = text.lower()

        for i in range(self.tutorial_list.count()):
            item = self.tutorial_list.item(i)
            item_text = item.text().lower()
            filename = item.data(Qt.ItemDataRole.UserRole)

            # Also search in description
            matches = search_text in item_text or search_text in filename.lower()
            item.setHidden(not matches)

    def on_tutorial_selected(self, current, previous):
        """Handle tutorial selection"""
        if current is None:
            return

        filename = current.data(Qt.ItemDataRole.UserRole)

        # Try current language first, then fallback to Italian
        filepath = os.path.join(self.get_tutorials_path(), filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(self.get_tutorials_path('it'), filename)

        if os.path.exists(filepath):
            self.load_tutorial_content(filepath)
        else:
            is_dark = ThemeManager.is_dark_theme()
            bg = '#1e1e1e' if is_dark else '#ffffff'
            fg = '#e0e0e0' if is_dark else '#333333'
            self.content_browser.setHtml(
                f"<html><body style='background:{bg};color:{fg};padding:20px;'>"
                f"<h2>{self.labels['not_available']}</h2>"
                f"<p>{self.labels['file_not_found']}</p>"
                f"<p>{self.labels['path']}: <code>{filepath}</code></p>"
                f"</body></html>"
            )

    def load_tutorial_content(self, filepath):
        """Load and display tutorial content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Store tutorial directory for image path resolution
            self.current_tutorial_dir = os.path.dirname(filepath)

            # Initialize image caches and reset hover state
            self._image_cache = {}
            self._figure_images = []
            self._thumb_to_full = {}
            self._last_hover_path = None
            self.hide_hover_popup()

            # Convert markdown to HTML
            html_content = self.markdown_to_html(markdown_content)

            # Determine text direction for Arabic
            direction = 'rtl' if self.current_lang == 'ar' else 'ltr'
            text_align = 'right' if direction == 'rtl' else 'left'
            border_side = 'right' if direction == 'rtl' else 'left'
            padding_side = 'right' if direction == 'rtl' else 'left'

            # Theme-aware CSS
            is_dark = ThemeManager.is_dark_theme()
            if is_dark:
                bg_color = '#1e1e1e'
                text_color = '#e0e0e0'
                h1_color = '#4da6ff'
                h2_color = '#7fbbf5'
                h3_color = '#a0c4e8'
                h4_color = '#8ab4d9'
                code_bg = '#2d2d2d'
                code_color = '#e0e0e0'
                pre_bg = '#2d2d2d'
                pre_border = '#444444'
                table_border = '#444444'
                th_bg = '#2a6496'
                th_color = '#ffffff'
                tr_even_bg = '#252525'
                tr_hover_bg = '#2a2a2a'
                blockquote_bg = '#252525'
                blockquote_border = '#4da6ff'
                link_color = '#4da6ff'
                hr_color = '#444444'
                img_border = '#444444'
                highlight_bg = '#4a4a00'
                highlight_color = '#ffff66'
            else:
                bg_color = '#ffffff'
                text_color = '#333333'
                h1_color = '#2c3e50'
                h2_color = '#34495e'
                h3_color = '#555555'
                h4_color = '#666666'
                code_bg = '#f0f0f0'
                code_color = '#333333'
                pre_bg = '#f5f5f5'
                pre_border = '#dddddd'
                table_border = '#dddddd'
                th_bg = '#3498db'
                th_color = '#ffffff'
                tr_even_bg = '#f9f9f9'
                tr_hover_bg = '#f5f5f5'
                blockquote_bg = '#ecf0f1'
                blockquote_border = '#3498db'
                link_color = '#3498db'
                hr_color = '#bdc3c7'
                img_border = '#dddddd'
                highlight_bg = '#fff3cd'
                highlight_color = '#333333'

            # Add CSS styling
            styled_html = f"""
            <!DOCTYPE html>
            <html dir="{direction}">
            <head>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                        font-size: 14px;
                        line-height: 1.6;
                        color: {text_color};
                        background-color: {bg_color};
                        max-width: 100%;
                        padding: 10px;
                        direction: {direction};
                    }}
                    h1 {{
                        color: {h1_color};
                        border-bottom: 2px solid {link_color};
                        padding-bottom: 10px;
                        font-size: 24px;
                    }}
                    h2 {{
                        color: {h2_color};
                        border-bottom: 1px solid {hr_color};
                        padding-bottom: 5px;
                        margin-top: 25px;
                        font-size: 20px;
                    }}
                    h3 {{
                        color: {h3_color};
                        margin-top: 20px;
                        font-size: 16px;
                    }}
                    h4 {{
                        color: {h4_color};
                        font-size: 14px;
                    }}
                    code {{
                        background-color: {code_bg};
                        color: {code_color};
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
                        font-size: 13px;
                    }}
                    pre {{
                        background-color: {pre_bg};
                        color: {code_color};
                        padding: 15px;
                        border-radius: 5px;
                        border: 1px solid {pre_border};
                        overflow-x: auto;
                        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
                        font-size: 13px;
                    }}
                    pre code {{
                        background-color: transparent;
                        color: {code_color};
                        padding: 0;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 15px 0;
                    }}
                    th, td {{
                        border: 1px solid {table_border};
                        padding: 10px;
                        text-align: {text_align};
                    }}
                    th {{
                        background-color: {th_bg};
                        color: {th_color};
                    }}
                    tr:nth-child(even) {{
                        background-color: {tr_even_bg};
                    }}
                    tr:hover {{
                        background-color: {tr_hover_bg};
                    }}
                    blockquote {{
                        border-{border_side}: 4px solid {blockquote_border};
                        margin: 15px 0;
                        padding: 10px 20px;
                        background-color: {blockquote_bg};
                        font-style: italic;
                        color: {text_color};
                    }}
                    ul, ol {{
                        margin: 10px 0;
                        padding-{padding_side}: 25px;
                    }}
                    li {{
                        margin: 5px 0;
                    }}
                    a {{
                        color: {link_color};
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    hr {{
                        border: none;
                        border-top: 1px solid {hr_color};
                        margin: 20px 0;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        display: block;
                        border: 1px solid {img_border};
                        border-radius: 4px;
                    }}
                    .figure {{
                        margin: 15px 0;
                        padding: 0;
                    }}
                    .figure-title {{
                        font-weight: bold;
                        margin-bottom: 5px;
                    }}
                    .figure img {{
                        margin-bottom: 0;
                    }}
                    strong {{
                        color: {text_color};
                    }}
                    em {{
                        color: {text_color};
                    }}
                    .highlight {{
                        background-color: #ffc107;
                        color: #000000;
                        padding: 1px 4px;
                        border-radius: 3px;
                    }}
                    .highlight-green {{
                        background-color: #28a745;
                        color: #000000;
                        padding: 1px 4px;
                        border-radius: 3px;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # Ensure we're showing the markdown page (not animation)
            self.content_stack.setCurrentIndex(0)
            self.back_button.setVisible(False)
            self.content_browser.setHtml(styled_html)

        except Exception as e:
            is_dark = ThemeManager.is_dark_theme()
            bg = '#1e1e1e' if is_dark else '#ffffff'
            fg = '#e0e0e0' if is_dark else '#333333'
            error_html = (
                f"<html><body style='background:{bg};color:{fg};padding:20px;'>"
                f"<h2>{self.labels['load_error']}</h2>"
                f"<p>{self.labels['error_loading']}</p>"
                f"<pre>{str(e)}</pre>"
                f"</body></html>"
            )
            self.content_browser.setHtml(error_html)

    def markdown_to_html(self, markdown_text):
        """
        Convert markdown to HTML using basic regex patterns.
        This is a simple converter that handles common markdown elements.
        """
        html = markdown_text

        # Escape HTML special characters in code blocks first
        # Handle fenced code blocks (```)
        def replace_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2)
            # Escape HTML in code
            code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return f'<pre><code class="language-{lang}">{code}</code></pre>'

        html = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, html, flags=re.DOTALL)

        # Inline code (must be after code blocks)
        def replace_inline_code(match):
            code = match.group(1)
            code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return f'<code>{code}</code>'

        html = re.sub(r'`([^`]+)`', replace_inline_code, html)

        # Headers
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Images - MUST be processed BEFORE links (otherwise link regex captures [alt](path) part)
        def replace_image(match):
            alt_text = match.group(1)
            img_path = match.group(2)

            # Build absolute path
            if hasattr(self, 'current_tutorial_dir'):
                abs_path = os.path.join(self.current_tutorial_dir, img_path)
                if os.path.exists(abs_path):
                    # QTextBrowser: show only caption, image on hover
                    import base64
                    try:
                        # Store full image for hover popup
                        if not hasattr(self, '_image_cache'):
                            self._image_cache = {}
                        with open(abs_path, 'rb') as f:
                            self._image_cache[img_path] = base64.b64encode(f.read()).decode('utf-8')
                        # Create a small thumbnail for preview
                        from PIL import Image as PILImage
                        from io import BytesIO
                        pil_img = PILImage.open(abs_path)
                        # Create thumbnail maintaining aspect ratio
                        max_thumb = 80
                        ratio = min(max_thumb / pil_img.width, max_thumb / pil_img.height)
                        thumb_size = (int(pil_img.width * ratio), int(pil_img.height * ratio))
                        pil_thumb = pil_img.resize(thumb_size, PILImage.LANCZOS)
                        thumb_buffer = BytesIO()
                        pil_thumb.save(thumb_buffer, format='PNG')
                        thumb_data = base64.b64encode(thumb_buffer.getvalue()).decode('utf-8')
                        # Store mapping: hash of thumbnail data URI -> full image path
                        thumb_uri = f"data:image/png;base64,{thumb_data}"
                        thumb_key = hash(thumb_uri[:100])
                        if not hasattr(self, '_thumb_to_full'):
                            self._thumb_to_full = {}
                        self._thumb_to_full[thumb_key] = img_path
                        # Also keep list for backwards compatibility
                        if not hasattr(self, '_figure_images'):
                            self._figure_images = []
                        self._figure_images.append(img_path)
                        # Display thumbnail with data URI
                        return (f'<p><img src="{thumb_uri}" '
                                f'style="vertical-align: middle; border: 2px solid currentColor; '
                                f'border-radius: 4px;"> '
                                f'<b>{alt_text}</b> '
                                f'<small>(clicca per ingrandire)</small></p>')
                    except Exception as e:
                        return f'<p><span class="highlight">[Errore immagine: {e}]</span></p>'
                else:
                    return f'<p><span class="highlight">[Image not found: {alt_text}]</span></p>'

            return f'<img src="{img_path}" alt="{alt_text}">'

        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, html)

        # Links (after images to avoid capturing image syntax)
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

        # Horizontal rules
        html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)

        # Tables
        html = self.convert_tables(html)

        # Blockquotes
        def convert_blockquote(match):
            content = match.group(0)
            lines = content.split('\n')
            quote_lines = []
            for line in lines:
                if line.startswith('>'):
                    quote_lines.append(line[1:].strip())
            return '<blockquote>' + '<br>'.join(quote_lines) + '</blockquote>'

        html = re.sub(r'(^>.*$\n?)+', convert_blockquote, html, flags=re.MULTILINE)

        # Unordered lists
        html = self.convert_lists(html)

        # Paragraphs (double newlines)
        html = re.sub(r'\n\n+', '</p><p>', html)
        html = '<p>' + html + '</p>'

        # Clean up empty paragraphs and fix nesting issues
        html = re.sub(r'<p>\s*</p>', '', html)
        html = re.sub(r'<p>\s*(<h[1-6]>)', r'\1', html)
        html = re.sub(r'(</h[1-6]>)\s*</p>', r'\1', html)
        html = re.sub(r'<p>\s*(<pre>)', r'\1', html)
        html = re.sub(r'(</pre>)\s*</p>', r'\1', html)
        html = re.sub(r'<p>\s*(<table>)', r'\1', html)
        html = re.sub(r'(</table>)\s*</p>', r'\1', html)
        html = re.sub(r'<p>\s*(<ul>)', r'\1', html)
        html = re.sub(r'(</ul>)\s*</p>', r'\1', html)
        html = re.sub(r'<p>\s*(<ol>)', r'\1', html)
        html = re.sub(r'(</ol>)\s*</p>', r'\1', html)
        html = re.sub(r'<p>\s*(<blockquote>)', r'\1', html)
        html = re.sub(r'(</blockquote>)\s*</p>', r'\1', html)
        html = re.sub(r'<p>\s*(<hr>)', r'\1', html)
        html = re.sub(r'(<hr>)\s*</p>', r'\1', html)

        return html

    def convert_tables(self, html):
        """Convert markdown tables to HTML"""
        lines = html.split('\n')
        result = []
        in_table = False
        table_html = []

        for i, line in enumerate(lines):
            # Check if line is a table row
            if '|' in line and line.strip().startswith('|'):
                cells = [c.strip() for c in line.strip().split('|')[1:-1]]

                if not in_table:
                    in_table = True
                    table_html = ['<table>']
                    # This is the header
                    table_html.append('<thead><tr>')
                    for cell in cells:
                        table_html.append(f'<th>{cell}</th>')
                    table_html.append('</tr></thead>')
                elif all(c.replace('-', '').replace(':', '').strip() == '' for c in cells):
                    # This is the separator row, start tbody
                    table_html.append('<tbody>')
                else:
                    # Regular data row
                    table_html.append('<tr>')
                    for cell in cells:
                        table_html.append(f'<td>{cell}</td>')
                    table_html.append('</tr>')
            else:
                if in_table:
                    # End of table
                    table_html.append('</tbody></table>')
                    result.append('\n'.join(table_html))
                    in_table = False
                    table_html = []
                result.append(line)

        # Handle table at end of file
        if in_table:
            table_html.append('</tbody></table>')
            result.append('\n'.join(table_html))

        return '\n'.join(result)

    def convert_lists(self, html):
        """Convert markdown lists to HTML"""
        lines = html.split('\n')
        result = []
        in_ul = False
        in_ol = False

        for line in lines:
            stripped = line.strip()

            # Unordered list item
            if stripped.startswith('- ') or stripped.startswith('* '):
                if not in_ul:
                    if in_ol:
                        result.append('</ol>')
                        in_ol = False
                    result.append('<ul>')
                    in_ul = True
                content = stripped[2:]
                result.append(f'<li>{content}</li>')
            # Ordered list item
            elif re.match(r'^\d+\.\s', stripped):
                if not in_ol:
                    if in_ul:
                        result.append('</ul>')
                        in_ul = False
                    result.append('<ol>')
                    in_ol = True
                content = re.sub(r'^\d+\.\s', '', stripped)
                result.append(f'<li>{content}</li>')
            else:
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append(line)

        # Close any open lists
        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')

        return '\n'.join(result)
