#!/usr/bin/env python
#!/usr/bin/python

import sys

def decrementSP(): #helper function for decrementing pointer
	print "@SP"
	print "AM=M-1"

def accessLoc(inputC, writeTo, typeC): #inputC and writeTo are the same as in decode(). typeC is a string that is passed from the if statement blocks
	if not writeTo: #in decode that signifies the assembler-friendly representation of the address
		print "@"+typeC
		print "D=M"
		print "@"+inputC[1]
		print "A=D+A"
		print "D=M"
		print "@SP"
		print "A=M"
		return "D"

	print "@"+typeC
	print "D=M"
	print "@"+inputC[1]
	print "D=D+A"
	print "@SP"
	print "A=M"

	return "D"

def decode(inputC,writeTo): #gets the desired address/value from inputC case by case depending on whether writeTo is true/false. writeTo signifies either pop or push
	if inputC[0]=="local": #LCL, ARG, THIS and THAT are first accessed in memory by passing in relevant arguments to accessLoc() to get the value that is being stored in the respective register
		return accessLoc(inputC, writeTo, "LCL")
	elif inputC[0]=="argument":
		return accessLoc(inputC, writeTo, "ARG")
	elif inputC[0]=="this":
		return accessLoc(inputC, writeTo, "THIS")
	elif inputC[0]=="that":
		return accessLoc(inputC, writeTo, "THAT")

	elif inputC[0]=="temp": #temp, pointer and constant are handled on their own. The first two simply add 5 or 3 (temp and pointer respectively) to the second element of inputC
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
	elif inputC[0]=="constant": #constant is handled by simply loading it into the A register and then into the D register. No support for writing to a constant is offered.
		if not writeTo:
			print "@"+inputC[1]
			print "D=A"
			print "@SP"
			print "A=M"
			return "D"

		print "why are you trying to write to a constant"

	elif inputC[0]=="static": #static variables are allocated their own space using path from command line arguments.
		tempname = path.split("/")[-1].split(".")[0]
		tempname += "."
		if not writeTo:
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

def arithC(inputC,typeC): #general arithmatic handler, typeC is a string that holds the assembler-friendly representation of the desired address
	decrementSP()
	print "D=M"
	decrementSP()
	print "D=M"+typeC+"D"
	print "@SP"
	print "A=M"
	print "M=D"
	print "@SP"
	print "M=M+1"

def notC(inputC): #loads SP and takes the bitwise ! of its current value. I suppose I could have combined this with negC(), but since each is so short I decided to leave them be.
	print "@SP"
	print "D=M-1"
	print "A=D"
	print "M=!M"

def compC(input, typeC): #general comparative helper function. typeC is passed in through the main lood and represents an assembler-friendly versin of the desired comparison
	global jumpct
	decrementSP()
	print "D=M"
	decrementSP()
	print "D=M-D"
	print "@"+typeC+str(jumpct)
	print "D;"+typeC
	print "@SP"
	print "A=M"
	print "M=0"
	print "@END"+str(jumpct)
	print "0;JMP"
	print "("+typeC+str(jumpct)+")"
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
