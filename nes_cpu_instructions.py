import nes_memory

class Instructions:

	cpu = None
	memory = None

	def __init__(self, cpu):
		self.cpu = cpu
		self.memory = self.cpu.memory

	def execute_cld(self, addr):
		self.cpu.decimal_flag = 0

	def execute_sei(self, addr):
		self.cpu.interrupt_flag = 0

	def execute_lda(self, addr):
		self.cpu.accumulator = self.cpu.memory.read_byte_from_memory(addr)

	# BPL: Branch on PLus (negative clear)
	def execute_bpl(self, addr):
		if (self.cpu.negative_flag == 0):
			print ('bpl addr:'+str(addr))
			self.cpu.program_counter = addr

	def execute_instruction(self, opcode_name, addr):
		print ('execute: '+opcode_name)
		try:
			self.function_table[opcode_name](self, addr)
		except:
			print ('execute: '+opcode_name) 
		return

	function_table = {
	'cld' : execute_cld,
	'sei' : execute_sei,
	'lda' : execute_lda,
	'bpl' : execute_bpl
	}