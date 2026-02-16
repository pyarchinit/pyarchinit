#!/usr/bin/env python3
"""Add database sync translations to all language files."""

import os
import re

# Translations for Database Sync functionality
SYNC_TRANSLATIONS = {
    "Database Synchronization (Local ↔ Remote)": {
        "it_IT": "Sincronizzazione Database (Locale ↔ Remoto)",
        "en_US": "Database Synchronization (Local ↔ Remote)",
        "de_DE": "Datenbanksynchronisation (Lokal ↔ Remote)",
        "fr_FR": "Synchronisation de base de données (Local ↔ Distant)",
        "es_ES": "Sincronización de base de datos (Local ↔ Remoto)",
        "ca_ES": "Sincronització de base de dades (Local ↔ Remot)",
        "ar_LB": "مزامنة قاعدة البيانات (محلي ↔ بعيد)",
        "ro_RO": "Sincronizare Bază de Date (Local ↔ Distant)",
        "pt_PT": "Sincronização de Base de Dados (Local ↔ Remoto)",
        "el_GR": "Συγχρονισμός Βάσης Δεδομένων (Τοπική ↔ Απομακρυσμένη)",
    },
    "Local Database (PostgreSQL)": {
        "it_IT": "Database Locale (PostgreSQL)",
        "en_US": "Local Database (PostgreSQL)",
        "de_DE": "Lokale Datenbank (PostgreSQL)",
        "fr_FR": "Base de données locale (PostgreSQL)",
        "es_ES": "Base de datos local (PostgreSQL)",
        "ca_ES": "Base de dades local (PostgreSQL)",
        "ar_LB": "قاعدة بيانات محلية (PostgreSQL)",
        "ro_RO": "Bază de Date Locală (PostgreSQL)",
        "pt_PT": "Base de Dados Local (PostgreSQL)",
        "el_GR": "Τοπική Βάση Δεδομένων (PostgreSQL)",
    },
    "Remote Database (Server/Cloud)": {
        "it_IT": "Database Remoto (Server/Cloud)",
        "en_US": "Remote Database (Server/Cloud)",
        "de_DE": "Remote-Datenbank (Server/Cloud)",
        "fr_FR": "Base de données distante (Serveur/Cloud)",
        "es_ES": "Base de datos remota (Servidor/Nube)",
        "ca_ES": "Base de dades remota (Servidor/Núvol)",
        "ar_LB": "قاعدة بيانات بعيدة (خادم/سحابة)",
        "ro_RO": "Bază de Date Distantă (Server/Cloud)",
        "pt_PT": "Base de Dados Remota (Servidor/Cloud)",
        "el_GR": "Απομακρυσμένη Βάση Δεδομένων (Διακομιστής/Cloud)",
    },
    "Host:": {
        "it_IT": "Host:",
        "en_US": "Host:",
        "de_DE": "Host:",
        "fr_FR": "Hôte :",
        "es_ES": "Host:",
        "ca_ES": "Host:",
        "ar_LB": "المضيف:",
        "ro_RO": "Gazdă:",
        "pt_PT": "Anfitrião:",
        "el_GR": "Διακομιστής:",
    },
    "Port:": {
        "it_IT": "Porta:",
        "en_US": "Port:",
        "de_DE": "Port:",
        "fr_FR": "Port :",
        "es_ES": "Puerto:",
        "ca_ES": "Port:",
        "ar_LB": "المنفذ:",
        "ro_RO": "Port:",
        "pt_PT": "Porta:",
        "el_GR": "Θύρα:",
    },
    "Database:": {
        "it_IT": "Database:",
        "en_US": "Database:",
        "de_DE": "Datenbank:",
        "fr_FR": "Base de données :",
        "es_ES": "Base de datos:",
        "ca_ES": "Base de dades:",
        "ar_LB": "قاعدة البيانات:",
        "ro_RO": "Bază de date:",
        "pt_PT": "Base de dados:",
        "el_GR": "Βάση δεδομένων:",
    },
    "User:": {
        "it_IT": "Utente:",
        "en_US": "User:",
        "de_DE": "Benutzer:",
        "fr_FR": "Utilisateur :",
        "es_ES": "Usuario:",
        "ca_ES": "Usuari:",
        "ar_LB": "المستخدم:",
        "ro_RO": "Utilizator:",
        "pt_PT": "Utilizador:",
        "el_GR": "Χρήστης:",
    },
    "Password:": {
        "it_IT": "Password:",
        "en_US": "Password:",
        "de_DE": "Passwort:",
        "fr_FR": "Mot de passe :",
        "es_ES": "Contraseña:",
        "ca_ES": "Contrasenya:",
        "ar_LB": "كلمة المرور:",
        "ro_RO": "Parolă:",
        "pt_PT": "Palavra-passe:",
        "el_GR": "Κωδικός πρόσβασης:",
    },
    "Save Credentials": {
        "it_IT": "Salva Credenziali",
        "en_US": "Save Credentials",
        "de_DE": "Anmeldedaten speichern",
        "fr_FR": "Enregistrer les identifiants",
        "es_ES": "Guardar credenciales",
        "ca_ES": "Desar credencials",
        "ar_LB": "حفظ بيانات الاعتماد",
        "ro_RO": "Salvează Credențialele",
        "pt_PT": "Guardar Credenciais",
        "el_GR": "Αποθήκευση Διαπιστευτηρίων",
    },
    "Analyze Differences": {
        "it_IT": "Analizza Differenze",
        "en_US": "Analyze Differences",
        "de_DE": "Unterschiede analysieren",
        "fr_FR": "Analyser les différences",
        "es_ES": "Analizar diferencias",
        "ca_ES": "Analitzar diferències",
        "ar_LB": "تحليل الاختلافات",
        "ro_RO": "Analizează Diferențele",
        "pt_PT": "Analisar Diferenças",
        "el_GR": "Ανάλυση Διαφορών",
    },
    "Upload to Remote": {
        "it_IT": "Carica sul Remoto",
        "en_US": "Upload to Remote",
        "de_DE": "Auf Remote hochladen",
        "fr_FR": "Téléverser vers le distant",
        "es_ES": "Subir al remoto",
        "ca_ES": "Pujar al remot",
        "ar_LB": "رفع إلى البعيد",
        "ro_RO": "Încarcă pe Distant",
        "pt_PT": "Enviar para Remoto",
        "el_GR": "Μεταφόρτωση στον Απομακρυσμένο",
    },
    "Download from Remote": {
        "it_IT": "Scarica dal Remoto",
        "en_US": "Download from Remote",
        "de_DE": "Von Remote herunterladen",
        "fr_FR": "Télécharger depuis le distant",
        "es_ES": "Descargar del remoto",
        "ca_ES": "Descarregar del remot",
        "ar_LB": "تحميل من البعيد",
        "ro_RO": "Descarcă de pe Distant",
        "pt_PT": "Descarregar do Remoto",
        "el_GR": "Λήψη από Απομακρυσμένο",
    },
    "Analyzing differences...": {
        "it_IT": "Analisi delle differenze...",
        "en_US": "Analyzing differences...",
        "de_DE": "Unterschiede werden analysiert...",
        "fr_FR": "Analyse des différences...",
        "es_ES": "Analizando diferencias...",
        "ca_ES": "Analitzant diferències...",
        "ar_LB": "تحليل الاختلافات...",
        "ro_RO": "Analizarea diferențelor...",
        "pt_PT": "A analisar diferenças...",
        "el_GR": "Ανάλυση διαφορών...",
    },
    "Analysis complete": {
        "it_IT": "Analisi completata",
        "en_US": "Analysis complete",
        "de_DE": "Analyse abgeschlossen",
        "fr_FR": "Analyse terminée",
        "es_ES": "Análisis completado",
        "ca_ES": "Anàlisi completada",
        "ar_LB": "اكتمل التحليل",
        "ro_RO": "Analiză completă",
        "pt_PT": "Análise concluída",
        "el_GR": "Ολοκλήρωση ανάλυσης",
    },
    "Error": {
        "it_IT": "Errore",
        "en_US": "Error",
        "de_DE": "Fehler",
        "fr_FR": "Erreur",
        "es_ES": "Error",
        "ca_ES": "Error",
        "ar_LB": "خطأ",
        "ro_RO": "Eroare",
        "pt_PT": "Erro",
        "el_GR": "Σφάλμα",
    },
    "Remote host not configured.": {
        "it_IT": "Host remoto non configurato.",
        "en_US": "Remote host not configured.",
        "de_DE": "Remote-Host nicht konfiguriert.",
        "fr_FR": "Hôte distant non configuré.",
        "es_ES": "Host remoto no configurado.",
        "ca_ES": "Host remot no configurat.",
        "ar_LB": "لم يتم تكوين المضيف البعيد.",
        "ro_RO": "Gazda distantă nu este configurată.",
        "pt_PT": "Anfitrião remoto não configurado.",
        "el_GR": "Ο απομακρυσμένος διακομιστής δεν έχει ρυθμιστεί.",
    },
    "Local database not configured.": {
        "it_IT": "Database locale non configurato.",
        "en_US": "Local database not configured.",
        "de_DE": "Lokale Datenbank nicht konfiguriert.",
        "fr_FR": "Base de données locale non configurée.",
        "es_ES": "Base de datos local no configurada.",
        "ca_ES": "Base de dades local no configurada.",
        "ar_LB": "لم يتم تكوين قاعدة البيانات المحلية.",
        "ro_RO": "Baza de date locală nu este configurată.",
        "pt_PT": "Base de dados local não configurada.",
        "el_GR": "Η τοπική βάση δεδομένων δεν έχει ρυθμιστεί.",
    },
    "Database Synchronization - Differences Analysis": {
        "it_IT": "Sincronizzazione Database - Analisi Differenze",
        "en_US": "Database Synchronization - Differences Analysis",
        "de_DE": "Datenbanksynchronisation - Unterschiedsanalyse",
        "fr_FR": "Synchronisation de base de données - Analyse des différences",
        "es_ES": "Sincronización de base de datos - Análisis de diferencias",
        "ca_ES": "Sincronització de base de dades - Anàlisi de diferències",
        "ar_LB": "مزامنة قاعدة البيانات - تحليل الاختلافات",
        "ro_RO": "Sincronizare Bază de Date - Analiză Diferențe",
        "pt_PT": "Sincronização de Base de Dados - Análise de Diferenças",
        "el_GR": "Συγχρονισμός Βάσης Δεδομένων - Ανάλυση Διαφορών",
    },
    "Select": {
        "it_IT": "Seleziona",
        "en_US": "Select",
        "de_DE": "Auswählen",
        "fr_FR": "Sélectionner",
        "es_ES": "Seleccionar",
        "ca_ES": "Seleccionar",
        "ar_LB": "تحديد",
        "ro_RO": "Selectează",
        "pt_PT": "Selecionar",
        "el_GR": "Επιλογή",
    },
    "Table Name": {
        "it_IT": "Nome Tabella",
        "en_US": "Table Name",
        "de_DE": "Tabellenname",
        "fr_FR": "Nom de la table",
        "es_ES": "Nombre de tabla",
        "ca_ES": "Nom de la taula",
        "ar_LB": "اسم الجدول",
        "ro_RO": "Numele Tabelului",
        "pt_PT": "Nome da Tabela",
        "el_GR": "Όνομα Πίνακα",
    },
    "Local": {
        "it_IT": "Locale",
        "en_US": "Local",
        "de_DE": "Lokal",
        "fr_FR": "Local",
        "es_ES": "Local",
        "ca_ES": "Local",
        "ar_LB": "محلي",
        "ro_RO": "Local",
        "pt_PT": "Local",
        "el_GR": "Τοπικό",
    },
    "Remote": {
        "it_IT": "Remoto",
        "en_US": "Remote",
        "de_DE": "Remote",
        "fr_FR": "Distant",
        "es_ES": "Remoto",
        "ca_ES": "Remot",
        "ar_LB": "بعيد",
        "ro_RO": "Distant",
        "pt_PT": "Remoto",
        "el_GR": "Απομακρυσμένο",
    },
    "Only Local": {
        "it_IT": "Solo Locale",
        "en_US": "Only Local",
        "de_DE": "Nur Lokal",
        "fr_FR": "Uniquement local",
        "es_ES": "Solo local",
        "ca_ES": "Només local",
        "ar_LB": "محلي فقط",
        "ro_RO": "Doar Local",
        "pt_PT": "Apenas Local",
        "el_GR": "Μόνο Τοπικά",
    },
    "Only Remote": {
        "it_IT": "Solo Remoto",
        "en_US": "Only Remote",
        "de_DE": "Nur Remote",
        "fr_FR": "Uniquement distant",
        "es_ES": "Solo remoto",
        "ca_ES": "Només remot",
        "ar_LB": "بعيد فقط",
        "ro_RO": "Doar Distant",
        "pt_PT": "Apenas Remoto",
        "el_GR": "Μόνο Απομακρυσμένα",
    },
    "Modified": {
        "it_IT": "Modificati",
        "en_US": "Modified",
        "de_DE": "Geändert",
        "fr_FR": "Modifié",
        "es_ES": "Modificado",
        "ca_ES": "Modificat",
        "ar_LB": "معدل",
        "ro_RO": "Modificat",
        "pt_PT": "Modificado",
        "el_GR": "Τροποποιημένο",
    },
    "Status": {
        "it_IT": "Stato",
        "en_US": "Status",
        "de_DE": "Status",
        "fr_FR": "Statut",
        "es_ES": "Estado",
        "ca_ES": "Estat",
        "ar_LB": "الحالة",
        "ro_RO": "Stare",
        "pt_PT": "Estado",
        "el_GR": "Κατάσταση",
    },
    "Differences found": {
        "it_IT": "Differenze trovate",
        "en_US": "Differences found",
        "de_DE": "Unterschiede gefunden",
        "fr_FR": "Différences trouvées",
        "es_ES": "Diferencias encontradas",
        "ca_ES": "Diferències trobades",
        "ar_LB": "تم العثور على اختلافات",
        "ro_RO": "Diferențe găsite",
        "pt_PT": "Diferenças encontradas",
        "el_GR": "Βρέθηκαν διαφορές",
    },
    "Synchronized": {
        "it_IT": "Sincronizzato",
        "en_US": "Synchronized",
        "de_DE": "Synchronisiert",
        "fr_FR": "Synchronisé",
        "es_ES": "Sincronizado",
        "ca_ES": "Sincronitzat",
        "ar_LB": "متزامن",
        "ro_RO": "Sincronizat",
        "pt_PT": "Sincronizado",
        "el_GR": "Συγχρονισμένο",
    },
    "Select All": {
        "it_IT": "Seleziona Tutto",
        "en_US": "Select All",
        "de_DE": "Alles auswählen",
        "fr_FR": "Tout sélectionner",
        "es_ES": "Seleccionar todo",
        "ca_ES": "Seleccionar tot",
        "ar_LB": "تحديد الكل",
        "ro_RO": "Selectează Tot",
        "pt_PT": "Selecionar Tudo",
        "el_GR": "Επιλογή Όλων",
    },
    "Select None": {
        "it_IT": "Deseleziona Tutto",
        "en_US": "Select None",
        "de_DE": "Nichts auswählen",
        "fr_FR": "Ne rien sélectionner",
        "es_ES": "No seleccionar ninguno",
        "ca_ES": "No seleccionar cap",
        "ar_LB": "إلغاء تحديد الكل",
        "ro_RO": "Deselectează Tot",
        "pt_PT": "Não Selecionar Nenhum",
        "el_GR": "Αποεπιλογή Όλων",
    },
    "Select Only Different": {
        "it_IT": "Seleziona Solo Differenti",
        "en_US": "Select Only Different",
        "de_DE": "Nur Unterschiedliche auswählen",
        "fr_FR": "Sélectionner uniquement les différents",
        "es_ES": "Seleccionar solo diferentes",
        "ca_ES": "Seleccionar només els diferents",
        "ar_LB": "تحديد المختلفة فقط",
        "ro_RO": "Selectează Doar Diferitele",
        "pt_PT": "Selecionar Apenas Diferentes",
        "el_GR": "Επιλογή Μόνο Διαφορετικών",
    },
    "Close": {
        "it_IT": "Chiudi",
        "en_US": "Close",
        "de_DE": "Schließen",
        "fr_FR": "Fermer",
        "es_ES": "Cerrar",
        "ca_ES": "Tancar",
        "ar_LB": "إغلاق",
        "ro_RO": "Închide",
        "pt_PT": "Fechar",
        "el_GR": "Κλείσιμο",
    },
    "No Tables Selected": {
        "it_IT": "Nessuna Tabella Selezionata",
        "en_US": "No Tables Selected",
        "de_DE": "Keine Tabellen ausgewählt",
        "fr_FR": "Aucune table sélectionnée",
        "es_ES": "No se seleccionaron tablas",
        "ca_ES": "No s'han seleccionat taules",
        "ar_LB": "لم يتم تحديد جداول",
        "ro_RO": "Niciun Tabel Selectat",
        "pt_PT": "Nenhuma Tabela Selecionada",
        "el_GR": "Δεν Επιλέχθηκαν Πίνακες",
    },
    "Please select at least one table to synchronize.": {
        "it_IT": "Seleziona almeno una tabella da sincronizzare.",
        "en_US": "Please select at least one table to synchronize.",
        "de_DE": "Bitte wählen Sie mindestens eine Tabelle zum Synchronisieren aus.",
        "fr_FR": "Veuillez sélectionner au moins une table à synchroniser.",
        "es_ES": "Por favor seleccione al menos una tabla para sincronizar.",
        "ca_ES": "Si us plau, seleccioneu almenys una taula per sincronitzar.",
        "ar_LB": "يرجى تحديد جدول واحد على الأقل للمزامنة.",
        "ro_RO": "Vă rugăm selectați cel puțin un tabel pentru sincronizare.",
        "pt_PT": "Por favor selecione pelo menos uma tabela para sincronizar.",
        "el_GR": "Παρακαλώ επιλέξτε τουλάχιστον έναν πίνακα για συγχρονισμό.",
    },
    "Confirm Synchronization": {
        "it_IT": "Conferma Sincronizzazione",
        "en_US": "Confirm Synchronization",
        "de_DE": "Synchronisation bestätigen",
        "fr_FR": "Confirmer la synchronisation",
        "es_ES": "Confirmar sincronización",
        "ca_ES": "Confirmar sincronització",
        "ar_LB": "تأكيد المزامنة",
        "ro_RO": "Confirmă Sincronizarea",
        "pt_PT": "Confirmar Sincronização",
        "el_GR": "Επιβεβαίωση Συγχρονισμού",
    },
    "Confirm Download": {
        "it_IT": "Conferma Download",
        "en_US": "Confirm Download",
        "de_DE": "Download bestätigen",
        "fr_FR": "Confirmer le téléchargement",
        "es_ES": "Confirmar descarga",
        "ca_ES": "Confirmar descàrrega",
        "ar_LB": "تأكيد التحميل",
        "ro_RO": "Confirmă Descărcarea",
        "pt_PT": "Confirmar Descarga",
        "el_GR": "Επιβεβαίωση Λήψης",
    },
    "Confirm Upload": {
        "it_IT": "Conferma Upload",
        "en_US": "Confirm Upload",
        "de_DE": "Upload bestätigen",
        "fr_FR": "Confirmer le téléversement",
        "es_ES": "Confirmar subida",
        "ca_ES": "Confirmar pujada",
        "ar_LB": "تأكيد الرفع",
        "ro_RO": "Confirmă Încărcarea",
        "pt_PT": "Confirmar Envio",
        "el_GR": "Επιβεβαίωση Μεταφόρτωσης",
    },
    "Missing Configuration": {
        "it_IT": "Configurazione Mancante",
        "en_US": "Missing Configuration",
        "de_DE": "Fehlende Konfiguration",
        "fr_FR": "Configuration manquante",
        "es_ES": "Configuración faltante",
        "ca_ES": "Configuració que falta",
        "ar_LB": "تكوين مفقود",
        "ro_RO": "Configurație Lipsă",
        "pt_PT": "Configuração em Falta",
        "el_GR": "Ελλιπής Ρύθμιση",
    },
    # ========== CONNECTION PROFILES ==========
    "Connection Profiles": {
        "it_IT": "Profili di Connessione",
        "en_US": "Connection Profiles",
        "de_DE": "Verbindungsprofile",
        "fr_FR": "Profils de connexion",
        "es_ES": "Perfiles de conexión",
        "ca_ES": "Perfils de connexió",
        "ar_LB": "ملفات تعريف الاتصال",
        "ro_RO": "Profile de Conexiune",
        "pt_PT": "Perfis de Conexão",
        "el_GR": "Προφίλ Σύνδεσης",
    },
    "Saved Profiles:": {
        "it_IT": "Profili Salvati:",
        "en_US": "Saved Profiles:",
        "de_DE": "Gespeicherte Profile:",
        "fr_FR": "Profils enregistrés :",
        "es_ES": "Perfiles guardados:",
        "ca_ES": "Perfils desats:",
        "ar_LB": "الملفات المحفوظة:",
        "ro_RO": "Profile Salvate:",
        "pt_PT": "Perfis Guardados:",
        "el_GR": "Αποθηκευμένα Προφίλ:",
    },
    "-- Select a profile --": {
        "it_IT": "-- Seleziona un profilo --",
        "en_US": "-- Select a profile --",
        "de_DE": "-- Profil auswählen --",
        "fr_FR": "-- Sélectionner un profil --",
        "es_ES": "-- Seleccionar un perfil --",
        "ca_ES": "-- Selecciona un perfil --",
        "ar_LB": "-- اختر ملف تعريف --",
        "ro_RO": "-- Selectează un profil --",
        "pt_PT": "-- Selecionar um perfil --",
        "el_GR": "-- Επιλέξτε προφίλ --",
    },
    "\U0001f4be Save": {
        "it_IT": "\U0001f4be Salva",
        "en_US": "\U0001f4be Save",
        "de_DE": "\U0001f4be Speichern",
        "fr_FR": "\U0001f4be Enregistrer",
        "es_ES": "\U0001f4be Guardar",
        "ca_ES": "\U0001f4be Desar",
        "ar_LB": "\U0001f4be حفظ",
        "ro_RO": "\U0001f4be Salvează",
        "pt_PT": "\U0001f4be Guardar",
        "el_GR": "\U0001f4be Αποθήκευση",
    },
    "\U0001f5d1\ufe0f Delete": {
        "it_IT": "\U0001f5d1\ufe0f Elimina",
        "en_US": "\U0001f5d1\ufe0f Delete",
        "de_DE": "\U0001f5d1\ufe0f Löschen",
        "fr_FR": "\U0001f5d1\ufe0f Supprimer",
        "es_ES": "\U0001f5d1\ufe0f Eliminar",
        "ca_ES": "\U0001f5d1\ufe0f Eliminar",
        "ar_LB": "\U0001f5d1\ufe0f حذف",
        "ro_RO": "\U0001f5d1\ufe0f Șterge",
        "pt_PT": "\U0001f5d1\ufe0f Eliminar",
        "el_GR": "\U0001f5d1\ufe0f Διαγραφή",
    },
    "Save current settings as a new profile": {
        "it_IT": "Salva le impostazioni correnti come nuovo profilo",
        "en_US": "Save current settings as a new profile",
        "de_DE": "Aktuelle Einstellungen als neues Profil speichern",
        "fr_FR": "Enregistrer les paramètres actuels comme nouveau profil",
        "es_ES": "Guardar la configuración actual como nuevo perfil",
        "ca_ES": "Desar la configuració actual com a nou perfil",
        "ar_LB": "حفظ الإعدادات الحالية كملف تعريف جديد",
        "ro_RO": "Salvează setările curente ca profil nou",
        "pt_PT": "Guardar as definições atuais como novo perfil",
        "el_GR": "Αποθήκευση τρεχουσών ρυθμίσεων ως νέο προφίλ",
    },
    "Delete the selected profile": {
        "it_IT": "Elimina il profilo selezionato",
        "en_US": "Delete the selected profile",
        "de_DE": "Ausgewähltes Profil löschen",
        "fr_FR": "Supprimer le profil sélectionné",
        "es_ES": "Eliminar el perfil seleccionado",
        "ca_ES": "Eliminar el perfil seleccionat",
        "ar_LB": "حذف الملف الشخصي المحدد",
        "ro_RO": "Șterge profilul selectat",
        "pt_PT": "Eliminar o perfil selecionado",
        "el_GR": "Διαγραφή του επιλεγμένου προφίλ",
    },
    "Save Connection Profile": {
        "it_IT": "Salva Profilo Connessione",
        "en_US": "Save Connection Profile",
        "de_DE": "Verbindungsprofil speichern",
        "fr_FR": "Enregistrer le profil de connexion",
        "es_ES": "Guardar perfil de conexión",
        "ca_ES": "Desar perfil de connexió",
        "ar_LB": "حفظ ملف تعريف الاتصال",
        "ro_RO": "Salvează Profilul de Conexiune",
        "pt_PT": "Guardar Perfil de Conexão",
        "el_GR": "Αποθήκευση Προφίλ Σύνδεσης",
    },
    "Enter a name for this connection profile:": {
        "it_IT": "Inserisci un nome per questo profilo di connessione:",
        "en_US": "Enter a name for this connection profile:",
        "de_DE": "Geben Sie einen Namen für dieses Verbindungsprofil ein:",
        "fr_FR": "Entrez un nom pour ce profil de connexion :",
        "es_ES": "Introduzca un nombre para este perfil de conexión:",
        "ca_ES": "Introduïu un nom per a aquest perfil de connexió:",
        "ar_LB": "أدخل اسمًا لملف تعريف الاتصال هذا:",
        "ro_RO": "Introduceți un nume pentru acest profil de conexiune:",
        "pt_PT": "Introduza um nome para este perfil de conexão:",
        "el_GR": "Εισαγάγετε ένα όνομα για αυτό το προφίλ σύνδεσης:",
    },
    "Profile Exists": {
        "it_IT": "Profilo Esistente",
        "en_US": "Profile Exists",
        "de_DE": "Profil existiert",
        "fr_FR": "Le profil existe",
        "es_ES": "El perfil existe",
        "ca_ES": "El perfil existeix",
        "ar_LB": "الملف الشخصي موجود",
        "ro_RO": "Profilul Există",
        "pt_PT": "O Perfil Existe",
        "el_GR": "Το Προφίλ Υπάρχει",
    },
    "A profile named '{name}' already exists. Do you want to overwrite it?": {
        "it_IT": "Un profilo chiamato '{name}' esiste già. Vuoi sovrascriverlo?",
        "en_US": "A profile named '{name}' already exists. Do you want to overwrite it?",
        "de_DE": "Ein Profil mit dem Namen '{name}' existiert bereits. Möchten Sie es überschreiben?",
        "fr_FR": "Un profil nommé '{name}' existe déjà. Voulez-vous l'écraser ?",
        "es_ES": "Ya existe un perfil llamado '{name}'. ¿Desea sobrescribirlo?",
        "ca_ES": "Ja existeix un perfil anomenat '{name}'. Voleu sobreescriure'l?",
        "ar_LB": "يوجد بالفعل ملف تعريف باسم '{name}'. هل تريد استبداله؟",
        "ro_RO": "Un profil numit '{name}' există deja. Doriți să-l suprascrieți?",
        "pt_PT": "Já existe um perfil chamado '{name}'. Deseja substituí-lo?",
        "el_GR": "Ένα προφίλ με το όνομα '{name}' υπάρχει ήδη. Θέλετε να το αντικαταστήσετε;",
    },
    "Profile Saved": {
        "it_IT": "Profilo Salvato",
        "en_US": "Profile Saved",
        "de_DE": "Profil gespeichert",
        "fr_FR": "Profil enregistré",
        "es_ES": "Perfil guardado",
        "ca_ES": "Perfil desat",
        "ar_LB": "تم حفظ الملف الشخصي",
        "ro_RO": "Profil Salvat",
        "pt_PT": "Perfil Guardado",
        "el_GR": "Το Προφίλ Αποθηκεύτηκε",
    },
    "No Profile Selected": {
        "it_IT": "Nessun Profilo Selezionato",
        "en_US": "No Profile Selected",
        "de_DE": "Kein Profil ausgewählt",
        "fr_FR": "Aucun profil sélectionné",
        "es_ES": "No hay perfil seleccionado",
        "ca_ES": "No hi ha cap perfil seleccionat",
        "ar_LB": "لم يتم تحديد أي ملف تعريف",
        "ro_RO": "Niciun Profil Selectat",
        "pt_PT": "Nenhum Perfil Selecionado",
        "el_GR": "Δεν Επιλέχθηκε Προφίλ",
    },
    "Please select a profile to delete.": {
        "it_IT": "Seleziona un profilo da eliminare.",
        "en_US": "Please select a profile to delete.",
        "de_DE": "Bitte wählen Sie ein zu löschendes Profil aus.",
        "fr_FR": "Veuillez sélectionner un profil à supprimer.",
        "es_ES": "Por favor, seleccione un perfil para eliminar.",
        "ca_ES": "Si us plau, seleccioneu un perfil per eliminar.",
        "ar_LB": "يرجى تحديد ملف تعريف للحذف.",
        "ro_RO": "Vă rugăm selectați un profil de șters.",
        "pt_PT": "Por favor selecione um perfil para eliminar.",
        "el_GR": "Παρακαλώ επιλέξτε ένα προφίλ για διαγραφή.",
    },
    "Confirm Deletion": {
        "it_IT": "Conferma Eliminazione",
        "en_US": "Confirm Deletion",
        "de_DE": "Löschen bestätigen",
        "fr_FR": "Confirmer la suppression",
        "es_ES": "Confirmar eliminación",
        "ca_ES": "Confirmar eliminació",
        "ar_LB": "تأكيد الحذف",
        "ro_RO": "Confirmă Ștergerea",
        "pt_PT": "Confirmar Eliminação",
        "el_GR": "Επιβεβαίωση Διαγραφής",
    },
    "Profile Deleted": {
        "it_IT": "Profilo Eliminato",
        "en_US": "Profile Deleted",
        "de_DE": "Profil gelöscht",
        "fr_FR": "Profil supprimé",
        "es_ES": "Perfil eliminado",
        "ca_ES": "Perfil eliminat",
        "ar_LB": "تم حذف الملف الشخصي",
        "ro_RO": "Profil Șters",
        "pt_PT": "Perfil Eliminado",
        "el_GR": "Το Προφίλ Διαγράφηκε",
    },
    # DB Settings Profile translations
    "-- Select profile --": {
        "it_IT": "-- Seleziona profilo --",
        "en_US": "-- Select profile --",
        "de_DE": "-- Profil auswählen --",
        "fr_FR": "-- Sélectionner un profil --",
        "es_ES": "-- Seleccionar perfil --",
        "ca_ES": "-- Seleccionar perfil --",
        "ar_LB": "-- اختر ملف تعريف --",
        "ro_RO": "-- Selectează profil --",
        "pt_PT": "-- Selecionar perfil --",
        "el_GR": "-- Επιλέξτε προφίλ --",
    },
    "Connection Profiles:": {
        "it_IT": "Profili Connessione:",
        "en_US": "Connection Profiles:",
        "de_DE": "Verbindungsprofile:",
        "fr_FR": "Profils de connexion :",
        "es_ES": "Perfiles de conexión:",
        "ca_ES": "Perfils de connexió:",
        "ar_LB": "ملفات تعريف الاتصال:",
        "ro_RO": "Profile de Conexiune:",
        "pt_PT": "Perfis de Conexão:",
        "el_GR": "Προφίλ Σύνδεσης:",
    },
    "Profiles:": {
        "it_IT": "Profili:",
        "en_US": "Profiles:",
        "de_DE": "Profile:",
        "fr_FR": "Profils :",
        "es_ES": "Perfiles:",
        "ca_ES": "Perfils:",
        "ar_LB": "الملفات الشخصية:",
        "ro_RO": "Profile:",
        "pt_PT": "Perfis:",
        "el_GR": "Προφίλ:",
    },
    "Saved:": {
        "it_IT": "Salvati:",
        "en_US": "Saved:",
        "de_DE": "Gespeichert:",
        "fr_FR": "Enregistrés :",
        "es_ES": "Guardados:",
        "ca_ES": "Desats:",
        "ar_LB": "المحفوظة:",
        "ro_RO": "Salvate:",
        "pt_PT": "Guardados:",
        "el_GR": "Αποθηκευμένα:",
    },
    "Save current database settings as a profile": {
        "it_IT": "Salva le impostazioni correnti del database come profilo",
        "en_US": "Save current database settings as a profile",
        "de_DE": "Aktuelle Datenbankeinstellungen als Profil speichern",
        "fr_FR": "Enregistrer les paramètres de base de données actuels comme profil",
        "es_ES": "Guardar la configuración actual de la base de datos como perfil",
        "ca_ES": "Desar la configuració actual de la base de dades com a perfil",
        "ar_LB": "حفظ إعدادات قاعدة البيانات الحالية كملف تعريف",
        "ro_RO": "Salvează setările curente ale bazei de date ca profil",
        "pt_PT": "Guardar as definições atuais da base de dados como perfil",
        "el_GR": "Αποθήκευση τρεχουσών ρυθμίσεων βάσης δεδομένων ως προφίλ",
    },
    "Profile Loaded": {
        "it_IT": "Profilo Caricato",
        "en_US": "Profile Loaded",
        "de_DE": "Profil geladen",
        "fr_FR": "Profil chargé",
        "es_ES": "Perfil cargado",
        "ca_ES": "Perfil carregat",
        "ar_LB": "تم تحميل الملف الشخصي",
        "ro_RO": "Profil Încărcat",
        "pt_PT": "Perfil Carregado",
        "el_GR": "Το Προφίλ Φορτώθηκε",
    },
    "Profile '{name}' loaded successfully!\n\nClick 'Save Parameters' to apply the connection.": {
        "it_IT": "Profilo '{name}' caricato con successo!\n\nClicca 'Salva Parametri' per applicare la connessione.",
        "en_US": "Profile '{name}' loaded successfully!\n\nClick 'Save Parameters' to apply the connection.",
        "de_DE": "Profil '{name}' erfolgreich geladen!\n\nKlicken Sie auf 'Parameter speichern', um die Verbindung anzuwenden.",
        "fr_FR": "Profil '{name}' chargé avec succès !\n\nCliquez sur 'Enregistrer les paramètres' pour appliquer la connexion.",
        "es_ES": "¡Perfil '{name}' cargado correctamente!\n\nHaga clic en 'Guardar parámetros' para aplicar la conexión.",
        "ca_ES": "Perfil '{name}' carregat correctament!\n\nFeu clic a 'Desar paràmetres' per aplicar la connexió.",
        "ar_LB": "تم تحميل الملف الشخصي '{name}' بنجاح!\n\nانقر على 'حفظ المعلمات' لتطبيق الاتصال.",
        "ro_RO": "Profilul '{name}' a fost încărcat cu succes!\n\nFaceți clic pe 'Salvează Parametrii' pentru a aplica conexiunea.",
        "pt_PT": "Perfil '{name}' carregado com sucesso!\n\nClique em 'Guardar Parâmetros' para aplicar a conexão.",
        "el_GR": "Το προφίλ '{name}' φορτώθηκε επιτυχώς!\n\nΚάντε κλικ στο 'Αποθήκευση Παραμέτρων' για εφαρμογή της σύνδεσης.",
    },
    "Enter a name for this database connection profile:": {
        "it_IT": "Inserisci un nome per questo profilo di connessione al database:",
        "en_US": "Enter a name for this database connection profile:",
        "de_DE": "Geben Sie einen Namen für dieses Datenbank-Verbindungsprofil ein:",
        "fr_FR": "Entrez un nom pour ce profil de connexion à la base de données :",
        "es_ES": "Introduzca un nombre para este perfil de conexión a la base de datos:",
        "ca_ES": "Introduïu un nom per a aquest perfil de connexió a la base de dades:",
        "ar_LB": "أدخل اسمًا لملف تعريف اتصال قاعدة البيانات هذا:",
        "ro_RO": "Introduceți un nume pentru acest profil de conexiune la baza de date:",
        "pt_PT": "Introduza um nome para este perfil de conexão à base de dados:",
        "el_GR": "Εισαγάγετε ένα όνομα για αυτό το προφίλ σύνδεσης βάσης δεδομένων:",
    },
    "Database connection profile '{name}' saved successfully!\n\nServer: {server}\nHost: {host}:{port}\nDatabase: {database}": {
        "it_IT": "Profilo di connessione al database '{name}' salvato con successo!\n\nServer: {server}\nHost: {host}:{port}\nDatabase: {database}",
        "en_US": "Database connection profile '{name}' saved successfully!\n\nServer: {server}\nHost: {host}:{port}\nDatabase: {database}",
        "de_DE": "Datenbank-Verbindungsprofil '{name}' erfolgreich gespeichert!\n\nServer: {server}\nHost: {host}:{port}\nDatenbank: {database}",
        "fr_FR": "Profil de connexion à la base de données '{name}' enregistré avec succès !\n\nServeur : {server}\nHôte : {host}:{port}\nBase de données : {database}",
        "es_ES": "¡Perfil de conexión a la base de datos '{name}' guardado correctamente!\n\nServidor: {server}\nHost: {host}:{port}\nBase de datos: {database}",
        "ca_ES": "Perfil de connexió a la base de dades '{name}' desat correctament!\n\nServidor: {server}\nHost: {host}:{port}\nBase de dades: {database}",
        "ar_LB": "تم حفظ ملف تعريف اتصال قاعدة البيانات '{name}' بنجاح!\n\nالخادم: {server}\nالمضيف: {host}:{port}\nقاعدة البيانات: {database}",
        "ro_RO": "Profilul de conexiune la baza de date '{name}' a fost salvat cu succes!\n\nServer: {server}\nGazdă: {host}:{port}\nBază de date: {database}",
        "pt_PT": "Perfil de conexão à base de dados '{name}' guardado com sucesso!\n\nServidor: {server}\nAnfitrião: {host}:{port}\nBase de dados: {database}",
        "el_GR": "Το προφίλ σύνδεσης βάσης δεδομένων '{name}' αποθηκεύτηκε επιτυχώς!\n\nΔιακομιστής: {server}\nHost: {host}:{port}\nΒάση δεδομένων: {database}",
    },
}

