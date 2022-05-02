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
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database


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

    def restore_schema(self):
        raw_schema = ''
        with io.open(self.schema_file_path) as sql_schema:
            raw_schema = sql_schema.read()
        engine = create_engine(self.db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        conn = engine.connect()
        transaction = conn.begin()
        try:
            conn.execute(text(raw_schema))
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            raise e
        finally:
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

    def createdb(self):
        engine = create_engine("postgresql://{}:{}@{}:{}/{}".format(self.user, self.passwd, self.db_host, self.port, self.db_name))
        if not database_exists(engine.url):
            create_database(engine.url)
            return True, engine.url

        return False, None


class DropDatabase(object):

    def __init__(self, db_url):
        self.db_url = db_url

    def dropdb(self):
        if database_exists(self.db_url):
            drop_database(self.db_url)