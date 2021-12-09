'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class INVENTARIO_MATERIALI_TOIMP(object):
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
                 rivestimento
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

    # def __repr__"
    def __repr__(self):
        return "<INVENTARIO_MATERIALI_TOIMP('%d', '%s', '%d', '%s', '%s', '%s', '%s', '%d', '%d', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%d', '%d','%s', '%s')>" % (
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
            self.rivestimento
        )
