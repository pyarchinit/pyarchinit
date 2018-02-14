l1 = [u'Necropoli di Malignano, Sovicille (Si)', u'536', u'Reperto ceramico', u'Vernice nera', u'Forma aperta', u"2 frammenti di parete contigui che conservano parzialmente la decorazione centrale a palmette e fiori di loto incorniciati da cerchi incisi.\nVernice omogenea con chiazze brune e linee di tornitura all'esterno della vasca.", u'2', u'1', u'Si', u'None', u'Comune Sovicille', u'', u'', u"[[u'parete', u'frammenti', u'2']]", u"[[u'peso', u'g', u'24'], [u'forme massime', u'1'], [u'forme minime', u'1']]", u'[]', u"[[u'Impasto', u'I'], [u'Vernice', u'A2']]", u'1', u'1', u'None', u'I', u'A2', u'0.000', u'24.000', u'', u'0.000'] temp [u'Necropoli di Malignano, Sovicille (Si)', u'536', u'Reperto ceramico', u'Vernice nera', u'Forma aperta', u"2 frammenti di parete contigui che conservano parzialmente la decorazione centrale a palmette e fiori di loto incorniciati da cerchi incisi.\nVernice omogenea con chiazze brune e linee di tornitura all'esterno della vasca.", u'2', u'1', u'Si', u'None', u'Comune Sovicille', u'', u'', u"[[u'parete', u'frammenti', u'2']]", u"[[u'forme massime', u'1'], [u'forme minime', u'1'], [u'peso', u'g', u'24']]", u'[]', u"[[u'Impasto', u'I'], [u'Vernice', u'A2']]", u'1', u'1', u'None', u'I', u'A2', u'0.000', u'24.000', u'', u'0.000']
l2 =   [u'Necropoli di Malignano, Sovicille (Si)', u'3', u'Reperto ceramico', u'Vernice nera', u'Coppa', u"Coppa di forma conica presumibilmente biansata, frammentaria ricomposta parzialmente da 11 frammenti contigui che ne restituiscono il profilo completo ad eccezione dell'ansa, verticale, di cui rimane traccia sulla parete esterna. Orlo leggermente assottigliato e arrotondato superiormente. Parete decorata esternamente all'altezza dell'attaccatura inferiore dell'ansa con linee parallele incise orizzontalmente che corrono per tutta la circonferenza interrompendosi in prossimita' dell'ansa. Piede distinto, svasato, con spigolo laterale. \nVernice liscia e uniforme con piccole chiazze rossastre attorno al piede segno dell'applicazione delle dita. Fondo esterno parzialmente verniciato. Tracce di tornitura leggermente visibili all'esterno, invisibili all'interno. \nForma:l'assenza dell'ansa non permette di definirne accuratamente la forma. Genere Morel 3100, tra la forma Pasquinucci 48 e Pasquinucci 127.\nLa maggior parte dei frammenti proviene dallo scavo del '65 (US1), solo una parete dallo scavo del 2002 US3018/228", u'2', u'3018', u'Si', u'1', u'Magazzino Sovicille', u'Buono', u'III - II sec. a.C.', u"[[u'orlo', u'frammenti', u'6'], [u'parete', u'frammenti', u'3'], [u'piede', u'frammenti', u'2']]", u"[[u'altezza', u'cm', u'7,6'], [u'conservazione orlo', u'percento', u'60'], [u'diametro orlo', u'cm', u'13'], [u'diametro piede esterno', u'cm', u'4,6'], [u'diametro piede interno', u'cm', u'3,4'], [u'forme massime', u'1'], [u'forme minime', u'1'], [u'spessore max', u'cm', u'0,75'], [u'spessore orlo', u'cm', u'0,4']]", u"[[u'Montagna Pasquinucci', u'1972', u'', u'338-344', u'Inv. 44'], [u'Montagna Pasquinucci', u'1972', u'', u'400-403', u'Inv. 28'], [u'Schippa', u'1990', u'43-44']]", u"[[u'Impasto', u'0'], [u'Vernice', u'A3']]", u'0', u'0', u'None', u'0', u'A3', u'13.000', u'0.000', u'', u'60.000']


for i in range(len(l1)):
    if l1[i] != l2[i]:
        print str(l1[i] ) + "   !=  " + str(l2[i] )
    else:
        print "ok"








