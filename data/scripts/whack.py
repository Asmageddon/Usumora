import random
print props
for xz in props:
	pos=self.position
	px=float(xz[0]-pos[0])
	py=float(xz[1]-pos[1])
	a= max(abs(px),abs(py))
	i2=0.0
	if px!=0 or py!=0:
		px/= a
		py/= a
		#print px,py
		#offset=[px,py]
		for i in range(0,10):
			#for y in range(0,i):
			dest2=(xz[0]+int(i2*px),xz[1]+int(i2*py))
			if self.world.gamemap.damageTile(dest2,(11-i)*10) == 32: i2+=1.0
		success = 1
