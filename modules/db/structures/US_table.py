'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class US_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables check per verifica fill fields 20/10/2016 OK
    us_table = Table('us_table', metadata,
                     Column('id_us', Integer, primary_key=True),  # 0
                     Column('sito', Text),  # 1
                     Column('area', String(20)),  # 2
                     Column('us', Integer),  # 3
                     Column('d_stratigrafica', String(255)),  # 4
                     Column('d_interpretativa', String(255)),  # 5
                     Column('descrizione', Text),  # 6
                     Column('interpretazione', Text),  # 7
                     Column('periodo_iniziale', String(4)),  # 8
                     Column('fase_iniziale', String(4)),  # 9
                     Column('periodo_finale', String(4)),  # 10
                     Column('fase_finale', String(4)),  # 11
                     Column('scavato', String(2)),  # 12
                     Column('attivita', String(4)),  # 13
                     Column('anno_scavo', String(4)),  # 14
                     Column('metodo_di_scavo', String(20)),  # 15
                     Column('inclusi', Text),  # 16
                     Column('campioni', Text),  # 17
                     Column('rapporti', Text),  # 18
                     Column('data_schedatura', String(20)),  # 19
                     Column('schedatore', String(25)),  # 20
                     Column('formazione', String(20)),  # 21
                     Column('stato_di_conservazione', String(20)),  # 22
                     Column('colore', String(20)),  # 23
                     Column('consistenza', String(20)),  # 24
                     Column('struttura', String(30)),  # 25
                     Column('cont_per', String(200)),  # 26
                     Column('order_layer', Integer),  # 27
                     Column('documentazione', Text),  # 28
                     Column('unita_tipo', Text),  # campi aggiunti per USM    #29
                     Column('settore', Text),  # 30
                     Column('quad_par', Text),  # 31
                     Column('ambient', Text),  # 32
                     Column('saggio', Text),  # 33
                     Column('elem_datanti', Text),  # 34
                     Column('funz_statica', Text),  # 35
                     Column('lavorazione', Text),  # 36
                     Column('spess_giunti', Text),  # 37
                     Column('letti_posa', Text),  # 38
                     Column('alt_mod', Text),  # 39
                     Column('un_ed_riass', Text),  # 40
                     Column('reimp', Text),  # 41
                     Column('posa_opera', Text),  # 42
                     Column('quota_min_usm', Numeric(6, 2)),  # 43
                     Column('quota_max_usm', Numeric(6, 2)),  # 44
                     Column('cons_legante', Text),  # 45
                     Column('col_legante', Text),  # 46
                     Column('aggreg_legante', Text),  # 47
                     Column('con_text_mat', Text),  # 48
                     Column('col_materiale', Text),  # 49
                     Column('inclusi_materiali_usm', Text),  # 50
                     Column('n_catalogo_generale', Text),  # 51 campi aggiunti per archeo 3.0 e allineamento ICCD
                     Column('n_catalogo_interno', Text),  # 52
                     Column('n_catalogo_internazionale', Text),  #53
                     Column('soprintendenza', Text),  #54
                     Column('quota_relativa', Numeric(6, 2)),  #55
                     Column('quota_abs', Numeric(6, 2)),  #56
                     Column('ref_tm', Text),  #57
                     Column('ref_ra', Text),  #58
                     Column('ref_n', Text),  #59 OK
                     Column('posizione', Text),  #60
                     Column('criteri_distinzione', Text),  #61
                     Column('modo_formazione', Text),  #62
                     Column('componenti_organici', Text),  #63
                     Column('componenti_inorganici', Text),  #64
                     Column('lunghezza_max', Numeric(6, 2)),  #65
                     Column('altezza_max', Numeric(6, 2)),  #66 ok
                     Column('altezza_min', Numeric(6, 2)),  #67
                     Column('profondita_max', Numeric(6, 2)),  #68
                     Column('profondita_min', Numeric(6, 2)),  #69 ok
                     Column('larghezza_media', Numeric(6, 2)),  #70
                     Column('quota_max_abs', Numeric(6, 2)),  #71
                     Column('quota_max_rel', Numeric(6, 2)),  #72
                     Column('quota_min_abs', Numeric(6, 2)),  #73
                     Column('quota_min_rel', Numeric(6, 2)),  #74
                     Column('osservazioni', Text),  #75
                     Column('datazione', Text),  #76
                     Column('flottazione', Text),  #77
                     Column('setacciatura', Text),  #78
                     Column('affidabilita', Text),  #79
                     Column('direttore_us', Text),  #80
                     Column('responsabile_us', Text),  #81
                     Column('cod_ente_schedatore', Text),  #82
                     Column('data_rilevazione', String(20)),  #83
                     Column('data_rielaborazione', String(20)),  #84
                     Column('lunghezza_usm', Numeric(6, 2)),  #85
                     Column('altezza_usm', Numeric(6, 2)),  #86
                     Column('spessore_usm', Numeric(6, 2)),  #87
                     Column('tecnica_muraria_usm', Text),  #88 ok
                     Column('modulo_usm', Text),  #89
                     Column('campioni_malta_usm', Text),  #90
                     Column('campioni_mattone_usm', Text),  #91
                     Column('campioni_pietra_usm', Text),  #92 ok
                     Column('provenienza_materiali_usm', Text),  #93
                     Column('criteri_distinzione_usm', Text),  #94
                     Column('uso_primario_usm', Text),  #95 ok
                     Column('tipologia_opera', Text),  #95 ok
                     Column('sezione_muraria', Text),  #95 ok
                     Column('superficie_analizzata', Text),  #95 ok
                     Column('orientamento', Text),  #95 ok
                     Column('materiali_lat', Text),  #95 ok
                     Column('lavorazione_lat', Text),  #95 ok
                     Column('consistenza_lat', Text),  #95 ok
                     Column('forma_lat', Text),  #95 ok
                     Column('colore_lat', Text),  #95 ok
                     Column('impasto_lat', Text),  #95 ok
                     Column('forma_p', Text),  #95 ok
                     Column('colore_p', Text),  #95 ok
                     Column('taglio_p', Text),  #95 ok
                     Column('posa_opera_p', Text),  #95 ok
                     Column('inerti_usm', Text),  #95 ok
                     Column('tipo_legante_usm', Text),  #95 ok
                     Column('rifinitura_usm', Text),  #95 ok
                     Column('materiale_p', Text),  #95 ok
                     Column('consistenza_p', Text),  #95 ok
                     Column('rapporti2', Text),  #95 ok
                     Column('doc_usv', Text),  #95 ok

                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('sito', 'area', 'us','unita_tipo', name='ID_us_unico')
                     )

    metadata.create_all(engine)
