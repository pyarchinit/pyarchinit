CREATE VIEW pyarchinit_quote_view AS
 SELECT pyarchinit_quote.sito_q, pyarchinit_quote.area_q, pyarchinit_quote.us_q, pyarchinit_quote.unita_misu, pyarchinit_quote.quota_q, pyarchinit_quote.geometry, us_table.id_us, us_table.sito, us_table.area, us_table.us, us_table.struttura, us_table.definizione_stratigrafica, us_table.definizione_interpretativa, us_table.descrizione, us_table.interpretazione, us_table.rapporti, us_table.periodo_iniziale, us_table.fase_iniziale, us_table.periodo_finale, us_table.fase_finale, us_table.anno_scavo
   FROM pyarchinit_quote
   JOIN us_table ON pyarchinit_quote.sito_q = us_table.sito AND pyarchinit_quote.area_q = us_table.area AND pyarchinit_quote.us_q = us_table.us;


CREATE VIEW pyarchinit_us_view AS SELECT pyunitastratigrafiche.PK_UID, pyunitastratigrafiche.geometry, pyunitastratigrafiche.tipo_us_s, pyunitastratigrafiche.scavo_s, pyunitastratigrafiche.area_s, pyunitastratigrafiche.us_s, us_table.id_us, us_table.sito, us_table.area, us_table.us, us_table.struttura, us_table.definizione_stratigrafica, us_table.definizione_interpretativa, us_table.descrizione, us_table.interpretazione, us_table.rapporti, us_table.periodo_iniziale, us_table.fase_iniziale, us_table.periodo_finale, us_table.fase_finale, us_table.anno_scavo
   FROM pyunitastratigrafiche
   JOIN us_table ON pyunitastratigrafiche.scavo_s = us_table.sito AND pyunitastratigrafiche.area_s = us_table.area AND pyunitastratigrafiche.us_s = us_table.us

CREATE VIEW pyarchinit_uscaratterizzazioni_view AS
 SELECT pyuscaratterizzazioni.geometry, pyuscaratterizzazioni.tipo_us_c, pyuscaratterizzazioni.scavo_c, pyuscaratterizzazioni.area_c, pyuscaratterizzazioni.us_c, us_table.sito, us_table.id_us, us_table.area, us_table.us, us_table.struttura, us_table.definizione_stratigrafica, us_table.definizione_interpretativa, us_table.descrizione, us_table.interpretazione, us_table.rapporti, us_table.periodo_iniziale, us_table.fase_iniziale, us_table.periodo_finale, us_table.fase_finale, us_table.anno_scavo
   FROM pyuscaratterizzazioni
   JOIN us_table ON pyuscaratterizzazioni.scavo_c = us_table.sito AND pyuscaratterizzazioni.area_c = us_table.area AND pyuscaratterizzazioni.us_c = us_table.us;

/*
CREATE VIEW pyarchinit_us_view AS SELECT pyunitastratigrafiche.PK_UID, pyunitastratigrafiche.geometry, pyunitastratigrafiche.tipo_us_s, pyunitastratigrafiche.scavo_s, pyunitastratigrafiche.area_s, pyunitastratigrafiche.us_s, us_table.id_us, us_table.sito, us_table.area, us_table.us, us_table.struttura, us_table.definizione_stratigrafica, us_table.definizione_interpretativa, us_table.descrizione, us_table.interpretazione, us_table.rapporti, us_table.periodo_iniziale, us_table.fase_iniziale, us_table.periodo_finale, us_table.fase_finale, us_table.anno_scavo
   FROM pyunitastratigrafiche
   JOIN us_table ON pyunitastratigrafiche.scavo_s = us_table.sito AND pyunitastratigrafiche.area_s = us_table.area AND pyunitastratigrafiche.us_s = us_table.us
*/






