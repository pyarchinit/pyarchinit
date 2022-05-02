'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class DETETA(object):
    # def __init__"
    def __init__(self,
                 id_det_eta,
                 sito,
                 nr_individuo,
                 sinf_min,
                 sinf_max,
                 sinf_min_2,
                 sinf_max_2,
                 SSPIA,
                 SSPIB,
                 SSPIC,
                 SSPID,
                 sup_aur_min,
                 sup_aur_max,
                 sup_aur_min_2,
                 sup_aur_max_2,
                 ms_sup_min,
                 ms_sup_max,
                 ms_inf_min,
                 ms_inf_max,
                 usura_min,
                 usura_max,
                 Id_endo,
                 Is_endo,
                 IId_endo,
                 IIs_endo,
                 IIId_endo,
                 IIIs_endo,
                 IV_endo,
                 V_endo,
                 VI_endo,
                 VII_endo,
                 VIIId_endo,
                 VIIIs_endo,
                 IXd_endo,
                 IXs_endo,
                 Xd_endo,
                 Xs_endo,
                 endo_min,
                 endo_max,
                 volta_1,
                 volta_2,
                 volta_3,
                 volta_4,
                 volta_5,
                 volta_6,
                 volta_7,
                 lat_6,
                 lat_7,
                 lat_8,
                 lat_9,
                 lat_10,
                 volta_min,
                 volta_max,
                 ant_lat_min,
                 ant_lat_max,
                 ecto_min,
                 ecto_max):
        self.id_det_eta = id_det_eta  # 1
        self.sito = sito  # 2
        self.nr_individuo = nr_individuo  # 3
        self.sinf_min = sinf_min  # 4
        self.sinf_max = sinf_max  # 5
        self.sinf_min_2 = sinf_min  # 4
        self.sinf_max_2 = sinf_max  # 5
        self.SSPIA = SSPIA  # 6
        self.SSPIB = SSPIB  # 7
        self.SSPIC = SSPIC  # 8
        self.SSPID = SSPID  # 9
        self.sup_aur_min = sup_aur_min  # 10
        self.sup_aur_max = sup_aur_max  # 11
        self.sup_aur_min_2 = sup_aur_min  # 12
        self.sup_aur_max_2 = sup_aur_max  # 13
        self.ms_sup_min = ms_sup_min  # 14
        self.ms_sup_max = ms_sup_max  # 15
        self.ms_inf_min = ms_inf_min  # 16
        self.ms_inf_max = ms_inf_max  # 17
        self.usura_min = usura_min  # 18
        self.usura_max = usura_max  # 19
        self.Id_endo = Id_endo  # 20
        self.Is_endo = Is_endo  # 21
        self.IId_endo = IId_endo  # 22
        self.IIs_endo = IIs_endo  # 23
        self.IIId_endo = IIId_endo  # 24
        self.IIIs_endo = IIIs_endo  # 25
        self.IV_endo = IV_endo  # 26
        self.V_endo = V_endo  # 27
        self.VI_endo = VI_endo  # 28
        self.VII_endo = VII_endo  # 29
        self.VIIId_endo = VIIId_endo  # 30
        self.VIIIs_endo = VIIIs_endo  # 31
        self.IXd_endo = IXd_endo  # 32
        self.IXs_endo = IXs_endo  # 33
        self.Xd_endo = Xd_endo  # 34
        self.Xs_endo = Xs_endo  # 35
        self.endo_min = endo_min  # 36
        self.endo_max = endo_max  # 37
        self.volta_1 = volta_1  # 38
        self.volta_2 = volta_2  # 39
        self.volta_3 = volta_3  # 40
        self.volta_4 = volta_4  # 41
        self.volta_5 = volta_5  # 42
        self.volta_6 = volta_6  # 43
        self.volta_7 = volta_7  # 44
        self.lat_6 = lat_6  # 45
        self.lat_7 = lat_7  # 46
        self.lat_8 = lat_8  # 47
        self.lat_9 = lat_9  # 48
        self.lat_10 = lat_10  # 49
        self.volta_min = volta_min  # 50
        self.volta_max = volta_max  # 51
        self.ant_lat_min = ant_lat_min  # 52
        self.ant_lat_max = ant_lat_max  # 53
        self.ecto_min = ecto_min  # 54
        self.ecto_max = ecto_max  # 55

    # def __repr__"
    def __repr__(self):
        return "<DETETA('%d','%s','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d')>" % (
            self.id_det_eta,
            self.sito,
            self.nr_individuo,
            self.sinf_min,
            self.sinf_max,
            self.sinf_min_2,
            self.sinf_max_2,
            self.SSPIA,
            self.SSPIB,
            self.SSPIC,
            self.SSPID,
            self.sup_aur_min,
            self.sup_aur_max,
            self.sup_aur_min_2,
            self.sup_aur_max_2,
            self.ms_sup_min,
            self.ms_sup_max,
            self.ms_inf_min,
            self.ms_inf_max,
            self.usura_min,
            self.usura_max,
            self.Id_endo,
            self.Is_endo,
            self.IId_endo,
            self.IIs_endo,
            self.IIId_endo,
            self.IIIs_endo,
            self.IV_endo,
            self.V_endo,
            self.VI_endo,
            self.VII_endo,
            self.VIIId_endo,
            self.VIIIs_endo,
            self.IXd_endo,
            self.IXs_endo,
            self.Xd_endo,
            self.Xs_endo,
            self.endo_min,
            self.endo_max,
            self.volta_1,
            self.volta_2,
            self.volta_3,
            self.volta_4,
            self.volta_5,
            self.volta_6,
            self.volta_7,
            self.lat_6,
            self.lat_7,
            self.lat_8,
            self.lat_9,
            self.lat_10,
            self.volta_min,
            self.volta_max,
            self.ant_lat_min,
            self.ant_lat_max,
            self.ecto_min,
            self.ecto_max
        )
