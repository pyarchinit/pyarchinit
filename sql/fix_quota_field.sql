-- =====================================================
-- CORREZIONE CAMPO QUOTA - Solo UNA quota
-- =====================================================

-- Rimuovi i campi min/max se esistono
ALTER TABLE inventario_materiali_table
DROP COLUMN IF EXISTS quota_min_usm,
DROP COLUMN IF EXISTS quota_max_usm;

-- Aggiungi campo quota singolo
ALTER TABLE inventario_materiali_table
ADD COLUMN IF NOT EXISTS quota_usm FLOAT,
ADD COLUMN IF NOT EXISTS unita_misura_quota VARCHAR(20) DEFAULT 'm s.l.m.';

-- Commenti per documentazione
COMMENT ON COLUMN inventario_materiali_table.quota_usm IS 'Quota US/USM (può essere negativa)';
COMMENT ON COLUMN inventario_materiali_table.unita_misura_quota IS 'Unità di misura quota (es: m s.l.m., m, cm)';

-- Ricrea la vista pyarchinit_reperti_view
DROP VIEW IF EXISTS pyarchinit_reperti_view CASCADE;

CREATE OR REPLACE VIEW pyarchinit_reperti_view AS
SELECT
    im.id_invmat,
    im.sito,
    im.numero_inventario,
    im.tipo_reperto,
    im.criterio_schedatura,
    im.definizione,
    im.descrizione,
    im.area,
    im.us,
    im.lavato,
    im.nr_cassa,
    im.luogo_conservazione,
    im.stato_conservazione,
    im.datazione_reperto,
    im.elementi_reperto,
    im.misurazioni,
    im.rif_biblio,
    im.tecnologie,
    im.forme_minime,
    im.forme_massime,
    im.totale_frammenti,
    im.corpo_ceramico,
    im.rivestimento,
    im.diametro_orlo,
    im.peso,
    im.tipo,
    im.eve_orlo,
    im.repertato,
    im.diagnostico,
    -- Campo quota singolo
    im.quota_usm,
    im.unita_misura_quota,
    -- Campi di concorrenza
    im.last_modified_timestamp,
    im.last_modified_by,
    im.version_number,
    im.editing_by,
    im.editing_since
FROM inventario_materiali_table im;

-- Grant permessi sulla vista
GRANT SELECT ON pyarchinit_reperti_view TO PUBLIC;

DO $$
BEGIN
    RAISE NOTICE '✅ Campo quota corretto: ora solo quota_usm (singola)';
    RAISE NOTICE '✅ Vista pyarchinit_reperti_view aggiornata';
END $$;