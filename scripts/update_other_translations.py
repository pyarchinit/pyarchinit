#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiungere le traduzioni delle schede Sam, Pottery, Tma ai file .ts
"""

import os
import re
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent.parent
I18N_DIR = PLUGIN_DIR / "i18n"

# Traduzioni per SamSegmentationDialog (sorgente in inglese)
SAM_TRANSLATIONS = {
    "Select the orthophoto or image to segment": {
        "it_IT": "Seleziona l'ortofoto o l'immagine da segmentare",
        "de_DE": "Wählen Sie das Orthofoto oder Bild zur Segmentierung",
        "fr_FR": "Sélectionner l'orthophoto ou l'image à segmenter",
        "es_ES": "Seleccionar la ortofoto o imagen a segmentar",
        "ar_LB": "اختر الصورة الجوية أو الصورة للتجزئة",
        "ca_ES": "Selecciona l'ortofoto o imatge a segmentar"
    },
    "Select the target layer for polygons": {
        "it_IT": "Seleziona il layer di destinazione per i poligoni",
        "de_DE": "Ziel-Layer für Polygone auswählen",
        "fr_FR": "Sélectionner la couche cible pour les polygones",
        "es_ES": "Seleccionar la capa de destino para polígonos",
        "ar_LB": "اختر الطبقة المستهدفة للمضلعات",
        "ca_ES": "Selecciona la capa de destí per als polígons"
    },
    "Site from configuration (read-only)": {
        "it_IT": "Sito dalla configurazione (sola lettura)",
        "de_DE": "Fundstelle aus der Konfiguration (schreibgeschützt)",
        "fr_FR": "Site depuis la configuration (lecture seule)",
        "es_ES": "Sitio desde la configuración (solo lectura)",
        "ar_LB": "الموقع من التكوين (للقراءة فقط)",
        "ca_ES": "Jaciment des de la configuració (només lectura)"
    },
    "Area number": {
        "it_IT": "Numero area",
        "de_DE": "Bereichsnummer",
        "fr_FR": "Numéro de zone",
        "es_ES": "Número de área",
        "ar_LB": "رقم المنطقة",
        "ca_ES": "Número d'àrea"
    },
    "1 = stones/objects, 2 = soil/area": {
        "it_IT": "1 = pietre/oggetti, 2 = suolo/area",
        "de_DE": "1 = Steine/Objekte, 2 = Boden/Fläche",
        "fr_FR": "1 = pierres/objets, 2 = sol/zone",
        "es_ES": "1 = piedras/objetos, 2 = suelo/área",
        "ar_LB": "1 = حجارة/كائنات، 2 = تربة/منطقة",
        "ca_ES": "1 = pedres/objectes, 2 = sòl/àrea"
    },
    "Type of stratigraphic unit": {
        "it_IT": "Tipo di unità stratigrafica",
        "de_DE": "Typ der stratigraphischen Einheit",
        "fr_FR": "Type d'unité stratigraphique",
        "es_ES": "Tipo de unidad estratigráfica",
        "ar_LB": "نوع الوحدة الطبقية",
        "ca_ES": "Tipus d'unitat estratigràfica"
    },
    "Automatically segment all detected objects in the visible area": {
        "it_IT": "Segmenta automaticamente tutti gli oggetti rilevati nell'area visibile",
        "de_DE": "Alle erkannten Objekte im sichtbaren Bereich automatisch segmentieren",
        "fr_FR": "Segmenter automatiquement tous les objets détectés dans la zone visible",
        "es_ES": "Segmentar automáticamente todos los objetos detectados en el área visible",
        "ar_LB": "تجزئة تلقائية لجميع الكائنات المكتشفة في المنطقة المرئية",
        "ca_ES": "Segmentar automàticament tots els objectes detectats a l'àrea visible"
    },
    "Click on individual stones to segment them. Right-click or press Enter when done.": {
        "it_IT": "Clicca sulle singole pietre per segmentarle. Tasto destro o Invio per terminare.",
        "de_DE": "Klicken Sie auf einzelne Steine, um sie zu segmentieren. Rechtsklick oder Enter zum Beenden.",
        "fr_FR": "Cliquez sur les pierres individuelles pour les segmenter. Clic droit ou Entrée pour terminer.",
        "es_ES": "Haz clic en las piedras individuales para segmentarlas. Clic derecho o Enter para terminar.",
        "ar_LB": "انقر على الحجارة الفردية لتجزئتها. انقر بزر الماوس الأيمن أو اضغط Enter عند الانتهاء.",
        "ca_ES": "Fes clic a les pedres individuals per segmentar-les. Clic dret o Enter per acabar."
    },
    "Draw a rectangle to segment all stones within that area": {
        "it_IT": "Disegna un rettangolo per segmentare tutte le pietre nell'area",
        "de_DE": "Zeichnen Sie ein Rechteck, um alle Steine in diesem Bereich zu segmentieren",
        "fr_FR": "Dessinez un rectangle pour segmenter toutes les pierres dans cette zone",
        "es_ES": "Dibuja un rectángulo para segmentar todas las piedras en esa área",
        "ar_LB": "ارسم مستطيلاً لتجزئة جميع الحجارة في تلك المنطقة",
        "ca_ES": "Dibuixa un rectangle per segmentar totes les pedres en aquella àrea"
    },
    "Draw a polygon to define the area to segment. Click vertices, right-click to finish.": {
        "it_IT": "Disegna un poligono per definire l'area da segmentare. Clicca i vertici, tasto destro per finire.",
        "de_DE": "Zeichnen Sie ein Polygon, um den zu segmentierenden Bereich zu definieren. Klicken Sie auf Eckpunkte, Rechtsklick zum Beenden.",
        "fr_FR": "Dessinez un polygone pour définir la zone à segmenter. Cliquez sur les sommets, clic droit pour terminer.",
        "es_ES": "Dibuja un polígono para definir el área a segmentar. Haz clic en los vértices, clic derecho para terminar.",
        "ar_LB": "ارسم مضلعاً لتحديد المنطقة المراد تجزئتها. انقر على الرؤوس، انقر بزر الماوس الأيمن للإنهاء.",
        "ca_ES": "Dibuixa un polígon per definir l'àrea a segmentar. Fes clic als vèrtexs, clic dret per acabar."
    },
    "Select a polygon feature from an existing layer as the area to segment": {
        "it_IT": "Seleziona un elemento poligonale da un layer esistente come area da segmentare",
        "de_DE": "Wählen Sie ein Polygon-Feature aus einem vorhandenen Layer als zu segmentierenden Bereich",
        "fr_FR": "Sélectionnez un élément polygonal d'une couche existante comme zone à segmenter",
        "es_ES": "Selecciona un elemento poligonal de una capa existente como área a segmentar",
        "ar_LB": "اختر عنصر مضلع من طبقة موجودة كمنطقة للتجزئة",
        "ca_ES": "Selecciona un element poligonal d'una capa existent com a àrea a segmentar"
    },
    "Get your API key from replicate.com or roboflow.com": {
        "it_IT": "Ottieni la tua chiave API da replicate.com o roboflow.com",
        "de_DE": "Holen Sie Ihren API-Schlüssel von replicate.com oder roboflow.com",
        "fr_FR": "Obtenez votre clé API sur replicate.com ou roboflow.com",
        "es_ES": "Obtén tu clave API de replicate.com o roboflow.com",
        "ar_LB": "احصل على مفتاح API الخاص بك من replicate.com أو roboflow.com",
        "ca_ES": "Obtén la teva clau API de replicate.com o roboflow.com"
    },
    "Describe what objects to segment (SAM-3 only)": {
        "it_IT": "Descrivi quali oggetti segmentare (solo SAM-3)",
        "de_DE": "Beschreiben Sie, welche Objekte segmentiert werden sollen (nur SAM-3)",
        "fr_FR": "Décrivez quels objets segmenter (SAM-3 uniquement)",
        "es_ES": "Describe qué objetos segmentar (solo SAM-3)",
        "ar_LB": "صف الكائنات المراد تجزئتها (SAM-3 فقط)",
        "ca_ES": "Descriu quins objectes segmentar (només SAM-3)"
    },
    "Run segmentation on the selected raster": {
        "it_IT": "Esegui la segmentazione sul raster selezionato",
        "de_DE": "Segmentierung auf dem ausgewählten Raster ausführen",
        "fr_FR": "Exécuter la segmentation sur le raster sélectionné",
        "es_ES": "Ejecutar la segmentación en el ráster seleccionado",
        "ar_LB": "تشغيل التجزئة على النقطية المحددة",
        "ca_ES": "Executa la segmentació en el ràster seleccionat"
    },
}

# Traduzioni per PotteryToolsDialog (sorgente in inglese)
POTTERY_TRANSLATIONS = {
    "Larger = better quality but slower": {
        "it_IT": "Maggiore = migliore qualità ma più lento",
        "de_DE": "Größer = bessere Qualität aber langsamer",
        "fr_FR": "Plus grand = meilleure qualité mais plus lent",
        "es_ES": "Mayor = mejor calidad pero más lento",
        "ar_LB": "أكبر = جودة أفضل ولكن أبطأ",
        "ca_ES": "Més gran = millor qualitat però més lent"
    },
    "Overlap between patches to reduce seams": {
        "it_IT": "Sovrapposizione tra le sezioni per ridurre le giunture",
        "de_DE": "Überlappung zwischen Abschnitten zur Reduzierung von Nähten",
        "fr_FR": "Chevauchement entre les sections pour réduire les coutures",
        "es_ES": "Superposición entre parches para reducir costuras",
        "ar_LB": "تداخل بين الرقع لتقليل اللحامات",
        "ca_ES": "Superposició entre seccions per reduir les costures"
    },
    "Control dot pattern density": {
        "it_IT": "Controlla la densità del pattern a punti",
        "de_DE": "Punktmusterdichte steuern",
        "fr_FR": "Contrôler la densité du motif de points",
        "es_ES": "Controlar la densidad del patrón de puntos",
        "ar_LB": "التحكم في كثافة نمط النقاط",
        "ca_ES": "Controla la densitat del patró de punts"
    },
    "Apply automatic brightness/contrast adjustment": {
        "it_IT": "Applica regolazione automatica luminosità/contrasto",
        "de_DE": "Automatische Helligkeits-/Kontrastanpassung anwenden",
        "fr_FR": "Appliquer l'ajustement automatique de luminosité/contraste",
        "es_ES": "Aplicar ajuste automático de brillo/contraste",
        "ar_LB": "تطبيق ضبط السطوع/التباين التلقائي",
        "ca_ES": "Aplica l'ajust automàtic de brillantor/contrast"
    },
    "Manual contrast adjustment (1.0 = no change)": {
        "it_IT": "Regolazione manuale del contrasto (1.0 = nessun cambiamento)",
        "de_DE": "Manuelle Kontrastanpassung (1.0 = keine Änderung)",
        "fr_FR": "Ajustement manuel du contraste (1.0 = pas de changement)",
        "es_ES": "Ajuste manual del contraste (1.0 = sin cambio)",
        "ar_LB": "ضبط التباين اليدوي (1.0 = بدون تغيير)",
        "ca_ES": "Ajust manual del contrast (1.0 = sense canvi)"
    },
    "Manual brightness adjustment (1.0 = no change)": {
        "it_IT": "Regolazione manuale della luminosità (1.0 = nessun cambiamento)",
        "de_DE": "Manuelle Helligkeitsanpassung (1.0 = keine Änderung)",
        "fr_FR": "Ajustement manuel de la luminosité (1.0 = pas de changement)",
        "es_ES": "Ajuste manual del brillo (1.0 = sin cambio)",
        "ar_LB": "ضبط السطوع اليدوي (1.0 = بدون تغيير)",
        "ca_ES": "Ajust manual de la brillantor (1.0 = sense canvi)"
    },
    "Reset to default values": {
        "it_IT": "Ripristina i valori predefiniti",
        "de_DE": "Auf Standardwerte zurücksetzen",
        "fr_FR": "Réinitialiser aux valeurs par défaut",
        "es_ES": "Restablecer valores predeterminados",
        "ar_LB": "إعادة التعيين إلى القيم الافتراضية",
        "ca_ES": "Restableix els valors predeterminats"
    },
    "Background treatment for output image": {
        "it_IT": "Trattamento sfondo per immagine di output",
        "de_DE": "Hintergrundbehandlung für Ausgabebild",
        "fr_FR": "Traitement du fond pour l'image de sortie",
        "es_ES": "Tratamiento del fondo para imagen de salida",
        "ar_LB": "معالجة الخلفية لصورة الإخراج",
        "ca_ES": "Tractament del fons per a la imatge de sortida"
    },
    "Brightness threshold for background detection (higher = stricter)": {
        "it_IT": "Soglia di luminosità per rilevamento sfondo (più alta = più rigida)",
        "de_DE": "Helligkeitsschwelle für Hintergrunderkennung (höher = strenger)",
        "fr_FR": "Seuil de luminosité pour la détection du fond (plus élevé = plus strict)",
        "es_ES": "Umbral de brillo para detección de fondo (mayor = más estricto)",
        "ar_LB": "عتبة السطوع لاكتشاف الخلفية (أعلى = أكثر صرامة)",
        "ca_ES": "Llindar de brillantor per a la detecció del fons (més alt = més estricte)"
    },
}

# Traduzioni per pyarchinit_Tma (sorgente in italiano)
TMA_TRANSLATIONS = {
    "Apri ricerca avanzata per US e cassette": {
        "en_US": "Open advanced search for SU and boxes",
        "de_DE": "Erweiterte Suche für SE und Kisten öffnen",
        "fr_FR": "Ouvrir la recherche avancée pour US et caisses",
        "es_ES": "Abrir búsqueda avanzada para UE y cajas",
        "ar_LB": "فتح البحث المتقدم للوحدات الطبقية والصناديق",
        "ca_ES": "Obrir cerca avançada per a UE i caixes",
        "it_IT": "Apri ricerca avanzata per US e cassette"
    },
    "Passa alla vista tabella": {
        "en_US": "Switch to table view",
        "de_DE": "Zur Tabellenansicht wechseln",
        "fr_FR": "Passer à la vue tableau",
        "es_ES": "Cambiar a vista de tabla",
        "ar_LB": "التبديل إلى عرض الجدول",
        "ca_ES": "Canviar a vista de taula",
        "it_IT": "Passa alla vista tabella"
    },
}

# Combina tutte le traduzioni
ALL_TRANSLATIONS = {}
ALL_TRANSLATIONS.update(SAM_TRANSLATIONS)
ALL_TRANSLATIONS.update(POTTERY_TRANSLATIONS)
ALL_TRANSLATIONS.update(TMA_TRANSLATIONS)

# Lingue target
TARGET_LANGUAGES = ["en_US", "de_DE", "fr_FR", "es_ES", "ar_LB", "ca_ES", "it_IT"]


def escape_xml(text):
    """Escape special XML characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def update_ts_file(lang_code):
    """Update a single .ts file with translations."""
    ts_file = I18N_DIR / f"pyarchinit_plugin_{lang_code}.ts"

    if not ts_file.exists():
        print(f"File non trovato: {ts_file}")
        return 0

    print(f"\nAggiornamento {ts_file.name}...")

    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_count = 0

    for source_text, translations in ALL_TRANSLATIONS.items():
        if lang_code not in translations:
            continue

        translation = translations[lang_code]

        # Pattern to find unfinished translations for this source
        pattern = (
            r'(<source>' + re.escape(source_text) + r'</source>\s*'
            r'<translation type="unfinished")>[^<]*(</translation>)'
        )

        replacement = r'\1>' + escape_xml(translation) + r'\2'

        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated_count += count

        # Also handle empty translations without type="unfinished"
        pattern2 = (
            r'(<source>' + re.escape(source_text) + r'</source>\s*'
            r'<translation)>(</translation>)'
        )
        replacement2 = r'\1>' + escape_xml(translation) + r'\2'

        new_content, count2 = re.subn(pattern2, replacement2, content)
        if count2 > 0:
            content = new_content
            updated_count += count2

    # Write updated content
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Aggiornate {updated_count} traduzioni")
    return updated_count


def main():
    print("=" * 60)
    print("Aggiornamento traduzioni Sam, Pottery, Tma")
    print("=" * 60)

    total_updated = 0

    for lang in TARGET_LANGUAGES:
        count = update_ts_file(lang)
        total_updated += count

    print("\n" + "=" * 60)
    print(f"Totale traduzioni aggiornate: {total_updated}")
    print("=" * 60)


if __name__ == "__main__":
    main()
