import struct

def byte_to_signed_int(byte):
    if (type(byte).__name__ == 'int'): return byte
    value = struct.unpack('b', byte)[0]
    return value

def byte_to_unsigned_int(byte):
    if (type(byte).__name__ == 'int'): return byte
    value = struct.unpack('B', byte)[0]
    return value

def int_to_signed_byte(value):
    value = struct.pack('b',value)
    return value

def short_to_bytes(value):
    if value >0:
        value = struct.pack('H',value)
    else:
        value = struct.pack('h',value)
    return value

# negative byte wrap changes signed negative numbers to unsigned value
# e.g -1 becomes 255
def negative_byte_wrap(value):
    return value & 0xFF

# gets the sign of an unsigned byte
def get_sign_of_byte(byte):
    return byte >> 7 & 1

def int_to_hex(value):
    return hex(value)

def int_to_str(value):
    return str(int_to_hex(value))

def get_program_counter_as_str(pc):
    if (pc < 0xC000): 
        return str(int_to_hex(pc+0x4000))
    else:
        return str(int_to_hex(pc))