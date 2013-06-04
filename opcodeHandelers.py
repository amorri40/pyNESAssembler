import struct
nes_output_file = None

output_bytes=[]
label_list = {}

global_addr = 0
global_position_in_file = 0
global_previous_position_in_file = 0
global_line_number = 0
global_loc_at_start_of_current_opcode=0

def setLineNumber(lineno):
	global global_line_number
	global_line_number = lineno

def log(message):
	if global_line_number == -1: return
	if global_line_number < 2112: return
	#if global_line_number>9000 or global_line_number <126 or (global_position_in_file > 14100 and global_position_in_file < 14200):
	print ('Line:'+str(global_line_number)+', Byte: '+str(global_position_in_file)+' ', end="")
	print(message)

# Ths function calculates the current file position
# The current file position is the start of this instruction
# so it uses the previous position and subtracts 1
def getCurrentFilePosition():
	return global_previous_position_in_file #global_position_in_file

def writeToFile(bytes):
	global output_bytes, global_position_in_file
	global_position_in_file += (len(bytes))
	output_bytes.append(bytes)
	#nes_output_file.write('bytes')

def writeHexFromString(hex_value):
	byte_value = struct.pack('B',int(hex_value,16))
	writeToFile(byte_value)

def writeInt(int_value):
	byte_value = struct.pack('B',int_value)
	writeToFile(byte_value)

def handle_common_statement(original_string, location_of_match,tokens):
	global global_previous_position_in_file
	global_previous_position_in_file = global_position_in_file
	#if len(tokens) <1: return
	try:
		op = None
		if tokens[0] == '.': 
			op = tokens[1].lower()
		else:
			op = tokens[0].replace('.','',1).lower()
		if op in directivesList:
			directivesList[op](original_string, location_of_match, tokens)
		else: 
			if op in reservedWordList:
				handle_reserved_word(op,original_string, location_of_match, tokens)
			else:
				log("This op:"+op+" is not in list")
				log (tokens)
	except Exception as e:
	    log (e)
	

def handle_db(original_string, location_of_match,tokens):
	tokens_without_opcode = (tokens[1:])
	for token in tokens_without_opcode:
		if token == ',': continue
		if token == '$': continue
		writeToFile(token)

def handle_org(original_string, location_of_match,tokens):
	global global_addr
	print ("set the base address to:")
	print (tokens)
	
	hex_val = tokens[2]+tokens[3]
	global_addr = struct.unpack('>H',hex_val)[0]-16
	print (global_addr)

def handle_hex(original_string, location_of_match,tokens):
	#print ("write these hex values:")
	tokens_without_opcode = (tokens[1:])
	#print (tokens_without_opcode)
	for hex_value in tokens_without_opcode:
		byte_value = struct.pack('B',int(hex_value,16))
		writeToFile(byte_value)

def handle_dw(original_string, location_of_match,tokens):
	log('dw call')

directivesList = {
        #"":nothing,
        #"IF":_if,
        #"ELSEIF": handle_elseif,
        #"ELSE": handle__else,
        #"ENDIF": handle_endif,
        #"IFDEF": handle_ifdef,
        #"IFNDEF": handle_ifndef,
        #"=": handle_equal,
        #"EQU": handle_equ,
        "org": handle_org,
        #"BASE": handle_base,
        #"PAD": handle_pad,
        #"INCLUDE": handle_include,"INCSRC": handle_include,
        #"INCBIN": handle_incbin,"BIN": handle_incbin,
        "hex": handle_hex,
        #"WORD": handle_dw,
        "dw": handle_dw,
        #"DCW": handle_dw,
        #"DC.W": handle_dw,
        #"BYTE": handle_db,
        "db": handle_db,
        #"DCB": handle_db,"DC.B": handle_db,
        #"DSW": handle_dsw,"DS.W": handle_dsw,
        #"DSB": handle_dsb,"DS.B": handle_dsb,
        #"ALIGN": handle_align,
        #"MACRO": handle_macro,
        #"REPT": handle_rept,
        #"ENDM": handle_endm,
        #"ENDR": handle_endr,
        #"ENUM": handle__enum,
        #"ENDE": handle_ende,
        #"FILLVALUE": handle_fillval,
        #"DL": handle_dl,
        #"DH": handle_dh,
        #"ERROR": handle_make_error,
}


def handle_cld(original_string, location_of_match,tokens):
	writeHexFromString('d8')

def handle_sei(original_string, location_of_match,tokens):
	writeHexFromString('78') #sei[]={0x78,IMP,-1};

