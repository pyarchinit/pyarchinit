from docx import Document
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from qgis.PyQt.QtWidgets import *
import socket
# OpenAI import removed to avoid pydantic conflicts - will be imported lazily in generate_report_with_openai


class ReportGenerator(QWidget):

    MAX_TOKENS = 4096

    def __init__(self):
        super().__init__()


    @staticmethod
    def read_data_from_db(db_url, table_name):
        engine = create_engine(db_url)
        metadata = MetaData(bind=engine)
        table = Table(table_name, metadata, autoload_with=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        query = session.query(table)
        records = query.all()
        columns = [column.name for column in table.columns]
        session.close()
        return records, columns

    @staticmethod
    def chunk_data(data, chunk_size):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def generate_report_with_openai(self, prompt_completo, modello_selezionato, apikey):
        '''
        Usa l'API di OpenAI per generare un report basato sul prompt combinato e le descrizioni.
        '''
        # Lazy import to avoid pydantic conflicts
        try:
            from openai import OpenAI
        except ImportError as e:
            error_msg = f"Cannot import OpenAI: {str(e)}\n\nPlease install: python -m pip install --upgrade openai pydantic pydantic-core"
            QMessageBox.warning(None, "OpenAI Import Error", error_msg, QMessageBox.Ok)
            return "Error: Could not load OpenAI library"

        client= OpenAI(api_key=apikey)

        response = client.chat.completions.create(
            model=modello_selezionato,
            messages=[
                {"role": "user", "content": prompt_completo}
            ],
            stream=True,
            #max_tokens=ReportGenerator.MAX_TOKENS
        )

        messaggio_combinato = "\n "

        try:
            for chunk in response:
                delta_content = chunk.choices[0].delta.content
                if delta_content is not None:
                    messaggio_combinato += delta_content

        except Exception as e:
            print(f"Errore nel processo di stream: {e}")

        return messaggio_combinato

    @staticmethod
    def is_connected():
        try:
            # Try to connect to one of the DNS servers
            socket.create_connection(("1.1.1.1", 53))
            return True
        except OSError:
            pass
        return False

    @staticmethod
    def save_report_to_file_old(report, file_path):
        # Create a new Document
        doc = Document()
        # Add the report text to the document
        doc.add_paragraph(report)
        # Save the document to the specified file path
        doc.save(file_path)

