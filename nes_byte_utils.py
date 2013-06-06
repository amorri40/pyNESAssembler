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