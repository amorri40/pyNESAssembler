from emulate import *
import struct
from opcodeHandelers import *

class NesCPU():
    accumulator = 0
    x_register = 0
    y_register = 0
    program_counter = 0#0x8000
    stack = 0xFF
    
    renderer = None
    nes_file = None
    instructions = None
    memory = None

    opcode_table = {}

    nmi = 0
    irq = 0
    reset = 0

    #Flags
    decimal_flag = 0
    negative_flag = 0
    overflow_flag = 0
    break_flag = 0
    interrupt_flag = 0
    zero_flag = 0
    carry_flag = 0

    def __init__(self, nes_file):
        self.nes_file = nes_file
        self.instructions = Instructions(self)
        self.createOpCodeTable()
        self.memory = Memory()

    

    def readProgramByte(self):
        byte = Memory.program_sections[0][self.program_counter]
        self.program_counter += 1
        return byte

    def createOpCodeTable(self):
        for opcode in reservedWordList:
            opcode_mem_list = reservedWordList[opcode]
            for mem_type in opcode_mem_list:
                
                hex_value = opcode_mem_list[mem_type]
                if (hex_value.find('0')==0):
                    hex_value = int(hex_value,16)
                    self.opcode_table[hex_value] = {'opcode':opcode, 'mem_type':mem_type}


    def readInstruction(self):
        opcode = (self.readProgramByte())
        if (opcode in self.opcode_table):
            opcode_name = self.opcode_table[opcode]['opcode']
            
            mem_type = self.opcode_table[opcode]['mem_type']
            address = self.readInstructionParameters(opcode_name, mem_type)
            self.instructions.execute_instruction(opcode_name, address)
        else:
            print ('Error opcode not in table: '+str(opcode)+' at loc:'+str(self.program_counter))

    # 
    # reads instruction parameters and returns the address that this opcode will operate on
    # 
    def readInstructionParameters(self, opcode_name, mem_type):
        if mem_type == 'Implied':
            return -1 #implied doesn't need an address
        elif mem_type == 'Absolute':
            byte1 = self.readProgramByte()
            byte2 = self.readProgramByte()
            return byte1
        elif mem_type == 'AbsoluteX':
            byte1 = self.readProgramByte()
            byte2 = self.readProgramByte()
            return byte1
        elif mem_type == 'AbsoluteY':
            byte1 = self.readProgramByte()
            byte2 = self.readProgramByte()
            return byte1
        elif mem_type == 'REL':
            byte1 = self.readProgramByte()
            return byte1
        elif mem_type == 'Immediate':
            byte1 = self.readProgramByte()
            return byte1
        elif mem_type == 'ZeroPage':
            byte1 = self.readProgramByte()
            return byte1
        elif mem_type == 'ZeroPageX':
            byte1 = self.readProgramByte()
            return byte1
        elif mem_type == 'ZeroPageY':
            byte1 = self.readProgramByte()
            return byte1
        elif mem_type == 'IND':
            byte1 = self.readProgramByte()
            return byte1
        elif mem_type == 'INDY':
            byte1 = self.readProgramByte()
            return byte1
        elif mem_type == 'INDX':
            byte1 = self.readProgramByte()
            return byte1
        else:
            print (mem_type+' not implemented')


    def run_main_cpu_loop(self):
        self.nmi = self.memory.read_short_from_memory(0xFFFA)
        self.irq = self.memory.read_short_from_memory(0xFFFE)
        self.reset = self.memory.read_short_from_memory(0xFFFC)
        print (self.reset)

        for i in range(0,20):
            self.readInstruction()
            
