-- =====================================================
-- THESAURUS ENTRIES FOR SCHEDA STRUTTURA
-- Tutte le voci thesaurus per la scheda Struttura (6.1-6.15)
-- =====================================================

-- 6.1 - Sigla Struttura
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'STR', 'STR', 'Struttura generica', '6.1', 'IT', 6, 1, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='STR' AND tipologia_sigla='6.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MUR', 'MUR', 'Muro', '6.1', 'IT', 6, 1, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MUR' AND tipologia_sigla='6.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'AMB', 'AMB', 'Ambiente', '6.1', 'IT', 6, 1, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='AMB' AND tipologia_sigla='6.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'TOM', 'TOM', 'Tomba', '6.1', 'IT', 6, 1, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='TOM' AND tipologia_sigla='6.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FOR', 'FOR', 'Forno', '6.1', 'IT', 6, 1, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FOR' AND tipologia_sigla='6.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'POZ', 'POZ', 'Pozzo', '6.1', 'IT', 6, 1, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='POZ' AND tipologia_sigla='6.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'CIS', 'CIS', 'Cisterna', '6.1', 'IT', 6, 1, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='CIS' AND tipologia_sigla='6.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'PAV', 'PAV', 'Pavimento', '6.1', 'IT', 6, 1, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='PAV' AND tipologia_sigla='6.1' AND lingua='IT');

-- 6.2 - Categoria Struttura
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'CAT_1', 'Edilizia civile', 'Categoria edilizia civile', '6.2', 'IT', 6, 2, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='CAT_1' AND tipologia_sigla='6.2' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'CAT_2', 'Edilizia religiosa', 'Categoria edilizia religiosa', '6.2', 'IT', 6, 2, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='CAT_2' AND tipologia_sigla='6.2' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'CAT_3', 'Edilizia funeraria', 'Categoria edilizia funeraria', '6.2', 'IT', 6, 2, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='CAT_3' AND tipologia_sigla='6.2' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'CAT_4', 'Edilizia militare', 'Categoria edilizia militare', '6.2', 'IT', 6, 2, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='CAT_4' AND tipologia_sigla='6.2' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'CAT_5', 'Edilizia produttiva', 'Categoria edilizia produttiva', '6.2', 'IT', 6, 2, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='CAT_5' AND tipologia_sigla='6.2' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'CAT_6', 'Infrastrutture', 'Categoria infrastrutture', '6.2', 'IT', 6, 2, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='CAT_6' AND tipologia_sigla='6.2' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'CAT_7', 'Architettura rupestre', 'Categoria architettura rupestre', '6.2', 'IT', 6, 2, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='CAT_7' AND tipologia_sigla='6.2' AND lingua='IT');

-- 6.3 - Tipologia Struttura
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'TIP_1', 'Abitazione', 'Tipologia abitazione', '6.3', 'IT', 6, 3, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='TIP_1' AND tipologia_sigla='6.3' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'TIP_2', 'Chiesa', 'Tipologia chiesa', '6.3', 'IT', 6, 3, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='TIP_2' AND tipologia_sigla='6.3' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'TIP_3', 'Necropoli', 'Tipologia necropoli', '6.3', 'IT', 6, 3, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='TIP_3' AND tipologia_sigla='6.3' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'TIP_4', 'Fortificazione', 'Tipologia fortificazione', '6.3', 'IT', 6, 3, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='TIP_4' AND tipologia_sigla='6.3' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'TIP_5', 'Officina', 'Tipologia officina', '6.3', 'IT', 6, 3, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='TIP_5' AND tipologia_sigla='6.3' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'TIP_6', 'Ipogeo', 'Tipologia ipogeo', '6.3', 'IT', 6, 3, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='TIP_6' AND tipologia_sigla='6.3' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'TIP_7', 'Grotta', 'Tipologia grotta', '6.3', 'IT', 6, 3, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='TIP_7' AND tipologia_sigla='6.3' AND lingua='IT');

