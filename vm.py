def decrementSP(): #helper function for decrementing pointer
    print "@SP"
    print "M=M-1"

def pushC(input): #loads SP value and increments it while writing a decoded input to the next SP address
    print "@SP"
    print "@M"
    print "M="+decode(input[1:])
    print "@SP"
    print "M=M+1"

def popC(input): #decrements from SP and writes previous value to specified address
    decrementSP()
    print "@M"
    print "D=M"
    print "@"+decode(input[:1])
    print "M=D"

def addC(input): #takes 2 values from the stack and adds them
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=M+D"
    print "@SP"
    print "@M"
    print "M=D"

def subC(input): #same as addC() but with a minus sign
    decrementSP()
    print "D=M"
    decrementSP()
    print "D=M-D"
    print "@SP"
    print "@M"
    print "M=D"

def negC(input): #loads SP and negates the value at it
    print "@SP"
    print "D=M-1"
    print "@D"
    print "M=-M"

def andC(input): #loads 2 values from the stack and writes the & to the stack
    decrementSP()
    print "@M"
    print "D=M"
    decrementSP()
    print "@M"
    print "M=D&M"

def orC(input): #loads 2 values from the stack and writes the | to the stack
    decrementSP()
    print "@M"
    print "D=M"
    decrementSP()
    print "@M"
    print "M=D|M"

def notC(input): #loads SP and takes the bitwise ! of its current value
    print "@SP"
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
