-- =====================================================
-- Complete Thesaurus entries for Fauna table
-- All 7 supported languages: IT, EN, DE, ES, FR, AR, CA
-- Codes: 13.1 - 13.13
-- =====================================================

-- =====================================================
-- 13.1 - CONTESTO (Context)
-- =====================================================

-- Italian
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DOMESTICO', 'Contesto domestico', 'Contesto residenziale/abitativo', '13.1', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DOMESTICO' AND tipologia_sigla='13.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RITUALE', 'Contesto rituale', 'Contesto cerimoniale/rituale', '13.1', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RITUALE' AND tipologia_sigla='13.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FUNERARIO', 'Contesto funerario', 'Contesto sepolcrale/funerario', '13.1', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FUNERARIO' AND tipologia_sigla='13.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PRODUTTIVO', 'Contesto produttivo', 'Contesto artigianale/industriale', '13.1', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PRODUTTIVO' AND tipologia_sigla='13.1' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RIFIUTI', 'Deposito rifiuti', 'Scarico/deposito di rifiuti', '13.1', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RIFIUTI' AND tipologia_sigla='13.1' AND lingua='IT');

-- English
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DOMESTIC', 'Domestic context', 'Domestic/residential context', '13.1', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DOMESTIC' AND tipologia_sigla='13.1' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RITUAL', 'Ritual context', 'Ritual/ceremonial context', '13.1', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RITUAL' AND tipologia_sigla='13.1' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FUNERARY', 'Funerary context', 'Burial/funerary context', '13.1', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FUNERARY' AND tipologia_sigla='13.1' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'INDUSTRIAL', 'Industrial context', 'Industrial/workshop context', '13.1', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='INDUSTRIAL' AND tipologia_sigla='13.1' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'REFUSE', 'Refuse deposit', 'Waste/refuse deposit', '13.1', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='REFUSE' AND tipologia_sigla='13.1' AND lingua='EN');

-- German
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HAUSHALT', 'Haushaltskontext', 'Wohn-/Haushaltskontext', '13.1', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HAUSHALT' AND tipologia_sigla='13.1' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RITUELL', 'Ritueller Kontext', 'Zeremonieller/ritueller Kontext', '13.1', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RITUELL' AND tipologia_sigla='13.1' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'GRAB', 'Grabkontext', 'Bestattungs-/Grabkontext', '13.1', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='GRAB' AND tipologia_sigla='13.1' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'WERKSTATT', 'Werkstattkontext', 'Industrieller/Werkstattkontext', '13.1', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='WERKSTATT' AND tipologia_sigla='13.1' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ABFALL', 'Abfallablagerung', 'Abfall-/Müllablagerung', '13.1', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ABFALL' AND tipologia_sigla='13.1' AND lingua='DE');

-- Spanish
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DOMESTICO', 'Contexto domestico', 'Contexto residencial/domestico', '13.1', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DOMESTICO' AND tipologia_sigla='13.1' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RITUAL', 'Contexto ritual', 'Contexto ceremonial/ritual', '13.1', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RITUAL' AND tipologia_sigla='13.1' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FUNERARIO', 'Contexto funerario', 'Contexto sepulcral/funerario', '13.1', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FUNERARIO' AND tipologia_sigla='13.1' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PRODUCTIVO', 'Contexto productivo', 'Contexto industrial/artesanal', '13.1', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PRODUCTIVO' AND tipologia_sigla='13.1' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BASURA', 'Deposito de basura', 'Deposito de desechos/basura', '13.1', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BASURA' AND tipologia_sigla='13.1' AND lingua='ES');

-- French
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DOMESTIQUE', 'Contexte domestique', 'Contexte residentiel/domestique', '13.1', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DOMESTIQUE' AND tipologia_sigla='13.1' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RITUEL', 'Contexte rituel', 'Contexte ceremoniel/rituel', '13.1', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RITUEL' AND tipologia_sigla='13.1' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FUNERAIRE', 'Contexte funeraire', 'Contexte sepulcral/funeraire', '13.1', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FUNERAIRE' AND tipologia_sigla='13.1' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PRODUCTIF', 'Contexte productif', 'Contexte industriel/artisanal', '13.1', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PRODUCTIF' AND tipologia_sigla='13.1' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DECHETS', 'Depot de dechets', 'Depot de dechets/ordures', '13.1', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DECHETS' AND tipologia_sigla='13.1' AND lingua='FR');

