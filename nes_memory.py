import struct

class Memory:
    program_sections = []
    chr_sections = []
    main_memory = bytearray(0x10000)

    def write_program_to_memory(self, program_number):
        self.write_bytes_to_memory(0x8000, Memory.program_sections[program_number])

    def write_bytes_to_memory(self, memory_location, bytes):
        byte_end_location = memory_location+len(bytes)
        Memory.main_memory[memory_location : byte_end_location] = bytes

    def read_bytes_from_memory(self, memory_location, number_to_read):
        return self.main_memory[memory_location : memory_location+number_to_read]

    def read_short_from_memory(self, memory_location):
        bytes = self.main_memory[memory_location : memory_location+2]
        return struct.unpack('H', bytes)[0]

    def print_memory(self):
        print (self.main_memory)