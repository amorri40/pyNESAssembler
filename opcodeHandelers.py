import struct
nes_output_file = None

output_bytes=[]

global_addr = 0

def writeToFile(bytes):
	global output_bytes
	output_bytes.append(bytes)
	#nes_output_file.write('bytes')

def writeHexFromString(hex_value):
	byte_value = struct.pack('B',int(hex_value,16))
	writeToFile(byte_value)

def handle_common_statement(original_string, location_of_match,tokens):
	
	#if len(tokens) <1: return
	try:
		op = tokens[0].replace('.','',1).lower()
		if op in directivesList:
			directivesList[op](original_string, location_of_match, tokens)
		else: 
			if op in reservedWordList:
				handle_reserved_word(op,original_string, location_of_match, tokens)
			else:
				print(op+"not in list")
	except Exception as e:
	    print (e)
	

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
	global_addr = tokens[1]

def handle_hex(original_string, location_of_match,tokens):
	#print ("write these hex values:")
	tokens_without_opcode = (tokens[1:])
	#print (tokens_without_opcode)
	for hex_value in tokens_without_opcode:
		byte_value = struct.pack('B',int(hex_value,16))
		writeToFile(byte_value)


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
        #"DW": handle_dw,
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
	print ('handle_lda')#{0xa9,IMM,0xa1,INDX,0xb1,INDY,0xb5,ZPX,0xbd,ABSX,0xb9,ABSY,0xa5,ZP,0xad,ABS,-1};
	print (tokens)
	writeHexFromString('A9')

def write_absolute_value(value_bytes):
	writeToFile(value_bytes[1])
	writeToFile(value_bytes[0])

def handle_reserved_word(op,original_string, location_of_match,tokens):
	print ('handle_reserved_word:'+op)
	print (tokens)
	if len(tokens) == 1:
		normal_op = reservedWordList[op]['NORM']
		writeHexFromString(normal_op)
	else:
		hex_value = False
		binary_value = False
		value_bytes = []
		for token in tokens[1:]:
			if (token == '$'): 
				hex_value = True
			elif (type(token).__name__ == 'bytes'):
					value_bytes.append(token)
			else:
				print (token)
		if hex_value and len(value_bytes) == 2:
			print (op+' absolute addressing mode')
			absolute_op = reservedWordList[op]['Absolute']
			print (absolute_op)
			writeHexFromString(absolute_op)
			write_absolute_value(value_bytes)
		else:
			print('not hex and 2:'+op)