def handle_lda(original_string, location_of_match,tokens):
	log('handle_lda')#{0xa9,IMM,0xa1,INDX,0xb1,INDY,0xb5,ZPX,0xbd,ABSX,0xb9,ABSY,0xa5,ZP,0xad,ABS,-1};
	log(tokens)
	writeHexFromString('A9')

def write_absolute_value(value_bytes):
	writeToFile(value_bytes[1])
	writeToFile(value_bytes[0])

def write_immediate_value(value_bytes):
	writeToFile(value_bytes[0])

def write_zero_page_value(value_bytes):
	writeToFile(value_bytes[0])

def write_indirect_absolute(op, value_bytes):
	#This should only ever be called by jump
	if reservedWordList[op]["Type"] == "Jump":
		writeOp(op,'IND')
		write_absolute_value(value_bytes)
	else:
		log('ERROR: indirect absolute value thats not a jump:'+op)

#
# Write label is used when an instruction takes a label as a parameter
# This function tries to fixugre out if the opcode should write relative or absolute value
def write_label(op, label, x_index, y_index):
	global global_position_in_file
	label = label[0]
	if reservedWordList[op]["Type"] == "Jump":
		log('jump instruction')
		global_position_in_file +=2 #jump instructions use absolute addresses (2 bytes)
		label = '2'+label
		writeOp(op,'Absolute')
	elif reservedWordList[op]["Type"] == "Branch":
		writeOp(op,'REL')
		global_position_in_file +=1 #we need to increment position in file as the correct location byte will go here
	else:
		log ('Unknown label length for opcode with Type:'+reservedWordList[op]["Type"])
		global_position_in_file +=2
		label = '2'+label
		if x_index:
			writeOp(op,'AbsoluteX')
		elif y_index:
			writeOp(op,'AbsoluteY')
		else:
			writeOp(op,'Absolute')
	output_bytes.append(label) #we fix labels at a later stage just write it to outputbytes as string

def writeOp(op, _type):
	if _type in reservedWordList[op]:
		opcode = reservedWordList[op][_type]
	elif _type == "ZeroPageY":
		opcode = reservedWordList[op]['AbsoluteY']
	elif _type == "ZeroPageX":
		opcode = reservedWordList[op]['AbsoluteX']
	else: log('Error '+_type+' not in '+op+' '+str(reservedWordList[op]))
	writeHexFromString(opcode)

def handle_reserved_word(op,original_string, location_of_match,tokens):
	#log('handle_reserved_word:'+op)
	#log(tokens)
	if len(tokens) == 1:
		normal_op = reservedWordList[op]['Implied']
		writeHexFromString(normal_op)
	else:
		hex_value = False
		binary_value = False
		immediate_value = False
		indirect_value = False
		absolute_value = False
		zero_page = False
		x_index = False
		y_index = False
		label_value = False
		value_bytes = []
		#first lets get what the parameters to the opcode are
		# and what type they are (hex, binary, immediate)
		for token in tokens[1:]:
			if (token == '$'): 
				hex_value = True
			elif (token == '%'):
				binary_value = True
			elif (token == '(' or token == ')'):
				indirect_value = True
			elif (token == '#'):
				immediate_value = True
			elif (token.lower() == 'x'):
				x_index = True
			elif (token.lower() == 'y'):
				y_index = True
			elif (token == ','):
				continue
			elif (type(token).__name__ == 'bytes'):
					value_bytes.append(token)
			elif (type(token).__name__ == 'str'):
					label_value = True
					value_bytes.append(token)
			else:
				log('Unknown type of token')
				log(token)
		#absolute or zero page?
		if len(value_bytes) == 1 and not immediate_value and not label_value:
			zero_page = True
		elif len(value_bytes) == 2 and not immediate_value and not label_value:
			absolute_value = True
		writeInstruction(op, value_bytes, immediate_value, hex_value, binary_value, indirect_value, x_index, y_index, zero_page, absolute_value, label_value)