-- 6.4 - Definizione Struttura
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'DEF_1', 'Muro perimetrale', 'Definizione muro perimetrale', '6.4', 'IT', 6, 4, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='DEF_1' AND tipologia_sigla='6.4' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'DEF_2', 'Muro divisorio', 'Definizione muro divisorio', '6.4', 'IT', 6, 4, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='DEF_2' AND tipologia_sigla='6.4' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'DEF_3', 'Fondazione', 'Definizione fondazione', '6.4', 'IT', 6, 4, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='DEF_3' AND tipologia_sigla='6.4' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'DEF_4', 'Soglia', 'Definizione soglia', '6.4', 'IT', 6, 4, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='DEF_4' AND tipologia_sigla='6.4' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'DEF_5', 'Ambiente rupestre', 'Definizione ambiente rupestre', '6.4', 'IT', 6, 4, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='DEF_5' AND tipologia_sigla='6.4' AND lingua='IT');

-- 6.5 - Materiali Impiegati
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MAT_1', 'Pietra', 'Materiale pietra', '6.5', 'IT', 6, 5, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MAT_1' AND tipologia_sigla='6.5' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MAT_2', 'Laterizio', 'Materiale laterizio', '6.5', 'IT', 6, 5, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MAT_2' AND tipologia_sigla='6.5' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MAT_3', 'Malta', 'Materiale malta', '6.5', 'IT', 6, 5, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MAT_3' AND tipologia_sigla='6.5' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MAT_4', 'Legno', 'Materiale legno', '6.5', 'IT', 6, 5, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MAT_4' AND tipologia_sigla='6.5' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MAT_5', 'Terra', 'Materiale terra', '6.5', 'IT', 6, 5, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MAT_5' AND tipologia_sigla='6.5' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MAT_6', 'Ciottoli', 'Materiale ciottoli', '6.5', 'IT', 6, 5, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MAT_6' AND tipologia_sigla='6.5' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MAT_7', 'Roccia', 'Materiale roccia', '6.5', 'IT', 6, 5, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MAT_7' AND tipologia_sigla='6.5' AND lingua='IT');

-- 6.6 - Tipologia Elemento Strutturale
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELEM_1', 'Arco', 'Elemento arco', '6.6', 'IT', 6, 6, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELEM_1' AND tipologia_sigla='6.6' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELEM_2', 'Colonna', 'Elemento colonna', '6.6', 'IT', 6, 6, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELEM_2' AND tipologia_sigla='6.6' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELEM_3', 'Pilastro', 'Elemento pilastro', '6.6', 'IT', 6, 6, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELEM_3' AND tipologia_sigla='6.6' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELEM_4', 'Volta', 'Elemento volta', '6.6', 'IT', 6, 6, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELEM_4' AND tipologia_sigla='6.6' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELEM_5', 'Pavimento', 'Elemento pavimento', '6.6', 'IT', 6, 6, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELEM_5' AND tipologia_sigla='6.6' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELEM_6', 'Soglia', 'Elemento soglia', '6.6', 'IT', 6, 6, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELEM_6' AND tipologia_sigla='6.6' AND lingua='IT');

