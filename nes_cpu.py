from emulate import *
import struct
from opcodeHandelers import *
from nes_ppu import NesPPU
from nes_byte_utils import *

class NesCPU():
    accumulator = 0
    x_register = 0
    y_register = 0
    program_counter = 0x8000
    stack_pointer = 0xFF
    
    renderer = None
    nes_file = None
    instructions = None
    memory = None
    ppu = None

    opcode_table = {}
    loggingEnabled = False

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
        self.ppu = NesPPU()
        self.memory = Memory(self.ppu)
        

    

    def readProgramByte(self):
        #print ('pc='+str(self.program_counter))
        instruction_location = self.program_counter
        self.program_counter += 1
        byte_value = self.memory.read_byte_from_memory(instruction_location)
        
        return byte_value

    def readProgramShort(self):
        instruction_location = self.program_counter
        self.program_counter += 2
        short_value = self.memory.read_short_from_memory(instruction_location)
        
        return short_value

    def createOpCodeTable(self):
        for opcode in reservedWordList:
            opcode_mem_list = reservedWordList[opcode]
            for mem_type in opcode_mem_list:
                
                hex_value = opcode_mem_list[mem_type]
                if (hex_value.find('0')==0):
                    hex_value = int(hex_value,16)
                    self.opcode_table[hex_value] = {'opcode':opcode, 'mem_type':mem_type}

    def logInstruction(self, opcode_name, mem_type, address, cycles):
        if (self.loggingEnabled):
            
            print (opcode_name+'_'+mem_type+' '+str(address)+' ; cycles:'+str(cycles),end="")
            if (self.program_counter < 0xC000):
                print(' pc:'+str(int_to_hex(self.program_counter+0x4000)))
            else:
                print(' pc:'+str(int_to_hex(self.program_counter)))

    def readInstruction(self):
        opcode = (self.readProgramByte())
        if (opcode in self.opcode_table):
            opcode_name = self.opcode_table[opcode]['opcode']
            
            mem_type = self.opcode_table[opcode]['mem_type']
            address = self.readInstructionParameters(opcode_name, mem_type)
            cycles = self.instructions.execute_instruction(opcode_name, address)
            self.ppu.execute_cycles_for_instruction(cycles)
            self.logInstruction(opcode_name, mem_type, address, cycles)
        else:
            print ('Error opcode not in table: '+str(opcode)+' at loc:'+str(self.program_counter))

    # 
    # reads instruction parameters and returns the address that this opcode will operate on
    # 
    def readInstructionParameters(self, opcode_name, mem_type):
        if mem_type == 'Implied':
            return -1 #implied doesn't need an address
        elif mem_type == 'Absolute':
            mem_loc = self.readProgramShort()
            return mem_loc
        elif mem_type == 'AbsoluteX':
            mem_loc = self.readProgramShort()
            return mem_loc+x_register
        elif mem_type == 'AbsoluteY':
            mem_loc = self.readProgramShort()
            return mem_loc+y_register
        elif mem_type == 'REL':
            byte1 = self.readProgramByte()
            byte = (struct.pack('B',byte1))
            byte = struct.unpack('b',byte)[0]
            full_addr = self.program_counter + byte
            return full_addr
        elif mem_type == 'Immediate':
            byte1 = self.readProgramByte()
            return self.program_counter-1 #immediate value is stored after the current opcode
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
            #Post-indexed Indirect mode.
            #get 16 bit address from argument then add Y
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

        for i in range(0,30000):
            if self.ppu.end_of_current_frame:
                self.ppu.startFrame()
                self.ppu.end_of_current_frame = False

            self.readInstruction()
            
