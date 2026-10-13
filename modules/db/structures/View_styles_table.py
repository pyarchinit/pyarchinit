'''
Created on 2026-10-13
Stili delle viste: la tabella in cui vivono gli stili composti con la
finestra «Stili delle viste» (simbologia ed etichette come QML, più la
ricetta delle etichette che il QML non sa dire).
@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Column, Integer, MetaData, String, Table, Text


class View_styles_table:
    metadata = MetaData()
    pyarchinit_view_styles = Table(
        'pyarchinit_view_styles', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('view_name', String(64), nullable=False),      # la vista di pyArchInit
        Column('site', String(350)),                           # NULL = tutti i siti
        Column('name', String(200), nullable=False),
        Column('qml', Text, nullable=False),                   # simbologia ed etichette
        Column('recipe', Text),                                # ricetta delle etichette, JSON
        Column('is_default', Integer, nullable=False, default=0),
        Column('author', String(100)),
        Column('updated_at', String(32)),
    )
