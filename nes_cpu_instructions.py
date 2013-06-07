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

	def execute_clc(self, addr):
		self.cpu.carry_flag = 0

	def execute_sei(self, addr):
		self.cpu.interrupt_flag = 1

	def execute_lda(self, addr):
		value = self.cpu.accumulator = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
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
		self.push_short_to_stack(self.cpu.program_counter)
		self.cpu.program_counter = addr

	def execute_rts(self, addr):
		self.cpu.program_counter = self.pop_short_from_stack()

	def execute_and(self, addr):
		value = self.cpu.accumulator & byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		self.cpu.accumulator = value
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	def execute_adc(self, addr):
		memory_value = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		value = self.cpu.accumulator + memory_value + self.cpu.carry_flag
		
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.setCarryFlagForValue(value)
		self.setOverflowFlagForValue(self.cpu.accumulator, memory_value, value)
		self.cpu.accumulator = value # need to set accumulator after set overflow

	def execute_instruction(self, opcode_name, addr):
		#print ('execute: '+opcode_name)
		#try:
		if opcode_name in self.function_table:
			self.function_table[opcode_name](self, addr)
		else:
			print ('Error at pc='+get_program_counter_as_str(self.cpu.program_counter))
			print (opcode_name + ' '+str(addr))
			raise KeyError
		#except Exception as e:
		#	print (e)
		#	print ('execute: '+opcode_name) 
		return 2

	def push_short_to_stack(self, val):
		self.cpu.stack_pointer -= 2 #stack starts at 0xFF and shrinks
		addr = 0x0100 + self.cpu.stack_pointer
		self.cpu.memory.write_short_to_memory(addr, val)
		print ('pushed:'+str(val)+' to stack ( at location:'+str(addr)+' in mem)')
		return

	def pop_short_from_stack(self):
		#get the value pointed at by the stack pointer then decrement stack pointer
		addr = 0x0100 + self.cpu.stack_pointer
		value = self.cpu.memory.read_short_from_memory(addr)
		self.cpu.stack_pointer += 2
		print ('poped: '+str(value)+' from stack')
		return value

	# Carry indicates unsigned overflow, so check if the value is > 255
	def setCarryFlagForValue(self, value):
		if (value > 255):
			self.cpu.carry_flag = 1
		else:
			self.cpu.carry_flag = 0

	# Overflow indicates signed overflow
	def setOverflowFlagForValue(self, acc, mem, total):
		if acc >0 and mem >0 and total < 0:
			# positive and positive made negative so signed overflow
			self.cpu.overflow_flag = 1
		elif acc < 0 and mem < 0 and total > 0:
			# negative and negative made a positive so signed overflow
			self.cpu.overflow_flag = 1
		else:
			 self.cpu.overflow_flag = 0

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
	'adc' : execute_adc,
	'and' : execute_and,
	'clc' : execute_clc,
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
	'rts' : execute_rts,
	'bne' : execute_bne,
	'bpl' : execute_bpl
	}