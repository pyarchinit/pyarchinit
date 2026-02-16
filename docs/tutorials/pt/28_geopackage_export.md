# Tutorial 28: Exportacao GeoPackage

## Introducao

A funcao de **Exportacao GeoPackage** permite empacotar camadas vetoriais e raster do PyArchInit num unico ficheiro GeoPackage (.gpkg). Este formato e ideal para partilha, arquivo e portabilidade de dados.

### Vantagens do GeoPackage

| Aspeto | Vantagem |
|--------|----------|
| Ficheiro unico | Todos os dados num ficheiro |
| Portabilidade | Partilha facil |
| Norma OGC | Compatibilidade universal |
| Multicamada | Vetores e rasters juntos |
| Baseado em SQLite | Leve e rapido |

## Acesso

### Pelo Menu
**PyArchInit** > **Empacotar para GeoPackage**

## Interface

### Painel de Exportacao

```
+--------------------------------------------------+
|        Importar para GeoPackage                   |
+--------------------------------------------------+
| Destino:                                          |
|   [____________________________] [Procurar]      |
+--------------------------------------------------+
| [Exportar Camadas Vetoriais]                     |
| [Exportar Camadas Raster]                        |
+--------------------------------------------------+
```

## Procedimento

### Exportacao de Camadas Vetoriais

1. Selecionar camadas a exportar no painel de Camadas do QGIS
2. Abrir ferramenta de Exportacao GeoPackage
3. Especificar caminho e nome do ficheiro de destino
4. Clicar em **"Exportar Camadas Vetoriais"**

### Exportacao de Camadas Raster

1. Selecionar camadas raster no painel de Camadas
2. Especificar destino (mesmo ficheiro ou novo)
3. Clicar em **"Exportar Camadas Raster"**

### Exportacao Combinada

Para incluir vetores e rasters no mesmo GeoPackage:
1. Primeiro exportar vetores
2. Depois exportar rasters para o mesmo ficheiro
3. O sistema adiciona camadas ao GeoPackage existente

## Selecao de Camadas

### Metodo

1. No painel de Camadas do QGIS, selecionar camadas pretendidas
   - Ctrl+clique para selecao multipla
   - Shift+clique para intervalo
2. Abrir Exportacao GeoPackage
3. As camadas selecionadas serao exportadas

### Camadas Recomendadas

| Camada | Tipo | Notas |
|--------|------|-------|
| pyunitastratigrafiche | Vetorial | UE de deposito |
| pyunitastratigrafiche_usm | Vetorial | UE de muro |
| pyarchinit_quote | Vetorial | Pontos de cota |
| pyarchinit_siti | Vetorial | Sitios |
| Ortofoto | Raster | Ortofoto da escavacao |

## Resultado

### Estrutura do GeoPackage

```
output.gpkg
+-- pyunitastratigrafiche (vetorial)
+-- pyunitastratigrafiche_usm (vetorial)
+-- pyarchinit_quote (vetorial)
+-- ortofoto (raster)
```

### Caminho Predefinido

```
~/pyarchinit/pyarchinit_DB_folder/
```

## Opcoes de Exportacao

### Camadas Vetoriais

- Mantem geometrias originais
- Preserva todos os atributos
- Converte automaticamente nomes com espacos (utiliza sublinhado)

### Camadas Raster

- Suporta formatos comuns (GeoTIFF, etc.)
- Mantem georreferenciacao
- Preserva sistema de referencia de coordenadas

## Utilizacoes Tipicas

### Partilha de Projeto

```
1. Selecionar todas as camadas do projeto
2. Exportar para GeoPackage
3. Partilhar o ficheiro .gpkg
4. O destinatario abre diretamente no QGIS
```

### Arquivo de Campanha

```
1. No final da campanha, selecionar camadas finais
2. Exportar para GeoPackage com data
3. Arquivar com documentacao
```

### Copia de Seguranca SIG

```
1. Exportar periodicamente o estado atual
2. Manter versoes datadas
3. Utilizar para recuperacao de desastres
```

## Boas Praticas

### 1. Antes da Exportacao

- Verificar completude das camadas
- Verificar sistema de referencia de coordenadas
- Guardar projeto QGIS

### 2. Nomenclatura

- Utilizar nomes de ficheiro descritivos
- Incluir data no nome
- Evitar caracteres especiais

### 3. Verificacao

- Abrir o GeoPackage criado
- Verificar que todas as camadas estao presentes
- Confirmar atributos

## Resolucao de Problemas

### Exportacao Falhou

**Causas**:
- Camada invalida
- Caminho sem permissao de escrita
- Espaco em disco insuficiente

**Solucoes**:
- Verificar validade da camada
- Verificar permissoes da pasta
- Libertar espaco em disco

### Camadas em Falta

**Causa**: Camada nao selecionada

**Solucao**: Verificar selecao no painel de Camadas

### Raster Nao Exportado

**Causas**:
- Formato nao suportado
- Ficheiro de origem nao acessivel

**Solucoes**:
- Converter raster para GeoTIFF
- Verificar caminho do ficheiro de origem

## Referencias

### Ficheiros Fonte
- `tabs/gpkg_export.py` - Interface de exportacao
- `gui/ui/gpkg_export.ui` - Disposicao da UI

### Documentacao
- [Norma GeoPackage](https://www.geopackage.org/)
- [Suporte GeoPackage QGIS](https://docs.qgis.org/)

---

## Tutorial em Video

### Exportacao GeoPackage
`[Placeholder: video_geopackage.mp4]`

**Conteudos**:
- Selecao de camadas
- Exportacao vetorial e raster
- Verificacao do resultado
- Boas praticas

**Duracao prevista**: 8-10 minutos

---

*Ultima atualizacao: janeiro de 2026*