-- Arabic
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MANZILI', 'سياق منزلي', 'سياق سكني/منزلي', '13.1', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MANZILI' AND tipologia_sigla='13.1' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TAQSI', 'سياق طقسي', 'سياق احتفالي/طقسي', '13.1', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TAQSI' AND tipologia_sigla='13.1' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'JANAZI', 'سياق جنائزي', 'سياق دفن/جنائزي', '13.1', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='JANAZI' AND tipologia_sigla='13.1' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'INTAJI', 'سياق إنتاجي', 'سياق صناعي/حرفي', '13.1', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='INTAJI' AND tipologia_sigla='13.1' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'NIFAYAT', 'ترسب نفايات', 'ترسب نفايات/مخلفات', '13.1', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='NIFAYAT' AND tipologia_sigla='13.1' AND lingua='AR');

-- =====================================================
-- 13.11 - SPECIE (Species)
-- =====================================================

-- Italian
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Bovino domestico', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BOS_TAURUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Pecora domestica', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_ARIES' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Capra domestica', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPRA_HIRCUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Maiale domestico', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_SCROFA', 'Sus scrofa', 'Cinghiale', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_SCROFA' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'Cervo', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CERVUS_ELAPHUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPREOLUS', 'Capreolus capreolus', 'Capriolo', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPREOLUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Cavallo', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_CABALLUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_ASINUS', 'Equus asinus', 'Asino', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_ASINUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Cane domestico', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CANIS_FAMILIARIS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FELIS_CATUS', 'Felis catus', 'Gatto domestico', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FELIS_CATUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'GALLUS_DOMESTICUS', 'Gallus gallus domesticus', 'Pollo domestico', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='GALLUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ORYCTOLAGUS', 'Oryctolagus cuniculus', 'Coniglio', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ORYCTOLAGUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'LEPUS', 'Lepus europaeus', 'Lepre', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='LEPUS' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Ovicaprino indeterminato', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_CAPRA' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'AVES_INDET', 'Aves indet.', 'Uccello indeterminato', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='AVES_INDET' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PISCES_INDET', 'Pisces indet.', 'Pesce indeterminato', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PISCES_INDET' AND tipologia_sigla='13.11' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MAMMALIA_INDET', 'Mammalia indet.', 'Mammifero indeterminato', '13.11', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MAMMALIA_INDET' AND tipologia_sigla='13.11' AND lingua='IT');

-- English
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Domestic cattle', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BOS_TAURUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Domestic sheep', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_ARIES' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Domestic goat', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPRA_HIRCUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Domestic pig', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_SCROFA', 'Sus scrofa', 'Wild boar', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_SCROFA' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'Red deer', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CERVUS_ELAPHUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPREOLUS', 'Capreolus capreolus', 'Roe deer', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPREOLUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Horse', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_CABALLUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_ASINUS', 'Equus asinus', 'Donkey', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_ASINUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Domestic dog', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CANIS_FAMILIARIS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FELIS_CATUS', 'Felis catus', 'Domestic cat', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FELIS_CATUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'GALLUS_DOMESTICUS', 'Gallus gallus domesticus', 'Domestic chicken', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='GALLUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ORYCTOLAGUS', 'Oryctolagus cuniculus', 'Rabbit', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ORYCTOLAGUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'LEPUS', 'Lepus europaeus', 'Hare', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='LEPUS' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Sheep/Goat undetermined', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_CAPRA' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'AVES_INDET', 'Aves indet.', 'Bird undetermined', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='AVES_INDET' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PISCES_INDET', 'Pisces indet.', 'Fish undetermined', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PISCES_INDET' AND tipologia_sigla='13.11' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MAMMALIA_INDET', 'Mammalia indet.', 'Mammal undetermined', '13.11', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MAMMALIA_INDET' AND tipologia_sigla='13.11' AND lingua='EN');

-- German
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Hausrind', '13.11', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BOS_TAURUS' AND tipologia_sigla='13.11' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Hausschaf', '13.11', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_ARIES' AND tipologia_sigla='13.11' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Hausziege', '13.11', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPRA_HIRCUS' AND tipologia_sigla='13.11' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Hausschwein', '13.11', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_SCROFA', 'Sus scrofa', 'Wildschwein', '13.11', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_SCROFA' AND tipologia_sigla='13.11' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Pferd', '13.11', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_CABALLUS' AND tipologia_sigla='13.11' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Haushund', '13.11', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CANIS_FAMILIARIS' AND tipologia_sigla='13.11' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Schaf/Ziege unbestimmt', '13.11', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_CAPRA' AND tipologia_sigla='13.11' AND lingua='DE');

