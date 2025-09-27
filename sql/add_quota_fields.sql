-- =====================================================
-- AGGIUNTA CAMPI QUOTA A INVENTARIO MATERIALI
-- =====================================================

-- Aggiungi campo quota (FLOAT per valori anche negativi)
ALTER TABLE inventario_materiali_table
ADD COLUMN IF NOT EXISTS quota_min_usm FLOAT,
ADD COLUMN IF NOT EXISTS quota_max_usm FLOAT,
ADD COLUMN IF NOT EXISTS unita_misura_quota VARCHAR(10) DEFAULT 'm s.l.m.';

-- Commenti per documentazione
COMMENT ON COLUMN inventario_materiali_table.quota_min_usm IS 'Quota minima US/USM in metri (può essere negativa)';
COMMENT ON COLUMN inventario_materiali_table.quota_max_usm IS 'Quota massima US/USM in metri (può essere negativa)';
COMMENT ON COLUMN inventario_materiali_table.unita_misura_quota IS 'Unità di misura quota (es: m s.l.m., cm, m)';

-- Ricrea la vista pyarchinit_reperti_view se esiste
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
    -- Nuovi campi quota
    im.quota_min_usm,
    im.quota_max_usm,
    im.unita_misura_quota,
    -- Campi di concorrenza
    im.last_modified_timestamp,
    im.last_modified_by,
    im.version_number,
    im.editing_by,
    im.editing_since
FROM inventario_materiali_table im;

-- Crea indici per performance
CREATE INDEX IF NOT EXISTS idx_inventario_quota ON inventario_materiali_table(quota_min_usm, quota_max_usm);

-- Grant permessi sulla vista
GRANT SELECT ON pyarchinit_reperti_view TO PUBLIC;

DO $$
BEGIN
    RAISE NOTICE '✅ Campi quota aggiunti con successo a inventario_materiali_table';
    RAISE NOTICE '✅ Vista pyarchinit_reperti_view aggiornata';
END $$;