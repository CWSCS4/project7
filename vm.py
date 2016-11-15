#!/usr/bin/python

import sys

def decrementSP(): #helper function for decrementing pointer
	print "@SP"
	print "AM=M-1"

def decode(inputC,writeTo): #gets the desired address/value from inputC case by case depending on whether writeTo is true/false. writeTo signifies either pop or push
	if inputC[0]=="local": #LCL, ARG, THIS and THAT are first accessed in memory to get the value that is being stored in the respective register
		if not writeTo:
			print "@LCL"
			print "D=M"
			print "@"+inputC[1]
			print "A=D+A"
			print "D=M"
			print "@SP"
			print "A=M"
			return "D"

		print "@LCL"
		print "D=M"
		print "@"+inputC[1]
		print "D=D+A"
		print "@SP"
		print "A=M"

		return "D"
	elif inputC[0]=="argument":
		if not writeTo:
			print "@ARG"
			print "D=M"
			print "@"+inputC[1]
			print "A=D+A"
			print "D=M"
			print "@SP"
			print "A=M"
			return "D"

		print "@ARG"
		print "D=M"
		print "@"+inputC[1]
		print "D=D+A"
		print "@SP"
		print "A=M"

		return "D"
	elif inputC[0]=="this":
		if not writeTo:
			print "@THIS"
			print "D=M"
			print "@"+inputC[1]
			print "A=D+A"
			print "D=M"
			print "@SP"
			print "A=M"
			return "D"

		print "@THIS"
		print "D=M"
		print "@"+inputC[1]
		print "D=D+A"
		print "@SP"
		print "A=M"

		return "D"
	elif inputC[0]=="that":
		if not writeTo:
			print "@THAT"
			print "D=M"
			print "@"+inputC[1]
			print "A=D+A"
			print "D=M"
			print "@SP"
			print "A=M"
			return "D"

		print "@THAT"
		print "D=M"
		print "@"+inputC[1]
		print "D=D+A"
		print "@SP"
		print "A=M"

		return "D"
	elif inputC[0]=="temp":
		if not writeTo:
			print "@"+str(5+int(inputC[1]))
			print "D=M"
			print "@SP"
			print "A=M"
			return "D"

		return str(5+int(inputC[1]))
	elif inputC[0]=="pointer":
		if not writeTo:
			print "@"+str(3+int(inputC[1]))
			print "D=M"
			print "@SP"
			print "A=M"
			return "D"

		return str(3+int(inputC[1]))
	elif inputC[0]=="temp":
		if not writeTo:
			print "@"+str(5+int(inputC[1]))
			print "D=M"
			print "@SP"
			print "A=M"
			return "D"

		return str(5+int(inputC[1]))
	elif inputC[0]=="constant":
		if not writeTo:
			print "@"+inputC[1]
			print "D=A"
			print "@SP"
			print "A=M"
			return "D"

		print "why are you trying to write to a constant"

	elif inputC[0]=="static":
		if not writeTo:
			tempname = path.split("/")[-1].split(".")[0]
			print "@"+tempname+inputC[1]
			print "D=M"
			return "D"
		return tempname+inputC[1]

def pushC(inputC): #loads SP value and increments it while writing a decoded input to the next SP address
	temp = str(decode(inputC[1:], False))
	print "@SP"
	print "A=M"
	print "M="+temp
	print "@SP"
	print "M=M+1"

def popC(inputC): #decrements from SP and writes previous value to specified address
	temp = str(decode(inputC[1:], True))
	print "@R15"
	if temp == "D":
		print "M=D"
		decrementSP()
		print "D=M"
		print "@R15"
		print "A=M"
		print "M=D"
	else:
		print "@"+temp
		print "D=A"
		print "@R15"
		print "M=D"
		decrementSP()
		print "D=M"
		print "@R15"
		print "A=M"
		print "M=D"

def negC(inputC): #loads SP and negates the value at it
	print "@SP"
	print "D=M-1"
	print "A=D"
	print "M=-M"

def arithC(inputC,type):
	decrementSP()
	print "D=M"
	decrementSP()
	print "D=M"+type+"D"
	print "@SP"
	print "A=M"
	print "M=D"
	print "@SP"
	print "M=M+1"

def notC(inputC): #loads SP and takes the bitwise ! of its current value
	print "@SP"
	print "D=M-1"
	print "A=D"
	print "M=!M"

def compC(input, type): #loads 2 values and uses jump logic to set an appropiate value. If the values are not equal, the value is set to 0 and the program is
	global jumpct
	decrementSP() #unconditionally jumped to the end. If the values are equal, the program jumps to label (EQ) and runs to the end.
	print "D=M"
	decrementSP()
	print "D=M-D"
	print "@"+type+str(jumpct)
	print "D;"+type
	print "@SP"
	print "A=M"
	print "M=0"
	print "@END"+str(jumpct)
	print "0;JMP"
	print "("+type+str(jumpct)+")"
	print "@SP"
	print "A=M"
	print "M=-1"
	print "(END"+str(jumpct)+")"
	print "@SP"
	print "M=M+1"
	jumpct+=1

path = str(sys.argv[1])
jumpct = 0
print "@256"
print "D=A"
print "@SP"
print "M=D"
with open(path) as file:
	for line in file: #loops through standard input
		if line!='' and line[:2]!="//": #filters out empty lines, whitespace and comments
			try:
				line=line[:line.index("//")]
			except:
				pass
			current=line.split(" ")
			current = filter(lambda x:(x!=""),current)
			typeof = current[0].rstrip() #calls function based on type of command
			if typeof == "push":
				pushC(current)
			elif typeof == "pop":
				popC(current)
			elif typeof == "add":
				arithC(current,"+")
			elif typeof == "sub":
				arithC(current,"-")
			elif typeof == "neg":
				negC(current)
			elif typeof == "eq":
				compC(current,"JEQ")
			elif typeof == "gt":
				compC(current,"JGT")
			elif typeof == "lt":
				compC(current,"JLT")
			elif typeof == "and":
				arithC(current,"&")
			elif typeof == "or":
				arithC(current,"|")
			elif typeof == "not":
				notC(current)
