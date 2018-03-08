import os

excludes = [""]
matches = []

for path, dirs, files in os.walk(os.getcwd()):
	print(dirs)