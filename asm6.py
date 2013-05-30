# Port of asm6 to python
import sys
import re

class label:
    labelName = ""
    value = None #function to call to handle this label #PC (label), value (equate), param count (macro), funcptr (reserved)
    typeOfLabel=0
    isUsed=False #for EQU and MACRO recursion check
    passLabelWasDefined=-1 #when label was last defined
    scope = -1 # where visible (0=global, nonzero=local)

class Asm6:

    insideMacro = False
    verboseListing = False
    isVerbose = False
    asmFileInputName = ""
    binFileOutputName = ""
    listFileName = ""
    maxPasses = 7 # number of tries before giving up

    reptCount = 0 #counts rept statements during rept string storage

    def initLabels(self):
        print ("init Labels")

    def findLabel(self, start):
        return None

#
# getReserved, gets word in src and return reserved label
#
    def getReserved(self, src):
        return False

    def listLine(self, line, comment):
        if (self.listFileName == ""): return

    def handleMakeMacro(self):
        return

    def handleRept(self):
        return

    # seems to just return the line without the comment
    def expandLine(self, line):
        dst="" #dst is return value
        i=0
        def_skip = False
        start = ""
        comment = ""

        while i < len(line):
            current_char = line[i]
            
            #read past number
            if re.match("[$0-9]", current_char):
                while re.match("[$0-9]", current_char): # if(c=='$' || (c>='0' && c<='9')) {//read past numbers (could be mistaken for a symbol, i.e. $BEEF)
                    i += 1
                    dst += current_char
                    current_char = line[i]
            elif re.match("['\"]", current_char):
                #read past quotes
                while re.match("['\"]", current_char): # read past quotes
                    i += 1
                    dst += current_char
                    current_char = line[i]
            # check if symbol
            # 
            elif re.match("[A-Za-z_.@]", current_char): #else if(c=='_' || c=='.' || c==LOCALCHAR || (c>='A' && c<='Z') || (c>='a' && c<='z')) {//symbol
                start = line[i:]
                #scan to end of symbol
                while (re.match("[A-Za-z0-9_.@]", current_char)):
                    i += 1
                    dst += current_char
                    current_char = line[i]
                # now for the 'hack'
                if (def_skip == False):
                    upp = start.replace('.','',1).upper() #remove the . at the start and make it uppercase
                    if upp == "IFDEF" or upp == "IFNDEF":
                        def_skip = True
                    else:
                        p_label = self.findLabel(start)

                if (p_label):
                    NOP=0 # do nothing
                    #if((*p).type!=EQUATE || (*p).pass!=pass)//equates MUST be defined before being used otherwise they will be expanded in their own definition
                    #    #p=0;//i.e. (label equ whatever) gets translated to (whatever equ whatever)
                    #else {
                    #    if((*p).used) {
                    #        p=0;
                    #        errmsg=RecurseEQU;
                    #    }
                
                if (p_label): # if p_label is sill valid
                    p_label.used=True
                    self.expandLine(dst, start)
                    p_label.used = False
                else:
                    dst += start #strcpy(dst,start);
                #dst += len(dst) #move dst pointer along by length
                #*src=c;
            else:
                if line[i] == ";":
                    comment = (line[i:])
                    return (comment,dst)
                dst += current_char
                #dst++
                #src++
            i += 1
        return (comment,dst)

    def processLine(self, line, line_number):
        comment = self.expandLine(line)

        if (not self.insideMacro or self.verboseListing): #as long as we aren't in a macro
            self.listLine(line, comment)

        self.handleMakeMacro()
        self.handleRept()
        p_label = self.getReserved(line)
        # if(skipline[iflevel]) {blah..}
        # if(!p) {blah..} //maybe a label?
        if p_label:
            if(p_label.type == MACRO):
                s=self.expandmacro(p_label,errline,errsrc)
            else:
                s=p_label.value(p_label)


    def processFile(self, _file):
        print ("processFile")
        lines = _file.readlines()
        line_number=0;
        for line in lines:
            line_number=line_number+1
            self.processLine(line,line_number)

    def assembleIncludeFile(self,label,file_name):
        print ('assembleIncludeFile'+file_name)
        _file=open(file_name,'r')
        self.processFile(_file)
        _file.close()

    def mainAssemblyLoop(self, asmFileInputName):
        self.asmFileInputName = asmFileInputName
        needs_another_pass = True #start the assembly loop
        pass_count = 0
        while needs_another_pass:
            pass_count += 1
            if pass_count >= self.maxPasses: needs_another_pass = False
            print ("pass:"+str(pass_count))
            self.assembleIncludeFile(0,asmFileInputName)
            
        print ("mainAssemblyLoop")

    def setVerbose(self, isVerbose):
        self.isVerbose = isVerbose

    def handle_db_opcode(self):
        print ("db opcode")

#
# global functions for managing input to the asm6 class
#
def parseArgs():
        print ("Parse command line arugments")
        asmFileInputName = "../mario_bros.asm"
        return asmFileInputName

def showHelp():
    print ("show Help")

if __name__ == "__main__": 
    num_of_arguments = len(sys.argv)
    if (num_of_arguments < 2):
        showHelp()
        exit #EXIT_FAILURE

    asm6 = Asm6()

    asm6.initLabels();

    asmFileInputName = parseArgs();

    asm6.mainAssemblyLoop(asmFileInputName);
