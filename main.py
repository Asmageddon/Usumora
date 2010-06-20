import sys, os, pygame, psyco
from pygame.locals import *
import gameconstants as gc
import map, debug, tileset, utilities, objects, keyinput #, gui

psyco.profile()
psyco.full()

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

if(len(sys.argv)>1):
	if sys.argv[0] == "-d": datapath=sys.argv[1]
else:	
	datapath="data"

class SETTINGS: #Holds settings, this have got single instance in main GAME class. 
	def __init__(self):
		#Set default settings
		self.allplayersinput = 0
		self.chunkCacheRange = 4
		self.imageCacheRange = 3
		self.renderRange     = (0,2)
		self.chunkSize       = (32,32)
	def Type(self): return "SETTINGS"

class PLAYER:
	def __init__(self):
		self.camPosition  = [0,0]
		self.camFocus     = 0
		self.screenSize   = (0,0)
		self.color        = (0,0,0)
	def update(self):
		if self.camFocus!=0:
			self.camPosition= (self.camFocus.position[0]-self.screenSize[0]/64,self.camFocus.position[1]-self.screenSize[1]/64)
	def getInput(self,e):
		return 0
	def Type(self): return "PLAYER"

class GAME:
	def Type(self): return "GAME"
	def __init__(self):
		self.maxpfs=60
		self.fullscreen=0
		self.gameversion=""
		self.run = 0
		debug.debugMessage(5,"Starting the game")
		pygame.init()
		pygame.mouse.set_visible(0)
		self.run=1
		debug.debugMessage(3," Game started")
		self.clock = pygame.time.Clock()
		
		self.settings = SETTINGS()
		f=open(os.path.join(datapath, "config.txt"))
		ff=f.read()
		f.close()
		try: exec(ff)
		except: debug.debugMessage(1,"Something is wrong with config file!")
		if self.fullscreen==1: self.screen   = pygame.display.set_mode(self.resolution,pygame.FULLSCREEN)
		else: self.screen   = pygame.display.set_mode(self.resolution)
		
		self.keyinput   = keyinput.KEYMAP()
		self.keyinput.fromFile(datapath,"keymap")
		self.players  = [PLAYER()]
		self.players[0].screenSize=(640,480)
		self.objectset= objects.OBJECTSET(datapath,"objectset")
		self.objects  = []
		self.objects += [objects.OBJECT(self,1)]
		self.players[0].camFocus=self.objects[0]
		self.tileset  = tileset.TILESET()
		self.gamemap  = map.GLOBALMAP(self,72,8,64,24)
		self.tileset.fromFile(datapath,"tileset")
		
		
		pygame.display.set_caption("Usumora["+self.gameversion+"]")
		
	def main(self):
		debug.debugMessage(5," Running main loop...")
		while(self.run):
			self.clock.tick(self.maxfps)
			self.players[0].camPosition=(self.objects[0].position[0],self.objects[0].position[1])
			self.checkEvents()
			self.keyinput.keyInputRepeat(self)
			for p in self.players: p.update()
			self.gamemap.drawMap(self.screen,self.tileset,self.players[0],self.objects, self.objectset)
			#self.screen.blit(self.tileset.tileset,(0,0),self.tileset.tileDefinition[1].images[0])
			pygame.display.flip()
		debug.debugMessage(3, "  Main loop off.")
	
	
	def checkEvents(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN:
				self.keyinput.keyInput          (  event.key, pygame.key.get_mods() , self )
				self.keyinput.keyInputActivate  (  event.key, pygame.key.get_mods()  )
			elif event.type == KEYUP:
				self.keyinput.keyInputDeactivate(  event.key, pygame.key.get_mods()  )
			elif event.type == MOUSEBUTTONDOWN:
				continue
			elif event.type == MOUSEBUTTONUP:
				continue
	def receiveInput(self,action):
		print "Received following input: "+str(action)
		if (action==['game','exit']): self.run=0
		if (action==['player','move','l']): print "hai!";self.players[0].camFocus.execAction('move',{'vector':(-1,0),'mode':(gc.MOVE_AGGRO+gc.MOVE_FLOOR)})
if __name__ == '__main__':
	game=GAME()
	game.main()
	debug.debugMessage(5,"Game ended") #, generated " +str(genedchunks) +" in total
