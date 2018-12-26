
CREATE VIEW IF NOT EXISTS"pyarchinit_doc_view" AS
SELECT "a"."ROWID" AS "ROWID", "a"."id_documentazione" AS "id_documentazione",
"a"."sito" AS "sito", "a"."nome_doc" AS "nome_doc",
"a"."data" AS "data", "a"."tipo_documentazione" AS "tipo_documentazione",
"a"."sorgente" AS "sorgente", "a"."scala" AS "scala",
"a"."disegnatore" AS "disegnatore", "a"."note" AS "note",
"b"."ROWID" AS "ROWID_1", "b"."pkuid" AS "pkuid",
"b"."sito" AS "sito_1", "b"."nome_doc" AS "nome_doc_1",
"b"."tipo_doc" AS "tipo_doc", "b"."path_qgis_pj" AS "path_qgis_pj",
"b"."the_geom" AS "the_geom"
FROM "documentazione_table" AS "a"
JOIN "pyarchinit_documentazione" AS "b" ON ("a"."sito" = "b"."sito" AND "a"."nome_doc" = "b"."nome_doc"
AND "a"."tipo_documentazione" = "b"."tipo_doc");

