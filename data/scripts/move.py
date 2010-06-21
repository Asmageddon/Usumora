vector=[0,0]
if 'l' in props['vector']:   vector[0] = -1
elif 'r' in props['vector']: vector[0] =  1
if 'u' in props['vector']:   vector[1] = -1
elif 'd' in props['vector']: vector[1] =  1
mode=props['mode']
destination=(self.position[0]+vector[0],self.position[1]+vector[1])
selfdef=self.world.objectset.objectDefinition[self.type]
dmg=random.randint(selfdef.props.terrainAttack[0],selfdef.props.terrainAttack[1])
tileDef=self.world.tileset.tileDefinition[self.world.gamemap.getTile(destination)]
if(tileDef.collision==gc.C_NULL):
	#if self.world.objectset[self.type].
	if mode & gc.MOVE_CAREFULL: success = 0
	else:
		if mode & gc.MOVE: self.position=destination
		success = 1
elif(tileDef.collision==gc.C_FLOOR):
	if not mode & gc.MOVE_FLOOR:
		if mode & gc.MOVE_AGGRO:
			self.world.gamemap.damageTile(destination,dmg)
			success = 0
	else:
		if mode & gc.MOVE: self.position=destination
		success = 1
elif(tileDef.collision==gc.C_LIQUID):
	if not mode & gc.MOVE_LIQUID:
		if mode & gc.MOVE_AGGRO_V:
			self.world.gamemap.damageTile(destination,dmg)
			success = 0
	else:
		if mode & gc.MOVE: self.position=destination
		success = 1
elif(tileDef.collision==gc.C_WALL):
	if not mode & gc.MOVE_WALL:
		if mode & gc.MOVE_AGGRO:
			self.world.gamemap.damageTile(destination,dmg)
			success = 0
	else:
		if mode & gc.MOVE: self.position=destination
		success = 1
#if dest
success = 1
