# -*- coding: utf-8 -*-
"""Texts of the «Check relationships» window, in the ten languages of
pyArchInit (it, en, de, es, fr, ar, ca, ro, pt, el).

The window was written in Italian only: buttons, confirmations and the
continuity preview (27 Nov 2026). The issue titles and summaries stay in
:mod:`modules.utility.rapporti_check`.
"""

LANGS = ("it", "en", "de", "es", "fr", "ar", "ca", "ro", "pt", "el")

_T = {
    "site": {
        "it": "Sito:", "en": "Site:", "de": "Fundort:", "es": "Sitio:", "fr": "Site :",
        "ar": "الموقع:", "ca": "Jaciment:", "ro": "Sit:", "pt": "Sítio:", "el": "Θέση:"},
    "run": {
        "it": "Esegui verifica", "en": "Run check", "de": "Prüfung starten", "es": "Ejecutar verificación",
        "fr": "Lancer la vérification", "ar": "تشغيل الفحص", "ca": "Executa la verificació",
        "ro": "Rulează verificarea", "pt": "Executar verificação", "el": "Εκτέλεση ελέγχου"},
    "continuity": {
        "it": "Genera continuità", "en": "Generate continuity", "de": "Kontinuität erzeugen",
        "es": "Generar continuidad", "fr": "Générer la continuité", "ar": "توليد الاستمرارية",
        "ca": "Genera continuïtat", "ro": "Generează continuitatea", "pt": "Gerar continuidade",
        "el": "Δημιουργία συνέχειας"},
    "continuity_tip": {
        "it": "Crea/aggiorna le schede CON per le US/USM che attraversano più periodi (periodo iniziale ≠ finale).",
        "en": "Create/update the CON records for SU/WSU spanning several periods (initial period ≠ final).",
        "de": "Erstellt/aktualisiert die CON-Datensätze für SE/MSE, die mehrere Perioden umfassen (Anfangsperiode ≠ Endperiode).",
        "es": "Crea/actualiza las fichas CON de las UE/UEM que abarcan varios períodos (período inicial ≠ final).",
        "fr": "Crée/met à jour les fiches CON des US/USM qui traversent plusieurs périodes (période initiale ≠ finale).",
        "ar": "إنشاء/تحديث سجلات CON للوحدات الطبقية التي تمتد عبر عدة فترات (الفترة الأولى ≠ الأخيرة).",
        "ca": "Crea/actualitza les fitxes CON de les UE/UEM que travessen diversos períodes (període inicial ≠ final).",
        "ro": "Creează/actualizează fișele CON pentru US/USM care traversează mai multe perioade (perioada inițială ≠ finală).",
        "pt": "Cria/atualiza as fichas CON das UE/UEM que atravessam vários períodos (período inicial ≠ final).",
        "el": "Δημιουργεί/ενημερώνει τα δελτία CON για ΣΜ/ΤΣΜ που διασχίζουν περισσότερες περιόδους (αρχική περίοδος ≠ τελική)."},
    "phases": {
        "it": "anche i salti di fase", "en": "phase changes too", "de": "auch Phasenwechsel",
        "es": "también los saltos de fase", "fr": "aussi les sauts de phase", "ar": "وتغيّرات الطور أيضًا",
        "ca": "també els salts de fase", "ro": "și salturile de fază", "pt": "também os saltos de fase",
        "el": "και οι αλλαγές φάσης"},
    "phases_tip": {
        "it": "Spenta, la continuità nasce solo quando il periodo iniziale è diverso dal finale.\nAccesa, conta anche il salto di fase dentro lo stesso periodo (2/3 → 2/4): servono entrambe le fasi.\nUn'unità che non si muove — stesso periodo e stessa fase — non è mai una continuità.",
        "en": "Off: continuity only when the initial period differs from the final one.\nOn: a phase change within the same period counts too (2/3 → 2/4): both phases are needed.\nA unit that does not move — same period and same phase — is never a continuity.",
        "de": "Aus: Kontinuität nur, wenn die Anfangsperiode von der Endperiode abweicht.\nAn: auch ein Phasenwechsel innerhalb derselben Periode zählt (2/3 → 2/4): beide Phasen sind nötig.\nEine Einheit, die sich nicht bewegt — gleiche Periode, gleiche Phase — ist nie eine Kontinuität.",
        "es": "Desactivada: la continuidad nace solo cuando el período inicial es distinto del final.\nActivada: cuenta también el salto de fase dentro del mismo período (2/3 → 2/4): hacen falta ambas fases.\nUna unidad que no se mueve —mismo período y misma fase— nunca es una continuidad.",
        "fr": "Désactivée : la continuité n'apparaît que si la période initiale diffère de la finale.\nActivée : le saut de phase dans la même période compte aussi (2/3 → 2/4) : il faut les deux phases.\nUne unité qui ne bouge pas — même période et même phase — n'est jamais une continuité.",
        "ar": "مُعطّل: تنشأ الاستمرارية فقط عندما تختلف الفترة الأولى عن الأخيرة.\nمُفعّل: يُحتسب أيضًا تغيّر الطور داخل الفترة نفسها (2/3 ← 2/4): يلزم الطوران كلاهما.\nالوحدة التي لا تتغيّر — الفترة نفسها والطور نفسه — ليست استمرارية أبدًا.",
        "ca": "Desactivada: la continuïtat només neix quan el període inicial és diferent del final.\nActivada: també compta el salt de fase dins del mateix període (2/3 → 2/4): calen totes dues fases.\nUna unitat que no es mou —mateix període i mateixa fase— no és mai una continuïtat.",
        "ro": "Dezactivată: continuitatea apare doar când perioada inițială diferă de cea finală.\nActivată: contează și saltul de fază în aceeași perioadă (2/3 → 2/4): sunt necesare ambele faze.\nO unitate care nu se mișcă — aceeași perioadă și aceeași fază — nu este niciodată o continuitate.",
        "pt": "Desligada: a continuidade só surge quando o período inicial é diferente do final.\nLigada: conta também o salto de fase dentro do mesmo período (2/3 → 2/4): são precisas ambas as fases.\nUma unidade que não se move — mesmo período e mesma fase — nunca é uma continuidade.",
        "el": "Ανενεργό: συνέχεια μόνο όταν η αρχική περίοδος διαφέρει από την τελική.\nΕνεργό: μετρά και η αλλαγή φάσης μέσα στην ίδια περίοδο (2/3 → 2/4): χρειάζονται και οι δύο φάσεις.\nΜια μονάδα που δεν μετακινείται — ίδια περίοδος και ίδια φάση — δεν είναι ποτέ συνέχεια."},
    "retry": {
        "it": "Riprova", "en": "Retry", "de": "Erneut versuchen", "es": "Reintentar", "fr": "Réessayer",
        "ar": "إعادة المحاولة", "ca": "Torna-ho a provar", "ro": "Reîncearcă", "pt": "Tentar novamente",
        "el": "Επανάληψη"},
    "problem": {
        "it": "Problema", "en": "Problem", "de": "Problem", "es": "Problema", "fr": "Problème",
        "ar": "المشكلة", "ca": "Problema", "ro": "Problemă", "pt": "Problema", "el": "Πρόβλημα"},
    "rollback": {
        "it": "Annulla ultimo fix", "en": "Undo last fix", "de": "Letzte Korrektur rückgängig",
        "es": "Deshacer última corrección", "fr": "Annuler la dernière correction", "ar": "التراجع عن آخر تصحيح",
        "ca": "Desfés l'última correcció", "ro": "Anulează ultima corecție", "pt": "Anular última correção",
        "el": "Αναίρεση τελευταίας διόρθωσης"},
    "apply": {
        "it": "Applica fix selezionati", "en": "Apply selected fixes", "de": "Ausgewählte Korrekturen anwenden",
        "es": "Aplicar correcciones seleccionadas", "fr": "Appliquer les corrections sélectionnées",
        "ar": "تطبيق التصحيحات المحددة", "ca": "Aplica les correccions seleccionades",
        "ro": "Aplică corecțiile selectate", "pt": "Aplicar correções selecionadas",
        "el": "Εφαρμογή επιλεγμένων διορθώσεων"},
    "summary": {
        "it": "{n} problemi · {a} correggibili automaticamente", "en": "{n} problems · {a} fixable automatically",
        "de": "{n} Probleme · {a} automatisch korrigierbar", "es": "{n} problemas · {a} corregibles automáticamente",
        "fr": "{n} problèmes · {a} corrigeables automatiquement", "ar": "{n} مشكلة · {a} قابلة للتصحيح تلقائيًا",
        "ca": "{n} problemes · {a} corregibles automàticament", "ro": "{n} probleme · {a} corectabile automat",
        "pt": "{n} problemas · {a} corrigíveis automaticamente", "el": "{n} προβλήματα · {a} διορθώνονται αυτόματα"},
    "selected": {
        "it": " (selezionati)", "en": " (selected)", "de": " (ausgewählt)", "es": " (seleccionados)",
        "fr": " (sélectionnés)", "ar": " (محددة)", "ca": " (seleccionats)", "ro": " (selectate)",
        "pt": " (selecionados)", "el": " (επιλεγμένα)"},
    "proposals": {
        "it": " · {p} proposte, da spuntare a mano", "en": " · {p} proposals, to tick by hand",
        "de": " · {p} Vorschläge, von Hand anzukreuzen", "es": " · {p} propuestas, para marcar a mano",
        "fr": " · {p} propositions, à cocher à la main", "ar": " · {p} مقترحات، تُحدَّد يدويًا",
        "ca": " · {p} propostes, per marcar a mà", "ro": " · {p} propuneri, de bifat manual",
        "pt": " · {p} propostas, a assinalar à mão", "el": " · {p} προτάσεις, για επιλογή με το χέρι"},
    "preview_hint": {
        "it": ". Anteprima un elemento per i dettagli.", "en": ". Select an item for the details.",
        "de": ". Element auswählen für Details.", "es": ". Selecciona un elemento para ver los detalles.",
        "fr": ". Sélectionnez un élément pour les détails.", "ar": ". اختر عنصرًا لعرض التفاصيل.",
        "ca": ". Selecciona un element per veure'n els detalls.", "ro": ". Selectează un element pentru detalii.",
        "pt": ". Selecione um elemento para ver os detalhes.", "el": ". Επιλέξτε ένα στοιχείο για λεπτομέρειες."},
    "chrono_failed": {
        "it": "  ⚠ verifica cronologia non eseguita: {e}", "en": "  ⚠ chronology check not run: {e}",
        "de": "  ⚠ Chronologieprüfung nicht ausgeführt: {e}", "es": "  ⚠ verificación de cronología no ejecutada: {e}",
        "fr": "  ⚠ vérification de la chronologie non effectuée : {e}", "ar": "  ⚠ لم يُنفَّذ فحص التسلسل الزمني: {e}",
        "ca": "  ⚠ verificació de la cronologia no executada: {e}", "ro": "  ⚠ verificarea cronologiei nu a rulat: {e}",
        "pt": "  ⚠ verificação da cronologia não executada: {e}", "el": "  ⚠ ο έλεγχος χρονολογίας δεν εκτελέστηκε: {e}"},
    "check_failed": {
        "it": "Verifica fallita: {e}", "en": "Check failed: {e}", "de": "Prüfung fehlgeschlagen: {e}",
        "es": "Verificación fallida: {e}", "fr": "Échec de la vérification : {e}", "ar": "فشل الفحص: {e}",
        "ca": "Ha fallat la verificació: {e}", "ro": "Verificarea a eșuat: {e}", "pt": "A verificação falhou: {e}",
        "el": "Ο έλεγχος απέτυχε: {e}"},
    "none_selected": {
        "it": "Nessuna correzione selezionata.", "en": "No fix selected.", "de": "Keine Korrektur ausgewählt.",
        "es": "Ninguna corrección seleccionada.", "fr": "Aucune correction sélectionnée.",
        "ar": "لم يُحدَّد أي تصحيح.", "ca": "Cap correcció seleccionada.", "ro": "Nicio corecție selectată.",
        "pt": "Nenhuma correção selecionada.", "el": "Δεν επιλέχθηκε καμία διόρθωση."},
    "confirm_title": {
        "it": "Conferma", "en": "Confirm", "de": "Bestätigen", "es": "Confirmar", "fr": "Confirmer",
        "ar": "تأكيد", "ca": "Confirma", "ro": "Confirmă", "pt": "Confirmar", "el": "Επιβεβαίωση"},
    "confirm_text": {
        "it": "Applicare {n} correzioni al sito '{sito}'?\n(potrai annullare con '{undo}')",
        "en": "Apply {n} fixes to site '{sito}'?\n(you can undo with '{undo}')",
        "de": "{n} Korrekturen auf den Fundort '{sito}' anwenden?\n(rückgängig mit '{undo}')",
        "es": "¿Aplicar {n} correcciones al sitio '{sito}'?\n(podrás deshacer con '{undo}')",
        "fr": "Appliquer {n} corrections au site « {sito} » ?\n(vous pourrez annuler avec « {undo} »)",
        "ar": "تطبيق {n} تصحيحات على الموقع '{sito}'؟\n(يمكنك التراجع عبر '{undo}')",
        "ca": "Vols aplicar {n} correccions al jaciment '{sito}'?\n(podràs desfer-ho amb '{undo}')",
        "ro": "Aplici {n} corecții sitului „{sito}”?\n(poți anula cu „{undo}”)",
        "pt": "Aplicar {n} correções ao sítio '{sito}'?\n(poderá anular com '{undo}')",
        "el": "Εφαρμογή {n} διορθώσεων στη θέση «{sito}»;\n(μπορείτε να αναιρέσετε με «{undo}»)"},
    "backup_title": {
        "it": "Backup non disponibile", "en": "Backup not available", "de": "Sicherung nicht verfügbar",
        "es": "Copia de seguridad no disponible", "fr": "Sauvegarde indisponible", "ar": "النسخ الاحتياطي غير متاح",
        "ca": "Còpia de seguretat no disponible", "ro": "Copie de siguranță indisponibilă",
        "pt": "Cópia de segurança indisponível", "el": "Αντίγραφο ασφαλείας μη διαθέσιμο"},
    "backup_text": {
        "it": "pg_dump non trovato: procedo senza backup?", "en": "pg_dump not found: go on without a backup?",
        "de": "pg_dump nicht gefunden: ohne Sicherung fortfahren?", "es": "pg_dump no encontrado: ¿continuar sin copia de seguridad?",
        "fr": "pg_dump introuvable : continuer sans sauvegarde ?", "ar": "لم يُعثر على pg_dump: المتابعة دون نسخة احتياطية؟",
        "ca": "No s'ha trobat pg_dump: continuo sense còpia de seguretat?", "ro": "pg_dump nu a fost găsit: continui fără copie de siguranță?",
        "pt": "pg_dump não encontrado: continuar sem cópia de segurança?", "el": "Δεν βρέθηκε το pg_dump: συνέχεια χωρίς αντίγραφο ασφαλείας;"},
    "apply_failed": {
        "it": "Applicazione fallita: {e}", "en": "Apply failed: {e}", "de": "Anwenden fehlgeschlagen: {e}",
        "es": "Error al aplicar: {e}", "fr": "Échec de l'application : {e}", "ar": "فشل التطبيق: {e}",
        "ca": "Ha fallat l'aplicació: {e}", "ro": "Aplicarea a eșuat: {e}", "pt": "A aplicação falhou: {e}",
        "el": "Η εφαρμογή απέτυχε: {e}"},
    "cont_failed": {
        "it": "Genera continuità fallita: {e}", "en": "Generate continuity failed: {e}",
        "de": "Kontinuität erzeugen fehlgeschlagen: {e}", "es": "Error al generar la continuidad: {e}",
        "fr": "Échec de la génération de la continuité : {e}", "ar": "فشل توليد الاستمرارية: {e}",
        "ca": "Ha fallat la generació de la continuïtat: {e}", "ro": "Generarea continuității a eșuat: {e}",
        "pt": "A geração da continuidade falhou: {e}", "el": "Η δημιουργία συνέχειας απέτυχε: {e}"},
    "cont_aligned": {
        "it": "({n} già allineate)", "en": "({n} already aligned)", "de": "({n} bereits abgeglichen)",
        "es": "({n} ya alineadas)", "fr": "({n} déjà alignées)", "ar": "({n} متوافقة مسبقًا)",
        "ca": "({n} ja alineades)", "ro": "({n} deja aliniate)", "pt": "({n} já alinhadas)",
        "el": "({n} ήδη ευθυγραμμισμένες)"},
    "cont_no_span": {
        "it": "Nessuna US/USM ha il periodo iniziale diverso dal finale.",
        "en": "No SU/WSU has an initial period different from the final one.",
        "de": "Keine SE/MSE hat eine Anfangsperiode, die von der Endperiode abweicht.",
        "es": "Ninguna UE/UEM tiene el período inicial distinto del final.",
        "fr": "Aucune US/USM n'a une période initiale différente de la finale.",
        "ar": "لا توجد وحدة طبقية فترتها الأولى مختلفة عن الأخيرة.",
        "ca": "Cap UE/UEM no té el període inicial diferent del final.",
        "ro": "Nicio US/USM nu are perioada inițială diferită de cea finală.",
        "pt": "Nenhuma UE/UEM tem o período inicial diferente do final.",
        "el": "Καμία ΣΜ/ΤΣΜ δεν έχει αρχική περίοδο διαφορετική από την τελική."},
    "cont_phase_hint": {
        "it": "\nSe le tue unità cambiano solo fase dentro lo stesso periodo, spunta «{phases}».",
        "en": "\nIf your units only change phase within the same period, tick «{phases}».",
        "de": "\nWenn deine Einheiten nur die Phase innerhalb derselben Periode wechseln, kreuze «{phases}» an.",
        "es": "\nSi tus unidades solo cambian de fase dentro del mismo período, marca «{phases}».",
        "fr": "\nSi vos unités ne changent que de phase dans la même période, cochez « {phases} ».",
        "ar": "\nإذا كانت وحداتك تغيّر الطور فقط داخل الفترة نفسها، فحدِّد «{phases}».",
        "ca": "\nSi les teves unitats només canvien de fase dins del mateix període, marca «{phases}».",
        "ro": "\nDacă unitățile tale își schimbă doar faza în aceeași perioadă, bifează „{phases}”.",
        "pt": "\nSe as suas unidades só mudam de fase dentro do mesmo período, assinale «{phases}».",
        "el": "\nΑν οι μονάδες σας αλλάζουν μόνο φάση μέσα στην ίδια περίοδο, επιλέξτε «{phases}»."},
    "cont_nothing": {
        "it": "Nessuna continuità da generare per '{sito}'.\n{coda}", "en": "No continuity to generate for '{sito}'.\n{coda}",
        "de": "Keine Kontinuität für '{sito}' zu erzeugen.\n{coda}", "es": "No hay continuidad que generar para '{sito}'.\n{coda}",
        "fr": "Aucune continuité à générer pour « {sito} ».\n{coda}", "ar": "لا توجد استمرارية لتوليدها لـ '{sito}'.\n{coda}",
        "ca": "No hi ha cap continuïtat per generar per a '{sito}'.\n{coda}", "ro": "Nicio continuitate de generat pentru „{sito}”.\n{coda}",
        "pt": "Nenhuma continuidade a gerar para '{sito}'.\n{coda}", "el": "Καμία συνέχεια προς δημιουργία για «{sito}».\n{coda}"},
    "cont_preview": {
        "it": "Anteprima continuità", "en": "Continuity preview", "de": "Vorschau der Kontinuität",
        "es": "Vista previa de la continuidad", "fr": "Aperçu de la continuité", "ar": "معاينة الاستمرارية",
        "ca": "Previsualització de la continuïtat", "ro": "Previzualizarea continuității",
        "pt": "Pré-visualização da continuidade", "el": "Προεπισκόπηση συνέχειας"},
    "to_create": {
        "it": "Da creare", "en": "To create", "de": "Zu erstellen", "es": "Por crear", "fr": "À créer",
        "ar": "للإنشاء", "ca": "Per crear", "ro": "De creat", "pt": "A criar", "el": "Προς δημιουργία"},
    "to_update": {
        "it": "Da aggiornare", "en": "To update", "de": "Zu aktualisieren", "es": "Por actualizar",
        "fr": "À mettre à jour", "ar": "للتحديث", "ca": "Per actualitzar", "ro": "De actualizat",
        "pt": "A atualizar", "el": "Προς ενημέρωση"},
    "unchanged": {
        "it": "Invariate", "en": "Unchanged", "de": "Unverändert", "es": "Sin cambios", "fr": "Inchangées",
        "ar": "دون تغيير", "ca": "Sense canvis", "ro": "Neschimbate", "pt": "Inalteradas", "el": "Αμετάβλητες"},
    "orphans": {
        "it": "Orfane", "en": "Orphans", "de": "Verwaist", "es": "Huérfanas", "fr": "Orphelines",
        "ar": "يتيمة", "ca": "Òrfenes", "ro": "Orfane", "pt": "Órfãs", "el": "Ορφανές"},
    "periods": {
        "it": "periodi", "en": "periods", "de": "Perioden", "es": "períodos", "fr": "périodes",
        "ar": "الفترات", "ca": "períodes", "ro": "perioade", "pt": "períodos", "el": "περίοδοι"},
    "orphan": {
        "it": "orfana", "en": "orphan", "de": "verwaist", "es": "huérfana", "fr": "orpheline",
        "ar": "يتيمة", "ca": "òrfena", "ro": "orfană", "pt": "órfã", "el": "ορφανή"},
    "remove_orphans": {
        "it": "Rimuovi anche le CON orfane", "en": "Also remove orphan CON records",
        "de": "Auch verwaiste CON-Datensätze entfernen", "es": "Eliminar también las CON huérfanas",
        "fr": "Supprimer aussi les CON orphelines", "ar": "إزالة سجلات CON اليتيمة أيضًا",
        "ca": "Elimina també les CON òrfenes", "ro": "Elimină și fișele CON orfane",
        "pt": "Remover também as CON órfãs", "el": "Αφαίρεση και των ορφανών CON"},
    "generate": {
        "it": "Genera", "en": "Generate", "de": "Erzeugen", "es": "Generar", "fr": "Générer",
        "ar": "توليد", "ca": "Genera", "ro": "Generează", "pt": "Gerar", "el": "Δημιουργία"},
    "gen_failed": {
        "it": "Generazione fallita: {e}", "en": "Generation failed: {e}", "de": "Erzeugung fehlgeschlagen: {e}",
        "es": "Error en la generación: {e}", "fr": "Échec de la génération : {e}", "ar": "فشل التوليد: {e}",
        "ca": "Ha fallat la generació: {e}", "ro": "Generarea a eșuat: {e}", "pt": "A geração falhou: {e}",
        "el": "Η δημιουργία απέτυχε: {e}"},
    "cont_done": {
        "it": "Continuità generata per '{sito}'.\nCreate: {c} · Aggiornate: {u} · Invariate: {i} · Orfane rimosse: {o}",
        "en": "Continuity generated for '{sito}'.\nCreated: {c} · Updated: {u} · Unchanged: {i} · Orphans removed: {o}",
        "de": "Kontinuität für '{sito}' erzeugt.\nErstellt: {c} · Aktualisiert: {u} · Unverändert: {i} · Verwaiste entfernt: {o}",
        "es": "Continuidad generada para '{sito}'.\nCreadas: {c} · Actualizadas: {u} · Sin cambios: {i} · Huérfanas eliminadas: {o}",
        "fr": "Continuité générée pour « {sito} ».\nCréées : {c} · Mises à jour : {u} · Inchangées : {i} · Orphelines supprimées : {o}",
        "ar": "تم توليد الاستمرارية لـ '{sito}'.\nأُنشئ: {c} · حُدّث: {u} · دون تغيير: {i} · أُزيلت اليتيمة: {o}",
        "ca": "Continuïtat generada per a '{sito}'.\nCreades: {c} · Actualitzades: {u} · Sense canvis: {i} · Òrfenes eliminades: {o}",
        "ro": "Continuitate generată pentru „{sito}”.\nCreate: {c} · Actualizate: {u} · Neschimbate: {i} · Orfane eliminate: {o}",
        "pt": "Continuidade gerada para '{sito}'.\nCriadas: {c} · Atualizadas: {u} · Inalteradas: {i} · Órfãs removidas: {o}",
        "el": "Η συνέχεια δημιουργήθηκε για «{sito}».\nΔημιουργήθηκαν: {c} · Ενημερώθηκαν: {u} · Αμετάβλητες: {i} · Ορφανές αφαιρέθηκαν: {o}"},
    "warnings": {
        "it": "Avvisi", "en": "Warnings", "de": "Hinweise", "es": "Avisos", "fr": "Avertissements",
        "ar": "تحذيرات", "ca": "Avisos", "ro": "Avertismente", "pt": "Avisos", "el": "Προειδοποιήσεις"},
    "rollback_failed": {
        "it": "Annullamento fallito: {e}", "en": "Undo failed: {e}", "de": "Rückgängig fehlgeschlagen: {e}",
        "es": "Error al deshacer: {e}", "fr": "Échec de l'annulation : {e}", "ar": "فشل التراجع: {e}",
        "ca": "Ha fallat el desfer: {e}", "ro": "Anularea a eșuat: {e}", "pt": "A anulação falhou: {e}",
        "el": "Η αναίρεση απέτυχε: {e}"},
    "rollback_done": {
        "it": "Ultimo fix annullato.", "en": "Last fix undone.", "de": "Letzte Korrektur rückgängig gemacht.",
        "es": "Última corrección deshecha.", "fr": "Dernière correction annulée.", "ar": "تم التراجع عن آخر تصحيح.",
        "ca": "S'ha desfet l'última correcció.", "ro": "Ultima corecție a fost anulată.",
        "pt": "Última correção anulada.", "el": "Η τελευταία διόρθωση αναιρέθηκε."},
    "window_title": {
        "it": "Verifica rapporti stratigrafici", "en": "Check stratigraphic relationships",
        "de": "Stratigraphische Beziehungen prüfen", "es": "Verificar relaciones estratigráficas",
        "fr": "Vérifier les rapports stratigraphiques", "ar": "فحص العلاقات الطبقية",
        "ca": "Verifica les relacions estratigràfiques", "ro": "Verifică relațiile stratigrafice",
        "pt": "Verificar relações estratigráficas", "el": "Έλεγχος στρωματογραφικών σχέσεων"},
}


def t(lang, key, **kw) -> str:
    """The text in *lang* (Italian when the language is unknown)."""
    voce = _T[key]
    testo = voce.get(str(lang or "it")[:2]) or voce["it"]
    return testo.format(**kw) if kw else testo