-- =====================================================
-- 13.12 - PARTI SCHELETRICHE / PSI (Skeletal Parts)
-- =====================================================

-- Italian
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CRANIO', 'Cranio', 'Ossa del cranio', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CRANIO' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MANDIBOLA', 'Mandibola', 'Mandibola', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MANDIBOLA' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MASCELLARE', 'Mascellare', 'Osso mascellare', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MASCELLARE' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DENTI', 'Denti', 'Elementi dentari', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DENTI' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'VERTEBRE', 'Vertebre', 'Colonna vertebrale', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='VERTEBRE' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'COSTOLE', 'Costole', 'Coste/Costole', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='COSTOLE' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SCAPOLA', 'Scapola', 'Scapola', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SCAPOLA' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OMERO', 'Omero', 'Omero', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OMERO' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADIO', 'Radio', 'Radio', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADIO' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ULNA', 'Ulna', 'Ulna', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ULNA' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CARPO', 'Carpo', 'Ossa carpali', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CARPO' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METACARPO', 'Metacarpo', 'Metacarpo', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METACARPO' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PELVI', 'Pelvi', 'Bacino/Pelvi', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PELVI' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMORE', 'Femore', 'Femore', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMORE' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA', 'Tibia', 'Tibia', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FIBULA', 'Fibula', 'Fibula/Perone', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FIBULA' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ASTRAGALO', 'Astragalo', 'Astragalo/Talo', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ASTRAGALO' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CALCAGNO', 'Calcagno', 'Calcagno', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CALCAGNO' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METATARSO', 'Metatarso', 'Metatarso', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METATARSO' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGI', 'Falangi', 'Falangi', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGI' AND tipologia_sigla='13.12' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CORNO', 'Corno', 'Cavicchia ossea/corno', '13.12', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CORNO' AND tipologia_sigla='13.12' AND lingua='IT');

-- English
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SKULL', 'Skull', 'Cranial bones', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SKULL' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MANDIBLE', 'Mandible', 'Mandible/Lower jaw', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MANDIBLE' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MAXILLA', 'Maxilla', 'Upper jaw', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MAXILLA' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TEETH', 'Teeth', 'Dental elements', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TEETH' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'VERTEBRAE', 'Vertebrae', 'Vertebral column', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='VERTEBRAE' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RIBS', 'Ribs', 'Rib bones', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RIBS' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SCAPULA', 'Scapula', 'Shoulder blade', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SCAPULA' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERUS', 'Humerus', 'Upper arm bone', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERUS' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADIUS', 'Radius', 'Forearm bone', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADIUS' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ULNA', 'Ulna', 'Forearm bone', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ULNA' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METACARPUS', 'Metacarpus', 'Metacarpal bone', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METACARPUS' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PELVIS', 'Pelvis', 'Hip bone', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PELVIS' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR', 'Femur', 'Thigh bone', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA', 'Tibia', 'Shin bone', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METATARSUS', 'Metatarsus', 'Metatarsal bone', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METATARSUS' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANGES', 'Phalanges', 'Toe/Finger bones', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANGES' AND tipologia_sigla='13.12' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HORNCORE', 'Horn core', 'Horn core', '13.12', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HORNCORE' AND tipologia_sigla='13.12' AND lingua='EN');

-- =====================================================
-- 13.13 - ELEMENTO ANATOMICO (Anatomical Element for Measurements)
-- =====================================================

