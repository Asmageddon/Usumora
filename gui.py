import utilities
import pygame, sys, os, psyco

psyco.full()

class GUI_STYLE:
	def __init__(self):
		self.image=0
		self.border_l        = pygame.Rect(0,0,0,0)
		self.border_r        = pygame.Rect(0,0,0,0)
		self.border_u        = pygame.Rect(0,0,0,0)
		self.border_d        = pygame.Rect(0,0,0,0)
		self.border_lu       = pygame.Rect(0,0,0,0)
		self.border_ru       = pygame.Rect(0,0,0,0)
		self.border_ld       = pygame.Rect(0,0,0,0)
		self.border_rd       = pygame.Rect(0,0,0,0)
		self.border_focus_l  = pygame.Rect(0,0,0,0)
		self.border_focus_r  = pygame.Rect(0,0,0,0)
		self.border_focus_u  = pygame.Rect(0,0,0,0)
		self.border_focus_d  = pygame.Rect(0,0,0,0)
		self.border_focus_lu = pygame.Rect(0,0,0,0)
		self.border_focus_ru = pygame.Rect(0,0,0,0)
		self.border_focus_ld = pygame.Rect(0,0,0,0)
		self.border_focus_rd = pygame.Rect(0,0,0,0)
		self.background      = pygame.Rect(0,0,0,0)
		self.background_focus= pygame.Rect(0,0,0,0)
		self.padding         = (0,0,0,0)
	def fromFile(self,datapath,filename):
		if not os.path.exists(os.path.join(datapath, filename)): debug.debugMessage(3,"   Style file not located, using null style!")
		else:
			FILE=open(os.path.join(datapath, filename),"r")
			full=FILE.read()+chr(10)
			FILE.close()
			mode=0
			script=""
			cchar=''
			current=''
			numbers  =['0','1','2','3','4','5','6','7','8','9']
			letters  =[' ','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
			legitchars=letters+numbers+['_','.']
			funcchars=['#','=','-',':','+',';']
			endl     =[chr(10)]
			for cchar in full:
				current+=cchar
				if   mode==0:
					if   cchar in legitchars:
						current+=cchar
					elif cchar == chr(10):
						self.image=utilities.load_image(os.path.join(datapath,filename))
						current=''
				elif mode==1:
					if   cchar in numbers:
						current+=cchar
					else:
						current=''
class GUI_OBJECT:
	def getType(self): return "GUI_OBJECT"
	def __init__(self,size,parent,sprops={},style=0):
		self.visuals=pygame.Surface(size) #Cached visuals, image of this object alongside with all child objects
		self.parent=0                     #Parent of this object(container object, usually), used to order parent to redraw child object when it's visuals get updated
		self.cached=0                     #Are visuals already drawn? This gets set to 0, when 
		self.contents=[]                  #Contained objects
		self.focus=[]                     #If this object contains any objects and focus array is not empty received input is passed to every focused object(usefull in case of multiple player viewports, etc.)
		self.focused=0                    #Is focus on this object? May be usefull to change appearance of active button,list element, etc.
		self.position=(0,0)               #Position of this object in parent container
		self.visible=1
		self.border=0
		self.size=size
		if sprops: self.customInit(sprops)

	def customInit(self, sprops): return 1#Custom init params, to not have __init__ have to be overwritten

	def renderSelf(self): return 1        #Render self, null template, to be overriden

	def requestVisuals(self):             #Renders self, and all contained objects
		self.renderSelf()
		for obj in self.contents:
			if(obj.visible): self.visuals.blit(obj.requestVisuals,obj.position) #Request image of, and render each contained object, which is visible
		return self.visuals

	def getInput(self,action):
		#print "1:",action
		if action[0]=='gui':
			if   action[1]=='hide':
				self.visible=0
			elif action[1]=='show':
				self.visible=1
			elif action[1]=='toggle':
				self.visible=self.visible^1
			elif action[1]=='redraw':
				self.requestVisuals()
			else: self.customInput(action)
		else:
			self.customInput(action)
	def customInput(self,action):
		self.contents[self.focus].getInput(action)

#-----------------Redirector class(redirects different inputs to different controls

class REDIRECTOR(GUI_OBJECT):
	def getType(self): return "REDIRECTOR"
	def customInit(self, sprops): #Redirector sprops are in following format: {'input type':[element 1, element 2]}, so: {'player':[0,1]}
		for s in sprops:
			self.redirect[s]=sprops[s]
	def getInput(self, action):
		if self.redirect.has_key[action[0]]:
			for c in self.redirect[s]:
				if self.contents[redirects[c]].focus==1:
					self.contents[redirects[c]].getInput(action)

#-----------------Viewport class

class VIEWPORT(GUI_OBJECT):
	def getType(self): return "VIEWPORT"
	def customInit(self,sprops):
		self.player=sprops['player'] #Player holds pointer to the game instance, this allows me to retrieve all game data
		self.camPosition=(0,0)
		self.mode=0
		self.delayedAction=[]
		self.cursor=utilities.load_image(sprops['datapath'],"cursor.png")

	def customInput(self,action):
		#print "2:",action
		if self.mode<=0:
			self.delayedAction=[]+action
			self.mode=0
			for a in range(0,len(self.delayedAction)):
				if self.delayedAction[a] in ['target','ftarget']:
					self.mode+=1
					#del(self.delayedAction[a])
			if self.mode<=0: 
				self.player.getInput(action)
		else:
			if action[1]=='move':
				vector=[self.camPosition[0],self.camPosition[1]]
				if   'l' in action[2]: vector[0]=self.camPosition[0]-1
				elif 'r' in action[2]: vector[0]=self.camPosition[0]+1
				if   'u' in action[2]: vector[1]=self.camPosition[1]-1
				elif 'd' in action[2]: vector[1]=self.camPosition[1]+1
				self.camPosition=tuple(vector)
			elif action[1] in ['wait','confirm']:
				self.mode-=1
				self.delayedAction[3+self.mode]=(self.camPosition[0]+self.size[0]/64,self.camPosition[1]+self.size[1]/64)
			elif action[1] in ['cancel']:
				self.mode=-1
			if self.mode==0:
				self.player.getInput(self.delayedAction)

	def renderSelf(self):
		if self.mode==0: self.camPosition=(self.player.camPosition[0]-self.size[0]/64,self.player.camPosition[1]-self.size[1]/64)
		self.visuals.blit(self.player.world.gamemap.drawMap(self.visuals.get_size(), self.player.world.tileset, self.camPosition, self.player.world.objects, self.player.world.objectset),(0,0))
		if self.mode>0:
			self.visuals.blit(self.cursor,(self.size[0]//64*32,self.size[1]//64*32))
