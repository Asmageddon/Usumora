import debug, utilities, pygame, sys, os, psyco, random,math
import gameconstants as gc

psyco.full()

class OBJECTPROPS:
	def __init__(self):
		#Default values
		self.movemode      = 0
		self.weight        = 0
		self.speed         = 0
		self.hp            = 0
		self.magic_emit    = 0
		self.scripts       = {}
		self.terrainAttack = [0,0]

class OBJECTDEF:
	def __init__(self):
		self.image=pygame.Rect(0,0,32,32)
		self.props=OBJECTPROPS()
	def Type(self): return "OBJECTDEF"

class OBJECTSET:
	def __init__(self,datapath,filename):
		self.objectDefinition = []
		#self.graphics         = ""
		self.scripts          = {}
		
		#self.scripts['move']  = "def execute(self): return 1"
		#exec(objectset.scripts[object[i].props.scripts['move']]+chr(10)+execute(props))
		debug.debugMessage(5,"  Loading object data from file...")
		self.fromFile(datapath,filename)
		debug.debugMessage(4,"   Object data loaded succesfully!")
	
	def imageFromFile(self,datapath,filename):
		debug.debugMessage(5," Opening objects image file.")
		self.graphics  = utilities.load_image(datapath,filename)

	def loadScripts(self,datapath,filename):
		if not os.path.exists(os.path.join(datapath, filename)): debug.debugMessage(0,"   Object script list file not located!")
		FILE=open(os.path.join(datapath, filename),"r")
		full=FILE.read()+chr(10)
		FILE.close()
		mode=0
		script=""
		cchar=''
		current=''
		for i in range(0,len(full)):
			cchar=full[i]
			if mode==0:
				if cchar=="=":
					script=current
					current=''
					mode=1
				else:
					current+=cchar
			else:
				if cchar==chr(10):
					value=current
					debug.debugMessage(3,"Loading script "+script+" from: "+os.path.join(datapath, "scripts", value))
					if not os.path.exists(os.path.join(datapath, "scripts", value)): debug.debugMessage(1,"   Script '"+ script + "' file not located!")
					FILE2=open(os.path.join(datapath, "scripts", value),"r")
					self.scripts[script]=FILE2.read()
					FILE2.close()
					mode=0
					current=''
				else:
					current+=cchar
	def fromFile(self,datapath,filename):
		debug.debugMessage(5," Loading object set from file.")
		if not os.path.exists(os.path.join(datapath, filename)): debug.debugMessage(0,"   Objectset file not located")
		FILE=open(os.path.join(datapath, filename),"r")
		full=FILE.read()
		cchar=''
		current=''
		mode=-2
		curObject=0
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
			if   mode == -2:
				if a==4:
					self.graphics=utilities.load_image(datapath,current)
					mode=-1
					current=''
				else: current+=cchar
			elif mode == -1:
				if a==4:
					debug.debugMessage(5,"Loading object action scripts")
					self.loadScripts(datapath,current)
					mode=0
					current=''
				else: current+=cchar
			elif mode ==  0:    #This reads number of object, like "#134#"
				if   a==1:
					current+=cchar
				elif a==4:
					curObject=int(current)
					while(len(self.objectDefinition)<curObject+1):
						self.objectDefinition+= [OBJECTDEF()]
					debug.debugMessage(3,"Loading tile "+current)
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
						prop=current.lower()
						if prop in ["name","corpse","image"]:
							mode = 2
						else:
							mode = 3
						current=''
			elif mode==2:   #This reads string     value for the property and assigns it
				if a == 1 or a == 2 or a == 3 or a == 0:
					current+=cchar
				elif a == 4:
					if   prop == "name":
						self.objectDefinition[curObject].name=current
					elif prop == "corpse":
						objectset.props.corpse=current
					elif prop == "image":
						b=[]
						curpr=""
						for o in range(0,len(current)):
							if current[o] == ',' or current[o] == ';':
								b+=[int(curpr)]
								curpr=''
							else:
								curpr+=current[o]
						self.objectDefinition[curObject].image=pygame.Rect( b[0], b[1], b[2], b[3])
					print prop,"=",current
					current=''
					mode=1
			elif mode == 3: #This reads integer(s) value for the property and assigns it
				if   a == 1 or a == 2:
					current+=cchar
				elif a == 4:
					if   prop == "weight":       self.objectDefinition[curObject].props.weight       = int(current)
					elif prop == "speed":        self.objectDefinition[curObject].props.speed        = int(current)
					elif prop == "terrainattackmin":self.objectDefinition[curObject].props.terrainAttack[0] = int(current)
					elif prop == "terrainattackmax":self.objectDefinition[curObject].props.terrainAttack[1] = int(current)
					elif prop == "hp":           self.objectDefinition[curObject].props.hp           = int(current)
					elif prop == "magicemit":   self.objectDefinition[curObject].props.magic_emit    = int(current)
					elif prop[0:6] == "script":
						#print prop[6:,current
						#print "ABRAKADABRA!"
						self.objectDefinition[curObject].props.scripts[prop[6:len(prop)]]            = current
						print self.objectDefinition[curObject].props.scripts
					#if prop[0:6] == "script": print prop[6:len(prop)],"=",current
					#else: print prop,"=",current
					current=''
					mode=1
	def Type(self): return "OBJECTSET"

class OBJECT:
	def __init__(self,world,otype):
		self.position=[0,0]
		self.type=otype
		self.world=world
	
	def execAction(self,action,props):
		if not self.world.objectset.objectDefinition[self.type].props.scripts.has_key(action): debug.debugMessage(2,"Object does not have script for action: '"+action+"'")
		else:
			a= "props="+str(props)+chr(10)+self.world.objectset.scripts[self.world.objectset.objectDefinition[self.type].props.scripts[action]]
			exec(a)

	def getProp(self,propname):
		if propname in ["pos","position"]:
			return self.position
		elif propname in ["posX","positionX","pos.X","position.X"]:
			return self.position[0]
		elif propname in ["posY","positionY","pos.Y","position.Y"]:
			return self.position[1]
		elif propname == "type":
			return self.type
		elif propname in [""]:
			return self.position[0]

	def Type(self): return "OBJECT"
	
	

