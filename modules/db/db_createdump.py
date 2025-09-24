# -*- coding: utf-8 -*-
"""
/***************************************************************************
    pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
    stored in Postgres
    -------------------
    begin                : 2018-08-06
    copyright            : (C) 2018 by Salvatore Larosa; Enzo cocca <enzo.ccc@gmail.com>
    email                : lrssvtml (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *																		*
 ***************************************************************************/
"""

from builtins import object
import io
import datetime
import traceback
import warnings
import os

# Set environment variable to suppress SQLAlchemy warnings
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

# Suppress all deprecation warnings before any SQLAlchemy imports
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*Calling URL.*")

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database


class PyArchInitDBLogger:
    """Simple file logger for database operations"""
    def __init__(self):
        self.log_file = '/Users/enzo/pyarchinit_db_debug.log'

    def log(self, message):
        """Write a log message with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
                f.flush()
        except Exception:
            pass  # Silently fail if logging doesn't work

    def log_exception(self, exc, context=""):
        """Log an exception with traceback"""
        self.log(f"EXCEPTION in {context}: {type(exc).__name__}: {str(exc)}")
        tb = traceback.format_exc()
        for line in tb.split('\n'):
            if line:
                self.log(f"  {line}")


class SchemaDump(object):
    def __init__(self, db_url, schema_file_path):
        self.db_url = db_url
        self.schema_file_path = schema_file_path
        self.buf = io.BytesIO()

    def dump_shema(self):
        engine = create_engine(self.db_url)
        metadata = MetaData()
        metadata.reflect(engine)

        def dump(sql, *multiparams, **params):
            f = sql.compile(dialect=engine.dialect)
            self.buf.write(str(f))
            self.buf.write(str(';\n'))

        new_engine = create_engine(self.db_url, strategy='mock', executor=dump)
        metadata.create_all(new_engine, checkfirst=True)

        with io.open(self.schema_file_path, 'wb+') as schema:
            schema.write(self.buf.getvalue())


class RestoreSchema(object):
    def __init__(self, db_url, schema_file_path=None):
        self.db_url = db_url
        self.schema_file_path = schema_file_path
        self.logger = PyArchInitDBLogger()

    def restore_schema(self):
        self.logger.log(f"\n=== RestoreSchema.restore_schema called ===")
        self.logger.log(f"DB URL: {self.db_url}")
        self.logger.log(f"Schema file: {self.schema_file_path}")

        raw_schema = ''
        try:
            with io.open(self.schema_file_path) as sql_schema:
                raw_schema = sql_schema.read()
            self.logger.log(f"Read {len(raw_schema)} characters from schema file")
        except Exception as e:
            self.logger.log_exception(e, "reading schema file")
            raise

        self.logger.log("Creating engine and session")
        engine = create_engine(self.db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        conn = engine.connect()
        transaction = conn.begin()

        try:
            self.logger.log("Executing schema SQL...")
            conn.execute(text(raw_schema))
            self.logger.log("Committing transaction...")
            transaction.commit()
            self.logger.log("Schema restored successfully")
        except Exception as e:
            self.logger.log("Error executing schema, rolling back")
            self.logger.log_exception(e, "restore_schema")
            transaction.rollback()
            raise e
        finally:
            self.logger.log("Closing session")
            session.close()

    def update_geom_srid(self, schema, crs):
        sql_query_string = ("SELECT f_table_name, type FROM {}".format('geometry_columns'))
        engine = create_engine(self.db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        conn = engine.connect()
        try:
            res = conn.execute(sql_query_string)
            tables = []
            types = []
            for r in res:
                tables.append(r[0])
                types.append(r[1])
            tables_and_types = dict(zip(tables, types))
            for t, ty in tables_and_types.items():
                sql_queries = text("ALTER TABLE {0} ALTER COLUMN the_geom TYPE geometry({1}, {2}) USING ST_SetSRID(the_geom, {2})".format(
                    t, ty, crs
                ))
                res = conn.execute(sql_queries)
        except Exception as e:
            raise e
        finally:
            session.close()
        return True

    def set_owner(self, owner):
        sql = "SELECT table_name FROM information_schema.tables where table_schema = 'public'"
        engine = create_engine(self.db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        conn = engine.connect()
        try:
            res = conn.execute(sql)
            for r in res:
                sql_queries = text("ALTER TABLE public.{} OWNER TO {};".format(r[0], owner))
                res = conn.execute(sql_queries)
        except Exception as e:
            raise e
        finally:
            session.close()
        return True

    def update_geom_srid_sl(self, crs):
        sql_query_string = ("SELECT f_table_name, geometry_type, f_geometry_column FROM {}".format('geometry_columns'))
        engine = create_engine(self.db_url, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        conn = engine.connect()
        try:
            res = conn.execute(sql_query_string)
            tables = []
            types_and_geom = []
            for r in res:
                tables.append(r[0])
                types_and_geom.append((r[1], r[2]))
            tables_and_types = dict(zip(tables, types_and_geom))
            for t, ty in tables_and_types.items():
                sql_queries_1 = text("UPDATE geometry_columns SET srid = {1} WHERE f_table_name = '{0}';".format(
                    t, crs
                ))
                # sql_queries_2 = text("UPDATE {0} SET {1} = SetSRID({1}, {2});".format(
                #     t, ty[1], crs
                # ))
                conn.execute(sql_queries_1)
                # conn.execute(sql_queries_2)
        except Exception as e:
            raise e
        finally:
            session.close()
        return True


class CreateDatabase(object):

    def __init__(self, db_name, db_host, db_port, db_user, db_passwd):
        self.db_name = db_name
        self.db_host = db_host
        self.user = db_user
        self.passwd = db_passwd
        self.port = db_port
        self.logger = PyArchInitDBLogger()

    def createdb(self):
        self.logger.log(f"\n=== CreateDatabase.createdb called ===")
        self.logger.log(f"Database: {self.db_name}")
        self.logger.log(f"Host: {self.db_host}:{self.port}")
        self.logger.log(f"User: {self.user}")

        # Build connection URL (mask password in logs)
        url_string = "postgresql://{}:***@{}:{}/{}".format(self.user, self.db_host, self.port, self.db_name)
        self.logger.log(f"Connection URL (masked): {url_string}")

        try:
            # Create the database URL string
            db_url_string = "postgresql://{}:{}@{}:{}/{}".format(
                self.user, self.passwd, self.db_host, self.port, self.db_name)

            engine = create_engine(db_url_string)
            self.logger.log("Engine created")

            # Use the string URL directly to avoid deprecation warning
            if not database_exists(db_url_string):
                self.logger.log("Database does not exist, creating...")
                create_database(db_url_string)
                self.logger.log("Database created successfully")
                return True, db_url_string
            else:
                self.logger.log("Database already exists")
                return False, None
        except Exception as e:
            self.logger.log_exception(e, "createdb")
            raise


class DropDatabase(object):

    def __init__(self, db_url):
        self.db_url = db_url

    def dropdb(self):
        if database_exists(self.db_url):
            drop_database(self.db_url)