import struct

class Memory:
    program_sections = []
    chr_sections = []
    main_memory = bytearray(0x10000)
    ppu = None

    def __init__(self, ppu):
        self.ppu = ppu

    def write_program_to_memory(self, program_number):
        self.write_bytes_to_memory(0x8000, self.program_sections[program_number])

    def write_bytes_to_memory(self, memory_location, bytes):
        byte_end_location = memory_location+len(bytes)
        self.main_memory[memory_location : byte_end_location] = bytes

    def read_bytes_from_memory(self, memory_location, number_to_read):
        if (memory_location >= 0x2000): 
            self.getIOValue(memory_location)
        return self.main_memory[memory_location : memory_location+number_to_read]

    def read_short_from_memory(self, memory_location):
        bytes = self.main_memory[memory_location : memory_location+2]
        return struct.unpack('H', bytes)[0]

    def read_byte_from_memory(self, memory_location):
        if (memory_location > 0x4017):
            self.getByteFromROM(memory_location)
        elif (memory_location >= 0x2000): 
            return self.getIOValue(memory_location)
        bytes = self.main_memory[memory_location]
        return bytes

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