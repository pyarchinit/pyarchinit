'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text


# Table representing archaeological site budget and expense records
class Budget_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('budget_table', metadata,
                     # Unique identifier for each budget record
                     Column('id_budget', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Budget year
                     Column('anno', Integer),

                     # Expense category
                     Column('categoria', Text),

                     # Description of the expense
                     Column('descrizione', Text),

                     # Planned/estimated amount
                     Column('importo_previsto', Float),

                     # Actual amount spent
                     Column('importo_effettivo', Float),

                     # Registration date
                     Column('data_registrazione', Text),

                     # Expense date
                     Column('data_spesa', Text),

                     # Supplier/vendor name
                     Column('fornitore', Text),

                     # Invoice number
                     Column('numero_fattura', Text),

                     # Notes
                     Column('note', Text),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),
                     )
