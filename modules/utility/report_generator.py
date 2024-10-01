from docx import Document
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from qgis.PyQt.QtWidgets import *
import socket
import sys, subprocess

try:
    import openai

    print("openai is already installed")
except ImportError:
    print("openai is not installed, installing...")
    try:
        if sys.platform.startswith("win"):
            subprocess.check_call(["pip", "install", "openai"], shell=True)
        elif sys.platform.startswith("darwin") or sys.platform.startswith("linux"):
            subprocess.check_call(["python3", "-m", "pip", "install", "openai"], shell=False)
        else:
            raise Exception(f"Unsupported platform: {sys.platform}")
        print("openai installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing openai: {e}")
        sys.exit(1)
try:
    import docx

    print("docx is already installed")
except ImportError:
    print("docx is not installed, installing...")
    try:
        if sys.platform.startswith("win"):
            subprocess.check_call(["pip", "install", "python-docx"], shell=True)
        elif sys.platform.startswith("darwin") or sys.platform.startswith("linux"):
            subprocess.check_call(["python3", "-m", "pip", "install", "python-docx"], shell=False)
        else:
            raise Exception(f"Unsupported platform: {sys.platform}")
        print("openai installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing python-docx: {e}")
        sys.exit(1)


import time


class ReportGenerator(QWidget):
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
    def read_data_from_db_description_only(db_url, table_name):
        engine = create_engine(db_url)
        metadata = MetaData(bind=engine)
        table = Table(table_name, metadata, autoload_with=engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Adjust the query to only select the 'description' column
        query = select([table.c.descrizione])
        result_proxy = session.execute(query)
        records = result_proxy.fetchall()  # This will be a list of tuples with one element each

        # Extract the descriptions from the tuples
        descriptions = [record[0] for record in records if record[0] is not None]

        session.close()
        return descriptions


    @staticmethod
    def generate_report_with_openai(descriptions_text, api_key, model):
        prompt = descriptions_text
        prompt += "\n\nReport:"

        openai.api_key = api_key
        #while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt}]
            )

            QMessageBox.information(None,'ok',str(response))
            return response['choices'][0]['message']['content']
        except openai.error.OpenAIError as e:
            if isinstance(e, openai.error.RateLimitError):
                time.sleep(5)
                return ReportGenerator.generate_report_with_openai(descriptions_text, api_key, model)  # Retry
            else:
                raise e

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
    def save_report_to_file(report, file_path):
        # Create a new Document
        doc = Document()
        # Add the report text to the document
        doc.add_paragraph(report)
        # Save the document to the specified file path
        doc.save(file_path)


class ReportGenerator_new:
    @staticmethod
    def parse_prompt_for_relationships(prompt):
        '''
        Parse the prompt to identify tables and columns to be used in relationships.
        This is a simple placeholder logic, assuming the prompt contains keywords like "JOIN", "ON", etc.
        In a real-world scenario, NLP techniques would be employed for better extraction.
        '''
        relationships = []
        lines = prompt.split("\n")
        for line in lines:
            if "JOIN" in line or "join" in line:
                # Extract table and column information (simple parsing for demonstration purposes)
                tokens = line.split()
                if len(tokens) > 3:
                    table1 = tokens[1]
                    table2 = tokens[3]
                    on_clause = " ".join(tokens[4:])
                    relationships.append((table1, table2, on_clause))
        return relationships

    @staticmethod
    def query_database_with_relationships(db_url, relationships):
        '''
        Connect to the database and execute queries based on relationships extracted from the prompt.
        Returns the combined results as a string to be used in report generation.
        '''
        # Set up database connection
        engine = create_engine(db_url)
        metadata = MetaData(bind=engine)
        session = sessionmaker(bind=engine)()

        # Collect results from each relationship
        results_text = ""
        for table1, table2, on_clause in relationships:
            try:
                # Reflect tables
                t1 = Table(table1, metadata, autoload_with=engine)
                t2 = Table(table2, metadata, autoload_with=engine)

                # Build and execute the join query
                query = select([t1, t2]).where(on_clause)
                result = session.execute(query).fetchall()

                # Format results
                results_text += f"Results for {table1} JOIN {table2} ON {on_clause}:\n"
                for row in result:
                    results_text += str(row) + "\n"
                results_text += "\n"
            except Exception as e:
                results_text += f"Error querying {table1} JOIN {table2}: {e}\n"

        session.close()
        return results_text

    @staticmethod
    def generate_report_with_openai(full_prompt, api_key, selected_model):
        '''
        Uses OpenAI's API to generate a report based on the combined prompt and descriptions.
        '''
        openai.api_key = api_key
        response = openai.Completion.create(
            model=selected_model,
            prompt=full_prompt,
            max_tokens=1000  # Set max tokens as appropriate
        )
        return response.choices[0].text

    @staticmethod
    def save_report_to_file(report_text, file_path):
        '''
        Save the generated report to a .docx file.
        '''
        doc = Document()
        doc.add_paragraph(report_text)
        doc.save(file_path)

    @staticmethod
    def read_data_from_db(db_url, table_name):
        '''
        Placeholder method to read data from a single table.
        '''
        # Database connection setup
        engine = create_engine(db_url)
        metadata = MetaData(bind=engine)
        table = Table(table_name, metadata, autoload_with=engine)

        # Execute query
        session = sessionmaker(bind=engine)()
        query = select([table])
        result = session.execute(query).fetchall()
        columns = table.columns.keys()

        session.close()
        return result, columns

    @staticmethod
    def is_connected():
        '''
        Placeholder method to check if the system has internet connection.
        '''
        try:
            socket.create_connection(("1.1.1.1", 53))
            return True
        except OSError:
            return False