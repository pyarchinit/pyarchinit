'''
Created on 05 dic 2022

@author:  Enzo Cocca <enzo.ccc@gmail.com>
'''



class POTTERY(object):
	#def __init__"
	def __init__(self,
				id_rep,
				id_number,
				sito,
				area,
				us,
				box,
				photo,
				drawing,
				anno,
				fabric,
				percent,
				material,
				form,
				specific_form,
				ware,
				munsell,
				surf_trat,
				exdeco,
				intdeco,
				wheel_made,
				descrip_ex_deco,
				descrip_in_deco,
				note,
				diametro_max,
				qty,
				diametro_rim,
				diametro_bottom,
				diametro_height,
				diametro_preserved,
				specific_shape,
				bag,
				sector,
				decoration_type,
				decoration_motif,
				decoration_position,
				datazione
				):
		self.id_rep=id_rep
		self.id_number=id_number
		self.sito=sito
		self.area=area
		self.us=us
		self.box=box
		self.photo=photo
		self.drawing=drawing
		self.anno=anno
		self.fabric=fabric
		self.percent=percent
		self.material=material
		self.form=form
		self.specific_form=specific_form
		self.ware=ware
		self.munsell=munsell
		self.surf_trat=surf_trat
		self.exdeco=exdeco
		self.intdeco=intdeco
		self.wheel_made=wheel_made
		self.descrip_ex_deco=descrip_ex_deco
		self.descrip_in_deco=descrip_in_deco
		self.note=note
		self.diametro_max=diametro_max
		self.qty=qty
		self.diametro_rim=diametro_rim
		self.diametro_bottom=diametro_bottom
		self.diametro_height=diametro_height
		self.diametro_preserved=diametro_preserved
		self.specific_shape=specific_shape
		self.bag=bag
		self.sector = sector
		self.decoration_type = decoration_type
		self.decoration_motif = decoration_motif
		self.decoration_position = decoration_position
		self.datazione = datazione
	#def __repr__"
	def __repr__(self):
		return "<POTTERY('%d','%d','%s','%s',%d,'%d','%s', '%s', '%d', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%r','%d','%r','%r','%r','%r','%s','%d','%s','%s','%s','%s','%s')>" % (
		self.id_rep,
		self.id_number,
		self.sito,
		self.area,
		self.us,
		self.box,
		self.photo,
		self.drawing,
		self.anno,
		self.fabric,
		self.percent,
		self.material,
		self.form,
		self.specific_form,
		self.ware,
		self.munsell,
		self.surf_trat,
		self.exdeco,
		self.intdeco,
		self.wheel_made,
		self.descrip_ex_deco,
		self.descrip_in_deco,
		self.note,
		self.diametro_max,
		self.qty,
		self.diametro_rim,
		self.diametro_bottom,
		self.diametro_height,
		self.diametro_preserved,
		self.specific_shape,
		self.bag,
		self.sector,
		self.decoration_type,
		self.decoration_motif,
		self.decoration_position,
		self.datazione
		)
