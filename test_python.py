
#variabili
var_1 = "a"
var_2 = 34

#liste
l_1 = ["a", 34]
l_2 = [l_1, var_1, var_2]

#tuple
t_1 = (1, 2, 3, 4)
t_2 = (l_2, var_1, var_2)

#dizionari
diz_1 = {'a_1' : "valore primo", 'a_2': "valore secondo"}

#stringhe
s_1 = "il mondo e bello"

#elaborazioni
#stringhe
e_1 = s_1.find("mondo")
e_2 = s_1[e_1:]

#lista
e_3 = l_2[2]
e_4 = dir(l_2)
l_3 = []
l_3.append("gigi")
l_3.append(s_1)
l_3.append(1)
l_3.sort()
l_3.reverse()

#db con lista
db_1 = [["a", 12, "mondo"], ["b", 13, "casa"], ["c", 14, "monte"]]

#dizionari
e_5 = diz_1['a_1']

diz_1["c_1"] = 3

#iterazioni
#while
##cont = 0
##while cont != 2:
##	print db_1[cont]
##	cont += 1

#for

##for r in db_1:
##	print r
##
##for n in range(len(db_1)):
##	print db_1[n]

#condizioni

var_1 = "gigi"
var_2 = "gigi"

if var_1 != var_2:
	print("Vero")
else:
	print("Falso")

### il mio primo paciugo ###

l_3 = [[0,"il"], 
		[1, "mondo"], 
		[3, "piace"], 
		[2, "non"], 
		[4, "mi"]]

res_str = []


for n in range(len(l_3)):
	if l_3[n][0] != 2:
		res_str.append(l_3[n][1])

print(res_str)

###
#print diz_1.items()


class Mia_classe:
	
	def __init__(self,data):
		self.data = data
	
	def print_lista(self):
		for i in self.data:
			return i

test = Mia_classe(db_1)
print(test.print_lista())
