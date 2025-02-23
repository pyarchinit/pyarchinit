
from sys import platform

from sqlalchemy import create_engine



class ResponseSQL:
    def __init__(self):
        pass

    @staticmethod
    def execute_sql_and_display_results(con_string, sql, results_widget=None):
        global engine
        debug_messages = []
        #debug_messages.append(f"Executing SQL: {sql}")

        try:
            is_spatialite = 'sqlite' in con_string.lower() and any(x in sql.upper() for x in ['ST_', 'GEOMETRY'])

            if is_spatialite:
                debug_messages.append("\nUsing SpatiaLite connection...")
                # Rimuovi il prefisso sqlite:/// se presente
                db_path = con_string.replace('sqlite:///', '')

                # Usa sqlite3 direttamente per le query spaziali
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.enable_load_extension(True)
                if platform == 'win':
                    conn.load_extension('mod_spatialite')

                else:
                    conn.load_extension('mod_spatialite.so')



                debug_messages.append("SpatiaLite extension loaded successfully")



                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()

                # Ottieni i nomi delle colonne
                column_names = [description[0] for description in cursor.description]

                debug_messages.append(f"\nRaw results: {rows}")
                debug_messages.append(f"\nColumn names: {column_names}")

                # Converti in lista di dizionari
                result_dicts = [dict(zip(column_names, row)) for row in rows]
                debug_messages.append(f"\nConverted results: {result_dicts}")

                conn.close()

                if results_widget:
                    results_widget.setText("\n".join(debug_messages))
                return result_dicts
            else:
                # Usa SQLAlchemy per query non spaziali
                engine = create_engine(con_string)
                with engine.connect() as connection:
                    if sql.strip().upper().startswith("SELECT"):
                        result = connection.execute(sql)
                        rows = result.fetchall()
                        columns = result.keys()

                        if rows:
                            result_dicts = [dict(zip(columns, row)) for row in rows]
                            debug_messages.append(f"\nResults: {result_dicts}")
                            if results_widget:
                                results_widget.setText("\n".join(debug_messages))
                            return result_dicts
                        else:
                            debug_messages.append("\nNo rows returned")
                            if results_widget:
                                results_widget.setText("\n".join(debug_messages))
                            return []
                    else:
                        connection.execute(sql)
                        return 'Query executed successfully'

        except Exception as e:
            debug_messages.append(f"\nError: {str(e)}")
            if results_widget:
                results_widget.setText("\n".join(debug_messages))
            return None
        finally:
            if 'engine' in locals():
                engine.dispose()