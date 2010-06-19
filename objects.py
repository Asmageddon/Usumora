import debug, utilities, pygame, random, math, psyco
import gameconstants as gc

psyco.full()

class OBJECTDEF:
	def __init__(self):
		self.image=pygame.Rect(0,0,32,32)
		self.owner=0
		self.props=""
	def Type(self): return "OBJECTDEF"

class OBJECTSET:
	def __init__(self,datapath,filename):
		self.object = []
		debug.debugMessage(4,"  Object set initialized.")
		self.fromFile(datapath,filename)
		debug.debugMessage(5,"  Loading objects definitions from file...")
	
	def imageFromFile(self,datapath,filename):
		debug.debugMessage(5," Opening objects image file.")
		self.image  = utilities.load_image(datapath,filename)

	def fromFile(self,datapath,filename):
		debug.debugMessage(5," Opening objects image file.")
		self.image  = utilities.load_image(datapath,filename)

	def Type(self): return "OBJECTSET"

class OBJECT:
	def __init__(self,world):
		self.position=[0,0]
		self.type=0
		self.world=world
		self.terrainAttackMin=0
		self.terrainAttackMax=0
	
	def Type(self): return "OBJECT"
	
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

