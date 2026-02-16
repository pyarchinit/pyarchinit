# PyArchInit - StratiGraph: Identificadores UUID

## Indice
1. [Introducao](#introducao)
2. [O Que Sao UUIDs](#o-que-sao-uuids)
3. [Porque Sao Necessarios UUIDs no StratiGraph](#porque-sao-necessarios-uuids-no-stratigraph)
4. [Como Funcionam no PyArchInit](#como-funcionam-no-pyarchinit)
5. [Tabelas com UUID](#tabelas-com-uuid)
6. [Perguntas Frequentes](#perguntas-frequentes)

---

## Introducao

A partir da versao **5.0.1-alpha**, o PyArchInit integra um sistema de **Identificadores Unicos Universais (UUID)** para todas as entidades arqueologicas. Esta funcionalidade faz parte do projeto europeu **StratiGraph** (Horizon Europe) e garante que cada registo na base de dados tem um identificador estavel e globalmente unico.

<!-- VIDEO: Introducao aos UUIDs no StratiGraph -->
> **Tutorial em Video**: [Inserir ligacao do video de introducao UUID]

---

## O Que Sao UUIDs

Um **UUID** (Universally Unique Identifier) e um codigo alfanumerico de 128 bits que identifica de forma unica uma entidade. O PyArchInit utiliza a versao 4 (UUID v4), que e gerada aleatoriamente.

### Exemplo de UUID

```
a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### Caracteristicas do UUID

| Caracteristica | Descricao |
|---------------|-----------|
| **Formato** | 32 caracteres hexadecimais separados por hifenes (8-4-4-4-12) |
| **Unicidade** | A probabilidade de colisao e estatisticamente negligenciavel (~1 em 2^122) |
| **Independencia** | Nao depende da base de dados, servidor ou momento de criacao |
| **Persistencia** | Uma vez atribuido, nunca muda |
| **Versao** | UUID v4 (gerado aleatoriamente) |

### Diferenca com IDs tradicionais

| Tipo de ID | Exemplo | Estavel entre BDs? | Globalmente unico? |
|-----------|---------|-------------------|---------------------|
| Auto-incremento (id_us) | `1`, `2`, `3`... | Nao | Nao |
| Restricao composta | `Sitio1-Area1-UE100` | Sim (semantico) | Depende |
| **UUID** | `a3f7b2c1-8d4e-...` | **Sim** | **Sim** |

Os IDs auto-incrementais (`id_us`, `id_invmat`, etc.) mudam quando se copia uma base de dados ou importam dados. Os UUIDs, por outro lado, permanecem **sempre os mesmos**, independentemente de onde os dados se encontram.

---

## Porque Sao Necessarios UUIDs no StratiGraph

O projeto StratiGraph exige que os dados arqueologicos possam ser:

### 1. Exportados para o Knowledge Graph

Os dados do PyArchInit sao exportados como **bundles** (pacotes estruturados) para um Knowledge Graph central. Cada entidade deve ter um identificador estavel para ser reconhecida no grafo.

```
Entidade local (PyArchInit)  -->  UUID  -->  Knowledge Graph (StratiGraph)
     UE 100                   a3f7b2c1...        E18 Physical Thing
```

### 2. Sincronizados entre dispositivos

Quando se trabalha no campo sem ligacao a Internet, os dados sao guardados localmente. Ao restabelecer a conectividade, os dados sao sincronizados. Os UUIDs garantem que o mesmo registo e reconhecido e atualizado (nao duplicado).

### 3. Mapeados para CIDOC-CRM

A ontologia CIDOC-CRM exige **URIs persistentes** para cada entidade. Os UUIDs sao utilizados para construir estes URIs:

```
http://pyarchinit.org/entity/a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### 4. Rastreados ao longo do tempo

Cada modificacao, exportacao ou sincronizacao refere-se ao mesmo UUID. Isto permite:
- Reconstruir o historico de um registo
- Verificar a proveniencia dos dados
- Ligar dados entre diferentes projetos

---

## Como Funcionam no PyArchInit

### Geracao automatica

Os UUIDs sao gerados **automaticamente** em dois momentos:

| Momento | Descricao |
|---------|-----------|
| **Criacao de novo registo** | Ao inserir um novo registo (p. ex., nova UE), um UUID v4 e gerado automaticamente |
| **Migracao de base de dados existente** | No primeiro arranque apos a atualizacao, todos os registos existentes sem UUID recebem um UUID gerado |

O utilizador **nao precisa de fazer nada**: os UUIDs sao inteiramente geridos pelo sistema.

### Onde se encontra o UUID

Cada tabela principal da base de dados tem uma coluna `entity_uuid` de tipo TEXT. O campo e visivel na base de dados mas nao aparece nos formularios de entrada de dados, pois e gerido internamente.

### Migracao automatica

Ao atualizar o PyArchInit para a versao 5.0.1-alpha (ou posterior):

1. **No primeiro arranque**, o sistema verifica se as tabelas tem a coluna `entity_uuid`
2. Se estiver em falta, a coluna e **adicionada automaticamente**
3. Os registos existentes sem UUID recebem um **UUID gerado**
4. Esta operacao ocorre **apenas uma vez** por sessao QGIS

O processo e transparente e nao requer intervencao manual. Funciona tanto com **PostgreSQL** como com **SQLite**.

---

## Tabelas com UUID

A coluna `entity_uuid` esta presente nas seguintes 19 tabelas:

| Tabela | Conteudo |
|--------|---------|
| `site_table` | Sitios arqueologicos |
| `us_table` | Unidades Estratigraficas (UE/UEM) |
| `inventario_materiali_table` | Inventario de achados |
| `tomba_table` | Sepulturas |
| `periodizzazione_table` | Periodizacao e fases |
| `struttura_table` | Estruturas |
| `campioni_table` | Amostras |
| `individui_table` | Individuos antropologicos |
| `pottery_table` | Ceramica |
| `media_table` | Ficheiros media |
| `media_thumb_table` | Miniaturas de media |
| `media_to_entity_table` | Relacoes media-entidade |
| `fauna_table` | Dados arqueozoologicos (Fauna) |
| `ut_table` | Unidades Topograficas |
| `tma_materiali_archeologici` | TMA Materiais Arqueologicos |
| `tma_materiali_ripetibili` | TMA Materiais Repetiveis |
| `archeozoology_table` | Arqueozoologia |
| `documentazione_table` | Documentacao |
| `inventario_lapidei_table` | Inventario Lapideo |

---

## Perguntas Frequentes

### Preciso de inserir UUIDs manualmente?

**Nao.** Os UUIDs sao gerados automaticamente pelo sistema. Nao e necessario (nem recomendado) modifica-los manualmente.

### O que acontece se eu copiar a base de dados?

Os UUIDs sao copiados juntamente com a base de dados. Este e o comportamento desejado: o mesmo registo mantem o mesmo UUID mesmo em copias diferentes da base de dados.

### Posso ver os UUIDs nos formularios?

Atualmente, os UUIDs nao sao visiveis nos formularios de entrada de dados. Sao visiveis diretamente na base de dados (p. ex., atraves do Gestor de BD no QGIS) na coluna `entity_uuid` de cada tabela.

### Os UUIDs tornam a base de dados mais lenta?

Nao. O UUID e um simples campo TEXT e nao tem impacto significativo no desempenho da base de dados.

### O que acontece as bases de dados existentes?

As bases de dados existentes sao atualizadas automaticamente no primeiro arranque: a coluna `entity_uuid` e adicionada e todos os registos existentes recebem um UUID gerado.

### Os UUIDs funcionam com PostgreSQL e SQLite?

Sim. O sistema e compativel com ambos os tipos de base de dados suportados pelo PyArchInit.

---

*Documentacao PyArchInit - StratiGraph UUID*
*Versao: 5.0.1-alpha*
*Ultima atualizacao: fevereiro de 2026*
