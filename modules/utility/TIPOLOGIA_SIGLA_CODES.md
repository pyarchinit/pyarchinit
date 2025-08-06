# Codici Tipologia Sigla per PyArchInit

## Mapping dei codici per Area e Settore

### Area
- **US (Unità Stratigrafica)**: `2.43`
- **TMA (Materiali Archeologici)**: `10.7`
- **Inventario Materiali**: `10.7`
- **Tomba**: `10.7`
- **Individui**: `10.7`

### Settore
- **US (Unità Stratigrafica)**: `2.21`
- **TMA (Materiali Archeologici)**: `10.15`

### Altri codici TMA rilevanti
- **Località**: `10.3`
- **Categoria**: per materiali
- **Classe**: per materiali
- **Precisazione tipologica**: per materiali
- **Definizione**: per materiali

## Note importanti

1. I codici sono diversi tra le tabelle US e TMA
2. Quando si sincronizzano aree e settori, bisogna usare il codice corretto in base alla tabella di origine
3. Il thesaurus TMA usa principalmente i codici della serie 10.x
4. Il thesaurus US usa principalmente i codici della serie 2.x

## Sincronizzazione

La sincronizzazione ora tiene conto di questi codici diversi:
- Le aree da us_table vengono salvate con tipologia_sigla = '2.43'
- Le aree da tma e altre tabelle vengono salvate con tipologia_sigla = '10.7'
- I settori da us_table vengono salvati con tipologia_sigla = '2.21'
- I settori da tma vengono salvati con tipologia_sigla = '10.15'