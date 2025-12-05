-- =====================================================
-- THESAURUS ENTRIES FOR POTTERY TABLE
-- tipologia_sigla: 11.X series
-- =====================================================

-- =====================================================
-- 11.1 - Fabric
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FW', 'Fine ware', 'Fine ware fabric', '11.1', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MFW', 'Medium fine ware', 'Medium fine ware fabric', '11.1', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MCW', 'Medium coarse ware', 'Medium coarse ware fabric', '11.1', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CW', 'Coarse ware', 'Coarse ware fabric', '11.1', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- Italian translations
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FW', 'Ceramica fine', 'Impasto fine', '11.1', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MFW', 'Ceramica medio-fine', 'Impasto medio-fine', '11.1', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MCW', 'Ceramica medio-grossa', 'Impasto medio-grossolano', '11.1', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CW', 'Ceramica grossa', 'Impasto grossolano', '11.1', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- German translations
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FW', 'Feinkeramik', 'Feiner Ton', '11.1', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MFW', 'Mittelfeine Keramik', 'Mittelfeiner Ton', '11.1', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MCW', 'Mittelgrobe Keramik', 'Mittelgrober Ton', '11.1', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CW', 'Grobkeramik', 'Grober Ton', '11.1', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.2 - Percent (preserved %)
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '<5', '<5%', 'Less than 5% preserved', '11.2', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '5-25', '5-25%', '5 to 25% preserved', '11.2', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '25-50', '25-50%', '25 to 50% preserved', '11.2', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '>50', '>50%', 'More than 50% preserved', '11.2', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- Italian (same values)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '<5', '<5%', 'Conservato meno del 5%', '11.2', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '5-25', '5-25%', 'Conservato tra 5% e 25%', '11.2', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '25-50', '25-50%', 'Conservato tra 25% e 50%', '11.2', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '>50', '>50%', 'Conservato oltre il 50%', '11.2', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- German
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '<5', '<5%', 'Weniger als 5% erhalten', '11.2', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '5-25', '5-25%', '5 bis 25% erhalten', '11.2', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '25-50', '25-50%', '25 bis 50% erhalten', '11.2', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '>50', '>50%', 'Mehr als 50% erhalten', '11.2', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.3 - Material
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CER', 'Ceramic', 'Ceramic material', '11.3', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'STN', 'Stone', 'Stone material', '11.3', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CER', 'Ceramica', 'Materiale ceramico', '11.3', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'STN', 'Pietra', 'Materiale litico', '11.3', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CER', 'Keramik', 'Keramisches Material', '11.3', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'STN', 'Stein', 'Steinmaterial', '11.3', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.4 - Form (Open/Closed)
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'OPN', 'Open', 'Open form', '11.4', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CLS', 'Closed', 'Closed form', '11.4', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'UND', 'Undeterminable', 'Undeterminable form', '11.4', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'OPN', 'Aperta', 'Forma aperta', '11.4', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CLS', 'Chiusa', 'Forma chiusa', '11.4', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'UND', 'Indeterminabile', 'Forma indeterminabile', '11.4', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'OPN', 'Offen', 'Offene Form', '11.4', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CLS', 'Geschlossen', 'Geschlossene Form', '11.4', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'UND', 'Unbestimmbar', 'Unbestimmbare Form', '11.4', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.5 - Specific Form/Part
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'RIM', 'Rim', 'Rim fragment', '11.5', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'NCK', 'Neck', 'Neck fragment', '11.5', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'HDL', 'Handle', 'Handle fragment', '11.5', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'WLL', 'Wall', 'Wall fragment', '11.5', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BSE', 'Base', 'Base fragment', '11.5', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SPT', 'Spout', 'Spout fragment', '11.5', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'LIP', 'Lip', 'Lip fragment', '11.5', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FTD', 'Foot', 'Foot fragment', '11.5', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- Italian translations
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'RIM', 'Orlo', 'Frammento di orlo', '11.5', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'NCK', 'Collo', 'Frammento di collo', '11.5', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'HDL', 'Ansa', 'Frammento di ansa', '11.5', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'WLL', 'Parete', 'Frammento di parete', '11.5', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BSE', 'Fondo', 'Frammento di fondo', '11.5', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SPT', 'Beccuccio', 'Frammento di beccuccio', '11.5', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'LIP', 'Labbro', 'Frammento di labbro', '11.5', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FTD', 'Piede', 'Frammento di piede', '11.5', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- German translations
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'RIM', 'Rand', 'Randfragment', '11.5', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'NCK', 'Hals', 'Halsfragment', '11.5', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'HDL', 'Henkel', 'Henkelfragment', '11.5', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'WLL', 'Wandung', 'Wandungsfragment', '11.5', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BSE', 'Boden', 'Bodenfragment', '11.5', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SPT', 'Ausguss', 'Ausgussfragment', '11.5', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'LIP', 'Lippe', 'Lippenfragment', '11.5', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FTD', 'Fuss', 'Fussfragment', '11.5', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.6 - Ware Type
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FN', 'Fine', 'Fine ware', '11.6', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MD', 'Medium', 'Medium ware', '11.6', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CS', 'Coarse', 'Coarse ware', '11.6', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FN', 'Fine', 'Ceramica fine', '11.6', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MD', 'Media', 'Ceramica media', '11.6', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CS', 'Grossa', 'Ceramica grossa', '11.6', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FN', 'Fein', 'Feine Ware', '11.6', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'MD', 'Mittel', 'Mittlere Ware', '11.6', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CS', 'Grob', 'Grobe Ware', '11.6', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.7 - Munsell Color (common colors)
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '10YR8/2', '10YR 8/2 Very pale brown', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '7.5YR7/4', '7.5YR 7/4 Pink', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '5YR6/6', '5YR 6/6 Reddish yellow', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '2.5YR5/6', '2.5YR 5/6 Red', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '10R5/6', '10R 5/6 Red', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '7.5YR6/4', '7.5YR 6/4 Light brown', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '10YR6/3', '10YR 6/3 Pale brown', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '5YR5/4', '5YR 5/4 Reddish brown', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '2.5Y7/2', '2.5Y 7/2 Light gray', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'GLEY1-5/N', 'GLEY1 5/N Gray', 'Munsell color', '11.7', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- Copy for IT and DE (Munsell is universal)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '10YR8/2', '10YR 8/2 Marrone molto pallido', 'Colore Munsell', '11.7', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '7.5YR7/4', '7.5YR 7/4 Rosa', 'Colore Munsell', '11.7', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '5YR6/6', '5YR 6/6 Giallo rossastro', 'Colore Munsell', '11.7', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '2.5YR5/6', '2.5YR 5/6 Rosso', 'Colore Munsell', '11.7', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '10R5/6', '10R 5/6 Rosso', 'Colore Munsell', '11.7', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '10YR8/2', '10YR 8/2 Sehr hellbraun', 'Munsell-Farbe', '11.7', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '7.5YR7/4', '7.5YR 7/4 Rosa', 'Munsell-Farbe', '11.7', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '5YR6/6', '5YR 6/6 Rötlichgelb', 'Munsell-Farbe', '11.7', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '2.5YR5/6', '2.5YR 5/6 Rot', 'Munsell-Farbe', '11.7', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', '10R5/6', '10R 5/6 Rot', 'Munsell-Farbe', '11.7', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.8 - Surface Treatment
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SLR', 'Slipped red', 'Red slip coating', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BFF', 'Buff', 'Buff surface', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BSH', 'Burnished', 'Burnished surface', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PLH', 'Polished', 'Polished surface', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SMT', 'Smoothed', 'Smoothed surface', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'WSH', 'Washed', 'Washed surface', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SLW', 'Slipped white', 'White slip coating', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SLB', 'Slipped black', 'Black slip coating', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'GLZ', 'Glazed', 'Glazed surface', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'NON', 'None', 'No surface treatment', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- Italian translations
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SLR', 'Ingobbio rosso', 'Rivestimento a ingobbio rosso', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BFF', 'Buff', 'Superficie buff', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BSH', 'Brunita', 'Superficie brunita', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PLH', 'Levigata', 'Superficie levigata', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SMT', 'Lisciata', 'Superficie lisciata', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'WSH', 'Lavata', 'Superficie lavata', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SLW', 'Ingobbio bianco', 'Rivestimento a ingobbio bianco', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SLB', 'Ingobbio nero', 'Rivestimento a ingobbio nero', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'GLZ', 'Invetriata', 'Superficie invetriata', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'NON', 'Nessuno', 'Nessun trattamento superficiale', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- German translations
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SLR', 'Roter Überzug', 'Roter Slip-Überzug', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BFF', 'Buff', 'Buff-Oberfläche', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BSH', 'Geglättet', 'Geglättete Oberfläche', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PLH', 'Poliert', 'Polierte Oberfläche', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SMT', 'Verstrichen', 'Verstrichene Oberfläche', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'GLZ', 'Glasiert', 'Glasierte Oberfläche', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'NON', 'Keine', 'Keine Oberflächenbehandlung', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.9 - External Decoration (Yes/No)
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Yes', 'External decoration present', '11.9', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'No', 'No external decoration', '11.9', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Sì', 'Decorazione esterna presente', '11.9', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'No', 'Nessuna decorazione esterna', '11.9', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Ja', 'Außendekoration vorhanden', '11.9', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'Nein', 'Keine Außendekoration', '11.9', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.10 - Internal Decoration (Yes/No)
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Yes', 'Internal decoration present', '11.10', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'No', 'No internal decoration', '11.10', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Sì', 'Decorazione interna presente', '11.10', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'No', 'Nessuna decorazione interna', '11.10', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Ja', 'Innendekoration vorhanden', '11.10', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'Nein', 'Keine Innendekoration', '11.10', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.11 - Wheel Made (Yes/No)
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Yes', 'Wheel made', '11.11', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'No', 'Hand made', '11.11', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Sì', 'Tornio', '11.11', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'No', 'A mano', '11.11', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'Y', 'Ja', 'Scheibengedreht', '11.11', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'N', 'Nein', 'Handgeformt', '11.11', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- 11.12 - Specific Shape
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BWL', 'Bowl', 'Bowl shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'LID', 'Lid', 'Lid shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'JAR', 'Jar', 'Jar shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SPJ', 'Spouted jar', 'Spouted jar shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CUP', 'Cup', 'Cup shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PLT', 'Plate', 'Plate shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'JUG', 'Jug', 'Jug shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'AMP', 'Amphora', 'Amphora shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PTH', 'Pithos', 'Pithos shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FLK', 'Flask', 'Flask shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'KRT', 'Krater', 'Krater shape', '11.12', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- Italian translations
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BWL', 'Ciotola', 'Forma ciotola', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'LID', 'Coperchio', 'Forma coperchio', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'JAR', 'Giara', 'Forma giara', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SPJ', 'Giara con beccuccio', 'Forma giara con beccuccio', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CUP', 'Tazza', 'Forma tazza', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PLT', 'Piatto', 'Forma piatto', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'JUG', 'Brocca', 'Forma brocca', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'AMP', 'Anfora', 'Forma anfora', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PTH', 'Pithos', 'Forma pithos', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FLK', 'Fiasca', 'Forma fiasca', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'KRT', 'Cratere', 'Forma cratere', '11.12', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- German translations
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BWL', 'Schale', 'Schalenform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'LID', 'Deckel', 'Deckelform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'JAR', 'Krug', 'Krugform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'SPJ', 'Krug mit Ausguss', 'Krug mit Ausgussform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'CUP', 'Tasse', 'Tassenform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PLT', 'Teller', 'Tellerform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'JUG', 'Kanne', 'Kannenform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'AMP', 'Amphore', 'Amphorenform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'PTH', 'Pithos', 'Pithosform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'FLK', 'Flasche', 'Flaschenform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'KRT', 'Krater', 'Kraterform', '11.12', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- =====================================================
-- VERIFICA
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '=== POTTERY THESAURUS ENTRIES CREATED ===';
    RAISE NOTICE 'Tipologia codes used:';
    RAISE NOTICE '  4.1  - Fabric (Fine ware, Medium fine, Medium coarse, Coarse)';
    RAISE NOTICE '  4.2  - Percent preserved (<5%, 5-25%, 25-50%, >50%)';
    RAISE NOTICE '  4.3  - Material (Ceramic, Stone)';
    RAISE NOTICE '  4.4  - Form (Open, Closed, Undeterminable)';
    RAISE NOTICE '  4.5  - Specific Form/Part (Rim, Neck, Handle, Wall, Base, etc.)';
    RAISE NOTICE '  4.6  - Ware Type (Fine, Medium, Coarse)';
    RAISE NOTICE '  4.7  - Munsell Color';
    RAISE NOTICE '  4.8  - Surface Treatment (Slipped, Burnished, Polished, etc.)';
    RAISE NOTICE '  4.9  - External Decoration (Yes/No)';
    RAISE NOTICE '  4.10 - Internal Decoration (Yes/No)';
    RAISE NOTICE '  4.11 - Wheel Made (Yes/No)';
    RAISE NOTICE '  4.12 - Specific Shape (Bowl, Jar, Cup, Amphora, etc.)';
    RAISE NOTICE '';
    RAISE NOTICE 'Languages: EN, IT, DE';
