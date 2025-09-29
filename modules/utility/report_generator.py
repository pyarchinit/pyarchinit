from docx import Document
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from qgis.PyQt.QtWidgets import *
import socket
from openai import OpenAI
from modules.utility.report_text_cleaner import ReportTextCleaner


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

        # Clean the generated text before returning
        messaggio_combinato = ReportTextCleaner.clean_report_text(messaggio_combinato)

        return messaggio_combinato

    @staticmethod
    def is_connected():
        try:
            # Try to connect to one of the DNS servers
            sock = socket.create_connection(("1.1.1.1", 53), timeout=2)
            sock.close()  # Close the socket properly to avoid ResourceWarning
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

    @staticmethod
    def save_report_to_file(report, file_path):
        """
        Save report with proper formatting and cleaning
        """
        from docx.shared import Pt

        # Clean the report text first
        cleaned_report = ReportTextCleaner.clean_report_text(report)

        # Prepare for docx
        prepared = ReportTextCleaner.prepare_for_docx(cleaned_report)

        # Create document
        doc = Document()

        # Add paragraphs with proper formatting
        for para_info in prepared['paragraphs']:
            text = para_info['text']
            style = para_info['style']

            if style.startswith('heading'):
                level = int(style[-1]) if style[-1].isdigit() else 1
                para = doc.add_heading(text, level=level)
            elif style == 'list':
                para = doc.add_paragraph(text, style='List Bullet')
            else:
                para = doc.add_paragraph(text)

            # Apply Cambria font
            for run in para.runs:
                run.font.name = 'Cambria'
                run.font.size = Pt(12)

        # Save the document
        doc.save(file_path)

