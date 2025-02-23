import requests
from qgis.PyQt.QtWidgets import QMessageBox

from . import database_schema


class MakeSQL:
    def __init__(self):
        pass
    # Funzione per convertire lo schema in formato testuale (esempio semplificato)
    @staticmethod
    def schema_to_text(metadata):
        schema_text = ""
        for table in metadata.tables.values():
            # Inizia con il nome della tabella
            table_description = f"{table.name} ("
            # Aggiungi ogni colonna e il suo tipo
            columns_descriptions = [f"{col.name}" for col in table.columns]
            table_description += ", ".join(columns_descriptions)
            table_description += ");"
            # Aggiungi la descrizione della tabella al testo dello schema
            schema_text += table_description + "\n"
        return schema_text

    # Utilizzo della funzione per includere lo schema nella richiesta API
    @staticmethod
    def make_api_request(prompt,db,apikey):
        # Preparazione dello schema
        #schema = Base.metadata  # Assuming Campioni_table is part of Base
        schema_text = MakeSQL.schema_to_text(database_schema.metadata)  # Converti lo schema in testo
        #QMessageBox.information(None, "Schema", schema_text)
        api_key = apikey  # Sostituisci con la tua chiave API
        url = "https://app2.text2sql.ai/api/external/generate-sql"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "type": db,
            "schema": schema_text  # Utilizzo dello schema convertito
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json().get('output')
        except requests.exceptions.HTTPError as he:
            QMessageBox.critical(None, "Error", str(he))
            return None


        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(None, "Error", str(e))
            return None

        return None

    @staticmethod
    def explain_request(prompt, apikey):
        # Preparazione dello schema
        # schema = Base.metadata  # Assuming Campioni_table is part of Base
        #schema_text = MakeSQL.schema_to_text(database_schema.metadata)  # Converti lo schema in testo
        # QMessageBox.information(None, "Schema", schema_text)
        api_key = apikey  # Sostituisci con la tua chiave API
        url = "https://app2.text2sql.ai/api/external/explain-sql"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json().get('output')
        except requests.exceptions.HTTPError as he:
            QMessageBox.critical(None, "Error", str(he))
            return None


        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(None, "Error", str(e))
            return None

        return None