END $$;

-- =====================================================
-- 11.13 - Area
-- =====================================================
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'A', 'Area A', 'Area A', '11.13', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'B', 'Area B', 'Area B', '11.13', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'C', 'Area C', 'Area C', '11.13', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'D', 'Area D', 'Area D', '11.13', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- Italian
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'A', 'Area A', 'Area A', '11.13', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'B', 'Area B', 'Area B', '11.13', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'C', 'Area C', 'Area C', '11.13', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'D', 'Area D', 'Area D', '11.13', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- German
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'A', 'Area A', 'Area A', '11.13', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'B', 'Area B', 'Area B', '11.13', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'C', 'Area C', 'Area C', '11.13', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'D', 'Area D', 'Area D', '11.13', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

-- Additional Surface Treatment entries (slipped)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'GS', 'Gray slipped', 'Gray slipped surface treatment', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BS', 'Black slipped', 'Black slipped surface treatment', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BRS', 'Brown slipped', 'Brown slipped surface treatment', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'WS', 'White slipped', 'White slipped surface treatment', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'RBS', 'Reddish brown slipped', 'Reddish brown slipped surface treatment', '11.8', 'EN')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'GS', 'Ingobbio grigio', 'Trattamento superficie ingobbio grigio', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BS', 'Ingobbio nero', 'Trattamento superficie ingobbio nero', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BRS', 'Ingobbio marrone', 'Trattamento superficie ingobbio marrone', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'WS', 'Ingobbio bianco', 'Trattamento superficie ingobbio bianco', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'RBS', 'Ingobbio marrone rossastro', 'Trattamento superficie ingobbio marrone rossastro', '11.8', 'IT')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'GS', 'Grauer Überzug', 'Grauer Überzug Oberflächenbehandlung', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BS', 'Schwarzer Überzug', 'Schwarzer Überzug Oberflächenbehandlung', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'BRS', 'Brauner Überzug', 'Brauner Überzug Oberflächenbehandlung', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'WS', 'Weißer Überzug', 'Weißer Überzug Oberflächenbehandlung', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('Pottery', 'RBS', 'Rotbrauner Überzug', 'Rotbrauner Überzug Oberflächenbehandlung', '11.8', 'DE')
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla) DO NOTHING;
