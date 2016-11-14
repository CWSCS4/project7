def decrementSP(): #helper function for decrementing pointer
    print "@SP"
    print "AM=M-1"

def decode(inputC,writeTo): #could be made a lot nicer and shorter
    if inputC[0]=="local":
        if not writeTo:
            print "@"+inputC[0]
            print "D=A"
            print "@"+inputC[1]
            print "A=D+A"
            print "D=M"
            print "@SP"
            print "A=M"
            return "D"
        
        print "@"+inputC[0]
        print "D=A"
        print "@"+inputC[1]
        print "D=D+A"
        print "@SP"
        print "A=M"
        
        return "D"
    elif inputC[0]=="argument":
        if not writeTo:
            print "@"+inputC[0]
            print "D=A"
            print "@"+inputC[1]
            print "A=D+A"
            print "D=M"
            print "@SP"
            print "A=M"
            return "D"
        
        print "@"+inputC[0]
        print "D=A"
        print "@"+inputC[1]
        print "D=D+A"
        print "@SP"
        print "A=M"
        
        return "D"
    elif inputC[0]=="this":
        if not writeTo:
            print "@"+inputC[0]
            print "D=A"
            print "@"+inputC[1]
            print "A=D+A"
            print "D=M"
            print "@SP"
            print "A=M"
            return "D"
        
        print "@"+inputC[0]
        print "D=A"
        print "@"+inputC[1]
        print "D=D+A"
        print "@SP"
        print "A=M"
        
        return "D"
    elif inputC[0]=="that":
        if not writeTo:
            print "@"+inputC[0]
            print "D=A"
            print "@"+inputC[1]
            print "A=D+A"
            print "D=M"
            print "@SP"
            print "A=M"
            return "D"
        
        print "@"+inputC[0]
        print "D=A"
        print "@"+inputC[1]
        print "D=D+A"
        print "@SP"
        print "A=M"
        
        return "D"
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
            print "D=M"
            print "@SP"
            print "A=M"
            return "D"

        print "why are you trying to write to a constant"
def pushC(inputC): #loads SP value and increments it while writing a decoded input to the next SP address
    print "@SP"
    print "A=M"
    print "M="+decode(inputC[1:], False)
    print "@SP"
    print "M=M+1"

def popC(inputC): #decrements from SP and writes previous value to specified address
    decrementSP()
    print "D=M"
    print "@"+decode(inputC[:1], True)
    print "M=D"

def addC(inputC): #takes 2 values from the stack and adds them
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=M+D"
    print "@SP"
    print "@M"
    print "M=D"

def subC(inputC): #same as addC() but with a minus sign
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=M-D"
    print "@SP"
    print "@M"
    print "M=D"

def negC(inputC): #loads SP and negates the value at it
    print "@SP"
    print "A=M"
    print "D=M-1"
    print "@D"
    print "M=-M"

def andC(inputC): #loads 2 values from the stack and writes the & to the stack
    decrementSP()
    print "@M"
    print "D=M"
    decrementSP()
    print "@M"
    print "M=D&M"

def orC(inputC): #loads 2 values from the stack and writes the | to the stack
    decrementSP()
    print "@M"
    print "D=M"
    decrementSP()
    print "@M"
    print "M=D|M"

def notC(inputC): #loads SP and takes the bitwise ! of its current value
    print "@SP"
    print "A=M"
    print "D=M-1"
    print "@D"
    print "M=!M"

def eqC(input): #loads 2 values and uses jump logic to set an appropiate value. If the values are not equal, the value is set to 0 and the program is
    decrementSP() #unconditionally jumped to the end. If the values are equal, the program jumps to label (EQ) and runs to the end.
    print "D=M"
    decrementSP()
    print "D=D-M"
    print "@EQ"
    print "D;JEQ"
    print "@SP"
    print "M=0"
    print "@END"
    print "0;JMP"
    print "(EQ)"
    print "@SP"
    print "M=1"
    print "(END)"

def gtC(input): #very similar to eq(). Same logic behind jumping based on initial "D=D-M" value
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=D-M"
    print "@GT"
    print "D;JGT"
    print "@SP"
    print "M=0"
    print "@END"
    print "0;JMP"
    print "(GT)"
    print "@SP"
    print "M=1"
    print "(END)"

def gtC(input): #very similar to eq(). Same logic behind jumping based on initial "D=D-M" value
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=D-M"
    print "D=M-D"
    print "@LT"
    print "D;JLT"
    print "@SP"
    print "M=0"
    print "@END"
    print "0;JMP"
    print "(LT)"
    print "@SP"
    print "M=1"
    print "(END)"

stackPointer = 256
print "@SP"
print "M=256"
for line in sys.stdin: #loops through standard input
    if line!='' and line[:2]!="//": #filters out empty lines, whitespace and comments
        try:
            line=line[:line.index("//")]
        except:
            pass
        current=line.split(" ")
        current = filter(lambda x:(x!="",current)
        typeof = current[0] #calls function based on type of command
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
