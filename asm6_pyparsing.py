#!/usr/local/bin/python3

from pyparsing import *
import struct
import re

nes_output_file = None

output_bytes=[]

def writeToFile(bytes):
	global output_bytes
	output_bytes.append(bytes)
	#nes_output_file.write('bytes')

def handle_bin_num(original_string, location_of_match,tokens):
	return struct.pack('B', (int(tokens[0][1],2)))

def handle_hex_num(original_string, location_of_match,tokens):
	hex_values = re.findall('..',tokens[0][1])
	return_list = []
	for hex_value in hex_values:
		byte_value = struct.pack('B',int(hex_value,16))
		return_list.append(byte_value)
		print (byte_value)
	
	return return_list

def handle_dec_num(original_string, location_of_match,tokens):
	return struct.pack('B',(int(tokens[0])))

def handle_string(original_string, location_of_match,tokens):
	return (bytes(tokens[0].replace('"',''), 'UTF-8'))

def handle_db(original_string, location_of_match,tokens):
	print ("original_string: "+original_string)
	tokens_without_opcode = (tokens[1:])
	for token in tokens_without_opcode:
		if token == ',': continue
		writeToFile(token)
	print ("Define Byte")

################################################## 
# Forward Decl
##################################################
expression = Forward()

dbToken = Keyword(".db", caseless=True)
hexToken = Keyword(".hex", caseless=True)
originToken = Keyword(".org", caseless=True)

hex_num = Group('$' + Word(hexnums)).setParseAction(handle_hex_num) #hexnums + hexnums
binary_num = Group('%' + Word('01')).setParseAction(handle_bin_num)
dec_num = Word(nums).setParseAction(handle_dec_num)

labelStatement = Word(alphanums) + ":" #+ asm6

expression << (dec_num | quotedString.setParseAction(handle_string) | hex_num |binary_num | dec_num) + ZeroOrMore(','+expression)

################################################## 
#statements
################################################## 
dbStatement = (dbToken + expression).setParseAction(handle_db) #+ ', ' + hex_num + restOfLine
hexStatement = hexToken + OneOrMore(Word(hexnums, exact=2))
originStatement = originToken + expression

# define Oracle comment format, and ignore them
asm6Comment = ";" + restOfLine

asm6 = ZeroOrMore(dbStatement | hexStatement | originStatement | labelStatement) #+ restOfLine
asm6.ignore( asm6Comment )



reservedWordList = {
    #"BRK":handle_brk,
    #    "PHP":handle_php,
    #    "BPL":handle_bpl,
    #    "CLC":handle_clc,
    #    "JSR":handle_jsr,
    #    "PLP":handle_plp,
    #    "BMI":handle_bmi,
    #    "SEC":handle_sec,
    #    "RTI":handle_rti,
    #    "PHA":handle_pha,
    #    "BVC":handle_bvc,
    #    "CLI":handle_cli,
    #    "RTS":handle_rts,
    #    "PLA":handle_pla,
    #    "BVS":handle_bvs,
    #    "SEI":handle_sei,
    #    "DEY":handle_dey,
    #    "BCC":handle_bcc,
    #    "TYA":handle_tya,
    #    "LDY":handle_ldy,
    #    "TAY":handle_tay,
    #    "BCS":handle_bcs,
    #    "CLV":handle_clv,
    #    "CPY":handle_cpy,
    #    "INY":handle_iny,
    #    "BNE":handle_bne,
    #    "CLD":handle_cld,
    #    "CPX":handle_cpx,
    #    "INX":handle_inx,
    #    "BEQ":handle_beq,
    #    "SED":handle_sed,
    #    "ORA":handle_ora,
    #    "AND":handle_and,
    #    "EOR":handle_eor,
    #    "ADC":handle_adc,
    #    "STA":handle_sta,
    #    "LDA":handle_lda,
    #    "CMP":handle_cmp,
    #    "SBC":handle_sbc,
    #    "ASL":handle_asl,
    #    "ROL":handle_rol,
    #    "LSR":handle_lsr,
    #    "ROR":handle_ror,
    #    "TXA":handle_txa,
    #    "TXS":handle_txs,
    #    "LDX":handle_ldx,
    #    "TAX":handle_tax,
    #    "TSX":handle_tsx,
    #    "DEX":handle_dex,
    #    "NOP":handle_nop,
    #    "BIT":handle_bit,
    #    "JMP":handle_jmp,
    #    "STY":handle_sty,
    #    "STX":handle_stx,
    #    "DEC":handle_dec,
    #    "INC":handle_inc,
    }

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
        #"ORG": handle_org,
        #"BASE": handle_base,
        #"PAD": handle_pad,
        #"INCLUDE": handle_include,"INCSRC": handle_include,
        #"INCBIN": handle_incbin,"BIN": handle_incbin,
        #"HEX": handle_hex,
        #"WORD": handle_dw,
        #"DW": handle_dw,
        #"DCW": handle_dw,
        #"DC.W": handle_dw,
        #"BYTE": handle_db,
        "DB": handle_db,
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

def parseTokens(tokens):
	if len(tokens) <1: return
	op = tokens[0].replace('.','',1).upper()
	if op in directivesList:
		directivesList[op](tokens)
	else: print(op+"not in list")

if __name__ == "__main__":
	_file = open("mario_bros.asm", "r")
	nes_output_file = open('outfile.bin','wb')
	all_lines = _file.readlines()
	line_number = 0
	for line in all_lines:
		tokens = asm6.parseString( line )
		if len(tokens)<1:
			print ('didnt parse:'+line, end="")

		line_number += 1
		if line_number >40:
			break
	print (output_bytes)
	for byte in output_bytes:
		print (type(byte))
		nes_output_file.write(byte)
	nes_output_file.close()
	_file.close()