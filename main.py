import sys, os, pygame, random, math
from pygame.locals import *
import gameconstants as gc
import perlin, map, debug, tileset, utilities

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

 

class OBJECTDEF:
	def __init__(self):
		self.image=Rect(0,0,32,32)
		self.owner=0
		self.props=""

class OBJECTSET:
	def __init__(self,filename):
		debug.debugMessage(5," Opening objects image file.")
		#if not os.path.exists(os.path.join(datapath, filename)): debug.debugMessage(0,"   Object images file not located!")
		self.image  = utilities.load_image(datapath,filename)
		self.object = []
		debug.debugMessage(5,"  Object set initialized.")

class OBJECT:
	def __init__(self,world):
		self.position=[0,0]
		self.type=0
		self.world=world
		self.terrainAttackMin=0
		self.terrainAttackMax=0
	def Move(self,vector,mode):
		dmg=random.randint(self.terrainAttackMin,self.terrainAttackMax)
		modes=[0,0,0,0,0,0,0,0]
		for i in range(0,7):
			if mode>math.pow(2,7-i):
				modes[7-i]=1
				mode-=math.pow(2,7-i)
			else:
				modes[7-i]=0
		compos=((self.position[0]+vector[0]),(self.position[1]+vector[1]))
		tileDef=self.world.tileset.tileDefinition[self.world.gamemap.getTile(compos)]
		if(tileDef.collision==gc.C_NULL):
			#if self.world.objectset[self.type].
			if modes[gc.MOVE_CAREFULL_V]: return 0
			else:
				self.position=compos
				return 1
		elif(tileDef.collision==gc.C_FLOOR):
			if not modes[gc.MOVE_FLOOR_V]:
				if modes[gc.MOVE_AGGRO_V]:
					self.world.gamemap.damageTile(compos,dmg)
					return 0
			else:
				self.position=compos
				return 1
		elif(tileDef.collision==gc.C_LIQUID):
			if not modes[gc.MOVE_LIQUID_V]:
				if modes[gc.MOVE_AGGRO_V]:
					self.world.gamemap.damageTile(compos,dmg)
					return 0
			else:
				self.position=compos
				return 1
		elif(tileDef.collision==gc.C_WALL):
			if not modes[gc.MOVE_WALL_V]:
				if modes[gc.MOVE_AGGRO_V]:
					self.world.gamemap.damageTile(compos,dmg)
					return 0
			else:
				self.position=compos
				return 1
		#if dest
		return 1

class PLAYER:
	def __init__(self):
		self.camPosition  = [0,0]
		#self.camMovement = (0,0)
		self.color=(0,0,0)

class GAME:
	def __init__(self):
		self.maxpfs=60
		self.keymovX=0
		self.keymovY=0
		self.effmovX=0
		self.effmovY=0
		self.effcap=5
		self.gameversion=""
		self.run = 0
		debug.debugMessage(5,"Starting the game")
		pygame.init()
		pygame.mouse.set_visible(0)
		self.run=1
		debug.debugMessage(3," Game started")
		self.clock = pygame.time.Clock()
		
		self.screen   = pygame.display.set_mode((640, 480))
		
		self.players=[PLAYER()]
		self.objectset=OBJECTSET("objects1.png")
		self.objects  = []
		self.objectset.object   += [OBJECTDEF()]
		self.objectset.object[0].image = Rect(120,42,32,32) 
		self.objects+=[OBJECT(self)]
		self.objects[0].terrainAttackMin=17
		self.objects[0].terrainAttackMax=28
		
		self.settings = SETTINGS()
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
			if self.keymovX!=0: self.effmovX+=self.keymovX
			else: self.effmovX=0
			if self.keymovY!=0: self.effmovY+=self.keymovY
			else: self.effmovY=0
			if (self.effmovY > self.effcap or self.effmovY < -self.effcap) and self.effmovX==0:
				if self.effmovY < 0: self.effmovY=-self.effcap
				else: self.effmovY=self.effcap
				mode=gc.MOVE_AGGRO    +   gc.MOVE_FLOOR    +   gc.MOVE_CAREFULL   +   gc.MOVE
				self.objects[0].Move((0,(self.effmovY/self.effcap)),mode)
				self.effmovY=0
			if (self.effmovX > self.effcap or self.effmovX < -self.effcap) and self.effmovY==0:
				if self.effmovX < 0: self.effmovX=-self.effcap
				else: self.effmovX=self.effcap
				mode=gc.MOVE_AGGRO    +   gc.MOVE_FLOOR    +   gc.MOVE_CAREFULL   +   gc.MOVE
				self.objects[0].Move((self.effmovX/self.effcap,0),mode)
				self.effmovX=0
			if (self.effmovX > self.effcap or self.effmovX < -self.effcap) and (self.effmovY > self.effcap or self.effmovY < -self.effcap):
				if self.effmovY < 0: self.effmovY=-self.effcap
				else: self.effmovY=self.effcap
				if self.effmovX < 0: self.effmovX=-self.effcap
				else: self.effmovX=self.effcap
				mode=gc.MOVE_AGGRO    +   gc.MOVE_FLOOR    +   gc.MOVE_CAREFULL   +   gc.MOVE
				self.objects[0].Move((self.effmovX/self.effcap,self.effmovY/self.effcap),mode)
				self.effmovX=0
				self.effmovY=0
			self.players[0].camPosition=(self.objects[0].position[0]-10,self.objects[0].position[1]-7)
			self.checkEvents()
			self.gamemap.drawMap(self.screen,self.tileset,self.players[0],self.objects, self.objectset)
			
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
if __name__ == '__main__':
	game=GAME()
	game.main()
	debug.debugMessage(5,"Game ended") #, generated " +str(genedchunks) +" in total
