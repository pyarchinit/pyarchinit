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
                 indagini_preliminari,  # 41
                 # New survey fields (v4.9.21+)
                 visibility_percent=None,  # 42
                 vegetation_coverage=None,  # 43
                 gps_method=None,  # 44
                 coordinate_precision=None,  # 45
                 survey_type=None,  # 46
                 surface_condition=None,  # 47
                 accessibility=None,  # 48
                 photo_documentation=None,  # 49
                 weather_conditions=None,  # 50
                 team_members=None,  # 51
                 foglio_catastale=None,  # 52
                 # Analysis fields (v4.9.67+)
                 potential_score=None,  # 53 - Archaeological potential score (0-100)
                 risk_score=None,  # 54 - Archaeological risk score (0-100)
                 potential_factors=None,  # 55 - JSON with factor breakdown
                 risk_factors=None,  # 56 - JSON with risk factor breakdown
                 analysis_date=None,  # 57 - Date of last analysis
                 analysis_method=None,  # 58 - Analysis method used
                 entity_uuid=None  # 59
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
        # New survey fields (v4.9.21+)
        self.visibility_percent = visibility_percent  # 42
        self.vegetation_coverage = vegetation_coverage  # 43
        self.gps_method = gps_method  # 44
        self.coordinate_precision = coordinate_precision  # 45
        self.survey_type = survey_type  # 46
        self.surface_condition = surface_condition  # 47
        self.accessibility = accessibility  # 48
        self.photo_documentation = photo_documentation  # 49
        self.weather_conditions = weather_conditions  # 50
        self.team_members = team_members  # 51
        self.foglio_catastale = foglio_catastale  # 52
        # Analysis fields (v4.9.67+)
        self.potential_score = potential_score  # 53
        self.risk_score = risk_score  # 54
        self.potential_factors = potential_factors  # 55
        self.risk_factors = risk_factors  # 56
        self.analysis_date = analysis_date  # 57
        self.analysis_method = analysis_method  # 58
        self.entity_uuid = entity_uuid  # 59

    # def __repr__"
    def __repr__(self):
        return f"<UT(id_ut={self.id_ut}, progetto={self.progetto}, nr_ut={self.nr_ut})>"
