import debug, os, sys, utilities, pygame, psyco

psyco.full()

class TILE:     #This class contains tile information, self.tileDefinition are stored instead TILESET and define specific tile type properties
	def __init__(self):
		self.images      = [pygame.Rect(0,0,32,32),pygame.Rect(0,0,32,32),pygame.Rect(0,0,32,32),pygame.Rect(0,0,32,32),pygame.Rect(0,0,32,32),pygame.Rect(0,0,32,32),pygame.Rect(0,0,32,32),pygame.Rect(0,0,32,32)] #Image for 4xnormal, cracked, damaged and broken tile
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
	def Type(self): return "TILE"


class TILESET:
	def __init__(self):
		debug.debugMessage(3,"Creating tileset object...")
		self.tileset=[]
		self.tileDefinition=[]
		debug.debugMessage(4," Tileset created!")
	def Type(self): return "TILESET"
	def fromFile(self,datapath,filename):
		debug.debugMessage(3," Trying to load tileset from file: "+ os.path.join(datapath, filename))
		if not os.path.exists(os.path.join(datapath, filename)): debug.debugMessage(0,"   Tileset file not located")
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
					self.tileset=utilities.load_image(datapath,current)
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
								self.tileDefinition[curTile].images[i2]=pygame.Rect( (b[0]   )*32, b[1]*32, 32, 32)
							elif prop[6] == '+':
								self.tileDefinition[curTile].images[i2]=pygame.Rect( (b[0]+i2)*32, b[1]*32, 32, 32)
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
