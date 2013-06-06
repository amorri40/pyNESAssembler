import nes_memory
import struct
from nes_byte_utils import *

class Instructions:

	cpu = None
	memory = None

	def __init__(self, cpu):
		self.cpu = cpu
		self.memory = self.cpu.memory

	def execute_cld(self, addr):
		self.cpu.decimal_flag = 0

	def execute_sei(self, addr):
		self.cpu.interrupt_flag = 1

	def execute_lda(self, addr):
		value = self.cpu.accumulator = self.cpu.memory.read_byte_from_memory(addr)
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	def execute_ldx(self, addr):
		value = self.cpu.x_register = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	def execute_ldy(self, addr):
		value = self.cpu.y_register = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	def execute_sta(self, addr):
		self.cpu.memory.write_int_to_memory(addr, self.cpu.accumulator)
		#print('sta:'+str(addr))

	def execute_stx(self, addr):
		self.cpu.memory.write_int_to_memory(addr, self.cpu.x_register)

	def execute_sty(self, addr):
		self.cpu.memory.write_int_to_memory(addr, self.cpu.y_register)

	def execute_dex(self, addr):
		self.cpu.x_register -= 1
		value = self.cpu.x_register
		self.cpu.x_register = negative_byte_wrap(self.cpu.x_register)
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	def execute_dey(self, addr):
		#print ('execute_dey:'+str(self.cpu.y_register))
		self.cpu.y_register -= 1
		
		value = self.cpu.y_register
		self.cpu.y_register = negative_byte_wrap(self.cpu.y_register)
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	def execute_dec(self, addr):
		value = byte_to_unsigned_int(self.cpu.memory.read_byte_from_memory(addr))
		value -= 1
		self.cpu.memory.write_int_to_memory(addr, negative_byte_wrap(value))
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)



	def execute_txs(self, addr):
		self.cpu.stack = self.cpu.x_register

	#Transfer X to accumulator
	def execute_txa(self, addr):
		value = self.cpu.accumulator = self.cpu.x_register
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)


	# BPL: Branch on PLus (negative clear)
	def execute_bpl(self, addr):
		if (self.cpu.negative_flag == 0):
			self.cpu.program_counter = addr

	# Branch on not zero
	def execute_bne(self, addr):
		
		if (self.cpu.zero_flag == 0):
			self.cpu.program_counter = addr
			#print ('bne set pc to:'+str(addr))
	
	def execute_jmp(self, addr):
		self.cpu.program_counter = addr

	def execute_jsr(self, addr):
		self.push_to_stack(self.cpu.program_counter)
		self.cpu.program_counter = addr

	def execute_instruction(self, opcode_name, addr):
		#print ('execute: '+opcode_name)
		#try:
		self.function_table[opcode_name](self, addr)
		#except Exception as e:
		#	print (e)
		#	print ('execute: '+opcode_name) 
		return 2

	def push_to_stack(self, val):
		return

	def setNegativeFlagForValue(self, value):
		self.cpu.negative_flag = self.valueIsNegative(value)

	def setZeroFlagForValue(self, value):
		value = byte_to_signed_int(value)
		
		if (value == 0): 
			self.cpu.zero_flag = 1
		else:
			self.cpu.zero_flag = 0
		
	#
	# valueIsNegative returns 1 or 0 depending on if the value is 2's compliment negative
	# it moves the bits 7 positions to the right leaving just the last bit
	# the last bit is returned as it controls whether the value is + or -
	def valueIsNegative(self, value):
		value = byte_to_signed_int(value)
		if value < 0: return 1
		else: return 0

	function_table = {
	'cld' : execute_cld,
	'sei' : execute_sei,
	'lda' : execute_lda,
	'ldx' : execute_ldx,
	'ldy' : execute_ldy,
	'sta' : execute_sta,
	'stx' : execute_stx,
	'sty' : execute_sty,
	'dex' : execute_dex,
	'dey' : execute_dey,
	'dec' : execute_dec,
	'txs' : execute_txs,
	'txa' : execute_txa,
	'jmp' : execute_jmp,
	'jsr' : execute_jsr,
	'bne' : execute_bne,
	'bpl' : execute_bpl
	}