import debug, os

class KEYMAP:
	def __init__(self):
		self.keymap={}
		#keymap[(a key, a mod)] = [type,action,prop]
		self.bind=""
		self.monomodkeys=1
		self.activeInput={}
		self.keyRepeatStartup   = 8
		self.keyRepeat          = 2
		#self.activeInput[(a key, a mod)]=number #Number gets decreased each frame, when it reaches 0 the (a key, a mod) action is executed again, when corresponding key is released (a key, a mod) element is removed.

	def   keyInputActivate(self,key,mod):
		if mod & 4096: mod-=4096
		if self.monomodkeys==1:
			if mod & 2:     mod-=1
			if mod & 128:   mod-=64
			if mod & 16384: mod-=16128
		if self.keymap.has_key((key,mod)):
			self.activeInput[(key, mod)]=self.keyRepeatStartup

	def keyInputDeactivate(self,key,mod):
		if mod & 4096: mod-=4096
		if self.monomodkeys==1:
			if mod & 2:     mod-=1
			if mod & 128:   mod-=64
			if mod & 16384: mod-=16128
		if self.activeInput.has_key((key,mod)):
			del self.activeInput[(key, mod)]

	def keyInputRepeat(self,game):
		#print self.activeInput
		for a in self.activeInput:
			print a
			self.activeInput[a]-=1
			if self.activeInput[a]<0:
				print "Repeating: " + str(self.keymap[a])
				game.receiveInput(self.keymap[a])
				self.activeInput[a]=self.keyRepeat

	def keyInput(self,key,mod, game):
		if mod & 4096: mod-=4096
		if self.monomodkeys==1:
			if mod & 2:     mod-=1
			if mod & 128:   mod-=64
			if mod & 16384: mod-=16128
		print "Received: " + str(key) +", " + str(mod)
		if self.keymap.has_key((key,mod)): game.receiveInput(self.keymap[(key,mod)]); return 1
		else: return 0

	def fromFile(self,datapath, filename):
		debug.debugMessage(3,"Trying to load keymap from file: "+os.path.join(datapath,filename))
		if not os.path.exists(os.path.join(datapath, filename)): debug.debugMessage(0,"   Keymap file " + str(os.path.join(datapath, filename)) + " does not exist!")
		FILE=open(os.path.join(datapath, filename),"r")
		full=FILE.read()
		FILE.close()
		legitchars  = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']
		funcchars = [',','.','=','-',':']
		endl      = [chr(10),';']
		key       = 0
		mod       = 0
		action    = []
		mode      = 0
		current=''
		for i in range(0,len(full)):
			cchar=full[i]
			if cchar == '#': mode=-1
			if mode == -1:  #Comment rea... ignore mode :>
				if cchar in endl: mode=0; current=''
			elif mode == 0: #key read mode
				if cchar in funcchars:
					mode=1
					key=int(current)
					current=''
				elif cchar in legitchars:
					current+=cchar
			elif mode == 1:  #Modifier key read mode
				if cchar in funcchars:
					mode=2
					mod=int(current)
					if mod & 4096: mod-=4096
					if self.monomodkeys==1:
						if mod & 2:     mod-=1
						if mod & 128:   mod-=64
						if mod & 16384: mod-=16128
					current=''
				elif cchar in legitchars:
					current+=cchar
			elif mode == 2:
				if   cchar in endl:
					action+=[current]
					print str(key)+","+str(mod)+"="+str(action)
					self.bindKey(key,mod,action)
					action=[]
					mod=0
					key=0
					current=''
					mode=0
				elif cchar in funcchars:
					action+=[current]
					current=''
				elif cchar in legitchars:
					current+=cchar

	def bindKey(self,key,mod,action):
		self.keymap[(key,mod)]=action

	def stripNumlock(self, modifier):
		if modifier & 4096: modifier-=4096
		return modifier
