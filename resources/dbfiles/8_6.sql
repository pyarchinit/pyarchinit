CREATE VIEW "pyarchinit_reperti_view" AS
SELECT "a"."ROWID" AS "ROWID", "a"."ROWIND" AS "ROWIND",
    "a"."the_geom" AS "the_geom", "a"."gid" AS "gid",
    "a"."id_rep" AS "id_rep", "a"."siti" AS "siti", "a"."link" AS "link",
    "b"."ROWID" AS "ROWID_1", "b"."id_invmat" AS "id_invmat",
    "b"."sito" AS "sito", "b"."numero_inventario" AS "numero_inventario",
    "b"."tipo_reperto" AS "tipo_reperto", "b"."criterio_schedatura" AS "criterio_schedatura",
    "b"."definizione" AS "definizione", "b"."descrizione" AS "descrizione",
    "b"."area" AS "area", "b"."us" AS "us", "b"."lavato" AS "lavato",
    "b"."nr_cassa" AS "nr_cassa", "b"."luogo_conservazione" AS "luogo_conservazione",
    "b"."stato_conservazione" AS "stato_conservazione",
    "b"."datazione_reperto" AS "datazione_reperto",
    "b"."elementi_reperto" AS "elementi_reperto", "b"."misurazioni" AS "misurazioni",
    "b"."rif_biblio" AS "rif_biblio", "b"."tecnologie" AS "tecnologie",
    "b"."forme_minime" AS "forme_minime", "b"."forme_massime" AS "forme_massime",
    "b"."totale_frammenti" AS "totale_frammenti", "b"."corpo_ceramico" AS "corpo_ceramico",
    "b"."rivestimento" AS "rivestimento"
FROM "pyarchinit_reperti" AS "a"
JOIN "inventario_materiali_table_toimp" AS "b" ON ("a"."siti" = "b"."sito" AND "a"."id_rep" = "b"."numero_inventario")