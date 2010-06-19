import debug, perlin

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
		debug.debugMessage(3,"  Initializing generator...")
		self.big_feature   =perlin.PerlinNoise((big,big),perlin.ease_interpolation)
		self.small_feature =perlin.PerlinNoise((small,small),perlin.ease_interpolation)
		self.climate	   =perlin.PerlinNoise((climate,climate),perlin.ease_interpolation)
		self.lakes		   =perlin.PerlinNoise((lake,lake),perlin.ease_interpolation)
		debug.debugMessage(4,"   Generator initialized!")
