import sys, os, pygame, random, math
from pygame.locals import *
import gameconstants as gc
import perlin

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

if(len(sys.argv)>2):
	if sys.argv[0] == "-d": datapath=sys.argv[1]
else:	
	datapath="data"
datapath="data"

def load_image(name):
	fullname = os.path.join(datapath, name)
	debugMessage(5, '  Trying to load image file:'+fullname)
	try:
		image = pygame.image.load(fullname)
		debugMessage(4, '   Image loaded succesfully!')
	except pygame.error, message:
		debugMessage(1, 'Cannot load image:' + fullname)
		raise SystemExit, message
	image = image.convert()
	image.set_colorkey(pygame.Color(253,252,1))
	return image

def debugMessage(messageType,string):
	a=""
	if   messageType==0: a="\033[101m[FATAL ERROR]"  #Fatal error
	elif messageType==1: a="\033[100m\033[91m[ERROR]"#Error
	elif messageType==2: a="\033[91m[WARNING]"       #Warning
	elif messageType==3: a="\033[94m[NOTICE]"        #Regular notice
	elif messageType==4: a="\033[92m[NOTICE]"        #Succes  notice
	elif messageType==5: a="\033[95m[NOTICE]"        #Special notice
	print a+string+"\033[0m"
	if   messageType<2: print "Exiting"; raise SystemExit

class SETTINGS: #Holds settings, this have got single instance in main GAME class. 
	def __init__(self):
		#Set default settings
		self.chunkCacheRange = 4
		self.imageCacheRange = 3
		self.renderRange     = (0,2)
		self.chunkSize       = (32,32)

class TILE:     #This class contains tile information, self.tileDefinition are stored instead TILESET and define specific tile type properties
	def __init__(self):
		self.images      = [Rect(0,0,32,32),Rect(0,0,32,32),Rect(0,0,32,32),Rect(0,0,32,32),Rect(0,0,32,32),Rect(0,0,32,32),Rect(0,0,32,32),Rect(0,0,32,32)] #Image for 4xnormal, cracked, damaged and broken tile
		self.strength    = 9999 #How easy it is to break the tile from normal->cracked, cracked->damaged, damaged->broken and broken->destroyed
		self.strengthdec = 0    #How much tile strength decreases with each level of destruction
		self.lemit       = [0,0,0]
		self.name        = "tile"
		self.flammable   = 9999
		self.magic       = 0
		self.remains     = ""
		self.transparency= 0
		self.breaksInto  = 0
		self.collision   = 0

class GENERATOR:#This class holds instances of perlin.PerlinNoise used in generation and miscellanous map generation settings
	def __init__(self,big,small,climate,lake):
		self.s=small       #Small scale feautures - tunnels, pillars, etc.
		self.b=big         #Big scale features    - large caves, layers of solid rock
		self.l=lake        #Lakes                 - used for generation of lakes and - sometimes - misc stuff
		self.c=climate     #Climate               - Large scale noise, used for determining climate type of certain point.
		self.s_scale=1
		self.b_scale=2
		self.l_scale=1
		self.c_scale=4
		debugMessage(3,"  Initializing generator...")
		self.big_feature   =perlin.PerlinNoise((big,big),perlin.ease_interpolation)
		self.small_feature =perlin.PerlinNoise((small,small),perlin.ease_interpolation)
		self.climate	   =perlin.PerlinNoise((climate,climate),perlin.ease_interpolation)
		self.lakes		   =perlin.PerlinNoise((lake,lake),perlin.ease_interpolation)
		debugMessage(4,"   Generator initialized!")

class IMAGEMAP:
	def __init__(self,datafile):
		self.a=0

