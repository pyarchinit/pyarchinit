'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class INVENTARIO_MATERIALI(object):
    # def __init__"
    def __init__(self,
                 id_invmat,
                 sito,
                 numero_inventario,
                 tipo_reperto,
                 criterio_schedatura,
                 definizione,
                 descrizione,
                 area,
                 us,
                 lavato,
                 nr_cassa,
                 luogo_conservazione,
                 stato_conservazione,
                 datazione_reperto,
                 elementi_reperto,
                 misurazioni,
                 rif_biblio,
                 tecnologie,
                 forme_minime,
                 forme_massime,
                 totale_frammenti,
                 corpo_ceramico,
                 rivestimento,
                 diametro_orlo,
                 peso,
                 tipo,
                 eve_orlo,
                 repertato,
                 diagnostico,
                 n_reperto,
                 tipo_contenitore,
                 struttura,
                 years,
                 schedatore,
                 date_scheda,
                 punto_rinv,
                 negativo_photo,
                 diapositiva,
                 quota_usm,
                 unita_misura_quota,
                 photo_id,
                 drawing_id,
                 entity_uuid
                 ):
        self.id_invmat = id_invmat  # 0
        self.sito = sito  # 1
        self.numero_inventario = numero_inventario  # 2
        self.tipo_reperto = tipo_reperto  # 3
        self.criterio_schedatura = criterio_schedatura  # 4
        self.definizione = definizione  # 5
        self.descrizione = descrizione  # 6
        self.area = area  # 7
        self.us = us  # 8
        self.lavato = lavato  # 9
        self.nr_cassa = nr_cassa  # 10
        self.luogo_conservazione = luogo_conservazione  # 11
        self.stato_conservazione = stato_conservazione  # 12
        self.datazione_reperto = datazione_reperto  # 13
        self.elementi_reperto = elementi_reperto  # 14
        self.misurazioni = misurazioni  # 15
        self.rif_biblio = rif_biblio  # 16
        self.tecnologie = tecnologie  # 17
        self.forme_minime = forme_minime  # 18
        self.forme_massime = forme_massime  # 19
        self.totale_frammenti = totale_frammenti  # 20
        self.corpo_ceramico = corpo_ceramico  # 21
        self.rivestimento = rivestimento  # 22
        self.diametro_orlo = diametro_orlo  # 23
        self.peso = peso  # 24
        self.tipo = tipo  # 25
        self.eve_orlo = eve_orlo  # 26
        self.repertato = repertato  # 27
        self.diagnostico = diagnostico  # 28
        self.n_reperto = n_reperto  # 29
        self.tipo_contenitore = tipo_contenitore  # 30
        self.struttura = struttura  # 31
        self.years = years  # 32
        self.schedatore = schedatore  # 33
        self.date_scheda = date_scheda  # 34
        self.punto_rinv = punto_rinv  # 35
        self.negativo_photo = negativo_photo  # 36
        self.diapositiva = diapositiva  # 37
        self.quota_usm = quota_usm  # 38
        self.unita_misura_quota = unita_misura_quota  # 39
        self.photo_id = photo_id  # 40
        self.drawing_id = drawing_id  # 41
        self.entity_uuid = entity_uuid

    # def __repr__"
    def __repr__(self):
        return "<INVENTARIO_MATERIALI('%d', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%d', '%d', '%s', '%s', '%r', '%r', '%s', '%r', '%s', '%s', '%d', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%r', '%s', '%s', '%s')>" % (
            self.id_invmat,
            self.sito,
            self.numero_inventario,
            self.tipo_reperto,
            self.criterio_schedatura,
            self.definizione,
            self.descrizione,
            self.area,
            self.us,
            self.lavato,
            self.nr_cassa,
            self.luogo_conservazione,
            self.stato_conservazione,
            self.datazione_reperto,
            self.elementi_reperto,
            self.misurazioni,
            self.rif_biblio,
            self.tecnologie,
            self.forme_minime,
            self.forme_massime,
            self.totale_frammenti,
            self.corpo_ceramico,
            self.rivestimento,
            self.diametro_orlo,
            self.peso,
            self.tipo,
            self.eve_orlo,
            self.repertato,
            self.diagnostico,
            self.n_reperto,
            self.tipo_contenitore,
            self.struttura,
            self.years,
            self.schedatore,
            self.date_scheda,
            self.punto_rinv,
            self.negativo_photo,
            self.diapositiva,
            self.quota_usm,
            self.unita_misura_quota,
            self.photo_id,
            self.drawing_id
        )