-- Italian
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OMERO_DX', 'Omero destro', 'Omero lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OMERO_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OMERO_SX', 'Omero sinistro', 'Omero lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OMERO_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADIO_DX', 'Radio destro', 'Radio lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADIO_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADIO_SX', 'Radio sinistro', 'Radio lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADIO_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMORE_DX', 'Femore destro', 'Femore lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMORE_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMORE_SX', 'Femore sinistro', 'Femore lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMORE_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_DX', 'Tibia destra', 'Tibia lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_SX', 'Tibia sinistra', 'Tibia lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METACARPO_DX', 'Metacarpo destro', 'Metacarpo lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METACARPO_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METACARPO_SX', 'Metacarpo sinistro', 'Metacarpo lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METACARPO_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METATARSO_DX', 'Metatarso destro', 'Metatarso lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METATARSO_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METATARSO_SX', 'Metatarso sinistro', 'Metatarso lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METATARSO_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ASTRAGALO_DX', 'Astragalo destro', 'Astragalo lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ASTRAGALO_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ASTRAGALO_SX', 'Astragalo sinistro', 'Astragalo lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ASTRAGALO_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CALCAGNO_DX', 'Calcagno destro', 'Calcagno lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CALCAGNO_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CALCAGNO_SX', 'Calcagno sinistro', 'Calcagno lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CALCAGNO_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SCAPOLA_DX', 'Scapola destra', 'Scapola lato destro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SCAPOLA_DX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SCAPOLA_SX', 'Scapola sinistra', 'Scapola lato sinistro', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SCAPOLA_SX' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_1', 'Prima falange', 'Prima falange', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_1' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_2', 'Seconda falange', 'Seconda falange', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_2' AND tipologia_sigla='13.13' AND lingua='IT');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_3', 'Terza falange', 'Terza falange', '13.13', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_3' AND tipologia_sigla='13.13' AND lingua='IT');

-- English
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERUS_R', 'Right humerus', 'Humerus right side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERUS_R' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERUS_L', 'Left humerus', 'Humerus left side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERUS_L' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADIUS_R', 'Right radius', 'Radius right side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADIUS_R' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADIUS_L', 'Left radius', 'Radius left side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADIUS_L' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_R', 'Right femur', 'Femur right side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_R' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_L', 'Left femur', 'Femur left side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_L' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_R', 'Right tibia', 'Tibia right side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_R' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_L', 'Left tibia', 'Tibia left side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_L' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METACARPUS_R', 'Right metacarpus', 'Metacarpus right side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METACARPUS_R' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METACARPUS_L', 'Left metacarpus', 'Metacarpus left side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METACARPUS_L' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METATARSUS_R', 'Right metatarsus', 'Metatarsus right side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METATARSUS_R' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'METATARSUS_L', 'Left metatarsus', 'Metatarsus left side', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='METATARSUS_L' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANX_1', 'First phalanx', 'First phalanx', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANX_1' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANX_2', 'Second phalanx', 'Second phalanx', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANX_2' AND tipologia_sigla='13.13' AND lingua='EN');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANX_3', 'Third phalanx', 'Third phalanx', '13.13', 'EN'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANX_3' AND tipologia_sigla='13.13' AND lingua='EN');

-- =====================================================
-- ADDITIONAL LANGUAGES FOR 13.11 - SPECIE (Species)
-- Spanish, French, Arabic, Catalan
-- =====================================================

-- Spanish (ES)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Bovino domestico', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BOS_TAURUS' AND tipologia_sigla='13.11' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Oveja domestica', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_ARIES' AND tipologia_sigla='13.11' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Cabra domestica', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPRA_HIRCUS' AND tipologia_sigla='13.11' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Cerdo domestico', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_SCROFA', 'Sus scrofa', 'Jabali', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_SCROFA' AND tipologia_sigla='13.11' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'Ciervo', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CERVUS_ELAPHUS' AND tipologia_sigla='13.11' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Caballo', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_CABALLUS' AND tipologia_sigla='13.11' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Perro domestico', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CANIS_FAMILIARIS' AND tipologia_sigla='13.11' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Oveja/Cabra indeterminado', '13.11', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_CAPRA' AND tipologia_sigla='13.11' AND lingua='ES');

-- French (FR)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Bovin domestique', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BOS_TAURUS' AND tipologia_sigla='13.11' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Mouton domestique', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_ARIES' AND tipologia_sigla='13.11' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Chevre domestique', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPRA_HIRCUS' AND tipologia_sigla='13.11' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Porc domestique', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_SCROFA', 'Sus scrofa', 'Sanglier', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_SCROFA' AND tipologia_sigla='13.11' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'Cerf', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CERVUS_ELAPHUS' AND tipologia_sigla='13.11' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Cheval', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_CABALLUS' AND tipologia_sigla='13.11' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Chien domestique', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CANIS_FAMILIARIS' AND tipologia_sigla='13.11' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Mouton/Chevre indetermine', '13.11', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_CAPRA' AND tipologia_sigla='13.11' AND lingua='FR');

