-- SQL per sincronizzare il thesaurus TMA con le altre tabelle
-- Compatibile con PostgreSQL e SQLite

-- 1. Funzione per sincronizzare le aree al thesaurus TMA
-- PostgreSQL version
CREATE OR REPLACE FUNCTION sync_areas_to_tma_thesaurus() RETURNS void AS $$
BEGIN
    -- Aggiungi aree da us_table
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'area',
        'Area ' || area,
        area,
        'it',
        2
    FROM us_table
    WHERE area IS NOT NULL AND area != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    
    -- Aggiungi aree da inventario_materiali_table
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'area',
        'Area ' || area,
        area,
        'it',
        2
    FROM inventario_materiali_table
    WHERE area IS NOT NULL AND area != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    
    -- Aggiungi aree da tomba_table
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'area',
        'Area ' || area,
        area,
        'it',
        2
    FROM tomba_table
    WHERE area IS NOT NULL AND area != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    
    -- Aggiungi aree da individui_table
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'area',
        'Area ' || area,
        area,
        'it',
        2
    FROM individui_table
    WHERE area IS NOT NULL AND area != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    
    -- Aggiungi aree da tma_materiali_archeologici
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'area',
        'Area ' || area,
        area,
        'it',
        2
    FROM tma_materiali_archeologici
    WHERE area IS NOT NULL AND area != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- 2. Funzione per sincronizzare i campi materiali dall'inventario al thesaurus TMA
CREATE OR REPLACE FUNCTION sync_inventory_to_tma_thesaurus() RETURNS void AS $$
BEGIN
    -- Sincronizza tipo_reperto -> Categoria
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'Categoria',
        tipo_reperto,
        tipo_reperto,
        'it',
        3
    FROM inventario_materiali_table
    WHERE tipo_reperto IS NOT NULL AND tipo_reperto != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    
    -- Sincronizza classe_materiale -> Classe
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'Classe',
        classe_materiale,
        classe_materiale,
        'it',
        3
    FROM inventario_materiali_table
    WHERE classe_materiale IS NOT NULL AND classe_materiale != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    
    -- Sincronizza tipo -> Precisazione tipologica
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'Precisazione tipologica',
        tipo,
        tipo,
        'it',
        3
    FROM inventario_materiali_table
    WHERE tipo IS NOT NULL AND tipo != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    
    -- Sincronizza definizione -> Definizione
    INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
    SELECT DISTINCT 
        'TMA materiali archeologici',
        'Definizione',
        definizione,
        definizione,
        'it',
        3
    FROM inventario_materiali_table
    WHERE definizione IS NOT NULL AND definizione != ''
    ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- 3. Trigger per sincronizzazione automatica quando si inserisce nell'inventario
CREATE OR REPLACE FUNCTION sync_inventory_insert_to_thesaurus() RETURNS TRIGGER AS $$
BEGIN
    -- Sincronizza area
    IF NEW.area IS NOT NULL AND NEW.area != '' THEN
        INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
        VALUES ('TMA materiali archeologici', 'area', 'Area ' || NEW.area, NEW.area, 'it', 2)
        ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    END IF;
    
    -- Sincronizza tipo_reperto
    IF NEW.tipo_reperto IS NOT NULL AND NEW.tipo_reperto != '' THEN
        INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
        VALUES ('TMA materiali archeologici', 'Categoria', NEW.tipo_reperto, NEW.tipo_reperto, 'it', 3)
        ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    END IF;
    
    -- Sincronizza classe_materiale
    IF NEW.classe_materiale IS NOT NULL AND NEW.classe_materiale != '' THEN
        INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
        VALUES ('TMA materiali archeologici', 'Classe', NEW.classe_materiale, NEW.classe_materiale, 'it', 3)
        ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    END IF;
    
    -- Sincronizza tipo
    IF NEW.tipo IS NOT NULL AND NEW.tipo != '' THEN
        INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
        VALUES ('TMA materiali archeologici', 'Precisazione tipologica', NEW.tipo, NEW.tipo, 'it', 3)
        ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    END IF;
    
    -- Sincronizza definizione
    IF NEW.definizione IS NOT NULL AND NEW.definizione != '' THEN
        INSERT INTO pyarchinit_thesaurus (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
        VALUES ('TMA materiali archeologici', 'Definizione', NEW.definizione, NEW.definizione, 'it', 3)
        ON CONFLICT (nome_tabella, tipologia_sigla, thesaurus_sigle) DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crea il trigger
DROP TRIGGER IF EXISTS sync_inventory_to_thesaurus_trigger ON inventario_materiali_table;
CREATE TRIGGER sync_inventory_to_thesaurus_trigger
AFTER INSERT OR UPDATE ON inventario_materiali_table
FOR EACH ROW
EXECUTE FUNCTION sync_inventory_insert_to_thesaurus();

-- 4. Esegui la sincronizzazione iniziale
SELECT sync_areas_to_tma_thesaurus();
SELECT sync_inventory_to_tma_thesaurus();

-- 5. Query di verifica
-- Mostra tutte le aree nel thesaurus TMA
SELECT thesaurus_sigle, sigla_estesa 
FROM pyarchinit_thesaurus 
WHERE nome_tabella = 'TMA materiali archeologici' 
AND tipologia_sigla = 'area'
ORDER BY thesaurus_sigle;

-- Mostra i valori per i campi materiali
SELECT tipologia_sigla, COUNT(*) as num_valori
FROM pyarchinit_thesaurus 
WHERE nome_tabella = 'TMA materiali archeologici' 
AND tipologia_sigla IN ('Categoria', 'Classe', 'Precisazione tipologica', 'Definizione')
GROUP BY tipologia_sigla;