-- Script per aggiornare la periodizzazione di Al-Khutm
-- Basato sulle note stratigrafiche del sito
-- Database: Supabase khutm2

-- Prima verifichiamo i dati esistenti
-- SELECT * FROM periodizzazione WHERE sito = 'Al-Khutm' ORDER BY periodo, fase;

-- Elimina i periodi esistenti per Al-Khutm (se presenti)
DELETE FROM periodizzazione WHERE sito = 'Al-Khutm';

-- Inserisce i nuovi periodi per Al-Khutm basati sulla stratigrafia del sito
-- Nota: cron_iniziale e cron_finale sono in BCE (numeri positivi = BCE)

-- Periodo 5 Fase 1: Late Umm an-Nar (2200-2000 BCE)
INSERT INTO periodizzazione (sito, periodo, fase, cron_iniziale, cron_finale, descrizione, datazione_estesa, cont_per)
VALUES ('Al-Khutm', 5, 1, 2200, 2000, 'Late Umm an-Nar', '2200-2000 BCE', 1);

-- Periodo 4 Fase 1: Early Wadi Suq (2000-1700 BCE)
INSERT INTO periodizzazione (sito, periodo, fase, cron_iniziale, cron_finale, descrizione, datazione_estesa, cont_per)
VALUES ('Al-Khutm', 4, 1, 2000, 1700, 'Early Wadi Suq', '2000-1700 BCE', 1);

-- Periodo 4 Fase 2: Late Wadi Suq (1700-1300 BCE)
INSERT INTO periodizzazione (sito, periodo, fase, cron_iniziale, cron_finale, descrizione, datazione_estesa, cont_per)
VALUES ('Al-Khutm', 4, 2, 1700, 1300, 'Late Wadi Suq', '1700-1300 BCE', 1);

-- Periodo 3 Fase 1: Late Bronze Age (1300-1100 BCE)
INSERT INTO periodizzazione (sito, periodo, fase, cron_iniziale, cron_finale, descrizione, datazione_estesa, cont_per)
VALUES ('Al-Khutm', 3, 1, 1300, 1100, 'Late Bronze Age', '1300-1100 BCE', 1);

-- Periodo 2 Fase 1: Iron Age (1100-300 BCE)
INSERT INTO periodizzazione (sito, periodo, fase, cron_iniziale, cron_finale, descrizione, datazione_estesa, cont_per)
VALUES ('Al-Khutm', 2, 1, 1100, 300, 'Iron Age', '1100-300 BCE', 1);

-- Periodo 1 Fase 1: Islamic (630-1900 CE)
-- Nota: per le date CE, usare numeri negativi o invertire la logica
INSERT INTO periodizzazione (sito, periodo, fase, cron_iniziale, cron_finale, descrizione, datazione_estesa, cont_per)
VALUES ('Al-Khutm', 1, 1, -630, -1900, 'Islamic Period', '630-1900 CE', 1);

-- Verifica l'inserimento
SELECT * FROM periodizzazione WHERE sito = 'Al-Khutm' ORDER BY periodo DESC, fase;

-- ============================================================================
-- AGGIORNAMENTO US_TABLE: Calcola datazione da periodo/fase
-- ============================================================================
-- Dopo aver impostato periodo_iniziale, fase_iniziale, periodo_finale, fase_finale
-- sulle schede US, questa query aggiorna automaticamente il campo datazione

-- Query per aggiornare datazione basandosi sulla periodizzazione
UPDATE pyunitastratigrafiche us
SET datazione = (
    SELECT COALESCE(p1.datazione_estesa, '') ||
           CASE WHEN p2.datazione_estesa IS NOT NULL AND p2.datazione_estesa != p1.datazione_estesa
                THEN ' - ' || p2.datazione_estesa
                ELSE ''
           END
    FROM periodizzazione p1
    LEFT JOIN periodizzazione p2 ON p2.sito = us.sito
                                  AND p2.periodo = us.periodo_finale
                                  AND p2.fase = us.fase_finale
    WHERE p1.sito = us.sito
      AND p1.periodo = us.periodo_iniziale
      AND p1.fase = us.fase_iniziale
)
WHERE sito = 'Al-Khutm'
  AND periodo_iniziale IS NOT NULL
  AND periodo_iniziale != 0;

-- Query per verificare le US con le loro datazioni
SELECT us_id, us, sito,
       periodo_iniziale, fase_iniziale,
       periodo_finale, fase_finale,
       datazione
FROM pyunitastratigrafiche
WHERE sito = 'Al-Khutm'
  AND (periodo_iniziale IS NOT NULL AND periodo_iniziale != 0)
ORDER BY us_id;

-- ============================================================================
-- MAPPATURA PERIODI Al-Khutm (riferimento per l'inserimento manuale)
-- ============================================================================
-- Periodo 5 Fase 1: Late Umm an-Nar (2200-2000 BCE)
-- Periodo 4 Fase 1: Early Wadi Suq (2000-1700 BCE)
-- Periodo 4 Fase 2: Late Wadi Suq (1700-1300 BCE)
-- Periodo 3 Fase 1: Late Bronze Age (1300-1100 BCE)
-- Periodo 2 Fase 1: Iron Age (1100-300 BCE)
-- Periodo 1 Fase 1: Islamic Period (630-1900 CE)
-- ============================================================================
