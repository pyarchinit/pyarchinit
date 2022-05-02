'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class DETSESSO(object):
    # def __init__"
    def __init__(self,
                 id_det_sesso,
                 sito,
                 num_individuo,
                 glab_grado_imp,
                 pmast_grado_imp,
                 pnuc_grado_imp,
                 pzig_grado_imp,
                 arcsop_grado_imp,
                 tub_grado_imp,
                 pocc_grado_imp,
                 inclfr_grado_imp,
                 zig_grado_imp,
                 msorb_grado_imp,
                 glab_valori,
                 pmast_valori,
                 pnuc_valori,
                 pzig_valori,
                 arcsop_valori,
                 tub_valori,
                 pocc_valori,
                 inclfr_valori,
                 zig_valori,
                 msorb_valori,
                 palato_grado_imp,
                 mfmand_grado_imp,
                 mento_grado_imp,
                 anmand_grado_imp,
                 minf_grado_imp,
                 brmont_grado_imp,
                 condm_grado_imp,
                 palato_valori,
                 mfmand_valori,
                 mento_valori,
                 anmand_valori,
                 minf_valori,
                 brmont_valori,
                 condm_valori,
                 sex_cr_tot,
                 ind_cr_sex,
                 sup_p_I,
                 sup_p_II,
                 sup_p_III,
                 sup_p_sex,
                 in_isch_I,
                 in_isch_II,
                 in_isch_III,
                 in_isch_sex,
                 arco_c_sex,
                 ramo_ip_I,
                 ramo_ip_II,
                 ramo_ip_III,
                 ramo_ip_sex,
                 prop_ip_sex,
                 ind_bac_sex):
        self.id_det_sesso = id_det_sesso  # 1
        self.sito = sito  # 2
        self.num_individuo = num_individuo  # 3
        self.glab_grado_imp = glab_grado_imp  # 4
        self.pmast_grado_imp = pmast_grado_imp  # 5
        self.pnuc_grado_imp = pnuc_grado_imp  # 6
        self.pzig_grado_imp = pzig_grado_imp  # 7
        self.arcsop_grado_imp = arcsop_grado_imp  # 8
        self.tub_grado_imp = tub_grado_imp  # 9
        self.pocc_grado_imp = pocc_grado_imp  # 10
        self.inclfr_grado_imp = inclfr_grado_imp  # 11
        self.zig_grado_imp = zig_grado_imp  # 12
        self.msorb_grado_imp = msorb_grado_imp  # 13
        self.glab_valori = glab_valori  # 14
        self.pmast_valori = pmast_valori  # 15
        self.pnuc_valori = pnuc_valori  # 16
        self.pzig_valori = pzig_valori  # 17
        self.arcsop_valori = arcsop_valori  # 18
        self.tub_valori = tub_valori  # 19
        self.pocc_valori = pocc_valori  # 20
        self.inclfr_valori = inclfr_valori  # 21
        self.zig_valori = zig_valori  # 22
        self.msorb_valori = msorb_valori  # 23
        self.palato_grado_imp = palato_grado_imp  # 24
        self.mfmand_grado_imp = mfmand_grado_imp  # 25
        self.mento_grado_imp = mento_grado_imp  # 26
        self.anmand_grado_imp = anmand_grado_imp  # 27
        self.minf_grado_imp = minf_grado_imp  # 28
        self.brmont_grado_imp = brmont_grado_imp  # 29
        self.condm_grado_imp = condm_grado_imp  # 30
        self.palato_valori = palato_valori  # 31
        self.mfmand_valori = mfmand_valori  # 32
        self.mento_valori = mento_valori  # 33
        self.anmand_valori = anmand_valori  # 34
        self.minf_valori = minf_valori  # 35
        self.brmont_valori = brmont_valori  # 36
        self.condm_valori = condm_valori  # 37
        self.sex_cr_tot = sex_cr_tot  # 38
        self.ind_cr_sex = ind_cr_sex  # 39
        self.sup_p_I = sup_p_I  # 40
        self.sup_p_II = sup_p_II  # 41
        self.sup_p_III = sup_p_III  # 42
        self.sup_p_sex = sup_p_sex  # 43
        self.in_isch_I = in_isch_I  # 44
        self.in_isch_II = in_isch_II  # 45
        self.in_isch_III = in_isch_III  # 46
        self.in_isch_sex = in_isch_sex  # 47
        self.arco_c_sex = arco_c_sex  # 48
        self.ramo_ip_I = ramo_ip_I  # 49
        self.ramo_ip_II = ramo_ip_II  # 50
        self.ramo_ip_III = ramo_ip_III  # 51
        self.ramo_ip_sex = ramo_ip_sex  # 52
        self.prop_ip_sex = prop_ip_sex  # 53
        self.ind_bac_sex = ind_bac_sex  # 54

    # def __repr__"
    def __repr__(self):
        return "<DETSESSO('%d','%s','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d', '%d', '%d', '%d', '%d', '%d','%d','%d','%d','%d','%r','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_det_sesso,
            self.sito,
            self.num_individuo,
            self.glab_grado_imp,
            self.pmast_grado_imp,
            self.pnuc_grado_imp,
            self.pzig_grado_imp,
            self.arcsop_grado_imp,
            self.tub_grado_imp,
            self.pocc_grado_imp,
            self.inclfr_grado_imp,
            self.zig_grado_imp,
            self.msorb_grado_imp,
            self.glab_valori,
            self.pmast_valori,
            self.pnuc_valori,
            self.pzig_valori,
            self.arcsop_valori,
            self.tub_valori,
            self.pocc_valori,
            self.inclfr_valori,
            self.zig_valori,
            self.msorb_valori,
            self.palato_grado_imp,
            self.mfmand_grado_imp,
            self.mento_grado_imp,
            self.anmand_grado_imp,
            self.minf_grado_imp,
            self.brmont_grado_imp,
            self.condm_grado_imp,
            self.palato_valori,
            self.mfmand_valori,
            self.mento_valori,
            self.anmand_valori,
            self.minf_valori,
            self.brmont_valori,
            self.condm_valori,
            self.sex_cr_tot,
            self.ind_cr_sex,
            self.sup_p_I,
            self.sup_p_II,
            self.sup_p_III,
            self.sup_p_sex,
            self.in_isch_I,
            self.in_isch_II,
            self.in_isch_III,
            self.in_isch_sex,
            self.arco_c_sex,
            self.ramo_ip_I,
            self.ramo_ip_II,
            self.ramo_ip_III,
            self.ramo_ip_sex,
            self.prop_ip_sex,
            self.ind_bac_sex
        )