class TILESET:
	def __init__(self):
		debugMessage(3,"Creating tileset object...")
		self.tileset=[]
		self.tileDefinition=[]
		debugMessage(4," Tileset created!")
	def fromFile(self,filename):
		debugMessage(3," Trying to load tileset from file: "+ os.path.join(datapath, filename))
		if not os.path.exists(os.path.join(datapath, filename)): debugMessage(0,"   Tileset file not located")
		FILE=open(os.path.join(datapath, filename),"r")
		full=FILE.read()
		cchar=''
		current=''
		mode=-1
		curTile=0
		prop=""
		numbers  =['0','1','2','3','4','5','6','7','8','9']
		letters  =[' ','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
		funcchars=['#','=','-',':','+',';']
		endl     =[chr(10)]
		for i in range(0,len(full)):
			cchar=full[i]
			if   cchar in numbers:   a=1
			elif cchar in letters:   a=2
			elif cchar in funcchars: a=3
			elif cchar in endl:      a=4
			else:                    a=0
			if   mode == -1:
				if a==4:
					self.tileset=load_image(current)
					mode=0
					current=''
				else: current+=cchar
			elif mode ==  0:    #This reads number of tile, like "#133#"
				if   a==1:
					current+=cchar
				elif a==4:
					curTile=int(current)
					while(len(self.tileDefinition)<curTile+1):
						self.tileDefinition+= [TILE()]
					debugMessage(3,"Loading tile "+current)
					mode=1
					current=''
			elif mode == 1:  #This reads name of the property, like: "name="
				if   a == 1 or a == 2:
					current+=cchar
				elif a==3:
					if cchar == '-' or cchar == '+':
						current+=cchar
					elif cchar == '#':
						current=''
						cchar=''
						mode=0
					else:
						prop=current
						if prop in ["name","remains"] or prop[0:5]=="image":
							mode = 2
						else:
							mode = 3
						current=''
			elif mode==2:   #This reads string     value for the property and assigns it
				if a == 1 or a == 2 or a == 3 or a == 0:
					current+=cchar
				elif a == 4:
					if   prop      == "name":
						self.tileDefinition[curTile].name=current
					elif prop      == "remains":
						tileset.remains=current
					elif prop[0:5] == "image":
						b=[]
						curpr=""
						for o in range(0,len(current)):
							if current[o] == ',' or current[o] == ';':
								b+=[int(curpr)]
								curpr=''
							else:
								curpr+=current[o]
						for i2 in range(int(prop[5])-1,int(prop[7])-1):
							if   prop[6] == '-':
								self.tileDefinition[curTile].images[i2]=Rect( (b[0]   )*32, b[1]*32, 32, 32)
							elif prop[6] == '+':
								self.tileDefinition[curTile].images[i2]=Rect( (b[0]+i2)*32, b[1]*32, 32, 32)
					current=''
					mode=1
			elif mode == 3: #This reads integer(s) value for the property and assigns it
				if   a == 1:
					current+=cchar
				elif a == 4:
					if   prop == "flammable":    self.tileDefinition[curTile].flammable    = int(current)
					elif prop == "strengthdec":  self.tileDefinition[curTile].strengthdec  = int(current)
					elif prop == "strength":     self.tileDefinition[curTile].strength     = int(current)
					elif prop == "lemitR":       self.tileDefinition[curTile].lemit[0]     = int(current)
					elif prop == "lemitG":       self.tileDefinition[curTile].lemit[1]     = int(current)
					elif prop == "lemitB":       self.tileDefinition[curTile].lemit[2]     = int(current)
					elif prop == "transparency": self.tileDefinition[curTile].transparency = int(current)
					elif prop == "magic":        self.tileDefinition[curTile].magic        = int(current)
					elif prop == "breaks":       self.tileDefinition[curTile].breaksInto   = int(current)
					elif prop == "collision":    self.tileDefinition[curTile].collision    = int(current)
					current=''
					mode=1
		FILE.close()
		for i in range(0,0):#self.tileDefinition:
			print "flammable", i.flammable    
			print "strengthdec", i.strengthdec  
			print "strength", i.strength     
			print "lemitR", i.lemit[0]     
			print "lemitG", i.lemit[1]     
			print "lemitB", i.lemit[2]     
			print "transparency", i.transparency 
			print "magic", i.magic        
			print "breaks", i.breaksInto   
			print "collision", i.collision    

class LOCALMAP:
	#genedchunks=0
	def generate(self,generator,positionX,positionY):
		debugMessage(3,"  Generating chunk...")
		rmatrix=[0,0,0,0]
		#for z in range(0,2):
		#	if z==0:
		#		a=generator.big_feature
		#		a=generator.small_feature
		#	for x in range(0,32):
		#		for y in range(0,32):
					#print "blah"
		for x in range(0,32):
			self.mapChunk+=[[]]
			self.tileVariation+=[[]]
			for y in range(0,32):
				tilevar=random.randint(0,4)
				tile=0
				nx1 = (x+positionX*32) / float(generator.b)
				ny1 = (y+positionY*32) / float(generator.b)
				nx2 = (x+positionX*32) / float(generator.s)
				ny2 = (y+positionY*32) / float(generator.s)
				nx3 = (x+positionX*32) / float(generator.l)
				ny3 = (y+positionY*32) / float(generator.l)
				v1=generator.big_feature.value_at(   (nx1,ny1) )
				v2=generator.small_feature.value_at( (nx2,ny2) )
				v3=generator.lakes.value_at(         (nx3,ny3) )
				#Actual generation code
				if v3 < -0.4:
					if(v2 < 0.32  ):
						tile=3
					else:
						tile=1
				elif 0.45 > v3 > 0.38:
					if(v2 < 0.32  ):
						tile=4
						tilevar=random.randint(2,4)
					else:
						tile=1
				elif v3 > 0.45:
					if(v2 < 0.32  ):
						tilevar=random.randint(0,2)
						tile=4
					else:
						tile=1
				else:
					if( v1 < -0.15  ): #open air
						if( v2 > 0.4  ):
							tile=2
						else:
							tile=1
					else:
						if( v2 < -0.1  ):
							tile=1
						else:
							tile=2
				#Actual generation code end
				self.mapChunk[x]+=[tile]
				self.tileVariation[x]+=[tilevar]
		debugMessage(4,"   Chunk generated("+str(positionX)+","+str(positionY)+")")
	def __init__(self,generator,positionX,positionY):
		self.modified=0
		#self.genedchunks=0
		self.mapChunk=[[]]
		self.tileVariation=[[]]
		self.cachedimage="NULL"
		self.tileVariation=[[]]
		self.generate(generator,positionX,positionY)
	def requestChunkImage(self,tileset):
		if self.cachedimage == "NULL":
			self.cachedimage=pygame.Surface((1024,1024))
			for x in range(0,32):
				for y in range(0,32):
					pos=(x*32,y*32)
					clip=tileset.tileDefinition[self.mapChunk[x][y]].images[self.tileVariation[x][y]]
					self.cachedimage.blit(tileset.tileset,pos,clip)
			debugMessage(4,"  Drawn a new chunk!")
			#genedchunks+=1
		return self.cachedimage
	
	def updateTile(self, tileset, position):
		if self.cachedimage == "NULL":
			self.requestChunkImage(tileset)
		pos=(position[0]*32,position[1]*32)
		clip=tileset.tileDefinition[self.mapChunk[position[0]][position[1]]].images[self.tileVariation[position[0]][position[1]]]
		self.cachedimage.blit(tileset.tileset,pos,clip)
	
	def requestTile(self,position):
		return self.mapChunk[position[0],position[1]]
	
	def damageTile(self, tileset, position, damage):
		a=0
		vari=self.tileVariation[position[0]][position[1]]
		smashed=0
		dmg=damage
		tileDef=tileset.tileDefinition[self.mapChunk[position[0]][position[1]]]
		while dmg > 0:
			multiplier = (100.0-tileDef.strengthdec)/100.0
			if vari>3: a=int(tileDef.strength*multiplier)
			else: a=tileDef.strength
			if dmg>=a and a!=0:
				smashed+=1
				dmg-=a
			else:
				dmg=-1
		if vari<4:
			self.tileVariation[position[0]][position[1]]=4+smashed
		else:
			self.tileVariation[position[0]][position[1]]+=smashed
		if self.tileVariation[position[0]][position[1]]>7:
			self.tileVariation[position[0]][position[1]]=random.randint(0,4)
			self.modifyTile(tileset, position,tileDef.breaksInto)
			return 32
		else:
			return smashed
			self.updateTile(tileset, position)
	def  modifyTile(self,tileset,position,newtype):
		self.mapChunk[position[0]][position[1]]=newtype
		self.updateTile(tileset, position)

class GLOBALMAP:
	def __init__(self,parent,big,small,climate,lake):
		self.chunkCollection={}
		self.parent=parent
		self.generator=[]
		debugMessage(3," Initializing world map...")
		self.chunkCollection={}
		self.generator=GENERATOR(big,small,climate,lake)
		debugMessage(3," World map initialized")
	def requestChunk(self, pos):
		if not self.chunkCollection.has_key(pos):
			self.chunkCollection[pos]=LOCALMAP(self.generator,pos[0],pos[1])
		return self.chunkCollection[pos]
		#return LOCALMAP(self.generator,x,y)
	def getTile(self, pos):
		x=pos[0]
		y=pos[1]
		return self.requestChunk((x//32, y//32)).mapChunk[x-(x//32)*32][y-(y//32)*32]
	def setTile(self, pos, newType):
		x=pos[0]
		y=pos[1]
		#self.requestChunk((x//32, y//32)).mapChunk[]=newType
		self.requestChunk((x//32, y//32)).modifyTile(self.parent.tileset,(x-(x//32)*32,y-(y//32)*32),newType)
	def damageTile(self, pos, damage):
		x=pos[0]
		y=pos[1]
		return self.requestChunk((x//32, y//32)).damageTile(self.parent.tileset,(x-(x//32)*32,y-(y//32)*32),damage)
	def requestChunkDeletion(self, pos):
		if self.chunkCollection.has_key(pos) and not self.chunkCollection[pos].modified:
			del self.chunkCollection[pos]
			#debugMessage("Deleted chunk"+str(pos)+"!")
			return 1
		else:
			return 0
	def requestChunkImageDeletion(self, pos):
		if self.chunkCollection.has_key(pos) and not self.chunkCollection[pos].cachedimage=="NULL":
			self.chunkCollection[pos].cachedimage="NULL"
			#debugMessage("Deleted chunk"+str(pos)+"!")
			return 1
		else:
			return 0
	def drawMap(self, screen, tileset, player, objects, objectset):
		positionX = player.camPosition[0]
		positionY = player.camPosition[1]
                screen.fill((0,0,0))
		for x in range(0,2):
			for y in range(0,2):
                                chunk_x = (positionX // 32) + x
                                chunk_y = (positionY // 32) + y
                                
				chunk = self.requestChunk((chunk_x, chunk_y))
                                
                                pos = (32 * (32 * chunk_x - positionX),
                                       32 * (32 * chunk_y - positionY))
                
				screen.blit(chunk.requestChunkImage(tileset), pos)
                                if x == 0 and y == 0:
                                        self.uncacheChunks((chunk_x,chunk_y))
		for i in objects:
			screen.blit(objectset.image,(32*(i.position[0]-positionX),32*(i.position[1]-positionY)),objectset.object[i.type].image)
	def uncacheChunks(self,position):
		a = self.parent.settings.chunkCacheRange
		b=0
		for x in range(position[0]-a,position[0]+a):
			b+=self.requestChunkDeletion((x , -a + position[1]))
			b+=self.requestChunkDeletion((x ,  a + position[1]))
		for y in range(position[1]-a+1,position[1]+a-1):
			b+=self.requestChunkDeletion((-a + position[0] , y))
			b+=self.requestChunkDeletion((a  + position[0] , y))
		a2 = self.parent.settings.imageCacheRange
		b2=0
		for x in range(position[0]-a2,position[0]+a2):
			b2+=self.requestChunkImageDeletion((x , -a2 + position[1]))
			b2+=self.requestChunkImageDeletion((x ,  a2 + position[1]))
		for y in range(position[1]-a2+1,position[1]+a-1):
			b2+=self.requestChunkImageDeletion((-a2 + position[0] , y))
			b2+=self.requestChunkImageDeletion((a2  + position[0] , y))
		if(b>0 or b2>0): debugMessage(5, "Deleted " + str(b) +" chunks and " +str(b+b2) + " cached images!")
		return 1

class OBJECTDEF:
	def __init__(self):
		self.image=Rect(0,0,32,32)
		self.owner=0
		self.props=""

class OBJECTSET:
	def __init__(self,filename):
		debugMessage(5," Opening objects image file.")
		#if not os.path.exists(os.path.join(datapath, filename)): debugMessage(0,"   Object images file not located!")
		self.image  = load_image(filename)
		self.object = []
		debugMessage(5,"  Object set initialized.")

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
		debugMessage(5,"Starting the game")
		pygame.init()
		pygame.mouse.set_visible(0)
		self.run=1
		debugMessage(3," Game started")
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
		self.tileset  = TILESET()
		self.gamemap  = GLOBALMAP(self,72,8,64,24)
		self.tileset.fromFile("tileset")
		
		f=open(os.path.join(datapath, "config.txt"))
		ff=f.read()
		f.close()
		try: exec(ff)
		except: debugMessage(1,"Something is wrong with config file!")
		pygame.display.set_caption("Usumora["+self.gameversion+"]")
		
	def main(self):
		debugMessage(5," Running main loop...")
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
		debugMessage(3, "  Main loop off.")
	
	
	def checkEvents(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.run=0
					debugMessage(3, " Disabling main loop...")
				elif event.key == K_RETURN:
					self.gamemap=GLOBALMAP(self,72,8,64,24)
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
	debugMessage(5,"Game ended") #, generated " +str(genedchunks) +" in total
