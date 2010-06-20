vector=props['vector']
mode=props['mode']
destination=(self.position[0]+vector[0],self.position[1]+vector[1])
selfdef=self.world.objectset.objectDefinition[self.type]
dmg=random.randint(selfdef.props.terrainAttack[0],selfdef.props.terrainAttack[1])
modes=[0,0,0,0,0,0,0,0]
for i in range(0,7):
	if mode>math.pow(2,7-i):
		modes[7-i]=1
		mode-=math.pow(2,7-i)
	else:
		modes[7-i]=0
tileDef=self.world.tileset.tileDefinition[self.world.gamemap.getTile(destination)]
if(tileDef.collision==gc.C_NULL):
	#if self.world.objectset[self.type].
	if modes[gc.MOVE_CAREFULL_V]: success = 0
	else:
		self.position=destination
		success = 1
elif(tileDef.collision==gc.C_FLOOR):
	if not modes[gc.MOVE_FLOOR_V]:
		if modes[gc.MOVE_AGGRO_V]:
			self.world.gamemap.damageTile(destination,dmg)
			success = 0
	else:
		self.position=destination
		success = 1
elif(tileDef.collision==gc.C_LIQUID):
	if not modes[gc.MOVE_LIQUID_V]:
		if modes[gc.MOVE_AGGRO_V]:
			self.world.gamemap.damageTile(destination,dmg)
			success = 0
	else:
		self.position=destination
		success = 1
elif(tileDef.collision==gc.C_WALL):
	if not modes[gc.MOVE_WALL_V]:
		if modes[gc.MOVE_AGGRO_V]:
			self.world.gamemap.damageTile(destination,dmg)
			success = 0
	else:
		self.position=destination
		success = 1
#if dest
success = 1
