'''
Created on 2026-10-16
La memoria degli em.json importati da EMStudio: il file com'era, per sito.
pyArchInit tiene nelle sue tabelle unità, paradati, rapporti ed epoche; il
resto del grafo (risorse, forme, processi, gruppi, autori, licenze, la
georeferenziazione, il codice dello studio, i nomi) si rimette da qui
all'esportazione.
@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Column, Integer, MetaData, String, Table, Text


class Em_sources_table:
    metadata = MetaData()
    pyarchinit_em_sources = Table(
        'pyarchinit_em_sources', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('sito', String(350), nullable=False),     # il sito in cui si è importato
        Column('graph_id', String(200)),                 # l'id del grafo nell'em.json
        Column('source_name', String(500)),              # il nome del file importato
        Column('imported_at', String(32)),
        Column('payload', Text, nullable=False),         # l'em.json com'era, JSON
    )
