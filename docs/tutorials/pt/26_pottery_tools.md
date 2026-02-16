# Tutorial 26: Pottery Tools

## Introducao

**Pottery Tools** e um modulo avancado para processamento de imagens de ceramica. Oferece ferramentas para extrair imagens de PDFs, gerar composicoes de estampas, processar desenhos com AI (PotteryInk) e outras funcionalidades especializadas para documentacao ceramica.

### Funcionalidades Principais

- Extracao de imagens de PDFs
- Geracao de composicoes de estampas de ceramica
- Processamento de imagens com AI
- Conversao de formatos de desenho
- Integracao com o Formulario de Ceramica

## Acesso

### Pelo Menu
**PyArchInit** > **Pottery Tools**

## Interface

### Painel Principal

```
+--------------------------------------------------+
|              Pottery Tools                        |
+--------------------------------------------------+
| [Separador: Extracao PDF]                        |
| [Separador: Gerador de Composicao]               |
| [Separador: Processamento de Imagem]             |
| [Separador: PotteryInk AI]                       |
+--------------------------------------------------+
| [Barra de Progresso]                             |
| [Mensagens de Registo]                           |
+--------------------------------------------------+
```

## Separador de Extracao PDF

### Funcao

Extrai automaticamente imagens de documentos PDF contendo estampas de ceramica.

### Utilizacao

1. Selecionar ficheiro PDF de origem
2. Especificar pasta de destino
3. Clicar em **"Extrair"**
4. As imagens sao guardadas como ficheiros separados

### Opcoes

| Opcao | Descricao |
|-------|-----------|
| DPI | Resolucao de extracao (150-600) |
| Formato | PNG, JPG, TIFF |
| Paginas | Todas ou intervalo especifico |

## Separador do Gerador de Composicao

### Funcao

Gera automaticamente estampas de ceramica com composicao padronizada.

### Tipos de Composicao

| Composicao | Descricao |
|------------|-----------|
| Grelha | Imagens em grelha regular |
| Sequencia | Imagens em sequencia numerada |
| Comparacao | Composicao para comparacao |
| Catalogo | Formato de catalogo com legendas |

### Utilizacao

1. Selecionar imagens a incluir
2. Escolher tipo de composicao
3. Configurar parametros (dimensoes, margens)
4. Gerar estampa

### Parametros de Composicao

| Parametro | Descricao |
|-----------|-----------|
| Tamanho da pagina | A4, A3, Personalizado |
| Orientacao | Retrato, Paisagem |
| Margens | Espacamento das bordas |
| Espacamento | Distancia entre imagens |
| Legendas | Texto sob as imagens |

## Separador de Processamento de Imagem

### Funcao

Processamento em lote de imagens de ceramica.

### Operacoes Disponiveis

| Operacao | Descricao |
|----------|-----------|
| Redimensionar | Escalar imagens |
| Recortar | Recorte automatico/manual |
| Rodar | Rotacao em graus |
| Converter | Alteracao de formato |
| Otimizar | Compressao de qualidade |

### Processamento em Lote

1. Selecionar pasta de origem
2. Escolher operacoes a aplicar
3. Especificar destino
4. Executar processamento

## Separador PotteryInk AI

### Funcao

Utiliza inteligencia artificial para:
- Conversao de fotografia para desenho tecnico
- Reconhecimento de formas ceramicas
- Sugestoes de classificacao
- Medicao automatica

### Requisitos

- Ambiente virtual Python configurado
- Modelos AI descarregados (YOLO, etc.)
- GPU recomendada (mas nao obrigatoria)

### Utilizacao

1. Carregar imagem de ceramica
2. Selecionar tipo de processamento
3. Aguardar processamento AI
4. Verificar e guardar resultado

### Tipos de Processamento AI

| Tipo | Descricao |
|------|-----------|
| Conversao Ink | Converte fotografia em desenho tecnico |
| Detecao de Forma | Reconhece forma do recipiente |
| Extracao de Perfil | Extrai perfil ceramico |
| Analise de Decoracao | Analisa decoracoes |

## Ambiente Virtual

### Configuracao Automatica

No primeiro arranque, o Pottery Tools:
1. Cria ambiente virtual em `~/pyarchinit/bin/pottery_venv/`
2. Instala dependencias necessarias
3. Descarrega modelos AI (se necessario)

### Dependencias

- PyTorch
- Ultralytics (YOLO)
- OpenCV
- Pillow

### Verificacao da Instalacao

O registo mostra o estado:
```
Ambiente virtual criado
Dependencias instaladas
Modelos descarregados
Pottery Tools inicializado com sucesso!
```

## Integracao com Base de Dados

### Associacao ao Formulario de Ceramica

As imagens processadas podem ser:
- Automaticamente associadas a registos de Ceramica
- Guardadas com metadados adequados
- Organizadas por sitio/inventario

## Boas Praticas

### 1. Qualidade da Imagem de Entrada

- Resolucao minima: 300 DPI
- Iluminacao uniforme
- Fundo neutro (branco/cinzento)
- Escala metrica visivel

### 2. Processamento AI

- Verificar sempre os resultados da AI
- Corrigir manualmente se necessario
- Guardar originais e processados

### 3. Organizacao do Resultado

- Utilizar nomenclatura consistente
- Organizar por sitio/campanha
- Manter rastreabilidade

## Resolucao de Problemas

### Ambiente Virtual Nao Criado

**Causas**:
- Python nao encontrado
- Permissoes insuficientes

**Solucoes**:
- Verificar instalacao do Python
- Verificar permissoes da pasta

### Processamento AI Lento

**Causas**:
- GPU nao disponivel
- Imagens demasiado grandes

**Solucoes**:
- Reduzir tamanho da imagem
- Utilizar CPU (mais lento mas funciona)

### Extracao PDF Falhou

**Causas**:
- PDF protegido
- Formato nao suportado

**Solucoes**:
- Verificar protecao do PDF
- Tentar com outro software de PDF

## Referencias

### Ficheiros Fonte
- `tabs/Pottery_tools.py` - Interface principal
- `modules/utility/pottery_utilities.py` - Utilitarios de processamento
- `gui/ui/Pottery_tools.ui` - Disposicao da UI

### Pastas
- `~/pyarchinit/bin/pottery_venv/` - Ambiente virtual
- `~/pyarchinit/models/` - Modelos AI

---

## Tutorial em Video

### Pottery Tools Completo
`[Placeholder: video_pottery_tools.mp4]`

**Conteudos**:
- Extracao PDF
- Geracao de composicao
- Processamento AI
- Integracao com base de dados

**Duracao prevista**: 20-25 minutos

---

*Ultima atualizacao: janeiro de 2026*
