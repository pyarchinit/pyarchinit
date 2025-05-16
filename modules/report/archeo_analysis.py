from modules.report.processor import ArchaeologicalStepProcessor


class ArchaeologicalAnalysis:
    def __init__(self):
        self.current_step = 0
        self.processor = ArchaeologicalStepProcessor()
        self.token_count = 0
        self.tokens_per_section = {
            "INTRODUZIONE": 12000,
            "METODOLOGIA DI SCAVO": 16000,
            "ANALISI STRATIGRAFICA E INTERPRETAZIONE": 16000,
            "CATALOGO DEI MATERIALI": 16000,
            "CONCLUSIONI": 8000
        }
        self.max_tokens = 16000

    def get_max_tokens_for_section(self, section):
        return self.tokens_per_section.get(section, self.max_tokens)

    def get_next_analysis_step(self):
        steps = {
            0: self.get_introduction_step,
            1: self.get_methodology_step,
            2: self.get_stratigraphy_step,
            3: self.get_materials_step,
            4: self.get_conclusions_step
        }

        if self.current_step < len(steps):
            step = steps[self.current_step]()
            # Aggiungi il numero di token massimo per questa sezione
            step['max_tokens'] = self.get_max_tokens_for_section(step['section'])
            self.current_step += 1
            self.token_count = 0
            return step
        return None

    def get_introduction_step(self):
        return {
            "thought": "Sintetizzare i risultati della campagna di scavo",
            "action": "SintesiIntroduttiva",
            "section": "INTRODUZIONE",
            "required_table": ["site_table", "us_table"],
            "validation_tool": ["validate_site_info"],  # Aggiunto il validatore appropriato

            "prompt": (
                "Analizza e descrivi la campagna di scavo, fornendo l'anno di svolgimento, "
                "l'area indagata e le principali evidenze archeologiche rinvenute.una panoramica "
                "completa che includa il periodo di svolgimento, l'area indagata e "
                "le principali evidenze archeologiche rinvenute. Descrivi i rinvenimenti "
                "più significativi, sia strutturali che materiali, e delinea "
                "l'inquadramento cronologico generale del sito."
            )
        }

    def get_methodology_step(self):
        return {
            "thought": "Analizzare metodologia e organizzazione dello scavo",
            "action": "AnalisiAreaScavo",
            "section": "METODOLOGIA DI SCAVO",
            "required_table": ["us_table"],
            "validation_tool": ["validate_us"],
            "prompt": (
                "Descrivi dettagliatamente l'approccio metodologico utilizzato durante "
                "lo scavo, includendo l'organizzazione delle aree, le tecniche "
                "specifiche impiegate e i sistemi di documentazione adottati. "
                "Evidenzia le scelte strategiche e le loro motivazioni."
            )
        }

    def get_stratigraphy_step(self):
        return {
            "thought": "Analizzare la sequenza stratigrafica e creare elenchi strutturati",
            "action": "AnalisiStratigrafica",
            "section": "ANALISI STRATIGRAFICA E INTERPRETAZIONE",
            "required_table": ["us_table"],  # Corretto per essere una lista
            "validation_tool": ["validate_us"],  # Corretto per essere una lista
            "prompt": (
                "Elabora un'analisi approfondita della sequenza stratigrafica seguendo questa struttura:\n\n"
                "1. ELENCO STRUTTURATO DELLE US:\n"
                "   - Crea un elenco numerato di tutte le US identificate\n"
                "   - Per ogni US fornisci:\n"
                "     * Numero US\n"
                "     * Definizione/Tipologia\n"
                "     * Interpretazione dettagliata\n"
                "     * Quote (min/max se disponibili)\n"
                #"   - Per ogni US includi l'immagine associata usando questa sintassi:\n"
                #"     [IMMAGINE US X: url_immagine, caption_immagine]\n\n"
                "2. ANALISI DEI RAPPORTI STRATIGRAFICI:\n"
                "   - Per ogni US elenca:\n"
                "     * Rapporti fisici\n"
                "     * Rapporti indiretti\n"
                "   - Per le immagini dei rapporti usa la stessa sintassi:\n"
                "     [IMMAGINE US X: url_immagine, caption_immagine]\n\n"
                "3. INTERPRETAZIONE DELLE FASI:\n"
                "   - Raggruppa le US per fasi cronologiche\n"
                "   - Fornisci interpretazione funzionale per ogni fase\n"
                "   - Per le immagini delle fasi usa la stessa sintassi:\n"
                "     [IMMAGINE US X: url_immagine, caption_immagine]\n\n"
                "Usa un formato chiaro e strutturato, con sottotitoli e punti elenco per maggiore leggibilità.\n\n"
                "IMPORTANTE: Per ogni US menzionata, verifica se esistono immagini associate e inseriscile nel testo "
                "secondo la sintassi specificata. Le immagini sono disponibili nel contesto e possono essere referenziate "
                "usando l'URL e la caption forniti. Usa sempre il formato [IMMAGINE US X] per tutte le immagini."
                "Non duplicare le immagini, Se l'immagine è stata inserita in precedenza, non è necessario reinserirla.\n\n "
            )
        }

    def get_materials_step(self):
        return {
            "thought": "Analizzare i materiali rinvenuti con statistiche e catalogazione strutturata",
            "action": "AnalisiMaterialiComplessiva",
            "section": "CATALOGO DEI MATERIALI",
            "required_table": ["inventario_materiali_table", "pottery_table"],
            "validation_tool": ["validate_materials", "validate_pottery"],
            "prompt": (
                "Sviluppa un'analisi completa dei materiali archeologici seguendo questa struttura:\n\n"
                "1. QUADRO STATISTICO GENERALE:\n"
                "   - Conteggio totale dei reperti\n"
                "   - Distribuzione percentuale per categorie\n"
                #"   - Inserisci immagini pertinenti con caption descrittive dove necessario.\n\n"
                "2. ANALISI CERAMICA DETTAGLIATA:\n"
                "   - Statistiche e catalogo strutturato\n"
                #"   - Inserisci immagini pertinenti con caption descrittive dove necessario.\n\n"
                "3. ALTRI MATERIALI:\n"
                "   - Analisi quantitativa e catalogo ragionato\n"
                "   - Inserisci immagini pertinenti con caption descrittive dove necessario.\n\n"
                "4. ANALISI CONTESTUALE:\n"
                "   - Distribuzione spaziale dei materiali\n"
                #"   - Inserisci immagini pertinenti con caption descrittive dove necessario.\n\n"
                "5. CRONOLOGIA E INTERPRETAZIONE:\n"
                "   - Indicatori cronologici\n"
                "   - Inserisci immagini pertinenti con caption descrittive dove necessario.\n\n"
                "Includi tabelle riassuntive e usa un formato strutturato con numerazione chiara."
            )
        }

    def get_conclusions_step(self):
        return {
            "thought": "Elaborare le conclusioni dello scavo",
            "action": "AnalisiFinale",
            "section": "CONCLUSIONI",
            "required_table": [],  # Lista vuota invece di None
            "validation_tool": [],
            "prompt": (
                "Sintetizza i risultati principali emersi dallo scavo, mettendo in "
                "relazione i dati stratigrafici con i materiali rinvenuti. "
                "Evidenzia gli elementi più significativi per la comprensione del "
                "sito e del suo sviluppo nel tempo. Discuti eventuali risultati "
                "inattesi o problematiche aperte, suggerendo possibili direzioni "
                "per future ricerche. Inquadra i risultati nel più ampio contesto "
                "storico-archeologico dell'area."
            )
        }


# def process_analysis_step(step):
#     """
#     Processa ogni step dell'analisi archeologica
#     """
#     print(f"Elaborazione della sezione: {step['section']}")
#     print(f"Azione: {step['action']}")
#     print(f"Tabelle richieste: {step['required_table']}")
#     print(f"Validazione: {step['validation_tool']}")
#     print(f"Prompt di analisi: {step['prompt']}\n")
#
#
# # Esempio di utilizzo
# if __name__ == "__main__":
#     analysis = ArchaeologicalAnalysis()
#     while True:
#         step = analysis.get_next_analysis_step()
#         if not step:
#             break
#         process_analysis_step(step)