-- Arabic (AR)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BOS_TAURUS', 'Bos taurus', 'ماشية منزلية', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BOS_TAURUS' AND tipologia_sigla='13.11' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_ARIES', 'Ovis aries', 'خروف منزلي', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_ARIES' AND tipologia_sigla='13.11' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'ماعز منزلي', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPRA_HIRCUS' AND tipologia_sigla='13.11' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'خنزير منزلي', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_SCROFA', 'Sus scrofa', 'خنزير بري', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_SCROFA' AND tipologia_sigla='13.11' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'أيل', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CERVUS_ELAPHUS' AND tipologia_sigla='13.11' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'حصان', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_CABALLUS' AND tipologia_sigla='13.11' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'كلب منزلي', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CANIS_FAMILIARIS' AND tipologia_sigla='13.11' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'خروف/ماعز غير محدد', '13.11', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_CAPRA' AND tipologia_sigla='13.11' AND lingua='AR');

-- Catalan (CA)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Bovi domestic', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BOS_TAURUS' AND tipologia_sigla='13.11' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Ovella domestica', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_ARIES' AND tipologia_sigla='13.11' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Cabra domestica', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CAPRA_HIRCUS' AND tipologia_sigla='13.11' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Porc domestic', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_DOMESTICUS' AND tipologia_sigla='13.11' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SUS_SCROFA', 'Sus scrofa', 'Senglar', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SUS_SCROFA' AND tipologia_sigla='13.11' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'Cervo', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CERVUS_ELAPHUS' AND tipologia_sigla='13.11' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Cavall', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='EQUUS_CABALLUS' AND tipologia_sigla='13.11' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Gos domestic', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CANIS_FAMILIARIS' AND tipologia_sigla='13.11' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Ovella/Cabra indeterminat', '13.11', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='OVIS_CAPRA' AND tipologia_sigla='13.11' AND lingua='CA');

-- =====================================================
-- ADDITIONAL LANGUAGES FOR 13.12 - PARTI SCHELETRICHE (Skeletal Parts)
-- Spanish, French, Arabic, Catalan
-- =====================================================

-- Spanish (ES)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CRANEO', 'Craneo', 'Huesos del craneo', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CRANEO' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MANDIBULA', 'Mandibula', 'Mandibula', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MANDIBULA' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DIENTES', 'Dientes', 'Elementos dentales', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DIENTES' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'VERTEBRAS', 'Vertebras', 'Columna vertebral', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='VERTEBRAS' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'COSTILLAS', 'Costillas', 'Costillas', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='COSTILLAS' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ESCAPULA', 'Escapula', 'Escapula', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ESCAPULA' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERO', 'Humero', 'Humero', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERO' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADIO', 'Radio', 'Radio', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADIO' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PELVIS', 'Pelvis', 'Pelvis', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PELVIS' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR', 'Femur', 'Femur', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA', 'Tibia', 'Tibia', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA' AND tipologia_sigla='13.12' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGES', 'Falanges', 'Falanges', '13.12', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGES' AND tipologia_sigla='13.12' AND lingua='ES');

-- French (FR)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CRANE', 'Crane', 'Os du crane', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CRANE' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MANDIBULE', 'Mandibule', 'Mandibule', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MANDIBULE' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DENTS', 'Dents', 'Elements dentaires', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DENTS' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'VERTEBRES', 'Vertebres', 'Colonne vertebrale', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='VERTEBRES' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'COTES', 'Cotes', 'Cotes', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='COTES' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SCAPULA', 'Scapula', 'Omoplate', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SCAPULA' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERUS', 'Humerus', 'Humerus', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERUS' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADIUS', 'Radius', 'Radius', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADIUS' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'BASSIN', 'Bassin', 'Bassin', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='BASSIN' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR', 'Femur', 'Femur', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA', 'Tibia', 'Tibia', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA' AND tipologia_sigla='13.12' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANGES', 'Phalanges', 'Phalanges', '13.12', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANGES' AND tipologia_sigla='13.12' AND lingua='FR');

