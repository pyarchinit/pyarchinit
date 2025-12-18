# Changelog - Branch: feature/cloudinary-integration

This document tracks all commits made on the `feature/cloudinary-integration` branch.

## Recent Commits (December 2025)

### 2025-12-18

| Commit | Description |
|--------|-------------|
| `d2f2ebbe` | **feat(image-search):** fix path construction and add goto_record functionality |
| `691d237b` | **fix(image-search):** fix database connection and add export functionality |
| `9410b458` | **feat(media):** add dedicated Image Search dialog and search buttons to forms |
| `7aebd82e` | **fix(db):** use SQLAlchemy text() for raw SQL queries |
| `621ebaf4` | **fix(media-manager):** improve error handling in advanced search |
| `5889549b` | **feat(media-manager):** add advanced image search functionality |
| `38d8b2c0` | **refactor(ui):** change mDockWidget from QgsDockWidget to QDockWidget |
| `e6fb0e62` | **chore:** add .idea to gitignore and remove from tracking |
| `493aa2ba` | **chore(ui):** update Pottery form layout |
| `93cc5746` | **fix(inventario):** remove default values from entity fields |
| `da844c17` | **fix(inventario):** add missing fields to insert_values_reperti |
| `182af98f` | **fix(inventario):** add default values to optional fields in entity class |

### 2025-12-17

| Commit | Description |
|--------|-------------|
| `8c578a95` | **feat(pdf):** add photo_id and drawing_id to inventory and pottery PDF lists |
| `89a695b1` | **fix(inventario):** use query() instead of query_all() for mapper class |
| `fbb0cb13` | **debug(inventario):** add logging to filter dialog for troubleshooting |
| `2c572c67` | **fix(inventario):** correct table mapper name in filter dialog |
| `835dc6f4` | **feat(inventario):** add filter dialog for numero_inventario, n_reperto and years |

### 2025-12-16

| Commit | Description |
|--------|-------------|
| `1c19ca75` | **feat(sam):** enhance SAM segmentation with local model support and UI improvements |
| `f67e7fb7` | **feat(pottery):** add decoration crosstabs and fix chart type switching |
| `0b345a09` | **feat(pottery):** enhance statistics with specific_form, new charts and responsive layout |

### 2025-12-15

| Commit | Description |
|--------|-------------|
| `1006ce68` | **feat(sam):** add local SAM support and debug logging |
| `5b730325` | **fix(sam):** fix interactive modes and make cloud API default |
| `eb6aff39` | **feat(sam):** enable interactive click and box modes for segmentation |
| `8fb49f53` | **fix(report):** process image tags BEFORE markdown formatting |
| `3526ee13` | **fix(report):** improve image tag processing for Word export |
| `beb3b726` | **fix(report):** map tma_table to actual database name tma_materiali_archeologici |
| `5d84a1c4` | **fix(report):** handle missing database tables gracefully |
| `982063b9` | **fix(report):** improve image tag parsing for Word export |
| `01de9a4f` | **fix(report):** process image tags in regular paragraphs for Word export |
| `e5054f04` | **fix(report):** improve report generation and image handling |
| `8dc8a2e0` | **fix(sam):** load results as QGIS layer when target not found |
| `7dc8d474` | **fix(sam):** use subprocess for API to avoid numpy conflicts |
| `22a00f11` | **feat(sam):** add SAM API option via Replicate |

### 2025-12-14

| Commit | Description |
|--------|-------------|
| `9fcdb404` | **fix(toolbar):** add SAM button to all language blocks |
| `fea6c279` | **feat(gis):** add SAM stone segmentation tool |
| `30181cde` | **feat(pottery):** auto-rebuild indexes after KhutmML training |
| `ca21c77a` | **feat(pottery):** add KhutmML-CLIP model export/import and tips |
| `f97b6470` | **feat(pottery):** add KhutmML-CLIP fine-tuning and similarity search |
| `2e7c9c81` | **chore:** bump version to 4.9.14 |
| `baa3768c` | **chore:** bump version to 4.9.13 |
| `199537d6` | **chore:** bump version to 4.9.12 |

### 2025-12-13

| Commit | Description |
|--------|-------------|
| `32ed650a` | **feat(db):** add automatic GRANT sync when tables are recreated |
| `50c4b64f` | **chore:** bump version to 4.9.11 |
| `13dbd41c` | **feat(pottery):** add year filter to PotteryFilterDialog |
| `73186ae4` | **chore:** bump version to 4.9.10 |
| `44d5b8fb` | **feat(pottery):** add ID Number filter dialog with checkboxes |
| `ebb7e74d` | **chore:** bump version to 4.9.9 |
| `eafdc4c3` | **feat(pottery):** add decoration fields and fix Thesaurus bugs |

### 2025-12-12