def generate_context_xml(lang_code):
    """Generate XML for the pyarchinitConfigDialog context with sync translations."""
    lines = ['<context>',
             '    <name>pyarchinitConfigDialog</name>']

    for source, translations in SYNC_TRANSLATIONS.items():
        translation = translations.get(lang_code, source)
        lines.append('    <message>')
        lines.append(f'        <source>{escape_xml(source)}</source>')
        lines.append(f'        <translation>{escape_xml(translation)}</translation>')
        lines.append('    </message>')

    lines.append('</context>')
    return '\n'.join(lines)

def escape_xml(text):
    """Escape special XML characters."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))

def generate_message_xml(source, translation):
    """Generate XML for a single message."""
    return f"""    <message>
        <source>{escape_xml(source)}</source>
        <translation>{escape_xml(translation)}</translation>
    </message>"""

def add_translations_to_file(filepath, lang_code):
    """Add sync translations to a .ts file, merging with existing context."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if context already exists
    if '<name>pyarchinitConfigDialog</name>' in content:
        # Context exists - add new messages to it
        added_count = 0
        for source, translations in SYNC_TRANSLATIONS.items():
            escaped_source = escape_xml(source)
            # Check if this translation already exists
            if f'<source>{escaped_source}</source>' in content:
                continue  # Skip existing translations

            translation = translations.get(lang_code, source)
            new_message = generate_message_xml(source, translation)

            # Find the closing </context> tag for pyarchinitConfigDialog
            # We need to find the right context block
            context_start = content.find('<name>pyarchinitConfigDialog</name>')
            if context_start != -1:
                # Find the </context> that follows this context
                context_end = content.find('</context>', context_start)
                if context_end != -1:
                    # Insert the new message before </context>
                    content = content[:context_end] + new_message + '\n' + content[context_end:]
                    added_count += 1

        if added_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Added {added_count} new translations to {filepath}")
            return True
        else:
            print(f"  All translations already exist in {filepath}")
            return False
    else:
        # Context doesn't exist - add the whole context
        new_context = generate_context_xml(lang_code)

        # Insert before </TS>
        if '</TS>' in content:
            content = content.replace('</TS>', f'{new_context}\n</TS>')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  Added new context with translations to {filepath}")
        return True

