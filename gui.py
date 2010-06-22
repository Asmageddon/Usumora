import pygame, sys, os, psyco

psyco.full()

class GUI_object:
	def getType(self): return "GUI_OBJECT"

	def __init__(self,parent,sprops):
		self.visuals=pygame.Surface(size) #Cached visuals, image of this object alongside with all child objects
		self.parent=0                     #Parent of this object(container object, usually), used to order parent to redraw child object when it's visuals get updated
		self.cached=0                     #Are visuals already drawn? This gets set to 0, when 
		self.contents=[]                  #Contained objects
		self.focus=[]                     #If this object contains any objects and focus array is not empty received input is passed to every focused object(usefull in case of multiple player viewports, etc.)
		self.position=(0,0)               #Position of this object in parent container
		self.visible=1
		self.customInit(sprops)

	def customInit(self, sprops): return 1#Custom init params, to not have __init__ have to be overwritten

	def renderSelf(self): return 1        #Render self, null template, to be overriden

	def requestVisuals(self):             #Renders self, and all contained objects
		renderSelf()
		for obj in contents:
			if(obj.visible): self.visuals.blit(obj.requestVisuals,obj.position) #Request image of, and render each contained object, which is visible
		return self.visuals

	def receiveInput(self,action):
		if self.focus !=-1 and self.contents:
			self.contents[self.focus].receiveInput(action)

#-----------------Viewport class

class viewport(GUI_Object):
	def customInit(self,sprops):
		self.player=sprops['player'] #Player holds pointer to the game instance, this allows me to retrieve all game data

	def receiveInput(self,action):
		self.player.receiveInput(action)
	
	def renderSelf(self):
		self.player.world.gamemap.drawMap(self.visuals, self.player.world.tileset, self.player, self.player.world.objects, self.player.world.objectset):
