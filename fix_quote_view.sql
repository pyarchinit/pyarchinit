-- Fix pyarchinit_quote_view to include order_layer, cont_per and datazione
DROP VIEW IF EXISTS pyarchinit_quote_view;

CREATE VIEW pyarchinit_quote_view AS
SELECT 
    pyarchinit_quote.gid,
    pyarchinit_quote.sito_q, 
    pyarchinit_quote.area_q, 
    pyarchinit_quote.us_q, 
    pyarchinit_quote.unita_misu_q, 
    pyarchinit_quote.quota_q, 
    pyarchinit_quote.the_geom, 
    us_table.id_us, 
    us_table.sito, 
    us_table.area, 
    us_table.us, 
    us_table.struttura, 
    us_table.d_stratigrafica, 
    us_table.d_interpretativa, 
    us_table.descrizione, 
    us_table.interpretazione, 
    us_table.rapporti, 
    us_table.periodo_iniziale, 
    us_table.fase_iniziale, 
    us_table.periodo_finale, 
    us_table.fase_finale, 
    us_table.anno_scavo,
    us_table.cont_per,
    us_table.order_layer,
    us_table.datazione
FROM pyarchinit_quote
JOIN us_table ON 
    pyarchinit_quote.sito_q = us_table.sito 
    AND pyarchinit_quote.area_q = us_table.area 
    AND pyarchinit_quote.us_q = us_table.us;