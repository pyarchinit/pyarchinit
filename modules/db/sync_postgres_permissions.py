#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sync PyArchInit permissions with PostgreSQL database permissions
"""

import os
from sqlalchemy import create_engine, text
from modules.db.pyarchinit_conn_strings import Connection

class PostgresPermissionSync:
    """Synchronize PyArchInit permissions with PostgreSQL"""

    def __init__(self, db_manager=None):
        self.db_manager = db_manager

    def create_postgres_user(self, username, password, role):
        """
        Create a PostgreSQL user if it doesn't exist

        Args:
            username: Username to create
            password: Password for the user
            role: PyArchInit role (admin, archeologo, studente, guest)
        """
        try:
            # Connect as postgres superuser
            conn = Connection()
            conn_str = conn.conn_str()

            # Check if user exists
            check_query = text("""
                SELECT 1 FROM pg_user WHERE usename = :username
            """)

            result = self.db_manager.engine.execute(check_query, username=username)

            if not result.fetchone():
                # Create user
                create_query = text(f"""
                    CREATE USER {username} WITH PASSWORD '{password}'
                """)
                self.db_manager.engine.execute(create_query)

                # Grant basic connection
                grant_connect = text(f"""
                    GRANT CONNECT ON DATABASE {self.db_manager.engine.url.database} TO {username}
                """)
                self.db_manager.engine.execute(grant_connect)

                grant_usage = text(f"""
                    GRANT USAGE ON SCHEMA public TO {username}
                """)
                self.db_manager.engine.execute(grant_usage)

                print(f"Created PostgreSQL user: {username}")
            else:
                print(f"User {username} already exists")

            return True

        except Exception as e:
            print(f"Error creating PostgreSQL user {username}: {str(e)}")
            return False

    def sync_table_permissions(self, username, table_name, can_view, can_insert, can_update, can_delete):
        """
        Sync permissions for a specific table

        Args:
            username: Username
            table_name: Table name
            can_view: SELECT permission
            can_insert: INSERT permission
            can_update: UPDATE permission
            can_delete: DELETE permission
        """
        try:
            permissions = []
            if can_view:
                permissions.append('SELECT')
            if can_insert:
                permissions.append('INSERT')
            if can_update:
                permissions.append('UPDATE')
            if can_delete:
                permissions.append('DELETE')

            if permissions:
                # Revoke all first
                revoke_query = text(f"""
                    REVOKE ALL PRIVILEGES ON {table_name} FROM {username}
                """)

                try:
                    self.db_manager.engine.execute(revoke_query)
                except:
                    pass  # Table might not exist or user might not have permissions

                # Grant new permissions
                perm_str = ', '.join(permissions)
                grant_query = text(f"""
                    GRANT {perm_str} ON {table_name} TO {username}
                """)

                self.db_manager.engine.execute(grant_query)

                # If INSERT permission, also grant USAGE on sequences
                if can_insert:
                    # Find sequences for this table
                    seq_query = text(f"""
                        SELECT c.relname AS sequence_name
                        FROM pg_class c
                        JOIN pg_depend d ON d.objid = c.oid
                        JOIN pg_class t ON t.oid = d.refobjid
                        WHERE c.relkind = 'S'
                        AND t.relname = '{table_name}'
                    """)

                    sequences = self.db_manager.engine.execute(seq_query)
                    for seq in sequences:
                        grant_seq = text(f"""
                            GRANT USAGE, SELECT ON SEQUENCE {seq.sequence_name} TO {username}
                        """)
                        self.db_manager.engine.execute(grant_seq)

                print(f"Granted {perm_str} on {table_name} to {username}")
            else:
                # Revoke all permissions if none are granted
                revoke_query = text(f"""
                    REVOKE ALL PRIVILEGES ON {table_name} FROM {username}
                """)
                try:
                    self.db_manager.engine.execute(revoke_query)
                    print(f"Revoked all permissions on {table_name} from {username}")
                except:
                    pass

        except Exception as e:
            print(f"Error syncing permissions for {username} on {table_name}: {str(e)}")

    def sync_all_permissions(self):
        """
        Sync all permissions from pyarchinit_permissions table to PostgreSQL
        """
        try:
            # Get all users and their permissions
            query = text("""
                SELECT
                    u.username,
                    u.password_hash,
                    u.role,
                    p.table_name,
                    p.can_view,
                    p.can_insert,
                    p.can_update,
                    p.can_delete
                FROM pyarchinit_users u
                LEFT JOIN pyarchinit_permissions p ON p.user_id = u.id
                WHERE u.is_active = true
            """)

            result = self.db_manager.engine.execute(query)

            # Group permissions by user
            user_permissions = {}
            for row in result:
                username = row.username
                if username not in user_permissions:
                    user_permissions[username] = {
                        'password': row.password_hash[:10],  # Use first 10 chars as temp password
                        'role': row.role,
                        'tables': []
                    }

                if row.table_name:
                    user_permissions[username]['tables'].append({
                        'table_name': row.table_name,
                        'can_view': row.can_view,
                        'can_insert': row.can_insert,
                        'can_update': row.can_update,
                        'can_delete': row.can_delete
                    })

            # Process each user
            for username, info in user_permissions.items():
                if username == 'postgres':
                    continue  # Skip postgres superuser

                print(f"\nProcessing user: {username}")

                # Create PostgreSQL user if needed
                self.create_postgres_user(username, info['password'], info['role'])

                # Apply table permissions
                for table_perms in info['tables']:
                    self.sync_table_permissions(
                        username,
                        table_perms['table_name'],
                        table_perms['can_view'],
                        table_perms['can_insert'],
                        table_perms['can_update'],
                        table_perms['can_delete']
                    )

            print("\n✓ Permission synchronization complete")

        except Exception as e:
            print(f"Error syncing permissions: {str(e)}")

    def apply_role_based_permissions(self, username, role):
        """
        Apply default permissions based on role

        Args:
            username: Username
            role: Role (admin, archeologo, studente, guest)
        """
        try:
            if role == 'admin':
                # Grant all permissions
                grant_query = text(f"""
                    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {username};
                    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {username};
                    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO {username};
                """)
                self.db_manager.engine.execute(grant_query)

            elif role == 'archeologo':
                # Can view, insert, and update most tables
                grant_query = text(f"""
                    GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO {username};
                    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {username};
                """)
                self.db_manager.engine.execute(grant_query)

            elif role == 'studente':
                # Limited permissions - mainly view and some insert
                grant_query = text(f"""
                    GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username};
                    GRANT INSERT ON us_table, campioni_table TO {username};
                    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {username};
                """)
                self.db_manager.engine.execute(grant_query)

            elif role == 'guest':
                # Read-only access
                grant_query = text(f"""
                    GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username};
                """)
                self.db_manager.engine.execute(grant_query)

            print(f"Applied {role} role permissions to {username}")

        except Exception as e:
            print(f"Error applying role permissions: {str(e)}")

def sync_permissions_from_ui(db_manager):
    """
    Function to be called from PyArchInit UI after creating/modifying users
    """
    syncer = PostgresPermissionSync(db_manager)
    syncer.sync_all_permissions()