| Commit | Description |
|--------|-------------|
| `7f5b3aca` | **feat(similarity):** detailed feedback for all models when no results |
| `1eccae04` | **feat(similarity):** detailed feedback when no results found |
| `60b10c70` | **feat(similarity):** two search modes - Global and Combined |
| `88741eb8` | **debug(similarity):** add more logging to search_by_text |
| `f4070b3d` | **feat(similarity):** text-based semantic search without image |
| `c5ca823f` | **feat(similarity):** show custom prompt only when OpenAI is selected |
| `7f6095c7` | **feat(similarity):** add custom prompt for semantic search and show US in results |
| `57613003` | **fix(similarity):** add missing parameters to OpenAI get_embedding signature |
| `d1f4c152` | **debug(similarity):** add more logging to track fill_fields issue |
| `d3b5bb28` | **fix(similarity):** properly set record references before fill_fields |
| `aee11ba3` | **fix(similarity):** add debug logging to navigate_to_pottery |
| `4281aef8` | **feat(similarity):** add OpenAI specialized prompts and decoration segmentation |

### 2025-12-11

| Commit | Description |
|--------|-------------|
| `f48255e0` | **feat(similarity):** add incremental index update for all models |
| `056df6a9` | **feat(similarity):** add Import/Export indexes for sharing between PCs |
| `28152897` | **feat(similarity):** add Excel export with thumbnails + chart |
| `0a7b4538` | **feat(similarity):** add DINOv2 support + improved decoration preprocessing |
| `6acd5653` | **feat(similarity):** image selection + non-modal results dialog |
| `c559b864` | **fix(similarity):** view_all before navigate + keep dialog open |
| `52d07651` | **fix(similarity):** use id_number for display and navigation |
| `a11c0f16` | **fix(similarity):** add debug logging + fix navigation |
| `089c6a87` | **fix(similarity):** close dialog on navigate + add decoration filter |
| `c43aee99` | **fix:** add missing QPixmap import |
| `d8125138` | **feat(similarity):** improve search with multi-image + Cloudinary thumbnails |
| `688d2a81` | **fix(cloudinary):** remove _thumb suffix from URLs |
| `0bb2749e` | **debug:** add Cloudinary path logging for troubleshooting |
| `38a798dc` | **feat(pottery):** add AI visual similarity search + Cloudinary support |

### 2025-12-10

| Commit | Description |
|--------|-------------|
| `aea7a575` | **chore:** bump version to 4.9.8 |
| `0ecbb85f` | **feat(potteryink):** add manual contrast/brightness and background options |
| `63626d6a` | **chore:** bump version to 4.9.7 |
| `c8f39eaa` | **chore:** test version sync |
| `06468b5c` | **feat(repo):** add custom QGIS plugin repository XML |
| `d7d82cb5` | **feat(ui):** update icons and remove labels for specific UI elements |
| `d1cef03e` | **chore(resources):** add new icons to resources.qrc and recompile |
| `92dffbec` | **feat(US):** add icons and tooltips for 4 new toolbar buttons |
| `042bdc4e` | **feat(US):** connect 4 new toolbar buttons to existing functions |
| `75e3bce6` | **feat(ui):** add standalone AI Query Database toolbar button |
| `2fa65d9c` | **fix(ai-query):** fix US-specific data not appearing in AI responses |
| `e6ece560` | **feat(AI Query):** add persistent FAISS vectorstore storage |
| `cedfa2be` | **fix(AI Query):** improve media display and AI response quality |
| `ab2aec33` | **fix(AI Query):** add missing QPixmap import |
| `502ba90d` | **fix(AI Query):** fix media lookup and add support for all entity types |
| `47cac362` | **fix(AI Query):** fix vectorstore cache not being used on repeated queries |
| `7de8545d` | **fix(AI Query):** add Media tab at initialization for better UX |
| `a279ed50` | **fix(AI Query):** change default model from gpt-5.1 to gpt-4.1-mini |
| `85b7d4cf` | **feat(AI Query):** generic auto-load for all pyarchinit vector views |
| `1a387c92` | **fix(AI Query):** auto-load layer, optimize media, improve spatial |
| `54e9225d` | **feat(AI Query):** major RAG system enhancements |

## Key Features Added

### Image Search System
- Dedicated Image Search dialog accessible from all entity forms (US, Pottery, Materiali, Tomba, Struttura)
- Search by text, entity type, site, area, US, inventory number
- Search for untagged images
- Export functionality for images
- Navigate directly to associated records from search results

### SAM Segmentation Tool
- Local and cloud-based SAM (Segment Anything Model) support
- Interactive click and box modes for stone segmentation
- Integration with Replicate API

### Pottery Similarity Search
- AI-powered visual similarity search
- Multiple model support: CLIP, DINOv2, OpenAI
- Cloudinary CDN integration for thumbnails
- Export results to Excel with thumbnails and charts
- KhutmML-CLIP fine-tuning capabilities

### AI Query Database
- RAG-based natural language queries
- FAISS vectorstore for efficient search
- Multi-entity support
- Media preview integration

### Cloudinary Integration
- Remote storage support for thumbnails and images
- CDN-based image delivery
- Automatic path handling
