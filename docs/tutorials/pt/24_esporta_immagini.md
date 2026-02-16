# Tutorial 24: Exportar Imagens

## Introducao

A funcao **Exportar Imagens** permite a exportacao em lote de imagens associadas a registos arqueologicos, organizando-as automaticamente em pastas por periodo, fase e tipo de entidade.

## Acesso

### Pelo Menu
**PyArchInit** > **Exportar Imagens**

## Interface

### Painel de Exportacao

```
+--------------------------------------------------+
|           Exportar Imagens                        |
+--------------------------------------------------+
| Sitio: [ComboBox selecao de sitio]               |
| Ano: [ComboBox ano de escavacao]                 |
+--------------------------------------------------+
| Tipo de Exportacao:                               |
|   [o] Todas as imagens                           |
|   [ ] Apenas UE                                  |
|   [ ] Apenas achados                             |
|   [ ] Apenas ceramica                            |
+--------------------------------------------------+
| [Abrir Pasta]           [Exportar]               |
+--------------------------------------------------+
```

### Opcoes de Exportacao

| Opcao | Descricao |
|-------|-----------|
| Todas as imagens | Exportar todo o material fotografico |
| Apenas UE | Exportar apenas imagens associadas a UE |
| Apenas achados | Exportar apenas imagens de achados |
| Apenas ceramica | Exportar apenas imagens de ceramica |

## Estrutura de Saida

### Organizacao de Pastas

A exportacao cria uma estrutura hierarquica:

```
pyarchinit_image_export/
+-- [Nome do Sitio] - Todas as imagens/
    +-- Periodo - 1/
    |   +-- Fase - 1/
    |   |   +-- UE_001/
    |   |   |   +-- foto_001.jpg
    |   |   |   +-- foto_002.jpg
    |   |   +-- UE_002/
    |   |       +-- foto_003.jpg
    |   +-- Fase - 2/
    |       +-- UE_003/
    |           +-- foto_004.jpg
    +-- Periodo - 2/
        +-- ...
```

### Convencao de Nomenclatura

Os ficheiros mantem o nome original, organizados por:
1. **Periodo** - Periodo cronologico inicial
2. **Fase** - Fase cronologica inicial
3. **Entidade** - UE, Achado, etc.

## Processo de Exportacao

### Passo 1: Selecao de Parametros

1. Selecionar **Sitio** no ComboBox
2. Selecionar **Ano** (opcional)
3. Escolher **Tipo de exportacao**

### Passo 2: Execucao

1. Clicar em **"Exportar"**
2. Aguardar conclusao
3. Mensagem de confirmacao

### Passo 3: Verificacao

1. Clicar em **"Abrir Pasta"**
2. Verificar estrutura criada
3. Confirmar completude

## Pasta de Saida

### Caminho Padrao

```
~/pyarchinit/pyarchinit_image_export/
```

### Conteudos

- Pastas organizadas por sitio
- Subpastas por periodo/fase
- Imagens originais (sem redimensionamento)

## Filtro por Ano

O **Ano** no ComboBox permite:
- Exportar apenas imagens de uma campanha especifica
- Organizar exportacao por ano de escavacao
- Reduzir tamanho da exportacao

## Boas Praticas

### 1. Antes da Exportacao

- Verificar associacoes imagem-entidade
- Verificar periodizacao das UE
- Garantir espaco em disco suficiente

### 2. Durante a Exportacao

- Nao interromper o processo
- Aguardar mensagem de conclusao

### 3. Apos a Exportacao

- Verificar estrutura de pastas
- Confirmar completude das imagens
- Criar copia de seguranca se necessario

## Utilizacoes Tipicas

### Preparacao de Relatorio

```
1. Selecionar sitio
2. Exportar todas as imagens
3. Utilizar estrutura para capitulos do relatorio
```

### Entrega a Superintendencia

```
1. Selecionar sitio e ano
2. Exportar por tipo necessario
3. Organizar segundo normas ministeriais
```

### Copia de Seguranca de Campanha

```
1. No final da campanha, exportar tudo
2. Arquivar em armazenamento externo
3. Verificar integridade
```

## Resolucao de Problemas

### Exportacao Incompleta

**Causas**:
- Imagens nao associadas
- Caminhos de ficheiros incorretos

**Solucoes**:
- Verificar associacoes no Gestor de Media
- Confirmar existencia dos ficheiros de origem

### Estrutura Incorreta

**Causas**:
- Periodizacao em falta
- UE sem periodo/fase

**Solucoes**:
- Preencher periodizacao das UE
- Atribuir periodo/fase a todas as UE

## Referencias

### Ficheiros Fonte
- `tabs/Images_directory_export.py` - Interface de exportacao
- `gui/ui/Images_directory_export.ui` - Disposicao da UI

### Pastas
- `~/pyarchinit/pyarchinit_image_export/` - Saida da exportacao

---

## Tutorial em Video

### Exportacao de Imagens
`[Placeholder: video_export_immagini.mp4]`

**Conteudos**:
- Configuracao da exportacao
- Estrutura de saida
- Organizacao do arquivo

**Duracao prevista**: 10-12 minutos

---

*Ultima atualizacao: janeiro de 2026*

---

## Animacao Interativa

Explore a animacao interativa para saber mais sobre este topico.

[Abrir Animacao Interativa](../../animations/pyarchinit_image_export_animation.html)
