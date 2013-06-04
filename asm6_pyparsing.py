#!/usr/local/bin/python3

from pyparsing import *
import struct
import re

from opcodeHandelers import *
import opcodeHandelers

################################################## 
# Handle expressions
################################################## 
def handle_bin_num(original_string, location_of_match,tokens):
	return struct.pack('B', (int(tokens[0][1],2)))

def handle_hex_num(original_string, location_of_match,tokens):
	try:
		hex_values = re.findall('..',tokens[0][1])
		#print (hex_values)
		return_list = ['$']
		#print ('handle_hex')
		hex_temp=''
		for hex_value in hex_values:
			hex_temp+=hex_value
		
			#chr_value = chr(hex_value)
			#print (hex_value)
			#print (chr_value)
		
			byte_value = struct.pack('B',int(hex_value,16))
			#print (byte_value)
			return_list.append(byte_value)
		#print (hex_temp)
		#print (bytearray.fromhex(hex_temp))
		#print (return_list)
		return return_list
	except Exception as e:
		print (e)

def handle_dec_num(original_string, location_of_match,tokens):
	return struct.pack('B',(int(tokens[0])))

def handle_string(original_string, location_of_match,tokens):
	return (bytes(tokens[0].replace('"',''), 'UTF-8'))

# Handle label adds labels to the labellist
# It is called when a label definitoon is found
def handle_label(original_string, location_of_match,tokens):
	#this is called after the bytes for this instruction have been written
	location = getCurrentFilePosition() #opcodeHandelers.global_position_in_file + 1
	label_list[tokens[0]] = location 
	#log ('location of '+str(tokens[0])+' is '+ str(location))
	#log(output_bytes)
	return tokens[2:]

def handle_immediate_num(original_string, location_of_match,tokens):
	return tokens
	

################################################## 
# Forward Decl
##################################################
expression = Forward()
asm6 = Forward()
commonStatements = Forward()

dbToken = Keyword(".db", caseless=True)
hexToken = Keyword(".hex", caseless=True)
originToken = Keyword(".org", caseless=True)
labelToken = Word(srange("[a-zA-Z0-9_]"))

dotToken = '.' + Word(alphas, exact=2)
anyOpcodeToken = Word(alphas, exact=3)

################################################## 
# Expressions
################################################## 
hex_num = Group('$' + Word(hexnums)).setParseAction(handle_hex_num) #hexnums + hexnums
binary_num = Group('%' + Word('01')).setParseAction(handle_bin_num)
dec_num = Word(nums).setParseAction(handle_dec_num)

immediate_num = ('#' + (hex_num | binary_num)).setParseAction(handle_immediate_num)

labelStatement = (Word(srange("[a-zA-Z0-9_]")) + ":" + Optional(commonStatements)).setParseAction(handle_label)

expression << Optional('(') + (immediate_num | dec_num | quotedString.setParseAction(handle_string) | hex_num |binary_num | dec_num | labelToken) + Optional(')') + ZeroOrMore(','+expression) + Optional(')')

################################################## 
# Statements
################################################## 
anyStatement = (dotToken | anyOpcodeToken) + Optional(expression)
dbStatement = (dbToken + expression) #+ ', ' + hex_num + restOfLine
hexStatement = hexToken + OneOrMore(Word(hexnums, exact=2))
originStatement = originToken + expression

commonStatements << (dbStatement | hexStatement | originStatement | anyStatement).setParseAction(handle_common_statement)

# Ignore Comments
asm6Comment = ";" + restOfLine

################################################## 
# Main Statement
################################################## 
asm6 << ZeroOrMore(labelStatement | commonStatements) #+ restOfLine
asm6.ignore( asm6Comment )

def get_relative_location_as_byte(label, jump_loc, current_loc):
	#we want to get a relative location
	#from the last byte of the current opcode +1 (so it doesn't include it)
	# to the new byte -1
	#current_loc+=2
	#jump_loc-=1
	relative_loc = jump_loc - current_loc

	#when subtracting we want to go to the start of the instruction
	# when adding we want to start adding from the end of the current instruction

	#if (relative_loc<0): relative_loc-=1 #we need to ignore the byte already written for this instruction
	relative_loc-=1
	if relative_loc>127 or relative_loc<-128:
		print(label+': relative_loc:'+str(relative_loc)+' because:'+str(jump_loc)+' - '+str(current_loc))
		byte_value = struct.pack('h',relative_loc)
	else:
		byte_value = struct.pack('b',relative_loc)
	return byte_value

def write_absolute_jump_label(label):
	log('absolute jump')
	label = label[1:]
	try:
		location_of_label = (label_list[label])
		location_of_label += opcodeHandelers.global_addr
		byte_value = struct.pack('<H',location_of_label)
		opcodeHandelers.nes_output_file.write(byte_value) #todo fix this to work for 2 bytes
		#opcodeHandelers.nes_output_file.write(byte_value)

	except KeyError:
		byte_value = struct.pack('b',0)
		opcodeHandelers.nes_output_file.write(byte_value)
		opcodeHandelers.nes_output_file.write(byte_value)

if __name__ == "__main__":
	_file = open("mario_bros.asm", "r")
	opcodeHandelers.nes_output_file = open('outfile.bin','wb')
	all_lines = _file.readlines()
	line_number = 1
	for line in all_lines:
		setLineNumber(line_number)
		tokens = asm6.parseString( line )
		if len(tokens)<1:
			line = line.lstrip()
			if line.find(';') != 0 and len(line)>0:
				print ('didnt parse:'+line, end="")

		line_number += 1
		if line_number >65000:
			break
	#
	# Now done parsing lets fix labels and write to file
	#
	setLineNumber(-1) #indicate we are done to the log function
	current_location=0
	for byte in output_bytes:
		
		if type(byte).__name__ == 'str':
			label=byte
			if label.find('2') == 0:
				write_absolute_jump_label(label)
				current_location += 2 #not a relative location
			else: #relative location
				try:
					location_of_label = (label_list[label])
				except KeyError:
					location_of_label = current_location
					log ("haven't found the label yet: "+label)
				relative_location = get_relative_location_as_byte(label,location_of_label, current_location)
				opcodeHandelers.nes_output_file.write(relative_location)
				current_location += 1 #labels rel offsets take up 1 byte
			continue
		opcodeHandelers.nes_output_file.write(byte)
		current_location += len(byte)
	opcodeHandelers.nes_output_file.close()
	_file.close()