def writeInstruction(op, value_bytes, immediate_value, hex_value, binary_value, indirect_value, x_index, y_index, zero_page, absolute_value, label_value):
		############################
		# now lets use the data
		############################
		num_of_value_bytes = len(value_bytes)
		#log('num_of_value_bytes for '+op+": "+str(num_of_value_bytes))
		#log(value_bytes)
		
			
		if immediate_value:
			#log(op+' has immediate value parameter')
			writeOp(op,'Immediate')
			write_immediate_value(value_bytes)
		elif binary_value:
			log("binary value"+op)
		elif indirect_value and x_index:
			writeOp(op,'INDX')
			write_immediate_value(value_bytes)
		elif indirect_value and y_index:
			writeOp(op,'INDY')
			write_immediate_value(value_bytes)
		elif indirect_value:
			write_indirect_absolute(op, value_bytes)
		elif x_index and absolute_value:
			writeOp(op,'AbsoluteX')
			write_absolute_value(value_bytes)
		elif y_index and absolute_value:
			writeOp(op,'AbsoluteY')
			write_absolute_value(value_bytes)
		elif x_index and zero_page:
			writeOp(op,'ZeroPageX')
			write_zero_page_value(value_bytes)
		elif y_index and zero_page:
			writeOp(op,'ZeroPageY')
			write_zero_page_value(value_bytes)
		elif hex_value and zero_page:
			#log('hex value with 1 byte, zp?')
			writeOp(op,'ZeroPage')
			write_immediate_value(value_bytes)
		elif hex_value:
			#log(op+' absolute addressing mode')
			writeOp(op,'Absolute')
			write_absolute_value(value_bytes)
		elif label_value:
			#must be a label
			write_label(op, value_bytes, x_index, y_index)
		else:
			log ('ERROR Unknown type of address: '+op+' '+str(value_bytes))
		log("op:"+op+' '+str(output_bytes[-3:]))


