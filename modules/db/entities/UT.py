'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class UT(object):
    # def __init__"
    def __init__(self,
                 id_ut,  # 0
                 progetto,  # 1
                 nr_ut,  # 2
                 ut_letterale,  # 3
                 def_ut,  # 4
                 descrizione_ut,  # 5
                 interpretazione_ut,  # 6
                 nazione,  # 7
                 regione,  # 8
                 provincia,  # 9
                 comune,  # 10
                 frazione,  # 11
                 localita,  # 12
                 indirizzo,  # 13
                 nr_civico,  # 14
                 carta_topo_igm,  # 15
                 carta_ctr,  # 16
                 coord_geografiche,  # 17
                 coord_piane,  # 18
                 quota,  # 19
                 andamento_terreno_pendenza,  # 20
                 utilizzo_suolo_vegetazione,  # 21
                 descrizione_empirica_suolo,  # 22
                 descrizione_luogo,  # 23
                 metodo_rilievo_e_ricognizione,  # 24
                 geometria,  # 25
                 bibliografia,  # 26
                 data,  # 27
                 ora_meteo,  # 28
                 responsabile,  # 29
                 dimensioni_ut,  # 30
                 rep_per_mq,  # 31
                 rep_datanti,  # 32
                 periodo_I,  # 33
                 datazione_I,  # 34
                 interpretazione_I,  # 35
                 periodo_II,  # 36
                 datazione_II,  # 37
                 interpretazione_II,  # 38
                 documentazione,  # 39
                 enti_tutela_vincoli,  # 40
                 indagini_preliminari  # 41
                 ):
        self.id_ut = id_ut  # 0
        self.progetto = progetto  # 1
        self.nr_ut = nr_ut  # 2
        self.ut_letterale = ut_letterale  # 3
        self.def_ut = def_ut  # 4
        self.descrizione_ut = descrizione_ut  # 5
        self.interpretazione_ut = interpretazione_ut  # 6
        self.nazione = nazione  # 7
        self.regione = regione  # 8
        self.provincia = provincia  # 9
        self.comune = comune  # 10
        self.frazione = frazione  # 11
        self.localita = localita  # 12
        self.indirizzo = indirizzo  # 13
        self.nr_civico = nr_civico  # 14
        self.carta_topo_igm = carta_topo_igm  # 15
        self.carta_ctr = carta_ctr  # 16
        self.coord_geografiche = coord_geografiche  # 17
        self.coord_piane = coord_piane  # 18
        self.quota = quota  # 19
        self.andamento_terreno_pendenza = andamento_terreno_pendenza  # 20
        self.utilizzo_suolo_vegetazione = utilizzo_suolo_vegetazione  # 21
        self.descrizione_empirica_suolo = descrizione_empirica_suolo  # 22
        self.descrizione_luogo = descrizione_luogo  # 23
        self.metodo_rilievo_e_ricognizione = metodo_rilievo_e_ricognizione  # 24
        self.geometria = geometria  # 25
        self.bibliografia = bibliografia  # 26
        self.data = data  # 27
        self.ora_meteo = ora_meteo  # 28
        self.responsabile = responsabile  # 29
        self.dimensioni_ut = dimensioni_ut  # 30
        self.rep_per_mq = rep_per_mq  # 31
        self.rep_datanti = rep_datanti  # 32
        self.periodo_I = periodo_I  # 33
        self.datazione_I = datazione_I  # 34
        self.interpretazione_I = interpretazione_I  # 35
        self.periodo_II = periodo_II  # 36
        self.datazione_II = datazione_II  # 37
        self.interpretazione_II = interpretazione_II  # 38
        self.documentazione = documentazione  # 39
        self.enti_tutela_vincoli = enti_tutela_vincoli  # 40
        self.indagini_preliminari = indagini_preliminari  # 41

    # def __repr__"
    def __repr__(self):
        return "<UT('%d', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%f', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (

            self.id_ut,  # 0
            self.progetto,  # 1
            self.nr_ut,  # 2
            self.ut_letterale,  # 3
            self.def_ut,  # 4
            self.descrizione_ut,  # 5
            self.interpretazione_ut,  # 6
            self.nazione,  # 7
            self.regione,  # 8
            self.provincia,  # 9
            self.comune,  # 10
            self.frazione,  # 11
            self.localita,  # 12
            self.indirizzo,  # 13
            self.nr_civico,  # 14
            self.carta_topo_igm,  # 15
            self.carta_ctr,  # 16
            self.coord_geografiche,  # 17
            self.coord_piane,  # 18
            self.quota,  # 19
            self.andamento_terreno_pendenza,  # 20
            self.utilizzo_suolo_vegetazione,  # 21
            self.descrizione_empirica_suolo,  # 22
            self.descrizione_luogo,  # 23
            self.metodo_rilievo_e_ricognizione,  # 24
            self.geometria,  # 25
            self.bibliografia,  # 26
            self.data,  # 27
            self.ora_meteo,  # 28
            self.responsabile,  # 29
            self.dimensioni_ut,  # 30
            self.rep_per_mq,  # 31
            self.rep_datanti,  # 32
            self.periodo_I,  # 33
            self.datazione_I,  # 34
            self.interpretazione_I,  # 35
            self.periodo_II,  # 36
            self.datazione_II,  # 37
            self.interpretazione_II,  # 38
            self.documentazione,  # 39
            self.enti_tutela_vincoli,  # 40
            self.indagini_preliminari  # 41
        )
