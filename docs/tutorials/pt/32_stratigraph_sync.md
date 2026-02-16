# PyArchInit - StratiGraph: Painel de Sincronizacao

## Indice
1. [Introducao](#introducao)
2. [Aceder ao Painel](#aceder-ao-painel)
3. [Compreender a Interface](#compreender-a-interface)
4. [Exportar Bundles](#exportar-bundles)
5. [Sincronizacao](#sincronizacao)
6. [Gestao da Fila](#gestao-da-fila)
7. [Configuracao](#configuracao)
8. [Resolucao de Problemas](#resolucao-de-problemas)
9. [Perguntas Frequentes](#perguntas-frequentes)

---

## Introducao

A partir da versao **5.0.2-alpha**, o PyArchInit inclui um painel **StratiGraph Sync** que permite a sincronizacao de dados offline-first com o StratiGraph Knowledge Graph. Este painel faz parte do projeto europeu **StratiGraph** (Horizon Europe) e implementa o fluxo de trabalho offline-first: trabalha-se localmente sem Internet, exportam-se bundles quando prontos, e o sistema sincroniza automaticamente quando a conectividade e restabelecida.

<!-- VIDEO: Introducao ao StratiGraph Sync -->
> **Tutorial em Video**: [Inserir ligacao do video de introducao StratiGraph Sync]

### Visao Geral do Fluxo de Trabalho

```
1. Trabalhar offline     2. Exportar Bundle     3. Sincronizacao auto
   (OFFLINE_EDITING)       (LOCAL_EXPORT)        (QUEUED_FOR_SYNC)
        |                      |                      |
   Entrada de dados      Exportar + Validar      Carregar quando online
   normal no PyArchInit  + Colocar em fila       com tentativa automatica
```

---

## Aceder ao Painel

O painel StratiGraph Sync esta oculto por predefinicao e pode ser alternado atraves de um botao na barra de ferramentas.

### Pela Barra de Ferramentas

1. Procurar o botao **StratiGraph Sync** na barra de ferramentas do PyArchInit -- tem um icone verde com setas de sincronizacao e a letra "S"
2. Clicar no botao para **mostrar** o painel (e um botao de alternancia assinalavel)
3. Clicar novamente no botao para **ocultar** o painel

O painel aparece como um **widget acoplavel a esquerda** na interface do QGIS. Pode arrasta-lo e reposiciona-lo como qualquer painel acoplavel do QGIS.

<!-- IMAGEM: Botao da barra de ferramentas para StratiGraph Sync -->
> **Fig. 1**: O botao StratiGraph Sync na barra de ferramentas (icone verde com setas de sincronizacao e "S")

<!-- IMAGEM: Painel acoplado no lado esquerdo do QGIS -->
> **Fig. 2**: O painel StratiGraph Sync acoplado no lado esquerdo da janela do QGIS

---

## Compreender a Interface

O painel StratiGraph Sync esta dividido em varias seccoes, de cima para baixo.

### Indicador de Estado

O **indicador de estado** no topo do painel mostra o estado atual de sincronizacao dos dados. Os estados possiveis sao:

| Estado | Icone | Descricao |
|--------|-------|-----------|
| **OFFLINE_EDITING** | Lapis | Esta a trabalhar localmente, a editar dados normalmente |
| **LOCAL_EXPORT** | Pacote | Um bundle esta a ser exportado a partir dos dados locais |
| **LOCAL_VALIDATION** | Marca de verificacao | O bundle exportado esta a ser validado |
| **QUEUED_FOR_SYNC** | Relogio | O bundle foi validado e esta a aguardar carregamento |
| **SYNC_SUCCESS** | Circulo verde | A sincronizacao mais recente foi concluida com sucesso |
| **SYNC_FAILED** | Circulo vermelho | A tentativa de sincronizacao mais recente falhou |

### Indicador de Ligacao

Abaixo do indicador de estado, o **indicador de ligacao** mostra se o sistema consegue contactar o servidor StratiGraph:

| Estado | Significado |
|--------|------------|
| **Online** | O ponto de verificacao de saude esta acessivel; a sincronizacao automatica esta ativa |
| **Offline** | O ponto de verificacao de saude nao esta acessivel; os bundles serao colocados em fila |

O sistema verifica automaticamente a conectividade a cada **30 segundos** (configuravel).

### Contador da Fila

O **contador da fila** apresenta dois numeros:

- **Bundles pendentes**: Numero de bundles a aguardar carregamento
- **Bundles falhados**: Numero de bundles cujo carregamento falhou (serao tentados automaticamente)

### Ultima Sincronizacao

Mostra a **marca temporal** e o **resultado** (sucesso ou falha) da tentativa de sincronizacao mais recente.

### Botoes de Acao

| Botao | Acao |
|-------|------|
| **Exportar Bundle** | Cria um bundle a partir dos dados locais, valida-o e adiciona-o a fila de sincronizacao |
| **Sincronizar Agora** | Forca uma tentativa de sincronizacao imediata (apenas disponivel quando online) |
| **Fila...** | Abre o dialogo de gestao da fila mostrando todas as entradas |

### Registo de Atividade

Na parte inferior do painel, um **registo de atividade** com deslocamento apresenta entradas com marca temporal da atividade recente, incluindo alteracoes de estado, exportacoes, validacoes e tentativas de sincronizacao.

<!-- IMAGEM: Painel completo com todas as seccoes anotadas -->
> **Fig. 3**: O painel StratiGraph Sync completo com todas as seccoes identificadas

---

## Exportar Bundles

Exportar um bundle empacota os dados arqueologicos locais num formato estruturado pronto para carregamento para o StratiGraph Knowledge Graph.

### Exportacao Passo a Passo

1. Certificar-se de que guardou todo o trabalho atual no PyArchInit
2. Abrir o painel StratiGraph Sync (se ainda nao estiver visivel)
3. Clicar no botao **Exportar Bundle**
4. O sistema executa tres operacoes automaticamente:
   - **Exportar**: Os dados locais sao empacotados num ficheiro bundle
   - **Validar**: O bundle e verificado quanto a completude e integridade dos dados
   - **Colocar em fila**: O bundle validado e adicionado a fila de sincronizacao
5. Observar o **indicador de estado** transitar por: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. O **registo de atividade** regista cada passo com uma marca temporal

### O Que Esta Incluido num Bundle

Um bundle contem todas as entidades arqueologicas que possuem UUIDs (consultar Tutorial 31 para detalhes sobre UUID). Cada entidade e identificada pelo seu `entity_uuid`, garantindo que o mesmo registo e sempre reconhecido no servidor.

<!-- IMAGEM: Botao Exportar Bundle e transicao de estado -->
> **Fig. 4**: Clicar em "Exportar Bundle" e observar as alteracoes de estado no painel

---

## Sincronizacao

### Sincronizacao Automatica

Quando o sistema deteta que esta **online** (a verificacao de saude e bem-sucedida), carrega automaticamente todos os bundles pendentes da fila. Nao e necessaria intervencao manual.

O processo de sincronizacao automatica:

1. A verificacao de conectividade e bem-sucedida (o ponto de verificacao de saude responde)
2. O indicador de ligacao muda para **Online**
3. Os bundles pendentes na fila sao carregados um a um
4. Os bundles carregados com sucesso sao marcados como `SYNC_SUCCESS`
5. A marca temporal e o resultado da **ultima sincronizacao** sao atualizados

### Sincronizacao Manual

Se pretender forcar uma tentativa de sincronizacao imediata:

1. Certificar-se de que o indicador de ligacao mostra **Online**
2. Clicar no botao **Sincronizar Agora**
3. O sistema tenta imediatamente carregar todos os bundles pendentes

O botao **Sincronizar Agora** so e eficaz quando o sistema esta online.

### Tentativa Automatica com Recuo Exponencial

Se um carregamento falhar, o sistema **nao desiste**. Em vez disso, tenta automaticamente com intervalos crescentes:

| Tentativa | Intervalo |
|-----------|-----------|
| 1.a tentativa | 30 segundos |
| 2.a tentativa | 60 segundos |
| 3.a tentativa | 120 segundos |
| 4.a tentativa | 5 minutos |
| 5.a tentativa | 15 minutos |

Isto evita sobrecarregar o servidor quando esta temporariamente indisponivel, garantindo a entrega eventual.

<!-- IMAGEM: Botao Sincronizar Agora e indicador de ligacao -->
> **Fig. 5**: O botao "Sincronizar Agora" e o indicador de estado da ligacao

---

## Gestao da Fila

O botao **Fila...** abre um dialogo detalhado onde pode inspecionar todos os bundles na fila de sincronizacao.

### Colunas do Dialogo da Fila

| Coluna | Descricao |
|--------|-----------|
| **ID** | Identificador unico da entrada na fila |
| **Estado** | Estado atual da entrada (pendente, a sincronizar, sucesso, falhado) |
| **Tentativas** | Numero de tentativas de carregamento efetuadas ate ao momento |
| **Criado** | Marca temporal de quando o bundle foi adicionado a fila pela primeira vez |
| **Ultimo Erro** | Mensagem de erro da tentativa falhada mais recente (vazio se sem erro) |
| **Caminho do bundle** | Caminho no sistema de ficheiros para o ficheiro bundle |

### Interpretar Entradas da Fila

- Entradas **Pendentes** estao a aguardar carregamento
- Entradas **Sucesso** foram carregadas e confirmadas pelo servidor
- Entradas **Falhadas** serao tentadas automaticamente; verificar a coluna **Ultimo Erro** para detalhes
- A contagem de **Tentativas** ajuda a compreender quantas vezes o sistema tentou carregar um bundle particular

### Armazenamento da Fila

A base de dados da fila e armazenada como um ficheiro SQLite em:

```
$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite
```

Este ficheiro persiste entre sessoes do QGIS, de modo que os bundles pendentes nao se perdem ao fechar o QGIS.

<!-- IMAGEM: Dialogo da fila mostrando varias entradas -->
> **Fig. 6**: O dialogo de gestao da fila com entradas de bundles

---

## Configuracao

### URL de Verificacao de Saude

O sistema utiliza um URL de verificacao de saude para determinar a conectividade com o servidor StratiGraph. Pode configura-lo nas definicoes do QGIS:

| Definicao | Chave | Predefinicao |
|-----------|-------|-------------|
| URL de verificacao de saude | `pyArchInit/stratigraph/health_check_url` | `http://localhost:8080/health` |

Para alterar o URL de verificacao de saude:

1. Abrir **QGIS** -> **Definicoes** -> **Opcoes** (ou utilizar a consola Python do QGIS)
2. Navegar ate as definicoes do PyArchInit ou definir atraves de:

```python
from qgis.core import QgsSettings
s = QgsSettings()
s.setValue("pyArchInit/stratigraph/health_check_url", "https://seu-servidor.exemplo.com/health")
```

### Intervalo de Verificacao

O intervalo predefinido de verificacao de conectividade e de **30 segundos**. Este tambem pode ser configurado atraves de QgsSettings.

---

## Resolucao de Problemas

### O painel nao aparece

- Certificar-se de que esta a utilizar o PyArchInit versao **5.0.2-alpha** ou posterior
- Verificar que o botao StratiGraph Sync na barra de ferramentas esta visivel
- Tentar alternar o botao desligado e ligado novamente
- Verificar **Vista** -> **Paineis** no QGIS para ver se o widget acoplavel esta listado

### O indicador de ligacao mostra sempre "Offline"

- Verificar que o servidor StratiGraph esta em execucao e acessivel
- Verificar o URL de verificacao de saude nas definicoes (predefinicao: `http://localhost:8080/health`)
- Testar o URL manualmente num navegador ou com `curl`:

```bash
curl http://localhost:8080/health
```

- Se o servidor estiver noutra maquina, certificar-se de que nao existem regras de firewall a bloquear a ligacao

### A exportacao de Bundle falha

- Certificar-se de que a base de dados esta ligada e acessivel
- Verificar que os registos tem UUIDs validos (Tutorial 31)
- Verificar o registo de atividade para mensagens de erro especificas
- Garantir espaco em disco suficiente para o ficheiro bundle

### A sincronizacao falha repetidamente

- Verificar a coluna **Ultimo Erro** no dialogo da Fila para detalhes
- Causas comuns:
  - Servidor temporariamente indisponivel (o sistema tentara automaticamente)
  - Problemas de conectividade de rede
  - Servidor rejeitou o bundle (verificar registos do servidor)
- Se um bundle falhar consistentemente apos muitas tentativas, considerar re-exporta-lo

### Problemas com a base de dados da fila

- A base de dados da fila encontra-se em `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite`
- Se estiver corrompida, pode elimina-la com seguranca -- os bundles pendentes serao perdidos, mas pode re-exporta-los
- Faca copia de seguranca deste ficheiro se precisar de preservar o estado da fila

---

## Perguntas Frequentes

### Preciso de Internet para utilizar o PyArchInit?

**Nao.** O PyArchInit e totalmente funcional offline. O painel StratiGraph Sync apenas trata da sincronizacao com o servidor StratiGraph. Pode trabalhar inteiramente offline e exportar/sincronizar quando estiver pronto.

### O que acontece se eu fechar o QGIS com bundles pendentes?

Os bundles pendentes sao guardados na base de dados da fila e estarao disponiveis quando reiniciar o QGIS. O sistema retomara a sincronizacao automaticamente quando a conectividade for restabelecida.

### Posso exportar varios bundles?

Sim. Cada vez que clicar em "Exportar Bundle", um novo bundle e criado e adicionado a fila. Varios bundles podem ser colocados em fila e serao carregados sequencialmente.

### Como sei se os meus dados foram sincronizados?

Verifique o indicador de **ultima sincronizacao** no painel para o resultado mais recente. Tambem pode abrir o dialogo **Fila...** para ver o estado de cada bundle individual.

### O StratiGraph Sync funciona com PostgreSQL e SQLite?

Sim. O sistema de sincronizacao funciona com ambos os backends de base de dados suportados pelo PyArchInit. Os bundles sao exportados num formato independente da base de dados.

### Qual e a relacao entre UUIDs e sincronizacao?

Os UUIDs (Tutorial 31) fornecem os identificadores estaveis que tornam a sincronizacao possivel. Cada entidade num bundle e identificada pelo seu UUID, permitindo que o servidor faca a correspondencia, criacao ou atualizacao correta dos registos.

---

*Documentacao PyArchInit - StratiGraph Sync*
*Versao: 5.0.2-alpha*
*Ultima atualizacao: fevereiro de 2026*

---

## Animacao Interativa

Explore a animacao interativa para saber mais sobre este topico.

[Abrir Animacao Interativa](../../animations/stratigraph_sync_animation.html)
