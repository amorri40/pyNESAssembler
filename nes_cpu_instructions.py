import nes_memory
import struct

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
		self.cpu.accumulator = self.cpu.memory.read_byte_from_memory(addr)
		self.setZeroFlagForValue(self.cpu.accumulator)
		self.setNegativeFlagForValue(self.cpu.accumulator)

	# BPL: Branch on PLus (negative clear)
	def execute_bpl(self, addr):
		if (self.cpu.negative_flag == 0):
			#print ('bpl addr:'+str(addr))
			#print (self.cpu.negative_flag == 0)
			self.cpu.program_counter = addr

	def execute_instruction(self, opcode_name, addr):
		#print ('execute: '+opcode_name)
		try:
			self.function_table[opcode_name](self, addr)
		except Exception as e:
			print (e)
			print ('execute: '+opcode_name) 
		return 2


	def setNegativeFlagForValue(self, value):
		self.cpu.negative_flag = self.valueIsNegative(value)

	def setZeroFlagForValue(self, value):
		if (value == 0): 
			self.cpu.zero_flag = 1
		else:
			self.cpu.zero_flag = 0
	#
	# valueIsNegative returns 1 or 0 depending on if the value is 2's compliment negative
	# it moves the bits 7 positions to the right leaving just the last bit
	# the last bit is returned as it controls whether the value is + or -
	def valueIsNegative(self, value):
		value = struct.unpack('b',value)[0]
		if value < 0: return 1
		else: return 0

	function_table = {
	'cld' : execute_cld,
	'sei' : execute_sei,
	'lda' : execute_lda,
	'bpl' : execute_bpl
	}