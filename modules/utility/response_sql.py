from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class ResponseSQL:
    def __init__(self):
        pass

    @staticmethod
    def execute_sql_and_display_results(con_string, sql):
        engine = create_engine(con_string)
        try:
            with engine.connect() as connection:
                if sql.strip().upper().startswith("SELECT"):
                    result = connection.execute(sql)
                    #connection.commit()
                    return result.fetchall()  # Fetch and return the results for SELECT queries
                else:
                    connection.execute(sql)
                    #connection.commit()  # Commit the transaction for INSERT/UPDATE/DELETE
                    return 'Database updated'  # No result set to return
        except SQLAlchemyError as e:
            print(f"SQLAlchemy Error: {e}")
            return None



# Example usage:
# Assume 'generated_sql' is the SQL statement you received from the API response
#generated_sql = "SELECT * FROM your_table WHERE condition;"  # Replace with your actual SQL query
# Example usage:
#prompt = "conta quante us ci sono in us_table"
#db_type = "sqlite"
