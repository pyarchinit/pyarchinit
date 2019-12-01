import re


# percentuale delle forme in base al totale di tutte le forme
# percentuale diviso il singolo arco cronologico della forma
# assegnazione della singola frazione al cinquantennio
# somma delle frazioni per cinquantennio

class Cronology_convertion:
    def sum_list_of_tuples_for_value(self, l):
        self.l = l
        self.l.sort()
        cfr_txt = self.l[0][0]
        number = self.l[0][1]
        res_list = []
        for i in range(len(self.l)):
            if len(self.l) == 1:
                temp_tup = (cfr_txt, number)
                res_list.append(temp_tup)
            elif i > 0:
                if self.l[i][0] == cfr_txt:
                    number += self.l[i][1]

                if self.l[i][0] != cfr_txt and i < len(self.l) - 1:
                    temp_tup = (cfr_txt, number)
                    res_list.append(temp_tup)

                    cfr_txt = self.l[i][0]
                    number = self.l[i][1]

                if self.l[i][0] == cfr_txt and i == len(self.l) - 1:
                    temp_tup = (cfr_txt, number)
                    res_list.append(temp_tup)

                if self.l[i][0] != cfr_txt and i == len(self.l) - 1:
                    temp_tup1, temp_tup2 = (cfr_txt, number), (self.l[i][0], self.l[i][1])
                    res_list.append(temp_tup1)
                    res_list.append(temp_tup2)
        return res_list

    def convert_data(self, datazione_reperto):

        conversion_dict = {"I sec. a.C.": (-99, 0),
                           "II sec. a.C.": (-199, -100),
                           "III sec. a.C.": (-299, -200),
                           "III": (-299, -200),
                           "IV sec. a.C.": (-399, -300),
                           "IV": (-399, -300),
                           "V sec. a.C.": (-499, -400),
                           "VI sec. a.C.": (-599, -500),
                           "VII sec. a.C.": (-699, -600),
                           "II meta' I sec. a.C.": (-51, -1),
                           "I meta' I sec. a.C.": (-99, -50),
                           "II meta' II sec. a.C.": (-151, -100),
                           "I meta' II sec. a.C.": (-199, -151),
                           "II meta' III sec. a.C.": (-250, -200),
                           "II meta' II": (-250, -200),
                           "I meta' III sec. a.C.": (-299, -251),
                           "II meta' IV sec. a.C.": (-350, -300),
                           "II meta' IV": (-350, -300),
                           "I meta' IV sec. a.C.": (-399, -351),
                           "II meta' V sec. a.C.": (-450, -400),
                           "I meta' V sec. a.C.": (-499, -451),
                           "II meta' VI sec. a.C.": (-550, -500),
                           "I meta' VI sec. a.C.": (-599, -551),
                           "II": (-199, -100),
                           "Fine I sec. a.C.": (-15, 0),
                           "Fine III": (-215, -200),
                           "Fine IV": (-315, -300),
                           "Fine IV sec. a.C.": (-315, -300),
                           "Fine III sec. a.C.": (-215, -200),
                           "Fine III - II sec. a.C.": (-275, -100),
                           "inizi I sec. a.C.": (-99, -75),
                           "inizi II sec. a.C.": (-199, -175),
                           "inizi III sec. a.C.": (-299, -275),
                           "Inizi I sec. a.C.": (-99, -75),
                           "Inizi II sec. a.C.": (-199, -175),
                           "Inizi III sec. a.C.": (-299, -275),
                           "meta' II sec. a.C.": (-175, -125),
                           "Meta' II": (-175, -125),
                           "Meta' III sec. a.C.": (-275, -225),
                           "Meta' IV sec. a.C.": (-375, -325),
                           "Meta' IV": (-375, -325)}

        datazione_reperto_copy = datazione_reperto
        dat_iniziale = ""
        dat_finale = ""
        intervallo_temporale = ""

        i_stringa = 0
        for k, v in list(conversion_dict.items()):
            p = re.compile(k)
            res = p.match(datazione_reperto)

            if res != None:
                dat_iniziale = conversion_dict[k]
                i_stringa = len(k) + 3

        if i_stringa > 0:
            datazione_reperto = datazione_reperto[i_stringa:]
            for k, v in list(conversion_dict.items()):
                p = re.compile(k)
                res = p.match(datazione_reperto)
                if res != None:
                    # print k, ": ", conversion_dict[k]
                    dat_finale = conversion_dict[k]
        intervallo_temporale = []
        if dat_iniziale != "" and dat_finale == "":
            intervallo_temporale = [int(dat_iniziale[0]), int(dat_iniziale[1])]
        elif dat_iniziale != "" and dat_finale != "":
            intervallo_temporale = [int(dat_iniziale[0]), int(dat_finale[1])]

            # return "intervallo_temporale: " + datazione_reperto_copy +
        return intervallo_temporale

    def found_intervallo_per_forma(self, data):
        pass

    def calc_percent(self, val_parz, val_totale):
        # parz : tot = x = 100
        perc = val_parz * 100 / val_totale
        return perc

    def media_ponderata_perc_intervallo(self, lista_dati, valore):
        lista_dati_dup = lista_dati
        lista_dati_dup.sort()
        cron_iniz = ""
        cron_fin = ""
        cron_fin_temp = ""
        for i in lista_dati_dup:
            if i[0] == valore and cron_iniz == "":
                cron_iniz = i[1][0]
                cron_fin = i[1][1]
                cron_fin_temp = i[1][1]
            if i[0] != valore and cron_iniz != "":
                cron_fin = cron_fin_temp
                return cron_iniz, cron_fin
        return cron_iniz, cron_fin

    def totale_forme_min(self, data):
        cont = 0
        for sing_rec in data:
            cont += sing_rec[1]
        return cont

    def intervallo_numerico(self, lista_intervalli_cron_i_f):
        lista_intervallo_numerico = []
        for i in lista_intervalli_cron_i_f:
            intervallo_numerico = i[1][1] - i[1][0]
            lista_intervallo_numerico.append([i[0], intervallo_numerico])
        return lista_intervallo_numerico

    def check_value_parz_in_rif_value(self, val_parz, val_rif):

        if val_parz[0] > val_rif[1]:
            return 0
        elif val_parz[0] < val_rif[0] and val_parz[1] < val_rif[0]:
            return 0

        else:
            return 1


