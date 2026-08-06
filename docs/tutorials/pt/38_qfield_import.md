# Tutorial 38: Importar do QField (GPKG)

## Introdução

A função **Importar do QField (GPKG)** traz para o pyArchInit os dados recolhidos
no campo com o **QField** através do plugin companheiro **pyarchinit-qfield**. O
comando lê os GeoPackages (`.gpkg`) do projeto QField e as fotografias tiradas no
campo, e **acrescenta** os registos à base de dados do pyArchInit sem duplicar as
UE e os materiais já existentes: nos registos existentes preenche **apenas os
campos vazios**, sem nunca sobrescrever os valores já presentes.

O fluxo foi pensado para ser **seguro**: primeiro executa-se uma **Pré-visualização
(simulação)** que simula tudo sem escrever nada e, depois — só após confirmação —
lança-se a **Importação** real numa única transação.

> Pré-requisito: os dados têm de ter sido recolhidos no campo com o **QField**
> usando o plugin companheiro **pyarchinit-qfield**.

---

## 1. Pré-requisitos

- Dados recolhidos no campo com o **QField** através do plugin
  **pyarchinit-qfield**.
- A pasta do projeto QField contém os ficheiros **`.gpkg`** e as fotos em
  **`DCIM/pyarchinit`**.
- Uma base de dados pyArchInit configurada (SQLite/Spatialite ou
  PostgreSQL/PostGIS): a BD é **resolvida automaticamente** a partir da
  configuração do plugin.

---

## 2. Abrir a caixa de diálogo

O comando pode ser aberto de **duas formas**:

1. **Menu**: **Plugin → pyArchInit - Archaeological GIS Tools → Importa da
   QField (GPKG)**.
2. **Barra de ferramentas** (novidade): na barra de ferramentas do pyArchInit,
   abra o **botão pendente das ferramentas de análise** — o mesmo que reúne
   GeoArchaeo, MoveCost, Palimpsest e outras ferramentas — e escolha **Importa
   da QField (GPKG)**. A entrada reconhece-se pelo **novo ícone dedicado**: um
   mosaico verde arredondado ao estilo QField com um marcador branco a descer
   para um tabuleiro de importação.

Em ambos os casos abre-se a caixa de diálogo *Importar do QField*: o QGIS
**não bloqueia** durante a operação porque a cópia das fotos e o acesso ao
WebDAV correm num fio separado.

---

## 3. Selecionar a origem: pasta ou arquivo ZIP

1. Clique em **Procurar…** e escolha a **pasta do projeto QField**, ou
   clique em **Arquivo ZIP…** e escolha um arquivo **`.zip`** do projeto
   QField (o seletor de ficheiros filtra por `*.zip`). Em ambos os casos, o
   caminho escolhido aparece no mesmo campo de origem.
2. Se escolher uma pasta, a caixa de diálogo **analisa os GeoPackages** e
   preenche automaticamente a lista pendente **Sítio** com os sítios
   encontrados.
3. Se escolher um arquivo ZIP, este é **extraído automaticamente** para uma
   pasta temporária e a lista pendente **Sítio** volta a **Todos os sítios**
   (não é feita nenhuma pré-análise de sítios a partir de um zip): a
   importação (Pré-visualização/simulação ou Importação, incluindo fotos e
   miniaturas) é executada sobre a árvore extraída, e a pasta temporária é
   **removida automaticamente** no final da operação, mesmo em caso de erro.
4. Escolha um sítio específico ou deixe **Todos os sítios** para importar
   tudo.

> Enquanto uma importação está em curso, tanto **Procurar…** como
> **Arquivo ZIP…** ficam **desativados**, tal como todos os outros
> controlos da caixa de diálogo.

> Se o arquivo escolhido estiver **corrompido ou for inválido**, é mostrado
> um erro claro: **"Archivio ZIP non valido o corrotto: …"**. Se o zip não
> contiver nenhum ficheiro **`.gpkg`**, é mostrado em vez disso o erro
> habitual de "nenhuma camada encontrada".

---

## 4. Opções de importação

| Opção | Significado |
|---|---|
| **SRID (vazio = do GPKG)** | sistema de referência; deixe vazio para o ler do GeoPackage |
| **Destino das fotos** | pré-preenchido com a pasta de media configurada (local ou WebDAV) |
| **Desduplicar geometrias** | evita reinserir geometrias idênticas já presentes |
| **Copiar fotos** | copia as fotos para o backend de media |
| **Gerar miniaturas** | cria automaticamente as miniaturas das fotos |

As três caixas estão **ativadas por predefinição**.

---

## 5. Pré-visualização (simulação)

Clique em **Pré-visualização (simulação)**: toda a importação corre em
**simulação**, **sem escrever nada** na base de dados. O registo mostra:

- quantas **UE**, **materiais**, **geometrias**, **pontos de cota**, **fotos** e
  **ligações** seriam importados;
- exatamente **quais campos vazios** dos registos existentes seriam preenchidos.

É o passo a usar sempre para verificar o resultado antes de escrever.

---

## 6. Importar

Clique em **Importar** (é pedida uma **confirmação**). A operação:

- **acrescenta** os registos numa **única transação**;
- **não duplica** as UE e os materiais existentes: preenche **apenas os seus
  campos vazios**, sem nunca sobrescrever os valores já presentes;
- **copia as fotos** para o backend de media e **gera as suas miniaturas**
  automaticamente;
- atribui aos registos importados um **`node_uuid`** e marca-os com
  **`created_by = 'qfield_import'`**.

---

## 7. Após a importação

Verifique as **relações estratigráficas** das UE importadas: **não são deduzidas
automaticamente** e devem ser completadas à mão na ficha UE.

---

## 8. Alternativa por linha de comandos (CLI)

Para usos avançados ou sem interface está disponível um script CLI. A **simulação
é o comportamento predefinido**; acrescente `--apply` para escrever realmente.
O parâmetro `--qfield-dir` aceita tanto a **pasta do projeto** como um
arquivo **`.zip`**: se apontar para um zip, este é extraído automaticamente
para uma pasta temporária, removida no final da execução. Uma origem
inexistente termina o script com o erro **"Sorgente non trovata (cartella o
archivio .zip): …"**.

```bash
# Pré-visualização (simulação, predefinição) a partir de uma pasta
python3 scripts/import_qfield.py --qfield-dir <pasta>

# Pré-visualização (simulação, predefinição) a partir de um arquivo ZIP
python3 scripts/import_qfield.py --qfield-dir <arquivo.zip>

# Importação real
python3 scripts/import_qfield.py --qfield-dir <pasta> --apply
```

---

*Documentação PyArchInit — Julho 2026*
