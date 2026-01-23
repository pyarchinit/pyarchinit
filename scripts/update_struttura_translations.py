#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiungere le traduzioni della scheda Struttura ai file .ts
"""

import re
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent.parent
I18N_DIR = PLUGIN_DIR / "i18n"

# Traduzioni per la scheda Struttura (sorgente in italiano)
STRUTTURA_TRANSLATIONS = {
    "Data compilazione": {
        "en_US": "Compilation date",
        "de_DE": "Erstellungsdatum",
        "fr_FR": "Date de compilation",
        "es_ES": "Fecha de compilación",
        "ar_LB": "تاريخ الإعداد",
        "ca_ES": "Data de compilació",
        "it_IT": "Data compilazione"
    },
    "Nome compilatore": {
        "en_US": "Compiler name",
        "de_DE": "Name des Bearbeiters",
        "fr_FR": "Nom du compilateur",
        "es_ES": "Nombre del compilador",
        "ar_LB": "اسم المُعدّ",
        "ca_ES": "Nom del compilador",
        "it_IT": "Nome compilatore"
    },
    "dd/MM/yyyy": {
        "en_US": "MM/dd/yyyy",
        "de_DE": "dd.MM.yyyy",
        "fr_FR": "dd/MM/yyyy",
        "es_ES": "dd/MM/yyyy",
        "ar_LB": "yyyy/MM/dd",
        "ca_ES": "dd/MM/yyyy",
        "it_IT": "dd/MM/yyyy"
    },
    "Ubicazione": {
        "en_US": "Location",
        "de_DE": "Standort",
        "fr_FR": "Emplacement",
        "es_ES": "Ubicación",
        "ar_LB": "الموقع",
        "ca_ES": "Ubicació",
        "it_IT": "Ubicazione"
    },
    "Elementi architettonici": {
        "en_US": "Architectural elements",
        "de_DE": "Architektonische Elemente",
        "fr_FR": "Éléments architecturaux",
        "es_ES": "Elementos arquitectónicos",
        "ar_LB": "العناصر المعمارية",
        "ca_ES": "Elements arquitectònics",
        "it_IT": "Elementi architettonici"
    },
    "Stato conservazione": {
        "en_US": "Conservation state",
        "de_DE": "Erhaltungszustand",
        "fr_FR": "État de conservation",
        "es_ES": "Estado de conservación",
        "ar_LB": "حالة الحفظ",
        "ca_ES": "Estat de conservació",
        "it_IT": "Stato conservazione"
    },
    "Stato": {
        "en_US": "State",
        "de_DE": "Zustand",
        "fr_FR": "État",
        "es_ES": "Estado",
        "ar_LB": "الحالة",
        "ca_ES": "Estat",
        "it_IT": "Stato"
    },
    "Grado": {
        "en_US": "Degree",
        "de_DE": "Grad",
        "fr_FR": "Degré",
        "es_ES": "Grado",
        "ar_LB": "الدرجة",
        "ca_ES": "Grau",
        "it_IT": "Grado"
    },
    "Fattori agenti": {
        "en_US": "Acting factors",
        "de_DE": "Einwirkende Faktoren",
        "fr_FR": "Facteurs d'action",
        "es_ES": "Factores de acción",
        "ar_LB": "العوامل المؤثرة",
        "ca_ES": "Factors d'acció",
        "it_IT": "Fattori agenti"
    },
    "Dati architettura": {
        "en_US": "Architecture data",
        "de_DE": "Architekturdaten",
        "fr_FR": "Données d'architecture",
        "es_ES": "Datos de arquitectura",
        "ar_LB": "بيانات العمارة",
        "ca_ES": "Dades d'arquitectura",
        "it_IT": "Dati architettura"
    },
    "N. ambienti": {
        "en_US": "No. of rooms",
        "de_DE": "Anzahl Räume",
        "fr_FR": "Nb. de pièces",
        "es_ES": "N.º de ambientes",
        "ar_LB": "عدد الغرف",
        "ca_ES": "Núm. d'ambients",
        "it_IT": "N. ambienti"
    },
    "Sviluppo planimetrico": {
        "en_US": "Planimetric development",
        "de_DE": "Planimetrische Entwicklung",
        "fr_FR": "Développement planimétrique",
        "es_ES": "Desarrollo planimétrico",
        "ar_LB": "التطور المسطح",
        "ca_ES": "Desenvolupament planimètric",
        "it_IT": "Sviluppo planimetrico"
    },
    "Elementi costitutivi": {
        "en_US": "Constitutive elements",
        "de_DE": "Bestandteile",
        "fr_FR": "Éléments constitutifs",
        "es_ES": "Elementos constitutivos",
        "ar_LB": "العناصر المكونة",
        "ca_ES": "Elements constitutius",
        "it_IT": "Elementi costitutivi"
    },
    "Prospetto ingresso": {
        "en_US": "Entrance elevation",
        "de_DE": "Eingangsansicht",
        "fr_FR": "Élévation de l'entrée",
        "es_ES": "Alzado de entrada",
        "ar_LB": "واجهة المدخل",
        "ca_ES": "Alçat d'entrada",
        "it_IT": "Prospetto ingresso"
    },
    "Orientamento ambienti": {
        "en_US": "Rooms orientation",
        "de_DE": "Raumorientierung",
        "fr_FR": "Orientation des pièces",
        "es_ES": "Orientación de ambientes",
        "ar_LB": "توجيه الغرف",
        "ca_ES": "Orientació dels ambients",
        "it_IT": "Orientamento ambienti"
    },
    "Relazione topografica": {
        "en_US": "Topographic relation",
        "de_DE": "Topographische Beziehung",
        "fr_FR": "Relation topographique",
        "es_ES": "Relación topográfica",
        "ar_LB": "العلاقة الطوبوغرافية",
        "ca_ES": "Relació topogràfica",
        "it_IT": "Relazione topografica"
    },
    "Prospetto": {
        "en_US": "Elevation",
        "de_DE": "Ansicht",
        "fr_FR": "Élévation",
        "es_ES": "Alzado",
        "ar_LB": "الواجهة",
        "ca_ES": "Alçat",
        "it_IT": "Prospetto"
    },
    "Elemento": {
        "en_US": "Element",
        "de_DE": "Element",
        "fr_FR": "Élément",
        "es_ES": "Elemento",
        "ar_LB": "العنصر",
        "ca_ES": "Element",
        "it_IT": "Elemento"
    },
    "Articolazione": {
        "en_US": "Articulation",
        "de_DE": "Gliederung",
        "fr_FR": "Articulation",
        "es_ES": "Articulación",
        "ar_LB": "التفصيل",
        "ca_ES": "Articulació",
        "it_IT": "Articolazione"
    },
    "Orientamento ingresso": {
        "en_US": "Entrance orientation",
        "de_DE": "Eingangsorientierung",
        "fr_FR": "Orientation de l'entrée",
        "es_ES": "Orientación de entrada",
        "ar_LB": "اتجاه المدخل",
        "ca_ES": "Orientació de l'entrada",
        "it_IT": "Orientamento ingresso"
    },
    "Motivo decorativo": {
        "en_US": "Decorative motif",
        "de_DE": "Dekoratives Motiv",
        "fr_FR": "Motif décoratif",
        "es_ES": "Motivo decorativo",
        "ar_LB": "الزخرفة",
        "ca_ES": "Motiu decoratiu",
        "it_IT": "Motivo decorativo"
    },
    "Dati archeologici": {
        "en_US": "Archaeological data",
        "de_DE": "Archäologische Daten",
        "fr_FR": "Données archéologiques",
        "es_ES": "Datos arqueológicos",
        "ar_LB": "البيانات الأثرية",
        "ca_ES": "Dades arqueològiques",
        "it_IT": "Dati archeologici"
    },
    "Potenzialita' archeologica": {
        "en_US": "Archaeological potential",
        "de_DE": "Archäologisches Potenzial",
        "fr_FR": "Potentiel archéologique",
        "es_ES": "Potencial arqueológico",
        "ar_LB": "الإمكانات الأثرية",
        "ca_ES": "Potencial arqueològic",
        "it_IT": "Potenzialità archeologica"
    },
    "Fasi funzionali": {
        "en_US": "Functional phases",
        "de_DE": "Funktionsphasen",
        "fr_FR": "Phases fonctionnelles",
        "es_ES": "Fases funcionales",
        "ar_LB": "المراحل الوظيفية",
        "ca_ES": "Fases funcionals",
        "it_IT": "Fasi funzionali"
    },
    "Manufatto": {
        "en_US": "Artifact",
        "de_DE": "Artefakt",
        "fr_FR": "Artefact",
        "es_ES": "Artefacto",
        "ar_LB": "القطعة الأثرية",
        "ca_ES": "Artefacte",
        "it_IT": "Manufatto"
    },
    "Definizione e fasi funzionali": {
        "en_US": "Definition and functional phases",
        "de_DE": "Definition und Funktionsphasen",
        "fr_FR": "Définition et phases fonctionnelles",
        "es_ES": "Definición y fases funcionales",
        "ar_LB": "التعريف والمراحل الوظيفية",
        "ca_ES": "Definició i fases funcionals",
        "it_IT": "Definizione e fasi funzionali"
    },
    "Manufatti": {
        "en_US": "Artifacts",
        "de_DE": "Artefakte",
        "fr_FR": "Artefacts",
        "es_ES": "Artefactos",
        "ar_LB": "القطع الأثرية",
        "ca_ES": "Artefactes",
        "it_IT": "Manufatti"
    },
}

TARGET_LANGUAGES = ["en_US", "de_DE", "fr_FR", "es_ES", "ar_LB", "ca_ES", "it_IT"]


def escape_xml(text):
    """Escape special XML characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def update_ts_file(lang_code):
    """Update a single .ts file with Struttura translations."""
    ts_file = I18N_DIR / f"pyarchinit_plugin_{lang_code}.ts"

    if not ts_file.exists():
        print(f"File non trovato: {ts_file}")
        return 0

    print(f"\nAggiornamento {ts_file.name}...")

    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_count = 0

    for source_text, translations in STRUTTURA_TRANSLATIONS.items():
        if lang_code not in translations:
            continue

        translation = translations[lang_code]
        escaped_source = re.escape(source_text)

        # Pattern to find unfinished translations for this source
        pattern = (
            r'(<source>' + escaped_source + r'</source>\s*'
            r'<translation type="unfinished")>(</translation>)'
        )

        replacement = r'\1>' + escape_xml(translation) + r'\2'

        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated_count += count

    # Write updated content
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Aggiornate {updated_count} traduzioni")
    return updated_count


def main():
    print("=" * 60)
    print("Aggiornamento traduzioni scheda Struttura")
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
