class test:
	stop = 0
	l = [1, 2,3, 4, 5, 6, 7, 8, 9,10]
	
	def while_print_data(self):
		while self.stop == 0:
			self.print_data()
	
	def print_data(self):
		for i in self.l:
			try:
				if i != 7:
					print(i)
			except:
				self.stop =1
				return self.stop

t = test()
t.while_print_data()
			