-- 6.7 - Tipo Misura
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MIS_1', 'Lunghezza', 'Tipo misura lunghezza', '6.7', 'IT', 6, 7, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MIS_1' AND tipologia_sigla='6.7' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MIS_2', 'Larghezza', 'Tipo misura larghezza', '6.7', 'IT', 6, 7, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MIS_2' AND tipologia_sigla='6.7' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MIS_3', 'Altezza', 'Tipo misura altezza', '6.7', 'IT', 6, 7, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MIS_3' AND tipologia_sigla='6.7' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MIS_4', 'Spessore', 'Tipo misura spessore', '6.7', 'IT', 6, 7, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MIS_4' AND tipologia_sigla='6.7' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MIS_5', 'Diametro', 'Tipo misura diametro', '6.7', 'IT', 6, 7, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MIS_5' AND tipologia_sigla='6.7' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MIS_6', 'Profondita''', 'Tipo misura profondita', '6.7', 'IT', 6, 7, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MIS_6' AND tipologia_sigla='6.7' AND lingua='IT');

-- 6.8 - Unita di Misura
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'UM_1', 'm', 'Unita di misura metri', '6.8', 'IT', 6, 8, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='UM_1' AND tipologia_sigla='6.8' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'UM_2', 'cm', 'Unita di misura centimetri', '6.8', 'IT', 6, 8, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='UM_2' AND tipologia_sigla='6.8' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'UM_3', 'mm', 'Unita di misura millimetri', '6.8', 'IT', 6, 8, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='UM_3' AND tipologia_sigla='6.8' AND lingua='IT');

-- 6.9 - Elementi Architettonici (per misurazioni AR)
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ARCH_1', 'Arco', 'Elemento architettonico arco', '6.9', 'IT', 6, 9, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ARCH_1' AND tipologia_sigla='6.9' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ARCH_2', 'Colonna', 'Elemento architettonico colonna', '6.9', 'IT', 6, 9, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ARCH_2' AND tipologia_sigla='6.9' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ARCH_3', 'Pilastro', 'Elemento architettonico pilastro', '6.9', 'IT', 6, 9, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ARCH_3' AND tipologia_sigla='6.9' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ARCH_4', 'Volta', 'Elemento architettonico volta', '6.9', 'IT', 6, 9, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ARCH_4' AND tipologia_sigla='6.9' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ARCH_5', 'Nicchia', 'Elemento architettonico nicchia', '6.9', 'IT', 6, 9, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ARCH_5' AND tipologia_sigla='6.9' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ARCH_6', 'Bancone', 'Elemento architettonico bancone', '6.9', 'IT', 6, 9, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ARCH_6' AND tipologia_sigla='6.9' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ARCH_7', 'Gradino', 'Elemento architettonico gradino', '6.9', 'IT', 6, 9, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ARCH_7' AND tipologia_sigla='6.9' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ARCH_8', 'Ingresso', 'Elemento architettonico ingresso', '6.9', 'IT', 6, 9, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ARCH_8' AND tipologia_sigla='6.9' AND lingua='IT');

-- 6.10 - Fattori Agenti (per stato conservazione)
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FATT_1', 'Agenti atmosferici', 'Fattore agente atmosferico', '6.10', 'IT', 6, 10, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FATT_1' AND tipologia_sigla='6.10' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FATT_2', 'Intervento antropico', 'Fattore agente antropico', '6.10', 'IT', 6, 10, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FATT_2' AND tipologia_sigla='6.10' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FATT_3', 'Vegetazione', 'Fattore agente vegetazione', '6.10', 'IT', 6, 10, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FATT_3' AND tipologia_sigla='6.10' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FATT_4', 'Umidita''', 'Fattore agente umidita', '6.10', 'IT', 6, 10, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FATT_4' AND tipologia_sigla='6.10' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FATT_5', 'Crollo', 'Fattore agente crollo', '6.10', 'IT', 6, 10, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FATT_5' AND tipologia_sigla='6.10' AND lingua='IT');

-- 6.11 - Prospetto Ingresso
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'PROSP_1', 'A filo di roccia', 'Prospetto a filo di roccia', '6.11', 'IT', 6, 11, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='PROSP_1' AND tipologia_sigla='6.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'PROSP_2', 'Arretrato', 'Prospetto arretrato', '6.11', 'IT', 6, 11, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='PROSP_2' AND tipologia_sigla='6.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'PROSP_3', 'Aggettante', 'Prospetto aggettante', '6.11', 'IT', 6, 11, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='PROSP_3' AND tipologia_sigla='6.11' AND lingua='IT');

