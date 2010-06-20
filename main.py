import sys, os, pygame, psyco
from pygame.locals import *
import gameconstants as gc
import perlin, map, debug, tileset, utilities, objects

psyco.profile()
psyco.full()

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

if(len(sys.argv)>2):
	if sys.argv[0] == "-d": datapath=sys.argv[1]
else:	
	datapath="data"
datapath="data"

class SETTINGS: #Holds settings, this have got single instance in main GAME class. 
	def __init__(self):
		#Set default settings
		self.chunkCacheRange = 4
		self.imageCacheRange = 3
		self.renderRange     = (0,2)
		self.chunkSize       = (32,32)
	def Type(self): return "SETTINGS"

class PLAYER:
	def __init__(self):
		self.camPosition  = [0,0]
		self.camFocus     = 0
		self.color        = (0,0,0)
	def update(self):
		if self.camFocus!=0:
			self.camPosition=self.camFocus.position
	def Type(self): return "PLAYER"

class GAME:
	def Type(self): return "GAME"
	def __init__(self):
		self.maxpfs=60
		self.keymovX=0
		self.keymovY=0
		self.effmovX=0
		self.effmovY=0
		self.effcap=5
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
		if self.fullscreen: self.screen   = pygame.display.set_mode((640, 480),pygame.FULLSCREEN)
		else: self.screen   = pygame.display.set_mode((640, 480))
		
		self.players  = [PLAYER()]
		self.objectset= objects.OBJECTSET(datapath,"objectset")
		self.objects  = []
		self.objects += [objects.OBJECT(self,1)]
		self.players[0].camFocus=self.objects[0]
		self.tileset  = tileset.TILESET()
		self.gamemap  = map.GLOBALMAP(self,72,8,64,24)
		self.tileset.fromFile(datapath,"tileset")
		
		f=open(os.path.join(datapath, "config.txt"))
		ff=f.read()
		f.close()
		try: exec(ff)
		except: debug.debugMessage(1,"Something is wrong with config file!")
		pygame.display.set_caption("Usumora["+self.gameversion+"]")
		
	def main(self):
		debug.debugMessage(5," Running main loop...")
		while(self.run):
			self.clock.tick(self.maxfps)
			self.crappyMovePlaceHolder()
			self.players[0].camPosition=(self.objects[0].position[0]-10,self.objects[0].position[1]-7)
			self.checkEvents()
			for p in self.players: p.update()
			self.gamemap.drawMap(self.screen,self.tileset,self.players[0],self.objects, self.objectset)
			self.crappyMovePlaceHolder()
			#self.screen.blit(self.tileset.tileset,(0,0),self.tileset.tileDefinition[1].images[0])
			pygame.display.flip()
		debug.debugMessage(3, "  Main loop off.")
	
	
	def checkEvents(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.run=0
					debug.debugMessage(3, " Disabling main loop...")
				elif event.key == K_RETURN:
					self.gamemap=map.GLOBALMAP(self,72,8,64,24)
				elif event.key == K_KP1:
					self.keymovX=-1
					self.keymovY=1
				elif event.key == K_KP2:
					self.keymovY=1
				elif event.key == K_KP3:
					self.keymovY=1
					self.keymovX=1
				elif event.key == K_KP4:
					self.keymovX=-1
				elif event.key == K_KP5:
					self.gamemap.setTile(self.objects[0].position,2)
				elif event.key == K_KP6:
					self.keymovX=1
				elif event.key == K_KP7:
					self.keymovX=-1
					self.keymovY=-1
				elif event.key == K_KP8:
					self.keymovY=-1
				elif event.key == K_KP9:
					self.keymovY=-1
					self.keymovX=1
			elif event.type == KEYUP:
				if event.key == K_KP1:
					self.keymovX=0
					self.keymovY=0
				elif event.key == K_KP2:
					self.keymovY=0
				elif event.key == K_KP3:
					self.keymovY=0
					self.keymovX=0
				elif event.key == K_KP4:
					self.keymovX=0
				elif event.key == K_KP6:
					self.keymovX=0
				elif event.key == K_KP7:
					self.keymovX=0
					self.keymovY=0
				elif event.key == K_KP8:
					self.keymovY=0
				elif event.key == K_KP9:
					self.keymovY=0
					self.keymovX=0
			elif event.type == MOUSEBUTTONDOWN:
				continue
			elif event.type is MOUSEBUTTONUP:
				continue
	def crappyMovePlaceHolder(self):
		if self.keymovX!=0: self.effmovX+=self.keymovX
		else: self.effmovX=0
		if self.keymovY!=0: self.effmovY+=self.keymovY
		else: self.effmovY=0
		if (self.effmovY > self.effcap or self.effmovY < -self.effcap) and self.effmovX==0:
			if self.effmovY < 0: self.effmovY=-self.effcap
			else: self.effmovY=self.effcap
			mode=gc.MOVE_AGGRO    +   gc.MOVE_FLOOR    +   gc.MOVE_CAREFULL   +   gc.MOVE
			self.objects[0].execAction("move",{'vector':(0,(self.effmovY/self.effcap)),'mode':mode})
			self.effmovY=0
		if (self.effmovX > self.effcap or self.effmovX < -self.effcap) and self.effmovY==0:
			if self.effmovX < 0: self.effmovX=-self.effcap
			else: self.effmovX=self.effcap
			mode=gc.MOVE_AGGRO    +   gc.MOVE_FLOOR    +   gc.MOVE_CAREFULL   +   gc.MOVE
			self.objects[0].execAction("move",{'vector':(self.effmovX/self.effcap,0),'mode':mode})
			self.effmovX=0
		if (self.effmovX > self.effcap or self.effmovX < -self.effcap) and (self.effmovY > self.effcap or self.effmovY < -self.effcap):
			if self.effmovY < 0: self.effmovY=-self.effcap
			else: self.effmovY=self.effcap
			if self.effmovX < 0: self.effmovX=-self.effcap
			else: self.effmovX=self.effcap
			mode=gc.MOVE_AGGRO    +   gc.MOVE_FLOOR    +   gc.MOVE_CAREFULL   +   gc.MOVE
			self.objects[0].execAction("move", {'vector':(self.effmovX/self.effcap,self.effmovY/self.effcap),'mode':mode} )
			self.effmovX=0
			self.effmovY=0
if __name__ == '__main__':
	game=GAME()
	game.main()
	debug.debugMessage(5,"Game ended") #, generated " +str(genedchunks) +" in total
