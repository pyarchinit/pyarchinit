# Codici e Nomi Corretti per il Thesaurus PyArchInit

## Nomi Tabelle Corretti
- `Sito`
- `US`
- `Inventario Materiali`
- `Tombe`
- `Individui`
- `TMA materiali archeologici`

## Lingua
Sempre in MAIUSCOLO: `IT` (non `it`)

## Codici Tipologia Sigla per AREA

| Tabella | Codice Area |
|---------|-------------|
| US | 2.43 |
| Inventario Materiali | 3.41 |
| Tombe | 5.5 |
| Individui | 6.6 |
| TMA materiali archeologici | 10.7 |

## Codici Tipologia Sigla per SETTORE

| Tabella | Codice Settore |
|---------|----------------|
| US | 2.21 |
| TMA materiali archeologici | 10.15 |

## Codici per Inventario Materiali

| Campo Thesaurus | Codice | Campo Database |
|-----------------|--------|----------------|
| TIPO REPERTO | 3.1 | tipo_reperto |
| CLASSE MATERIALE | 3.2 | corpo_ceramico |
| DEFINIZIONE REPERTO | 3.3 | definizione |

**NOTA**: Tipologia (10.12) del TMA NON ha corrispondenza in Inventario Materiali

## Mapping Materiali TMA → Inventario

| TMA | Inventario Materiali |
|-----|---------------------|
| Categoria (10.10) | TIPO REPERTO (3.1) |
| Classe (10.11) | CLASSE MATERIALE (3.2) |
| Definizione (10.13) | DEFINIZIONE REPERTO (3.3) |
| Precisazione tipologica (10.12) | Non disponibile |

## Esempio di Record nel Thesaurus

```
nome_tabella: 'Inventario Materiali'
tipologia_sigla: '3.1'
sigla: 'Ceramica'
sigla_estesa: 'Ceramica comune'
descrizione: 'Sincronizzato da TMA'
lingua: 'IT'
order_layer: 3
```