-- Arabic (AR)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'JUMJUMA', 'جمجمة', 'عظام الجمجمة', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='JUMJUMA' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FAK_SUFLI', 'فك سفلي', 'الفك السفلي', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FAK_SUFLI' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ASNAN', 'أسنان', 'عناصر الأسنان', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ASNAN' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FIQARAT', 'فقرات', 'العمود الفقري', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FIQARAT' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DILUA', 'ضلوع', 'الضلوع', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DILUA' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'KATIF', 'كتف', 'عظم الكتف', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='KATIF' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ADHUD', 'عضد', 'عظم العضد', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ADHUD' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'KUAA', 'كعب', 'عظم الكعب', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='KUAA' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HAUD', 'حوض', 'عظم الحوض', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HAUD' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FAKHIDH', 'فخذ', 'عظم الفخذ', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FAKHIDH' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'QASABA', 'قصبة', 'عظم الساق', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='QASABA' AND tipologia_sigla='13.12' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SULAMIYYAT', 'سلاميات', 'عظام السلاميات', '13.12', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SULAMIYYAT' AND tipologia_sigla='13.12' AND lingua='AR');

-- Catalan (CA)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'CRANI', 'Crani', 'Ossos del crani', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='CRANI' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'MANDIBULA', 'Mandibula', 'Mandibula', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='MANDIBULA' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'DENTS', 'Dents', 'Elements dentals', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='DENTS' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'VERTEBRES', 'Vertebres', 'Columna vertebral', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='VERTEBRES' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'COSTELLES', 'Costelles', 'Costelles', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='COSTELLES' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ESCAPULA', 'Escapula', 'Escapula', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ESCAPULA' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMER', 'Humer', 'Humer', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMER' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'RADI', 'Radi', 'Radi', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='RADI' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PELVIS', 'Pelvis', 'Pelvis', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PELVIS' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR', 'Femur', 'Femur', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA', 'Tibia', 'Tibia', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA' AND tipologia_sigla='13.12' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGES', 'Falanges', 'Falanges', '13.12', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGES' AND tipologia_sigla='13.12' AND lingua='CA');

-- =====================================================
-- ADDITIONAL LANGUAGES FOR 13.13 - ELEMENTO ANATOMICO (Anatomical Element for Measurements)
-- German, Spanish, French, Arabic, Catalan
-- =====================================================

-- German (DE)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERUS_R', 'Rechter Humerus', 'Humerus rechte Seite', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERUS_R' AND tipologia_sigla='13.13' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERUS_L', 'Linker Humerus', 'Humerus linke Seite', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERUS_L' AND tipologia_sigla='13.13' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_R', 'Rechter Femur', 'Femur rechte Seite', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_R' AND tipologia_sigla='13.13' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_L', 'Linker Femur', 'Femur linke Seite', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_L' AND tipologia_sigla='13.13' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_R', 'Rechte Tibia', 'Tibia rechte Seite', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_R' AND tipologia_sigla='13.13' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_L', 'Linke Tibia', 'Tibia linke Seite', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_L' AND tipologia_sigla='13.13' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANX_1', 'Erste Phalanx', 'Erste Phalanx', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANX_1' AND tipologia_sigla='13.13' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANX_2', 'Zweite Phalanx', 'Zweite Phalanx', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANX_2' AND tipologia_sigla='13.13' AND lingua='DE');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANX_3', 'Dritte Phalanx', 'Dritte Phalanx', '13.13', 'DE'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANX_3' AND tipologia_sigla='13.13' AND lingua='DE');

-- Spanish (ES)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERO_DX', 'Humero derecho', 'Humero lado derecho', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERO_DX' AND tipologia_sigla='13.13' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERO_SX', 'Humero izquierdo', 'Humero lado izquierdo', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERO_SX' AND tipologia_sigla='13.13' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_DX', 'Femur derecho', 'Femur lado derecho', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_DX' AND tipologia_sigla='13.13' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_SX', 'Femur izquierdo', 'Femur lado izquierdo', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_SX' AND tipologia_sigla='13.13' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_DX', 'Tibia derecha', 'Tibia lado derecho', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_DX' AND tipologia_sigla='13.13' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_SX', 'Tibia izquierda', 'Tibia lado izquierdo', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_SX' AND tipologia_sigla='13.13' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_1', 'Primera falange', 'Primera falange', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_1' AND tipologia_sigla='13.13' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_2', 'Segunda falange', 'Segunda falange', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_2' AND tipologia_sigla='13.13' AND lingua='ES');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_3', 'Tercera falange', 'Tercera falange', '13.13', 'ES'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_3' AND tipologia_sigla='13.13' AND lingua='ES');