######################################################

conversion_dict = {"I sec. a.C.": (-99, 0),
                   "II sec. a.C.": (-199, -100),
                   "III sec. a.C.": (-299, -200),
                   "IV sec. a.C.": (-399, -300),
                   "V sec. a.C.": (-499, -400),
                   "VI sec. a.C.": (-599, -500),
                   "VII sec. a.C.": (-699, -600)}
##									"II meta' I sec. a.C." : (-51, -1),
##									"I meta' I sec. a.C." : (-99, -50),
##									"II meta' II sec. a.C." : (-151, -100),
##									"I meta' II sec. a.C." : (-199, -151),
##									"II meta' III sec. a.C." : (-250, -200),
##									"I meta' III sec. a.C." : (-299, -251),
##									"II meta' IV sec. a.C." : (-350, -300),
##									"I meta' IV sec. a.C." : (-399, -351),
##									"II meta' V sec. a.C." : (-450, -400),
##									"I meta' V sec. a.C." : (-499, -451),
##									"II meta' VI sec. a.C." : (-550, -500),
##									"I meta' VI sec. a.C." : (-599, -551),
##									"Fine I sec. a.C." : (-1, -1)}

data = [["morel 20", 50, "II sec. a.C."], ["morel 22", 50, "I sec. a.C."]]

CC = Cronology_convertion()

# calcola il totale delle forme minime
totale_forme_minime = CC.totale_forme_min(data)
print("totale_forme_minime: ", totale_forme_minime)
# restituisce una lista di liste con dentro forma e singoli intervalli parziali di tempo
lista_forme_dataz = []

for sing_rec in data:
    intervalli = CC.convert_data(sing_rec[2])
    lista_forme_dataz.append([sing_rec[0], intervalli])

print("lista_forme_dataz: ", lista_forme_dataz)
# crea la lista di tuple per avere il totale parziale di ogni forma
lista_tuple_forma_valore = []
for i in data:
    lista_tuple_forma_valore.append((i[0], i[1]))

# ottiene la lista di liste con tutti i totali per forma
totali_per_forma = CC.sum_list_of_tuples_for_value(lista_tuple_forma_valore)
print("totali_parziali_per_forma: ", totali_per_forma)

# ottiene la lista di liste con le perc_parziali per forma
perc_per_forma = []
for i in totali_per_forma:
    perc = CC.calc_percent(i[1], totale_forme_minime)
    perc_per_forma.append([i[0], perc])

print("perc per forma: ", perc_per_forma)

# lista valore, crono_iniz, cron_fin_globale
lista_intervalli_globali = []
valore_temp = ""
for i in lista_forme_dataz:
    if i[0] != valore_temp:
        intervallo_globale = CC.media_ponderata_perc_intervallo(lista_forme_dataz, i[0])
        lista_intervalli_globali.append([i[0], intervallo_globale])
    valore_temp = i[0]

print("lista_intervalli_globali", lista_intervalli_globali)

# lista valore / Intervallo numerico
intervallo_numerico = CC.intervallo_numerico(lista_intervalli_globali)
print("intervallo_numerico", intervallo_numerico)

# media_ponderata_singoli_valori
lista_valori_medie = []
for sing_perc in perc_per_forma:
    for sing_int in intervallo_numerico:
        if sing_int[0] == sing_perc[0]:
            valore_medio = float(sing_perc[1]) / float(sing_int[1])
            lista_valori_medie.append([sing_perc[0], valore_medio])

print("lista_valori_medie", lista_valori_medie)
# assegna valori ai singoli cinquatenni
##print CC.check_value_parz_in_rif_value([-170, -150], [-500, -400])
diz_medie_pond = {}
for forma_parz in lista_valori_medie:
    valore_riferimento = forma_parz[0]
    for sing_int in lista_intervalli_globali:
        ##		print "sing_int", sing_int
        if sing_int[0] == valore_riferimento:
            for k, v in list(conversion_dict.items()):
                ##				print sing_int[1][0], sing_int[1][1], v[0], v[1]
                test = CC.check_value_parz_in_rif_value([sing_int[1][0], sing_int[1][1]], [v[0], v[1]])
                if test == 1:
                    try:
                        ##						print k, forma_parz
                        diz_medie_pond[k] = diz_medie_pond[k] + forma_parz[1]
                    except:
                        diz_medie_pond[k] = forma_parz[1]
print(diz_medie_pond)

##l = [400, -650, -620]
##
##cron_sequence = [(-699, -651), (-650, -600)]
##for i in l:
##	#print i
##	for c in cron_sequence:
##		test = i in range(c[0],c[1])
##		#print test
##		if test == True:
##			print "ioppolo"
##		else:
##			print "nuuu"
