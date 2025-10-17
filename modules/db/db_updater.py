#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database updater module for PyArchInit
Handles automatic updates of triggers and other database objects
"""

import os
from qgis.core import QgsMessageLog, Qgis

class DatabaseUpdater:
    """
    Handles automatic database updates when connecting
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.HOME = os.environ['PYARCHINIT_HOME']

    def check_and_update_triggers(self):
        """
        Check and update database triggers to ensure they're compatible
        with multi-user permission system
        """
        try:
            # Check if we're connected to PostgreSQL
            if not hasattr(self.db_manager, 'engine'):
                return True  # No engine, skip
                
            # Check connection type - handle both string and engine object
            try:
                engine_str = str(self.db_manager.engine.url)
            except AttributeError:
                # engine might not have url attribute (e.g., for some SQLite connections)
                engine_str = str(self.db_manager.engine)
            
            if 'postgresql' not in engine_str:
                return True  # Skip for SQLite

            # Check if create_doc trigger needs updating
            self.update_create_doc_trigger()

            return True

        except Exception as e:
            QgsMessageLog.logMessage(f"Error updating database triggers: {str(e)}", "PyArchInit", Qgis.Warning)
            return False

    def update_create_doc_trigger(self):
        """
        Update the create_doc trigger to handle permission issues
        """
        try:
            # Check current trigger definition
            check_sql = """
            SELECT prosrc
            FROM pg_proc
            WHERE proname = 'create_doc'
            """

            result = self.db_manager.execute_sql(check_sql)

            if result and len(result) > 0:
                # Handle both tuple and dict results
                if isinstance(result[0], tuple):
                    current_def = result[0][0] if len(result[0]) > 0 else ''
                elif isinstance(result[0], dict):
                    current_def = result[0].get('prosrc', '')
                else:
                    current_def = str(result[0]) if result[0] else ''

                # Check if trigger needs updating (look for old pattern)
                if 'old.d_interpretativa' in current_def and 'TG_OP' not in current_def:
                    QgsMessageLog.logMessage("Updating create_doc trigger for permission compatibility", "PyArchInit", Qgis.Info)

                    # Drop and recreate the trigger with proper permission handling
                    update_sql = """
                    -- Drop existing trigger if exists
                    DROP TRIGGER IF EXISTS create_doc ON us_table;
                    DROP FUNCTION IF EXISTS create_doc();

                    -- Create improved function that handles permissions
                    CREATE OR REPLACE FUNCTION public.create_doc()
                        RETURNS trigger
                        LANGUAGE 'plpgsql'
                        COST 100
                        VOLATILE NOT LEAKPROOF
                    AS $BODY$
                    BEGIN
                        -- Only perform UPDATE if this is an UPDATE operation (not INSERT)
                        -- and only if the user has UPDATE permission
                        IF TG_OP = 'UPDATE' THEN
                            -- Check if d_interpretativa has changed
                            IF (NEW.d_interpretativa IS DISTINCT FROM OLD.d_interpretativa) THEN
                                -- Try to update related DOC records
                                -- This will fail if user doesn't have UPDATE permission, which is ok
                                BEGIN
                                    UPDATE us_table
                                    SET d_interpretativa = NEW.doc_usv
                                    WHERE sito = NEW.sito
                                      AND area = NEW.area
                                      AND us = NEW.us
                                      AND unita_tipo = 'DOC';
                                EXCEPTION
                                    WHEN insufficient_privilege THEN
                                        -- User doesn't have UPDATE permission, skip this operation
                                        NULL;
                                    WHEN OTHERS THEN
                                        -- Ignore other errors too
                                        NULL;
                                END;
                            END IF;
                        ELSIF TG_OP = 'INSERT' THEN
                            -- For INSERT operations, only update if d_interpretativa is empty
                            IF (NEW.d_interpretativa IS NULL OR NEW.d_interpretativa = '') THEN
                                -- Try to update, but ignore if user lacks permissions
                                BEGIN
                                    UPDATE us_table
                                    SET d_interpretativa = NEW.doc_usv
                                    WHERE sito = NEW.sito
                                      AND area = NEW.area
                                      AND us = NEW.us
                                      AND unita_tipo = 'DOC';
                                EXCEPTION
                                    WHEN insufficient_privilege THEN
                                        -- User doesn't have UPDATE permission, skip this operation
                                        NULL;
                                    WHEN OTHERS THEN
                                        -- Ignore other errors too
                                        NULL;
                                END;
                            END IF;
                        END IF;

                        RETURN NEW;
                    END;
                    $BODY$;

                    ALTER FUNCTION public.create_doc()
                        OWNER TO postgres;

                    COMMENT ON FUNCTION public.create_doc()
                        IS 'Updates d_interpretativa field for related DOC records with proper permission handling';

                    -- Create trigger
                    CREATE TRIGGER create_doc
                        AFTER INSERT OR UPDATE ON us_table
                        FOR EACH ROW
                        EXECUTE FUNCTION public.create_doc();
                    """

                    self.db_manager.execute_sql(update_sql)
                    QgsMessageLog.logMessage("create_doc trigger updated successfully", "PyArchInit", Qgis.Info)
                else:
                    # Trigger is already updated or doesn't exist
                    pass

        except Exception as e:
            # Log but don't fail - trigger update is not critical
            QgsMessageLog.logMessage(f"Could not update create_doc trigger: {str(e)}", "PyArchInit", Qgis.Info)