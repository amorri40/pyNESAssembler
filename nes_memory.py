import struct
from nes_byte_utils import *

class Memory:
    program_sections = []
    chr_sections = []
    main_memory = bytearray(0x10000)
    ppu = None
    cpu = None

    def __init__(self, ppu, cpu):
        self.ppu = ppu
        self.cpu = cpu
        self.reset_memory()

    #reset memory to starting state
    def reset_memory(self):
        #initial values are 0xFF for the first 0x2000 bytes
        for i in range(0,0x2000):
            self.main_memory[i] = 0xFF
        
        for p in range(0,3):
            i = p*0x800
            self.main_memory[i+0x008] = 0xF7
            self.main_memory[i+0x009] = 0xEF
            self.main_memory[i+0x00A] = 0xDF
            self.main_memory[i+0x00F] = 0xBF
        


    def write_program_to_memory_low(self, program_number):
        self.write_bytes_to_memory(0x8000, self.program_sections[program_number])

    def write_program_to_memory_high(self, program_number):
        self.write_bytes_to_memory(0xc000, self.program_sections[program_number])

    def write_bytes_to_memory(self, memory_location, bytes):
        self.handle_mem_breakpoints(memory_location, 'writebytes')
        byte_end_location = memory_location+len(bytes)
        self.main_memory[memory_location : byte_end_location] = bytes

    def write_int_to_memory(self, memory_location, value):
        self.handle_mem_breakpoints(memory_location, 'writeint:'+str(value))
        if (type(value).__name__ == 'bytes'): value = byte_to_signed_int(value)
        self.main_memory[memory_location] = value
        
    def write_short_to_memory(self, memory_location, value):
        self.handle_mem_breakpoints(memory_location, 'writeshort')
        self.main_memory[memory_location : memory_location+2] = short_to_bytes(value)

    def read_bytes_from_memory(self, memory_location, number_to_read):
        self.handle_mem_breakpoints(memory_location, 'readbytes')
        if (memory_location >= 0x2000): 
            self.getIOValue(memory_location)
        return self.main_memory[memory_location : memory_location+number_to_read]

    def read_short_from_memory(self, memory_location):
        self.handle_mem_breakpoints(memory_location, 'readshort')
        bytes = self.main_memory[memory_location : memory_location+2]
        return struct.unpack('H', bytes)[0]

    def read_byte_from_memory(self, memory_location):
        self.handle_mem_breakpoints(memory_location, 'readbyte')
        if (type(memory_location).__name__ == 'str'): return struct.pack('b', int(memory_location[1:], 16))
        if (memory_location > 0x4017):
            self.getByteFromROM(memory_location)
        elif (memory_location >= 0x2000): 
            return self.getIOValue(memory_location)
        bytes = self.main_memory[memory_location]
        return bytes

    def handle_mem_breakpoints(self, memory_location, intent_string):
        return
        if (memory_location == 20):
            self.print_breakpoint_info(memory_location, intent_string)

        pc = int(self.cpu.get_program_counter(), 16)
        if (pc >= 0xc01d and pc <= 0xc020 and self.cpu.y_register == 20):
            self.print_breakpoint_info(memory_location, intent_string)

    def print_breakpoint_info(self, memory_location, intent_string):
        print ('memLocation:'+str(memory_location)+' '+intent_string, end="")
        print (' :: memory breakpoint At pc: '+ self.cpu.get_program_counter_as_str(), end="")
        print (' y:'+ str(self.cpu.y_register) + ' x:'+ str(self.cpu.x_register) + ' acc:'+ str(self.cpu.accumulator))

    def print_memory(self):
        print (self.main_memory)

    def getByteFromROM(self, memory_location):
        #print ('getByteFromROM:'+str(memory_location))
        return

    def getIOValue(self, memory_location):
        if (memory_location == 0x2002):
            status = self.ppu.getStatusRegister()
            #print ('PPU Status Register: '+ str(status))
        else:
            print ('get unknown IO from location:'+str(memory_location))
        return status