#!/usr/local/bin/python3

from pyparsing import *
import struct
import re

from opcodeHandelers import *
import opcodeHandelers

label_list = []

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
		print (return_list)
		return return_list
	except Exception as e:
		print (e)

def handle_dec_num(original_string, location_of_match,tokens):
	return struct.pack('B',(int(tokens[0])))

def handle_string(original_string, location_of_match,tokens):
	return (bytes(tokens[0].replace('"',''), 'UTF-8'))

def handle_label(original_string, location_of_match,tokens):
	label_list.append(tokens[0])
	return tokens[2:]

	

################################################## 
# Forward Decl
##################################################
expression = Forward()
asm6 = Forward()

dbToken = Keyword(".db", caseless=True)
hexToken = Keyword(".hex", caseless=True)
originToken = Keyword(".org", caseless=True)

dotToken = '.' + Word(alphas, exact=2)
anyOpcodeToken = Word(alphas, exact=3)

# Expressions
hex_num = Group('$' + Word(hexnums)).setParseAction(handle_hex_num) #hexnums + hexnums
binary_num = Group('%' + Word('01')).setParseAction(handle_bin_num)
dec_num = Word(nums).setParseAction(handle_dec_num)

labelStatement = (Word(srange("[a-zA-Z0-9_]")) + ":" + Optional(asm6)).setParseAction(handle_label)

expression << (dec_num | quotedString.setParseAction(handle_string) | hex_num |binary_num | dec_num) + ZeroOrMore(','+expression)

################################################## 
# Statements
################################################## 
anyStatement = (dotToken | anyOpcodeToken) + Optional(expression)
dbStatement = (dbToken + expression) #+ ', ' + hex_num + restOfLine
hexStatement = hexToken + OneOrMore(Word(hexnums, exact=2))
originStatement = originToken + expression

commonStatements = (dbStatement | hexStatement | originStatement | anyStatement).setParseAction(handle_common_statement)

# Ignore Comments
asm6Comment = ";" + restOfLine

################################################## 
# Main Statement
################################################## 
asm6 << ZeroOrMore(labelStatement | commonStatements) #+ restOfLine
asm6.ignore( asm6Comment )


if __name__ == "__main__":
	_file = open("mario_bros.asm", "r")
	opcodeHandelers.nes_output_file = open('outfile.bin','wb')
	all_lines = _file.readlines()
	line_number = 0
	for line in all_lines:
		tokens = asm6.parseString( line )
		if len(tokens)<1:
			line = line.lstrip()
			if line.find(';') != 0 and len(line)>0:
				print ('didnt parse:'+line, end="")

		line_number += 1
		if line_number >40:
			break
	print (output_bytes)
	for byte in output_bytes:
		#print (type(byte))
		opcodeHandelers.nes_output_file.write(byte)
	opcodeHandelers.nes_output_file.close()
	_file.close()