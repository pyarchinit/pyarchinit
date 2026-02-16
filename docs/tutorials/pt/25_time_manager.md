# Tutorial 25: Time Manager (Controlador Temporal SIG)

## Introducao

O **Time Manager** (Controlador Temporal SIG) e uma ferramenta avancada para visualizar a sequencia estratigrafica ao longo do tempo. Permite "navegar" pelos niveis estratigraficos utilizando um controlo temporal, apresentando progressivamente as UE da mais recente a mais antiga.

### Funcionalidades Principais

- Visualizacao progressiva dos niveis estratigraficos
- Controlo por dial/barra deslizante
- Modo cumulativo ou nivel individual
- Geracao automatica de imagens/video
- Integracao com Harris Matrix

## Acesso

### Pelo Menu
**PyArchInit** > **Time Manager**

### Pre-requisitos

- Camada com campo `order_layer` (indice estratigrafico)
- UE com order_layer preenchido
- Camadas carregadas no QGIS

## Interface

### Painel Principal

```
+--------------------------------------------------+
|         Gestao Temporal SIG                       |
+--------------------------------------------------+
| Camadas disponiveis:                              |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] outra_camada                                 |
+--------------------------------------------------+
|              [Dial Circular]                      |
|                   /  \                            |
|                  /    \                            |
|                 /______\                           |
|                                                   |
|         Nivel: [SpinBox: 1-N]                    |
+--------------------------------------------------+
| [x] Modo Cumulativo (mostrar <= nivel)           |
+--------------------------------------------------+
| [ ] Mostrar Matrix    [Parar] [Gerar Video]      |
+--------------------------------------------------+
| [Pre-visualizacao Matrix/Imagem]                  |
+--------------------------------------------------+
```

### Controlos

| Controlo | Funcao |
|----------|--------|
| Caixa de selecao da camada | Selecionar camadas a controlar |
| Dial | Navegar entre niveis (rotacao) |
| SpinBox | Entrada direta do nivel |
| Modo Cumulativo | Mostrar todos os niveis ate ao selecionado |
| Mostrar Matrix | Apresentar Harris Matrix sincronizada |

## Campo order_layer

### O Que e o order_layer?

O campo `order_layer` define a ordem de apresentacao estratigrafica:
- **1** = Nivel mais recente (superficie)
- **N** = Nivel mais antigo (profundidade)

### Preencher o order_layer

No Formulario UE, campo **"Indice Estratigrafico"**:
1. Atribuir valores crescentes a partir da superficie
2. UE contemporaneas podem ter o mesmo valor
3. Seguir a sequencia da Matrix

### Exemplo

| UE | order_layer | Descricao |
|----|-------------|-----------|
| UE001 | 1 | Humus superficial |
| UE002 | 2 | Camada de lavoura |
| UE003 | 3 | Derrube |
| UE004 | 4 | Piso de utilizacao |
| UE005 | 5 | Fundacao |

## Modos de Visualizacao

### Modo de Nivel Individual

Caixa de selecao **NAO** ativa:
- Mostra APENAS as UE do nivel selecionado
- Util para isolar camadas individuais
- Visualizacao em "fatia"

### Modo Cumulativo

Caixa de selecao **ATIVA**:
- Mostra todas as UE ate ao nivel selecionado
- Simula escavacao progressiva
- Visualizacao mais realista

## Integracao com Matrix

### Visualizacao Sincronizada

Com a caixa de selecao **"Mostrar Matrix"** ativa:
- Harris Matrix aparece no painel
- Atualiza em sincronia com o nivel
- Destaca as UE do nivel atual

### Geracao de Imagens

O Time Manager pode gerar:
- Captura de ecra para cada nivel
- Sequencia de imagens
- Video time-lapse

## Geracao de Video/Imagem

### Processo

1. Selecionar camadas a incluir
2. Configurar intervalo de niveis (min-max)
3. Clicar em **"Gerar Video"**
4. Aguardar processamento
5. Saida na pasta designada

### Resultado

- Imagens PNG para cada nivel
- Opcional: video MP4 compilado

## Fluxo de Trabalho Tipico

### 1. Preparacao

```
1. Abrir projeto QGIS com camadas de UE
2. Verificar que o order_layer esta preenchido
3. Abrir o Time Manager
```

### 2. Selecao de Camadas

```
1. Selecionar camadas a controlar
2. Geralmente: pyunitastratigrafiche e/ou _usm
```

### 3. Navegacao

```
1. Utilizar dial ou spinbox
2. Observar alteracao da visualizacao
3. Ativar/desativar modo cumulativo
```

### 4. Documentacao

```
1. Ativar "Mostrar Matrix"
2. Gerar capturas de ecra significativas
3. Opcional: gerar video
```

## Modelos de Composicao

### Carregamento de Modelos

O Time Manager suporta modelos QGIS para:
- Composicoes de impressao personalizadas
- Cabecalhos e legendas
- Formatos padrao

### Modelos Disponiveis

Na pasta `resources/templates/`:
- Modelo base
- Modelo com Matrix
- Modelo para video

## Boas Praticas

### 1. order_layer

- Preencher ANTES de utilizar o Time Manager
- Utilizar valores consecutivos
- UE contemporaneas = mesmo valor

### 2. Visualizacao

- Comecar pelo nivel 1 (superficie)
- Prosseguir em ordem crescente
- Utilizar modo cumulativo para apresentacoes

### 3. Documentacao

- Capturar ecras em niveis significativos
- Documentar transicoes de fase
- Gerar video para relatorios

## Resolucao de Problemas

### Camadas Nao Visiveis na Lista

**Causa**: Camada sem campo order_layer

**Solucao**:
- Adicionar campo order_layer a camada
- Preencher com valores adequados

### Sem Alteracao Visual

**Causas**:
- order_layer nao preenchido
- Filtro nao aplicado

**Solucoes**:
- Verificar valores do order_layer nas UE
- Confirmar que a camada esta selecionada

### Dial Nao Responde

**Causa**: Nenhuma camada selecionada

**Solucao**: Selecionar pelo menos uma camada da lista

## Referencias

### Ficheiros Fonte
- `tabs/Gis_Time_controller.py` - Interface principal
- `gui/ui/Gis_Time_controller.ui` - Disposicao da UI

### Campo da Base de Dados
- `us_table.order_layer` - Indice estratigrafico

---

## Tutorial em Video

### Time Manager
`[Placeholder: video_time_manager.mp4]`

**Conteudos**:
- Configuracao do order_layer
- Navegacao temporal
- Geracao de video
- Integracao com Matrix

**Duracao prevista**: 15-18 minutos

---

*Ultima atualizacao: janeiro de 2026*

---

## Animacao Interativa

Explore a animacao interativa para saber mais sobre este topico.

[Abrir Animacao Interativa](../../animations/pyarchinit_timemanager_animation.html)
