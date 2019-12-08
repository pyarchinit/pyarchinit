CREATE VIEW IF NOT EXISTS"pyarchinit_us_negative_doc_view" AS
SELECT "a"."ROWID" AS "ROWID", "a"."pkuid" AS "pkuid",
"a"."sito_n" AS "sito_n", "a"."area_n" AS "area_n",
"a"."us_n" AS "us_n", "a"."tipo_doc_n" AS "tipo_doc_n",
"a"."nome_doc_n" AS "nome_doc_n", "a"."the_geom" AS "the_geom",
"b"."ROWID" AS "ROWID_1", "b"."id_us" AS "id_us",
"b"."sito" AS "sito", "b"."area" AS "area", "b"."us" AS "us",
"b"."d_stratigrafica" AS "d_stratigrafica", "b"."d_interpretativa" AS "d_interpretativa",
"b"."descrizione" AS "descrizione", "b"."interpretazione" AS "interpretazione",
"b"."periodo_iniziale" AS "periodo_iniziale", "b"."fase_iniziale" AS "fase_iniziale",
"b"."periodo_finale" AS "periodo_finale", "b"."fase_finale" AS "fase_finale",
"b"."scavato" AS "scavato", "b"."attivita" AS "attivita",
"b"."anno_scavo" AS "anno_scavo", "b"."metodo_di_scavo" AS "metodo_di_scavo",
"b"."inclusi" AS "inclusi", "b"."campioni" AS "campioni",
"b"."rapporti" AS "rapporti", "b"."data_schedatura" AS "data_schedatura",
"b"."schedatore" AS "schedatore", "b"."formazione" AS "formazione",
"b"."stato_di_conservazione" AS "stato_di_conservazione",
"b"."colore" AS "colore", "b"."consistenza" AS "consistenza",
"b"."struttura" AS "struttura", "b"."cont_per" AS "cont_per",
"b"."order_layer" AS "order_layer", "b"."documentazione" AS "documentazione"
FROM "pyarchinit_us_negative_doc" AS "a"
JOIN "us_table" AS "b" ON ("a"."sito_n" = "b"."sito" AND "a"."area_n" = "b"."area"
AND "a"."us_n" = "b"."us");

