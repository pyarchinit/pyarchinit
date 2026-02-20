import uuid


class COMPUTO_METRICO(object):
    def __init__(self,
                 id_computo,          # 0
                 sito,                # 1
                 nome_calcolo,        # 2
                 tipo_calcolo,        # 3
                 dem_pre,             # 4
                 dem_post,            # 5
                 layer_poligono,      # 6
                 area_mq,             # 7
                 volume_mc,           # 8
                 quota_min,           # 9
                 quota_max,           # 10
                 data_calcolo,        # 11
                 fase_scavo,          # 12
                 note,                # 13
                 entity_uuid=None     # 14
                 ):
        self.id_computo = id_computo
        self.sito = sito
        self.nome_calcolo = nome_calcolo
        self.tipo_calcolo = tipo_calcolo
        self.dem_pre = dem_pre
        self.dem_post = dem_post
        self.layer_poligono = layer_poligono
        self.area_mq = area_mq
        self.volume_mc = volume_mc
        self.quota_min = quota_min
        self.quota_max = quota_max
        self.data_calcolo = data_calcolo
        self.fase_scavo = fase_scavo
        self.note = note
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    def __repr__(self):
        return "<COMPUTO_METRICO('%d','%s','%s')>" % (
            self.id_computo, self.sito, self.nome_calcolo)
