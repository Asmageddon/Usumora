import  random, debug, generator, pygame, psyco

psyco.full()

class LOCALMAP:
	#genedchunks=0
	def Type(self): return "LOCALMAP"
	def generate(self,generator,positionX,positionY):
		debug.debugMessage(3,"  Generating chunk...")
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
		debug.debugMessage(4,"   Chunk generated("+str(positionX)+","+str(positionY)+")")
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
			debug.debugMessage(4,"  Drawn a new chunk!")
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
			if smashed>0: self.modified=1
			self.updateTile(tileset, position)
	def  modifyTile(self,tileset,position,newtype):
		self.mapChunk[position[0]][position[1]]=newtype
		self.updateTile(tileset, position)
		self.modified=1
class GLOBALMAP:
	def __init__(self,parent,big,small,climate,lake):
		self.chunkCollection={}
		self.parent=parent
		self.generator=[]
		debug.debugMessage(3," Initializing world map...")
		self.chunkCollection={}
		self.generator=generator.GENERATOR(big,small,climate,lake)
		debug.debugMessage(3," World map initialized")
	def Type(self): return "GLOBALMAP"
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
			#debug.debugMessage("Deleted chunk"+str(pos)+"!")
			return 1
		else:
			return 0
	def requestChunkImageDeletion(self, pos):
		if self.chunkCollection.has_key(pos) and not self.chunkCollection[pos].cachedimage=="NULL":
			self.chunkCollection[pos].cachedimage="NULL"
			#debug.debugMessage("Deleted chunk"+str(pos)+"!")
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
		if(b>0 or b2>0): debug.debugMessage(5, "Deleted " + str(b) +" chunks and " +str(b+b2) + " cached images!")
		return 1