reservedWordList = {
"brk" : {'NORM' : '0x00', 'Immediate' : '0x00', 'ZeroPage' : '0x00', 'Implied': '-1'},
"ora" : {'NORM' : '0x09', 'Immediate' : '0x01', 'INDX' : '0x11', 'INDY' : '0x15', 'ZeroPageX' : '0x1d', 'AbsoluteX' : '0x19', 'AbsoluteY' : '0x05', 'ZeroPage' : '0x0d', 'Absolute': '-1'},
"asl" : {'NORM' : '0x0a', 'ACC' : '0x16', 'ZeroPageX' : '0x1e', 'AbsoluteX' : '0x06', 'ZeroPage' : '0x0e', 'Absolute' : '0x0a', 'Implied': '-1'},
"php" : {'NORM' : '0x08', 'Implied': '-1'},
"bpl" : {'NORM' : '0x10', 'REL': '-1'},
"clc" : {'NORM' : '0x18', 'Implied': '-1'},
"jsr" : {'NORM' : '0x20', 'Absolute': '-1'},
"and" : {'NORM' : '0x29', 'Immediate' : '0x21', 'INDX' : '0x31', 'INDY' : '0x35', 'ZeroPageX' : '0x3d', 'AbsoluteX' : '0x39', 'AbsoluteY' : '0x25', 'ZeroPage' : '0x2d', 'Absolute': '-1'},
"bit" : {'NORM' : '0x24', 'ZeroPage' : '0x2c', 'Absolute': '-1'},
"rol" : {'NORM' : '0x2a', 'ACC' : '0x36', 'ZeroPageX' : '0x3e', 'AbsoluteX' : '0x26', 'ZeroPage' : '0x2e', 'Absolute' : '0x2a', 'Implied': '-1'},
"plp" : {'NORM' : '0x28', 'Implied': '-1'},
"bmi" : {'NORM' : '0x30', 'REL': '-1'},
"sec" : {'NORM' : '0x38', 'Implied': '-1'},
"rti" : {'NORM' : '0x40', 'Implied': '-1'},
"eor" : {'NORM' : '0x49', 'Immediate' : '0x41', 'INDX' : '0x51', 'INDY' : '0x55', 'ZeroPageX' : '0x5d', 'AbsoluteX' : '0x59', 'AbsoluteY' : '0x45', 'ZeroPage' : '0x4d', 'Absolute': '-1'},
"lsr" : {'NORM' : '0x4a', 'ACC' : '0x56', 'ZeroPageX' : '0x5e', 'AbsoluteX' : '0x46', 'ZeroPage' : '0x4e', 'Absolute' : '0x4a', 'Implied': '-1'},
"pha" : {'NORM' : '0x48', 'Implied': '-1'},
"jmp" : {'NORM' : '0x6c', 'IND' : '0x4c', 'Absolute': '-1'},
"bvc" : {'NORM' : '0x50', 'REL': '-1'},
"cli" : {'NORM' : '0x58', 'Implied': '-1'},
"rts" : {'NORM' : '0x60', 'Implied': '-1'},
"adc" : {'NORM' : '0x69', 'Immediate' : '0x61', 'INDX' : '0x71', 'INDY' : '0x75', 'ZeroPageX' : '0x7d', 'AbsoluteX' : '0x79', 'AbsoluteY' : '0x65', 'ZeroPage' : '0x6d', 'Absolute': '-1'},
"ror" : {'NORM' : '0x6a', 'ACC' : '0x76', 'ZeroPageX' : '0x7e', 'AbsoluteX' : '0x66', 'ZeroPage' : '0x6e', 'Absolute' : '0x6a', 'Implied': '-1'},
"pla" : {'NORM' : '0x68', 'Implied': '-1'},
"bvs" : {'NORM' : '0x70', 'REL': '-1'},
"sei" : {'NORM' : '0x78', 'Implied': '-1'},
"sta" : {'NORM' : '0x81', 'INDX' : '0x91', 'INDY' : '0x95', 'ZeroPageX' : '0x9d', 'AbsoluteX' : '0x99', 'AbsoluteY' : '0x85', 'ZeroPage' : '0x8d', 'Absolute': '-1'},
"sty" : {'NORM' : '0x94', 'ZeroPageX' : '0x84', 'ZeroPage' : '0x8c', 'Absolute': '-1'},
"stx" : {'NORM' : '0x96', 'ZeroPageY' : '0x86', 'ZeroPage' : '0x8e', 'Absolute': '0x8e'},
"dey" : {'NORM' : '0x88', 'Implied': '-1'},
"txa" : {'NORM' : '0x8a', 'Implied': '-1'},
"bcc" : {'NORM' : '0x90', 'REL': '-1'},
"tya" : {'NORM' : '0x98', 'Implied': '-1'},
"txs" : {'NORM' : '0x9a', 'Implied': '-1'},
"ldy" : {'NORM' : '0xa0', 'Immediate' : '0xb4', 'ZeroPageX' : '0xbc', 'AbsoluteX' : '0xa4', 'ZeroPage' : '0xac', 'Absolute': '-1'},
"lda" : {'NORM' : '0xa9', 'Immediate' : '0xa1', 'INDX' : '0xb1', 'INDY' : '0xb5', 'ZeroPageX' : '0xbd', 'AbsoluteX' : '0xb9', 'AbsoluteY' : '0xa5', 'ZeroPage' : '0xad', 'Absolute': '0xad'},
"ldx" : {'NORM' : '0xa2', 'Immediate' : '0xb6', 'ZeroPageY' : '0xbe', 'AbsoluteY' : '0xa6', 'ZeroPage' : '0xae', 'Absolute': '-1'},
"tay" : {'NORM' : '0xa8', 'Implied': '-1'},
"tax" : {'NORM' : '0xaa', 'Implied': '-1'},
"bcs" : {'NORM' : '0xb0', 'REL': '-1'},
"clv" : {'NORM' : '0xb8', 'Implied': '-1'},
"tsx" : {'NORM' : '0xba', 'Implied': '-1'},
"cpy" : {'NORM' : '0xc0', 'Immediate' : '0xc4', 'ZeroPage' : '0xcc', 'Absolute': '-1'},
"cmp" : {'NORM' : '0xc9', 'Immediate' : '0xc1', 'INDX' : '0xd1', 'INDY' : '0xd5', 'ZeroPageX' : '0xdd', 'AbsoluteX' : '0xd9', 'AbsoluteY' : '0xc5', 'ZeroPage' : '0xcd', 'Absolute': '-1'},
"dec" : {'NORM' : '0xd6', 'ZeroPageX' : '0xde', 'AbsoluteX' : '0xc6', 'ZeroPage' : '0xce', 'Absolute': '-1'},
"iny" : {'NORM' : '0xc8', 'Implied': '-1'},
"dex" : {'NORM' : '0xca', 'Implied': '-1'},
"bne" : {'NORM' : '0xd0', 'REL': '-1'},
"cld" : {'NORM' : '0xd8', 'Implied': '-1'},
"cpx" : {'NORM' : '0xe0', 'Immediate' : '0xe4', 'ZeroPage' : '0xec', 'Absolute': '-1'},
"sbc" : {'NORM' : '0xe9', 'Immediate' : '0xe1', 'INDX' : '0xf1', 'INDY' : '0xf5', 'ZeroPageX' : '0xfd', 'AbsoluteX' : '0xf9', 'AbsoluteY' : '0xe5', 'ZeroPage' : '0xed', 'Absolute': '-1'},
"inc" : {'NORM' : '0xf6', 'ZeroPageX' : '0xfe', 'AbsoluteX' : '0xe6', 'ZeroPage' : '0xee', 'Absolute': '-1'},
"inx" : {'NORM' : '0xe8', 'Implied': '-1'},
"nop" : {'NORM' : '0xea', 'Implied': '-1'},
"beq" : {'NORM' : '0xf0', 'REL': '-1'},
"sed" : {'NORM' : '0xf8', 'Implied': '-1'}
}
