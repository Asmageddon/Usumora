def debugMessage(messageType,string):
	#return 0
	a=""
	if   messageType==0: a="\033[101m[FATAL ERROR]"  #Fatal error
	elif messageType==1: a="\033[100m\033[91m[ERROR]"#Error
	elif messageType==2: a="\033[91m[WARNING]"       #Warning
	elif messageType==3: a="\033[94m[NOTICE]"        #Regular notice
	elif messageType==4: a="\033[92m[NOTICE]"        #Succes  notice
	elif messageType==5: a="\033[95m[NOTICE]"        #Special notice
	print a+string+"\033[0m"
	if   messageType<2: print "Exiting"; raise SystemExit
