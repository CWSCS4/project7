#!/usr/bin/env python

import sys

def decrementSP(): #helper function for decrementing pointer
    print "@SP"
    print "AM=M-1"

def decode(inputC,writeTo): #could be made a lot nicer and shorter
    if inputC[0]=="local":
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
            print "@tempname."+inputC[1]
            print "D=M"
            return "D"
        return "tempname."+inputC[1]

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


def addC(inputC): #takes 2 values from the stack and adds them
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=M+D"
    print "@SP"
    print "A=M"
    print "M=D"
    print "@SP"
    print "M=M+1"

def subC(inputC): #same as addC() but with a minus sign
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=M-D"
    print "@SP"
    print "A=M"
    print "M=D"
    print "@SP"
    print "M=M+1"

def negC(inputC): #loads SP and negates the value at it
    print "@SP"
    print "D=M-1"
    print "A=D"
    print "M=-M"

def andC(inputC): #loads 2 values from the stack and writes the & to the stack
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=D&M"
    print "@SP"
    print "A=M"
    print "M=D"
    print "@SP"
    print "M=M+1"

def orC(inputC): #loads 2 values from the stack and writes the | to the stack
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=D|M"
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

def eqC(input): #loads 2 values and uses jump logic to set an appropiate value. If the values are not equal, the value is set to 0 and the program is
    global jumpct
    decrementSP() #unconditionally jumped to the end. If the values are equal, the program jumps to label (EQ) and runs to the end.
    print "D=M"
    decrementSP()
    print "D=D-M"
    print "@EQ"+str(jumpct)
    print "D;JEQ"
    print "@SP"
    print "A=M"
    print "M=0"
    print "@END"+str(jumpct)
    print "0;JMP"
    print "(EQ"+str(jumpct)+")"
    print "@SP"
    print "A=M"
    print "M=-1"
    print "(END"+str(jumpct)+")"
    print "@SP"
    print "M=M+1"
    jumpct+=1

def gtC(input): #very similar to eq(). Same logic behind jumping based on initial "D=D-M" value
    global jumpct
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=M-D"
    print "@GT"+str(jumpct)
    print "D;JGT"
    print "@SP"
    print "A=M"
    print "M=0"
    print "@END"+str(jumpct)
    print "0;JMP"
    print "(GT"+str(jumpct)+")"
    print "@SP"
    print "A=M"
    print "M=-1"
    print "(END"+str(jumpct)+")"
    print "@SP"
    print "M=M+1"
    jumpct+=1

def ltC(input): #very similar to eq(). Same logic behind jumping based on initial "D=D-M" value
    global jumpct
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=M-D"
    print "@LT"+str(jumpct)
    print "D;JLT"
    print "@SP"
    print "A=M"
    print "M=0"
    print "@END"+str(jumpct)
    print "0;JMP"
    print "(LT"+str(jumpct)+")"
    print "@SP"
    print "A=M"
    print "M=-1"
    print "(END"+str(jumpct)+")"
    print "@SP"
    print "M=M+1"
    jumpct+=1

jumpct = 0
stackPointer = 256
print "@256"
print "D=A"
print "@SP"
print "M=D"
for line in sys.stdin: #loops through standard input
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
            addC(current)
        elif typeof == "sub":
            subC(current)
        elif typeof == "neg":
            negC(current)
        elif typeof == "eq":
            eqC(current)
        elif typeof == "gt":
            gtC(current)
        elif typeof == "lt":
            ltC(current)
        elif typeof == "and":
            andC(current)
        elif typeof == "or":
            orC(current)
        elif typeof == "not":
            notC(current)