-- French (FR)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERUS_D', 'Humerus droit', 'Humerus cote droit', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERUS_D' AND tipologia_sigla='13.13' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMERUS_G', 'Humerus gauche', 'Humerus cote gauche', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMERUS_G' AND tipologia_sigla='13.13' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_D', 'Femur droit', 'Femur cote droit', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_D' AND tipologia_sigla='13.13' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_G', 'Femur gauche', 'Femur cote gauche', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_G' AND tipologia_sigla='13.13' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_D', 'Tibia droit', 'Tibia cote droit', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_D' AND tipologia_sigla='13.13' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_G', 'Tibia gauche', 'Tibia cote gauche', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_G' AND tipologia_sigla='13.13' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANGE_1', 'Premiere phalange', 'Premiere phalange', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANGE_1' AND tipologia_sigla='13.13' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANGE_2', 'Deuxieme phalange', 'Deuxieme phalange', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANGE_2' AND tipologia_sigla='13.13' AND lingua='FR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'PHALANGE_3', 'Troisieme phalange', 'Troisieme phalange', '13.13', 'FR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='PHALANGE_3' AND tipologia_sigla='13.13' AND lingua='FR');

-- Arabic (AR)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ADHUD_AYMAN', 'عضد أيمن', 'عضد الجانب الأيمن', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ADHUD_AYMAN' AND tipologia_sigla='13.13' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ADHUD_AYSAR', 'عضد أيسر', 'عضد الجانب الأيسر', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ADHUD_AYSAR' AND tipologia_sigla='13.13' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FAKHIDH_AYMAN', 'فخذ أيمن', 'فخذ الجانب الأيمن', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FAKHIDH_AYMAN' AND tipologia_sigla='13.13' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FAKHIDH_AYSAR', 'فخذ أيسر', 'فخذ الجانب الأيسر', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FAKHIDH_AYSAR' AND tipologia_sigla='13.13' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'QASABA_AYMAN', 'قصبة يمنى', 'قصبة الجانب الأيمن', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='QASABA_AYMAN' AND tipologia_sigla='13.13' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'QASABA_AYSAR', 'قصبة يسرى', 'قصبة الجانب الأيسر', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='QASABA_AYSAR' AND tipologia_sigla='13.13' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SULAMIYYA_1', 'السلامية الأولى', 'السلامية الأولى', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SULAMIYYA_1' AND tipologia_sigla='13.13' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SULAMIYYA_2', 'السلامية الثانية', 'السلامية الثانية', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SULAMIYYA_2' AND tipologia_sigla='13.13' AND lingua='AR');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'SULAMIYYA_3', 'السلامية الثالثة', 'السلامية الثالثة', '13.13', 'AR'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='SULAMIYYA_3' AND tipologia_sigla='13.13' AND lingua='AR');

-- Catalan (CA)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMER_DX', 'Humer dret', 'Humer costat dret', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMER_DX' AND tipologia_sigla='13.13' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'HUMER_SX', 'Humer esquerre', 'Humer costat esquerre', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='HUMER_SX' AND tipologia_sigla='13.13' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_DX', 'Femur dret', 'Femur costat dret', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_DX' AND tipologia_sigla='13.13' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FEMUR_SX', 'Femur esquerre', 'Femur costat esquerre', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FEMUR_SX' AND tipologia_sigla='13.13' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_DX', 'Tibia dreta', 'Tibia costat dret', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_DX' AND tipologia_sigla='13.13' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'TIBIA_SX', 'Tibia esquerra', 'Tibia costat esquerre', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='TIBIA_SX' AND tipologia_sigla='13.13' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_1', 'Primera falange', 'Primera falange', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_1' AND tipologia_sigla='13.13' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_2', 'Segona falange', 'Segona falange', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_2' AND tipologia_sigla='13.13' AND lingua='CA');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'FALANGE_3', 'Tercera falange', 'Tercera falange', '13.13', 'CA'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='FALANGE_3' AND tipologia_sigla='13.13' AND lingua='CA');
