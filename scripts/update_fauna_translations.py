#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiungere le traduzioni della scheda Fauna ai file .ts
"""

import os
import re
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent.parent
I18N_DIR = PLUGIN_DIR / "i18n"

# Dizionario delle traduzioni per la scheda Fauna
# Chiave: stringa sorgente (italiano)
# Valore: dizionario con traduzioni per ogni lingua

FAUNA_TRANSLATIONS = {
    # === TAB NAMES ===
    "Dati Identificativi": {
        "en_US": "Identification Data",
        "de_DE": "Identifikationsdaten",
        "fr_FR": "Données d'identification",
        "es_ES": "Datos de Identificación",
        "ar_LB": "بيانات التعريف",
        "ca_ES": "Dades d'Identificació",
        "it_IT": "Dati Identificativi"
    },
    "Dati Archeozoologici": {
        "en_US": "Archaeozoological Data",
        "de_DE": "Archäozoologische Daten",
        "fr_FR": "Données archéozoologiques",
        "es_ES": "Datos Arqueozoológicos",
        "ar_LB": "البيانات الأثرية الحيوانية",
        "ca_ES": "Dades Arqueozoològiques",
        "it_IT": "Dati Archeozoologici"
    },
    "Dati Tafonomici": {
        "en_US": "Taphonomic Data",
        "de_DE": "Taphonomische Daten",
        "fr_FR": "Données taphonomiques",
        "es_ES": "Datos Tafonómicos",
        "ar_LB": "البيانات التافونومية",
        "ca_ES": "Dades Tafonòmiques",
        "it_IT": "Dati Tafonomici"
    },
    "Dati Contestuali": {
        "en_US": "Contextual Data",
        "de_DE": "Kontextdaten",
        "fr_FR": "Données contextuelles",
        "es_ES": "Datos Contextuales",
        "ar_LB": "البيانات السياقية",
        "ca_ES": "Dades Contextuals",
        "it_IT": "Dati Contestuali"
    },
    "Statistiche": {
        "en_US": "Statistics",
        "de_DE": "Statistiken",
        "fr_FR": "Statistiques",
        "es_ES": "Estadísticas",
        "ar_LB": "إحصائيات",
        "ca_ES": "Estadístiques",
        "it_IT": "Statistiche"
    },

    # === TOOLBAR ===
    "First record": {
        "en_US": "First record",
        "de_DE": "Erster Datensatz",
        "fr_FR": "Premier enregistrement",
        "es_ES": "Primer registro",
        "ar_LB": "السجل الأول",
        "ca_ES": "Primer registre",
        "it_IT": "Primo record"
    },
    "Previous record": {
        "en_US": "Previous record",
        "de_DE": "Vorheriger Datensatz",
        "fr_FR": "Enregistrement précédent",
        "es_ES": "Registro anterior",
        "ar_LB": "السجل السابق",
        "ca_ES": "Registre anterior",
        "it_IT": "Record precedente"
    },
    "Next record": {
        "en_US": "Next record",
        "de_DE": "Nächster Datensatz",
        "fr_FR": "Enregistrement suivant",
        "es_ES": "Siguiente registro",
        "ar_LB": "السجل التالي",
        "ca_ES": "Registre següent",
        "it_IT": "Record successivo"
    },
    "Last record": {
        "en_US": "Last record",
        "de_DE": "Letzter Datensatz",
        "fr_FR": "Dernier enregistrement",
        "es_ES": "Último registro",
        "ar_LB": "السجل الأخير",
        "ca_ES": "Últim registre",
        "it_IT": "Ultimo record"
    },
    "New record": {
        "en_US": "New record",
        "de_DE": "Neuer Datensatz",
        "fr_FR": "Nouvel enregistrement",
        "es_ES": "Nuevo registro",
        "ar_LB": "سجل جديد",
        "ca_ES": "Nou registre",
        "it_IT": "Nuovo record"
    },
    "Save": {
        "en_US": "Save",
        "de_DE": "Speichern",
        "fr_FR": "Enregistrer",
        "es_ES": "Guardar",
        "ar_LB": "حفظ",
        "ca_ES": "Desar",
        "it_IT": "Salva"
    },
    "Delete record": {
        "en_US": "Delete record",
        "de_DE": "Datensatz löschen",
        "fr_FR": "Supprimer l'enregistrement",
        "es_ES": "Eliminar registro",
        "ar_LB": "حذف السجل",
        "ca_ES": "Eliminar registre",
        "it_IT": "Elimina record"
    },
    "View all records": {
        "en_US": "View all records",
        "de_DE": "Alle Datensätze anzeigen",
        "fr_FR": "Voir tous les enregistrements",
        "es_ES": "Ver todos los registros",
        "ar_LB": "عرض جميع السجلات",
        "ca_ES": "Veure tots els registres",
        "it_IT": "Visualizza tutti i record"
    },
    "New search": {
        "en_US": "New search",
        "de_DE": "Neue Suche",
        "fr_FR": "Nouvelle recherche",
        "es_ES": "Nueva búsqueda",
        "ar_LB": "بحث جديد",
        "ca_ES": "Nova cerca",
        "it_IT": "Nuova ricerca"
    },
    "Execute search": {
        "en_US": "Execute search",
        "de_DE": "Suche ausführen",
        "fr_FR": "Exécuter la recherche",
        "es_ES": "Ejecutar búsqueda",
        "ar_LB": "تنفيذ البحث",
        "ca_ES": "Executar cerca",
        "it_IT": "Esegui ricerca"
    },
    "Export PDF sheets": {
        "en_US": "Export PDF sheets",
        "de_DE": "PDF-Blätter exportieren",
        "fr_FR": "Exporter les fiches PDF",
        "es_ES": "Exportar fichas PDF",
        "ar_LB": "تصدير صفحات PDF",
        "ca_ES": "Exportar fitxes PDF",
        "it_IT": "Esporta schede PDF"
    },

    # === TAB IDENTIFICATIVI ===
    "Dati Identificativi (da US)": {
        "en_US": "Identification Data (from SU)",
        "de_DE": "Identifikationsdaten (von SE)",
        "fr_FR": "Données d'identification (de l'US)",
        "es_ES": "Datos de Identificación (de UE)",
        "ar_LB": "بيانات التعريف (من الوحدة الطبقية)",
        "ca_ES": "Dades d'Identificació (de la UE)",
        "it_IT": "Dati Identificativi (da US)"
    },
    "Seleziona US": {
        "en_US": "Select SU",
        "de_DE": "SE auswählen",
        "fr_FR": "Sélectionner US",
        "es_ES": "Seleccionar UE",
        "ar_LB": "اختر الوحدة الطبقية",
        "ca_ES": "Seleccionar UE",
        "it_IT": "Seleziona US"
    },
    "Sito": {
        "en_US": "Site",
        "de_DE": "Fundstelle",
        "fr_FR": "Site",
        "es_ES": "Sitio",
        "ar_LB": "الموقع",
        "ca_ES": "Jaciment",
        "it_IT": "Sito"
    },
    "Area": {
        "en_US": "Area",
        "de_DE": "Bereich",
        "fr_FR": "Zone",
        "es_ES": "Área",
        "ar_LB": "المنطقة",
        "ca_ES": "Àrea",
        "it_IT": "Area"
    },
    "Saggio": {
        "en_US": "Excavation test",
        "de_DE": "Sondage",
        "fr_FR": "Sondage",
        "es_ES": "Sondeo",
        "ar_LB": "حفرية تجريبية",
        "ca_ES": "Sondeig",
        "it_IT": "Saggio"
    },
    "Datazione US": {
        "en_US": "SU Dating",
        "de_DE": "SE Datierung",
        "fr_FR": "Datation US",
        "es_ES": "Datación UE",
        "ar_LB": "تأريخ الوحدة الطبقية",
        "ca_ES": "Datació UE",
        "it_IT": "Datazione US"
    },
    "Dati Deposizionali": {
        "en_US": "Depositional Data",
        "de_DE": "Ablagerungsdaten",
        "fr_FR": "Données de dépôt",
        "es_ES": "Datos Deposicionales",
        "ar_LB": "بيانات الترسيب",
        "ca_ES": "Dades Deposicionals",
        "it_IT": "Dati Deposizionali"
    },
    "Responsabile": {
        "en_US": "Responsible",
        "de_DE": "Verantwortlich",
        "fr_FR": "Responsable",
        "es_ES": "Responsable",
        "ar_LB": "المسؤول",
        "ca_ES": "Responsable",
        "it_IT": "Responsabile"
    },
    "Data Compilazione": {
        "en_US": "Compilation Date",
        "de_DE": "Erstellungsdatum",
        "fr_FR": "Date de compilation",
        "es_ES": "Fecha de Compilación",
        "ar_LB": "تاريخ الإعداد",
        "ca_ES": "Data de Compilació",
        "it_IT": "Data Compilazione"
    },
    "Doc. Fotografica": {
        "en_US": "Photo Documentation",
        "de_DE": "Fotodokumentation",
        "fr_FR": "Doc. Photographique",
        "es_ES": "Doc. Fotográfica",
        "ar_LB": "التوثيق الفوتوغرافي",
        "ca_ES": "Doc. Fotogràfica",
        "it_IT": "Doc. Fotografica"
    },
    "Metodologia Recupero": {
        "en_US": "Recovery Methodology",
        "de_DE": "Bergungsmethode",
        "fr_FR": "Méthodologie de récupération",
        "es_ES": "Metodología de Recuperación",
        "ar_LB": "منهجية الاسترداد",
        "ca_ES": "Metodologia de Recuperació",
        "it_IT": "Metodologia Recupero"
    },
    "Contesto": {
        "en_US": "Context",
        "de_DE": "Kontext",
        "fr_FR": "Contexte",
        "es_ES": "Contexto",
        "ar_LB": "السياق",
        "ca_ES": "Context",
        "it_IT": "Contesto"
    },
    "Descrizione Contesto": {
        "en_US": "Context Description",
        "de_DE": "Kontextbeschreibung",
        "fr_FR": "Description du contexte",
        "es_ES": "Descripción del Contexto",
        "ar_LB": "وصف السياق",
        "ca_ES": "Descripció del Context",
        "it_IT": "Descrizione Contesto"
    },

    # === TAB ARCHEOZOOLOGICI ===
    "Connessione Anatomica": {
        "en_US": "Anatomical Connection",
        "de_DE": "Anatomische Verbindung",
        "fr_FR": "Connexion anatomique",
        "es_ES": "Conexión Anatómica",
        "ar_LB": "الاتصال التشريحي",
        "ca_ES": "Connexió Anatòmica",
        "it_IT": "Connessione Anatomica"
    },
    "Tipologia Accumulo": {
        "en_US": "Accumulation Type",
        "de_DE": "Akkumulationstyp",
        "fr_FR": "Type d'accumulation",
        "es_ES": "Tipo de Acumulación",
        "ar_LB": "نوع التراكم",
        "ca_ES": "Tipus d'Acumulació",
        "it_IT": "Tipologia Accumulo"
    },
    "Deposizione": {
        "en_US": "Deposition",
        "de_DE": "Ablagerung",
        "fr_FR": "Dépôt",
        "es_ES": "Deposición",
        "ar_LB": "الترسيب",
        "ca_ES": "Deposició",
        "it_IT": "Deposizione"
    },
    "Numero Stimato Resti": {
        "en_US": "Estimated Number of Remains",
        "de_DE": "Geschätzte Anzahl der Überreste",
        "fr_FR": "Nombre estimé de restes",
        "es_ES": "Número Estimado de Restos",
        "ar_LB": "العدد التقديري للبقايا",
        "ca_ES": "Nombre Estimat de Restes",
        "it_IT": "Numero Stimato Resti"
    },
    "Specie e Parti Scheletriche (PSI)": {
        "en_US": "Species and Skeletal Parts (SPI)",
        "de_DE": "Arten und Skelettelemente (SKI)",
        "fr_FR": "Espèces et parties squelettiques (IPS)",
        "es_ES": "Especies y Partes Esqueléticas (IPE)",
        "ar_LB": "الأنواع والأجزاء الهيكلية",
        "ca_ES": "Espècies i Parts Esquelètiques (IPE)",
        "it_IT": "Specie e Parti Scheletriche (PSI)"
    },
    "Aggiungi Riga": {
        "en_US": "Add Row",
        "de_DE": "Zeile hinzufügen",
        "fr_FR": "Ajouter une ligne",
        "es_ES": "Añadir Fila",
        "ar_LB": "إضافة صف",
        "ca_ES": "Afegir Fila",
        "it_IT": "Aggiungi Riga"
    },
    "Rimuovi Riga": {
        "en_US": "Remove Row",
        "de_DE": "Zeile entfernen",
        "fr_FR": "Supprimer la ligne",
        "es_ES": "Eliminar Fila",
        "ar_LB": "إزالة صف",
        "ca_ES": "Eliminar Fila",
        "it_IT": "Rimuovi Riga"
    },
    "Specie": {
        "en_US": "Species",
        "de_DE": "Art",
        "fr_FR": "Espèce",
        "es_ES": "Especie",
        "ar_LB": "النوع",
        "ca_ES": "Espècie",
        "it_IT": "Specie"
    },
    "PSI (Parti Scheletriche)": {
        "en_US": "SPI (Skeletal Parts)",
        "de_DE": "SKI (Skelettelemente)",
        "fr_FR": "IPS (Parties squelettiques)",
        "es_ES": "IPE (Partes Esqueléticas)",
        "ar_LB": "الأجزاء الهيكلية",
        "ca_ES": "IPE (Parts Esquelètiques)",
        "it_IT": "PSI (Parti Scheletriche)"
    },
    "Misure Ossa": {
        "en_US": "Bone Measurements",
        "de_DE": "Knochenmaße",
        "fr_FR": "Mesures osseuses",
        "es_ES": "Medidas de Huesos",
        "ar_LB": "قياسات العظام",
        "ca_ES": "Mesures d'Ossos",
        "it_IT": "Misure Ossa"
    },
    "Elemento Anatomico": {
        "en_US": "Anatomical Element",
        "de_DE": "Anatomisches Element",
        "fr_FR": "Élément anatomique",
        "es_ES": "Elemento Anatómico",
        "ar_LB": "العنصر التشريحي",
        "ca_ES": "Element Anatòmic",
        "it_IT": "Elemento Anatomico"
    },

    # === TAB TAFONOMICI ===
    "Stato Frammentazione": {
        "en_US": "Fragmentation State",
        "de_DE": "Fragmentierungszustand",
        "fr_FR": "État de fragmentation",
        "es_ES": "Estado de Fragmentación",
        "ar_LB": "حالة التجزئة",
        "ca_ES": "Estat de Fragmentació",
        "it_IT": "Stato Frammentazione"
    },
    "Tracce Combustione": {
        "en_US": "Combustion Traces",
        "de_DE": "Verbrennungsspuren",
        "fr_FR": "Traces de combustion",
        "es_ES": "Trazas de Combustión",
        "ar_LB": "آثار الاحتراق",
        "ca_ES": "Traces de Combustió",
        "it_IT": "Tracce Combustione"
    },
    "Combustione Altri Materiali US": {
        "en_US": "Combustion Other SU Materials",
        "de_DE": "Verbrennung anderer SE-Materialien",
        "fr_FR": "Combustion autres matériaux US",
        "es_ES": "Combustión Otros Materiales UE",
        "ar_LB": "احتراق مواد أخرى في الوحدة الطبقية",
        "ca_ES": "Combustió Altres Materials UE",
        "it_IT": "Combustione Altri Materiali US"
    },
    "Tipo Combustione": {
        "en_US": "Combustion Type",
        "de_DE": "Verbrennungstyp",
        "fr_FR": "Type de combustion",
        "es_ES": "Tipo de Combustión",
        "ar_LB": "نوع الاحتراق",
        "ca_ES": "Tipus de Combustió",
        "it_IT": "Tipo Combustione"
    },
    "Segni Tafonomici": {
        "en_US": "Taphonomic Signs",
        "de_DE": "Taphonomische Zeichen",
        "fr_FR": "Signes taphonomiques",
        "es_ES": "Signos Tafonómicos",
        "ar_LB": "علامات تافونومية",
        "ca_ES": "Signes Tafonòmics",
        "it_IT": "Segni Tafonomici"
    },
    "Caratterizzazione": {
        "en_US": "Characterization",
        "de_DE": "Charakterisierung",
        "fr_FR": "Caractérisation",
        "es_ES": "Caracterización",
        "ar_LB": "التوصيف",
        "ca_ES": "Caracterització",
        "it_IT": "Caratterizzazione"
    },
    "Stato Conservazione": {
        "en_US": "Conservation State",
        "de_DE": "Erhaltungszustand",
        "fr_FR": "État de conservation",
        "es_ES": "Estado de Conservación",
        "ar_LB": "حالة الحفظ",
        "ca_ES": "Estat de Conservació",
        "it_IT": "Stato Conservazione"
    },
    "Alterazioni Morfologiche": {
        "en_US": "Morphological Alterations",
        "de_DE": "Morphologische Veränderungen",
        "fr_FR": "Altérations morphologiques",
        "es_ES": "Alteraciones Morfológicas",
        "ar_LB": "التغيرات المورفولوجية",
        "ca_ES": "Alteracions Morfològiques",
        "it_IT": "Alterazioni Morfologiche"
    },

    # === TAB CONTESTUALI ===
    "Note Terreno Giacitura": {
        "en_US": "Terrain and Position Notes",
        "de_DE": "Gelände- und Lagehinweise",
        "fr_FR": "Notes terrain et position",
        "es_ES": "Notas Terreno y Posición",
        "ar_LB": "ملاحظات التضاريس والموقع",
        "ca_ES": "Notes Terreny i Posició",
        "it_IT": "Note Terreno Giacitura"
    },
    "Campionature Effettuate": {
        "en_US": "Samples Taken",
        "de_DE": "Durchgeführte Probennahmen",
        "fr_FR": "Échantillonnages effectués",
        "es_ES": "Muestreos Realizados",
        "ar_LB": "العينات المأخوذة",
        "ca_ES": "Mostrejos Realitzats",
        "it_IT": "Campionature Effettuate"
    },
    "Affidabilità Stratigrafica": {
        "en_US": "Stratigraphic Reliability",
        "de_DE": "Stratigraphische Zuverlässigkeit",
        "fr_FR": "Fiabilité stratigraphique",
        "es_ES": "Fiabilidad Estratigráfica",
        "ar_LB": "الموثوقية الطبقية",
        "ca_ES": "Fiabilitat Estratigràfica",
        "it_IT": "Affidabilità Stratigrafica"
    },
    "Classi Reperti Associazione": {
        "en_US": "Associated Finds Classes",
        "de_DE": "Zugehörige Fundklassen",
        "fr_FR": "Classes de mobilier associé",
        "es_ES": "Clases de Hallazgos Asociados",
        "ar_LB": "فئات اللقى المرتبطة",
        "ca_ES": "Classes de Troballes Associades",
        "it_IT": "Classi Reperti Associazione"
    },
    "Osservazioni": {
        "en_US": "Observations",
        "de_DE": "Beobachtungen",
        "fr_FR": "Observations",
        "es_ES": "Observaciones",
        "ar_LB": "ملاحظات",
        "ca_ES": "Observacions",
        "it_IT": "Osservazioni"
    },
    "Interpretazione": {
        "en_US": "Interpretation",
        "de_DE": "Interpretation",
        "fr_FR": "Interprétation",
        "es_ES": "Interpretación",
        "ar_LB": "التفسير",
        "ca_ES": "Interpretació",
        "it_IT": "Interpretazione"
    },
}

# Lingue target (escludendo italiano che è la sorgente)
TARGET_LANGUAGES = ["en_US", "de_DE", "fr_FR", "es_ES", "ar_LB", "ca_ES", "it_IT"]


def escape_xml(text):
    """Escape special XML characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def update_ts_file(lang_code):
    """Update a single .ts file with Fauna translations."""
    ts_file = I18N_DIR / f"pyarchinit_plugin_{lang_code}.ts"

    if not ts_file.exists():
        print(f"File non trovato: {ts_file}")
        return 0

    print(f"\nAggiornamento {ts_file.name}...")

    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_count = 0

    for source_text, translations in FAUNA_TRANSLATIONS.items():
        if lang_code not in translations:
            continue

        translation = translations[lang_code]

        # Pattern to find unfinished translations for this source
        # Match: <source>SOURCE_TEXT</source>\n        <translation type="unfinished">ANYTHING</translation>
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
    print("Aggiornamento traduzioni scheda Fauna")
    print("=" * 60)

    total_updated = 0

    for lang in TARGET_LANGUAGES:
        count = update_ts_file(lang)
        total_updated += count

    print("\n" + "=" * 60)
    print(f"Totale traduzioni aggiornate: {total_updated}")
    print("=" * 60)

    print("\nOra esegui 'lrelease' per compilare i file .qm:")
    print("  cd i18n && lrelease *.ts")


if __name__ == "__main__":
    main()
