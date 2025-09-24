-- Fix for thesaurus sigla field length issue
-- Changes sigla from character(3) to character varying(255)
-- This allows longer sigla values like 'AREA001'

ALTER TABLE public.pyarchinit_thesaurus_sigle
ALTER COLUMN sigla TYPE character varying(255);

-- If the above fails due to existing data, use this instead:
-- ALTER TABLE public.pyarchinit_thesaurus_sigle
-- ALTER COLUMN sigla TYPE character varying(255) USING sigla::character varying(255);