-- 6.12 - Elementi Costitutivi
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELCOS_1', 'Dromos', 'Elemento costitutivo dromos', '6.12', 'IT', 6, 12, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELCOS_1' AND tipologia_sigla='6.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELCOS_2', 'Vestibolo', 'Elemento costitutivo vestibolo', '6.12', 'IT', 6, 12, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELCOS_2' AND tipologia_sigla='6.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELCOS_3', 'Cella', 'Elemento costitutivo cella', '6.12', 'IT', 6, 12, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELCOS_3' AND tipologia_sigla='6.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'ELCOS_4', 'Anticella', 'Elemento costitutivo anticella', '6.12', 'IT', 6, 12, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='ELCOS_4' AND tipologia_sigla='6.12' AND lingua='IT');

-- 6.13 - Manufatti
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MANUF_1', 'Ceramica', 'Manufatto ceramica', '6.13', 'IT', 6, 13, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MANUF_1' AND tipologia_sigla='6.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MANUF_2', 'Metallo', 'Manufatto metallo', '6.13', 'IT', 6, 13, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MANUF_2' AND tipologia_sigla='6.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MANUF_3', 'Vetro', 'Manufatto vetro', '6.13', 'IT', 6, 13, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MANUF_3' AND tipologia_sigla='6.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MANUF_4', 'Litico', 'Manufatto litico', '6.13', 'IT', 6, 13, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MANUF_4' AND tipologia_sigla='6.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'MANUF_5', 'Osso', 'Manufatto osso', '6.13', 'IT', 6, 13, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='MANUF_5' AND tipologia_sigla='6.13' AND lingua='IT');

-- 6.14 - Definizione e Fasi Funzionali
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FUNZ_1', 'Abitativa', 'Funzione abitativa', '6.14', 'IT', 6, 14, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FUNZ_1' AND tipologia_sigla='6.14' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FUNZ_2', 'Cultuale', 'Funzione cultuale', '6.14', 'IT', 6, 14, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FUNZ_2' AND tipologia_sigla='6.14' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FUNZ_3', 'Funeraria', 'Funzione funeraria', '6.14', 'IT', 6, 14, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FUNZ_3' AND tipologia_sigla='6.14' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FUNZ_4', 'Produttiva', 'Funzione produttiva', '6.14', 'IT', 6, 14, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FUNZ_4' AND tipologia_sigla='6.14' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FUNZ_5', 'Stoccaggio', 'Funzione stoccaggio', '6.14', 'IT', 6, 14, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FUNZ_5' AND tipologia_sigla='6.14' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'FUNZ_6', 'Ricovero animali', 'Funzione ricovero animali', '6.14', 'IT', 6, 14, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='FUNZ_6' AND tipologia_sigla='6.14' AND lingua='IT');

-- 6.15 - Sviluppo Planimetrico
INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'SVIL_1', 'Assiale', 'Sviluppo planimetrico assiale', '6.15', 'IT', 6, 15, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='SVIL_1' AND tipologia_sigla='6.15' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'SVIL_2', 'Trasversale', 'Sviluppo planimetrico trasversale', '6.15', 'IT', 6, 15, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='SVIL_2' AND tipologia_sigla='6.15' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'SVIL_3', 'A croce', 'Sviluppo planimetrico a croce', '6.15', 'IT', 6, 15, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='SVIL_3' AND tipologia_sigla='6.15' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'SVIL_4', 'Circolare', 'Sviluppo planimetrico circolare', '6.15', 'IT', 6, 15, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='SVIL_4' AND tipologia_sigla='6.15' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, n_tipologia, n_sigla, hierarchy_level)
SELECT COALESCE(MAX(id_thesaurus_sigle), 0) + 1, 'struttura_table', 'SVIL_5', 'Irregolare', 'Sviluppo planimetrico irregolare', '6.15', 'IT', 6, 15, 0 FROM pyarchinit_thesaurus_sigle WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='struttura_table' AND sigla='SVIL_5' AND tipologia_sigla='6.15' AND lingua='IT');
