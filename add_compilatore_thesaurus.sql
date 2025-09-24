-- Add compilatore/schedatore thesaurus entry for inventario_materiali_table
-- This adds a new thesaurus entry with code 3.14 for the compilatore field
-- Note: tipologia and datazione now use TMA thesaurus codes (10.8 and 10.4)

-- Insert for Italian language
INSERT INTO pyarchinit_thesaurus_sigle (lingua, nome_tabella, tipologia_sigla, sigla_estesa, sigla, n_tipologia, n_sigla)
VALUES ('it', 'inventario_materiali_table', '3.14', 'Compilatore/Schedatore', 'COMP', 3, 14)
ON CONFLICT (lingua, nome_tabella, tipologia_sigla) DO NOTHING;

-- Insert for English language
INSERT INTO pyarchinit_thesaurus_sigle (lingua, nome_tabella, tipologia_sigla, sigla_estesa, sigla, n_tipologia, n_sigla)
VALUES ('en', 'inventario_materiali_table', '3.14', 'Compiler/Recorder', 'COMP', 3, 14)
ON CONFLICT (lingua, nome_tabella, tipologia_sigla) DO NOTHING;

-- Insert for German language
INSERT INTO pyarchinit_thesaurus_sigle (lingua, nome_tabella, tipologia_sigla, sigla_estesa, sigla, n_tipologia, n_sigla)
VALUES ('de', 'inventario_materiali_table', '3.14', 'Bearbeiter/Aufnehmer', 'COMP', 3, 14)
ON CONFLICT (lingua, nome_tabella, tipologia_sigla) DO NOTHING;

-- You can add common compiler names as separate entries
-- Example entries for common compilers/recorders
INSERT INTO pyarchinit_thesaurus_sigle (lingua, nome_tabella, tipologia_sigla, sigla_estesa, sigla, n_tipologia, n_sigla)
VALUES
    ('it', 'inventario_materiali_table', '3.14', 'Mario Rossi', 'MR', 3, 14),
    ('it', 'inventario_materiali_table', '3.14', 'Anna Bianchi', 'AB', 3, 14),
    ('it', 'inventario_materiali_table', '3.14', 'Giuseppe Verdi', 'GV', 3, 14),
    ('it', 'inventario_materiali_table', '3.14', 'Enzo Cocca', 'EC', 3, 14)
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla_estesa) DO NOTHING;