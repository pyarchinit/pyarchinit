-- =====================================================
-- Thesaurus entries for UT table (new survey fields)
-- =====================================================

-- UT Survey Type (survey_type)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'intensive', 'Intensive Survey', 'Intensive field walking survey', '12.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='intensive' AND tipologia_sigla='12.1');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'extensive', 'Extensive Survey', 'Extensive reconnaissance survey', '12.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='extensive' AND tipologia_sigla='12.1');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'targeted', 'Targeted Survey', 'Targeted investigation', '12.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='targeted' AND tipologia_sigla='12.1');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'random', 'Random Sampling', 'Random sampling methodology', '12.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='random' AND tipologia_sigla='12.1');

-- UT Vegetation Coverage (vegetation_coverage)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'none', 'No vegetation', 'Bare ground with no vegetation', '12.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='none' AND tipologia_sigla='12.2');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'sparse', 'Sparse vegetation', 'Less than 25% coverage', '12.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='sparse' AND tipologia_sigla='12.2');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'moderate', 'Moderate vegetation', '25-50% coverage', '12.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='moderate' AND tipologia_sigla='12.2');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'dense', 'Dense vegetation', '50-75% coverage', '12.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='dense' AND tipologia_sigla='12.2');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'very_dense', 'Very dense vegetation', 'Over 75% coverage', '12.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='very_dense' AND tipologia_sigla='12.2');

-- UT GPS Method (gps_method)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'handheld', 'Handheld GPS', 'Handheld GPS device', '12.3', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='handheld' AND tipologia_sigla='12.3');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'dgps', 'Differential GPS', 'DGPS with base station correction', '12.3', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='dgps' AND tipologia_sigla='12.3');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'rtk', 'RTK GPS', 'Real-time kinematic GPS', '12.3', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='rtk' AND tipologia_sigla='12.3');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'total_station', 'Total Station', 'Total station survey', '12.3', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='total_station' AND tipologia_sigla='12.3');

-- UT Surface Condition (surface_condition)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'ploughed', 'Ploughed', 'Recently ploughed field', '12.4', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='ploughed' AND tipologia_sigla='12.4');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'stubble', 'Stubble', 'Crop stubble present', '12.4', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='stubble' AND tipologia_sigla='12.4');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'pasture', 'Pasture', 'Grassland/pasture', '12.4', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='pasture' AND tipologia_sigla='12.4');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'woodland', 'Woodland', 'Wooded area', '12.4', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='woodland' AND tipologia_sigla='12.4');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'urban', 'Urban', 'Urban/built area', '12.4', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='urban' AND tipologia_sigla='12.4');

-- UT Accessibility (accessibility)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'easy', 'Easy access', 'No restrictions on access', '12.5', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='easy' AND tipologia_sigla='12.5');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'moderate_access', 'Moderate access', 'Some restrictions or difficulties', '12.5', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='moderate_access' AND tipologia_sigla='12.5');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'difficult', 'Difficult access', 'Significant access problems', '12.5', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='difficult' AND tipologia_sigla='12.5');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'restricted', 'Restricted access', 'Access by permission only', '12.5', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='restricted' AND tipologia_sigla='12.5');

-- UT Weather Conditions (weather_conditions)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'sunny', 'Sunny', 'Clear and sunny weather', '12.6', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='sunny' AND tipologia_sigla='12.6');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'cloudy', 'Cloudy', 'Overcast conditions', '12.6', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='cloudy' AND tipologia_sigla='12.6');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'rainy', 'Rainy', 'Rain during survey', '12.6', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='rainy' AND tipologia_sigla='12.6');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'ut_table', 'windy', 'Windy', 'Strong winds', '12.6', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='ut_table' AND sigla='windy' AND tipologia_sigla='12.6');

-- =====================================================
-- Thesaurus entries for Fauna table
-- =====================================================

-- Fauna Context (contesto)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'domestic', 'Domestic context', 'Domestic/residential context', '13.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='domestic' AND tipologia_sigla='13.1');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'ritual', 'Ritual context', 'Ritual/ceremonial context', '13.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='ritual' AND tipologia_sigla='13.1');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'funerary', 'Funerary context', 'Burial/funerary context', '13.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='funerary' AND tipologia_sigla='13.1');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'industrial', 'Industrial context', 'Industrial/workshop context', '13.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='industrial' AND tipologia_sigla='13.1');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'refuse', 'Refuse deposit', 'Waste/refuse deposit', '13.1', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='refuse' AND tipologia_sigla='13.1');

