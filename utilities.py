import os, debug, pygame

def load_image(datapath,name):
	fullname = os.path.join(datapath, name)
	debug.debugMessage(5, '  Trying to load image file:'+fullname)
	try:
		image = pygame.image.load(fullname)
		debug.debugMessage(4, '   Image loaded succesfully!')
	except pygame.error, message:
		debug.debugMessage(1, 'Cannot load image:' + fullname)
		raise SystemExit, message
	image = image.convert()
	image.set_colorkey(pygame.Color(253,252,1))
	return image