reservedWordList = {

# Storage
"ldy" : {'Immediate' : '0xa0', 'ZeroPageX' : '0xb4', 'AbsoluteX' : '0xbc', 'ZeroPage' : '0xa4', 'Absolute': '0xac', 'Type' : 'Storage' },
"lda" : {'Immediate' : '0xa9', 'INDX' : '0xa1', 'INDY' : '0xb1', 'ZeroPageX' : '0xb5', 'AbsoluteX' : '0xbd', 'AbsoluteY' : '0xb9', 'ZeroPage' : '0xa5', 'Absolute': '0xad', 'Type' : 'Storage'},
"ldx" : {'Immediate' : '0xa2', 'ZeroPageY' : '0xb6', 'AbsoluteY' : '0xbe', 'ZeroPage' : '0xa6', 'Absolute': '0xae', 'Type' : 'Storage'},
"sta" : {'INDX' : '0x81', 'INDY' : '0x91', 'ZeroPageX' : '0x95', 'AbsoluteX' : '0x9d', 'AbsoluteY' : '0x99', 'ZeroPage' : '0x85', 'Absolute': '0x8d', 'Type' : 'Storage' },
"sty" : {'ZeroPageX' : '0x94', 'ZeroPage' : '0x84', 'Absolute': '0x8c',  'Type' : 'Storage'},
"stx" : {'ZeroPageY' : '0x96', 'ZeroPage' : '0x86', 'Absolute': '0x8e', 'Type' : 'Storage'},
"txs" : {'Implied': '0x9a', 'Type' : 'Storage' },
"txa" : {'Implied': '0x8a',  'Type' : 'Storage'},
"tya" : {'Implied': '0x98', 'Type' : 'Storage'},
"tay" : {'Implied': '0xa8', 'Type' : 'Storage'},
"tax" : {'Implied': '0xaa', 'Type' : 'Storage'},
"tsx" : {'Implied': '0xba', 'Type' : 'Storage'},

# Math
"sbc" : {'Immediate' :'0xe9',  'INDX' :'0xe1', 'INDY' : '0xf1',  'ZeroPageX' : '0xf5', 'AbsoluteX' : '0xfd', 'AbsoluteY' : '0xf9', 'ZeroPage' : '0xe5', 'Absolute': '0xed', 'Type' : 'Math' },
"dex" : { 'Implied': '0xca', 'Type' : 'Math' },
"inx" : {'Implied': '0xe8',  'Type' : 'Math'},
"iny" : {'Implied': '0xc8',  'Type' : 'Math'},
"dey" : {'Implied': '0x88',  'Type' : 'Math'},
"dec" : {'ZeroPageX' : '0xd6', 'AbsoluteX' : '0xde', 'ZeroPage' : '0xc6', 'Absolute': '0xce',  'Type' : 'Math'},
"inc" : {'ZeroPageX' : '0xf6', 'AbsoluteX' : '0xfe', 'ZeroPage' : '0xe6', 'Absolute': '0xee', 'Type' : 'Math'},
"adc" : {'Immediate' : '0x69', 'INDX' : '0x61', 'INDY' : '0x71', 'ZeroPageX' : '0x75', 'AbsoluteX' : '0x7d', 'AbsoluteY' : '0x79', 'ZeroPage' : '0x65', 'Absolute': '0x6d',  'Type' : 'Math'},


# Bitwise
"and" : {'Immediate' : '0x29', 'INDX' : '0x21', 'INDY' : '0x31', 'ZeroPageX' : '0x35', 'AbsoluteX' : '0x3d', 'AbsoluteY' : '0x39', 'ZeroPage' : '0x25',  'Absolute': '0x2d', 'Type' : 'Bitwise' },
"bit" : {'ZeroPage' : '0x24', 'Absolute': '0x2c',  'Type' : 'Bitwise'},
"ora" : {'Immediate' : '0x09', 'INDX' : '0x01', 'INDY' : '0x11', 'ZeroPageX' : '0x15', 'AbsoluteX' : '0x1d', 'AbsoluteY' : '0x19', 'ZeroPage' : '0x05', 'Absolute': '0x0d',  'Type' : 'Bitwise' },
"asl" : {'ACC' : '0x0a', 'ZeroPageX' : '0x16', 'AbsoluteX' : '0x1e', 'ZeroPage' : '0x06', 'Absolute' : '0x0e', 'Implied': '0x0a',  'Type' : 'Bitwise' },
"rol" : {'ACC' : '0x2a', 'ZeroPageX' : '0x36', 'AbsoluteX' : '0x3e', 'ZeroPage' : '0x26', 'Absolute' : '0x2e', 'Implied': '0x2a',  'Type' : 'Bitwise'},
"ror" : {'ACC' : '0x6a', 'ZeroPageX' : '0x76', 'AbsoluteX' : '0x7e', 'ZeroPage' : '0x66', 'Absolute' : '0x6e', 'Implied':  '0x6a',  'Type' : 'Bitwise'},
"eor" : {'Immediate' : '0x49', 'INDX' : '0x41', 'INDY' : '0x51', 'ZeroPageX' : '0x55', 'AbsoluteX' : '0x5d', 'AbsoluteY' : '0x59', 'ZeroPage' : '0x45', 'Absolute': '0x4d',  'Type' : 'Bitwise'},
"lsr" : {'ACC' : '0x4a', 'ZeroPageX' : '0x56', 'AbsoluteX' : '0x5e', 'ZeroPage' : '0x46', 'Absolute' : '0x4e', 'Implied': '0x4a',  'Type' : 'Bitwise'},


# Branch
"beq" : {'REL': '0xf0',  'Type' : 'Branch'},
"bne" : {'REL': '0xd0',  'Type' : 'Branch'},
"bcs" : {'REL': '0xb0',  'Type' : 'Branch'},
"bcc" : {'REL': '0x90',  'Type' : 'Branch'},
"bvs" : {'REL': '0x70',  'Type' : 'Branch'},
"bvc" : {'REL': '0x50',  'Type' : 'Branch'},
"bmi" : {'REL': '0x30',  'Type' : 'Branch'},
"bpl" : {'REL': '0x10',  'Type' : 'Branch'},

#Jump
"jmp" : {'IND' : '0x6c', 'Absolute': '0x4c', 'Type' : 'Jump'},
"jsr" : {'Absolute': '0x20', 'Type' : 'Jump'},
"rti" : {'Implied': '0x40',  'Type' : 'Jump'},
"rts" : {'Implied': '0x60',  'Type' : 'Jump'},

#Registers
"cpx" : {'Immediate' : '0xe0', 'ZeroPage' : '0xe4', 'Absolute': '0xec',  'Type' : 'Register'},
"cpy" : {'Immediate' : '0xc0', 'ZeroPage' : '0xc4', 'Absolute': '0xcc', 'Type' : 'Register'},
"cmp" : {'Immediate' : '0xc9', 'INDX' : '0xc1', 'INDY' : '0xd1', 'ZeroPageX' : '0xd5', 'AbsoluteX' : '0xdd', 'AbsoluteY' : '0xd9', 'ZeroPage' : '0xc5', 'Absolute': '0xcd', 'Type' : 'Register'},
"cli" : {'Implied': '0x58',  'Type' : 'Register'},
"clc" : {'Implied': '0x18',  'Type' : 'Register'},
"clv" : {'Implied': '0xb8',  'Type' : 'Register'},
"cld" : {'Implied': '0xd8',  'Type' : 'Register'},
"sed" : {'Implied': '0xf8',  'Type' : 'Register'},
"sei" : {'Implied': '0x78',  'Type' : 'Register'},
"sec" : {'Implied': '0x38',  'Type' : 'Register'},

#Stack
"pla" : {'Implied': '0x68',  'Type' : 'Stack'},
"pha" : {'Implied': '0x48',  'Type' : 'Stack'},
"plp" : {'Implied': '0x28',  'Type' : 'Stack'},
"php" : {'Implied': '0x08',  'Type' : 'Stack'},

#System
"brk" : {'Immediate' : '0x00', 'ZeroPage' : '0x00',  'Implied': '0x00', 'Type' : 'System'},
"nop" : {'Implied':'0xea', 'Type' : 'System'},
}