-- Fauna Recovery Methodology (metodologia_recupero)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'hand', 'Hand collection', 'Manual collection during excavation', '13.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='hand' AND tipologia_sigla='13.2');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'sieving', 'Sieving', 'Dry or wet sieving', '13.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='sieving' AND tipologia_sigla='13.2');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'flotation', 'Flotation', 'Water flotation', '13.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='flotation' AND tipologia_sigla='13.2');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'total', 'Total recovery', 'Complete sediment collection', '13.2', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='total' AND tipologia_sigla='13.2');

-- Fauna Accumulation Type (tipologia_accumulo)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'primary', 'Primary deposit', 'In situ deposit', '13.3', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='primary' AND tipologia_sigla='13.3');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'secondary', 'Secondary deposit', 'Redeposited remains', '13.3', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='secondary' AND tipologia_sigla='13.3');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'mixed', 'Mixed deposit', 'Mixed primary and secondary', '13.3', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='mixed' AND tipologia_sigla='13.3');

-- Fauna Deposition (deposizione)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'intentional', 'Intentional', 'Intentional deposition', '13.4', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='intentional' AND tipologia_sigla='13.4');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'natural', 'Natural', 'Natural accumulation', '13.4', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='natural' AND tipologia_sigla='13.4');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'unknown_dep', 'Unknown', 'Deposition mode unknown', '13.4', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='unknown_dep' AND tipologia_sigla='13.4');

-- Fauna Fragmentation State (stato_frammentazione)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'complete', 'Complete', 'Complete/whole bones', '13.5', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='complete' AND tipologia_sigla='13.5');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'fragmentary', 'Fragmentary', 'Broken/fragmentary', '13.5', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='fragmentary' AND tipologia_sigla='13.5');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'highly_frag', 'Highly fragmented', 'Severely fragmented', '13.5', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='highly_frag' AND tipologia_sigla='13.5');

-- Fauna Conservation State (stato_conservazione)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'good', 'Good', 'Good preservation', '13.6', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='good' AND tipologia_sigla='13.6');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'moderate_cons', 'Moderate', 'Moderate preservation', '13.6', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='moderate_cons' AND tipologia_sigla='13.6');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'poor', 'Poor', 'Poor preservation', '13.6', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='poor' AND tipologia_sigla='13.6');

-- Fauna Stratigraphic Reliability (affidabilita_stratigrafica)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'high', 'High', 'High reliability', '13.7', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='high' AND tipologia_sigla='13.7');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'medium', 'Medium', 'Medium reliability', '13.7', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='medium' AND tipologia_sigla='13.7');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'low', 'Low', 'Low reliability', '13.7', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='low' AND tipologia_sigla='13.7');

-- Fauna Burning Traces (tracce_combustione)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'none_burn', 'None', 'No burning traces', '13.8', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='none_burn' AND tipologia_sigla='13.8');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'charred', 'Charred', 'Charred/blackened', '13.8', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='charred' AND tipologia_sigla='13.8');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'calcined', 'Calcined', 'Calcined/white', '13.8', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='calcined' AND tipologia_sigla='13.8');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'partial_burn', 'Partial burning', 'Partially burned', '13.8', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='partial_burn' AND tipologia_sigla='13.8');

-- Fauna Combustion Type (tipo_combustione)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'cooking', 'Cooking', 'Related to cooking', '13.9', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='cooking' AND tipologia_sigla='13.9');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'cremation', 'Cremation', 'Related to cremation rite', '13.9', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='cremation' AND tipologia_sigla='13.9');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'disposal', 'Disposal burning', 'Burning for waste disposal', '13.9', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='disposal' AND tipologia_sigla='13.9');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'accidental', 'Accidental', 'Accidental burning', '13.9', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='accidental' AND tipologia_sigla='13.9');

-- Fauna Anatomical Connection (resti_connessione_anatomica)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'articulated', 'Articulated', 'Fully articulated remains', '13.10', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='articulated' AND tipologia_sigla='13.10');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'partial_art', 'Partially articulated', 'Some articulation present', '13.10', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='partial_art' AND tipologia_sigla='13.10');

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'fauna_table', 'disarticulated', 'Disarticulated', 'Completely disarticulated', '13.10', 'en_US'
WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_thesaurus_sigle WHERE nome_tabella='fauna_table' AND sigla='disarticulated' AND tipologia_sigla='13.10');