def main():
    """Main function."""
    # Get the i18n directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.dirname(script_dir)
    i18n_dir = os.path.join(plugin_dir, 'i18n')

    print(f"Adding sync translations to files in: {i18n_dir}")

    # Language file mapping
    lang_files = {
        'it_IT': 'pyarchinit_plugin_it_IT.ts',
        'en_US': 'pyarchinit_plugin_en_US.ts',
        'de_DE': 'pyarchinit_plugin_de_DE.ts',
        'fr_FR': 'pyarchinit_plugin_fr_FR.ts',
        'es_ES': 'pyarchinit_plugin_es_ES.ts',
        'ca_ES': 'pyarchinit_plugin_ca_ES.ts',
        'ar_LB': 'pyarchinit_plugin_ar_LB.ts',
        'ro_RO': 'pyarchinit_plugin_ro_RO.ts',
        'pt_PT': 'pyarchinit_plugin_pt_PT.ts',
        'el_GR': 'pyarchinit_plugin_el_GR.ts',
    }

    for lang_code, filename in lang_files.items():
        filepath = os.path.join(i18n_dir, filename)
        if os.path.exists(filepath):
            add_translations_to_file(filepath, lang_code)
        else:
            print(f"  File not found: {filepath}")

    print("\nDone! Remember to compile .ts files to .qm using lrelease.")

if __name__ == '__main__':
    main()
