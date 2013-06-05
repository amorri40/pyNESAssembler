class Instructions:

	cpu = None

	def __init__(self, cpu):
		self.cpu = cpu

	def execute_cld(self, addr):
		self.cpu.decimal_flag = 0
		print ('execute cld')

	def execute_instruction(self, opcode_name, addr):
		try:
			self.function_table[opcode_name]()
		except:
			print ('execute: '+opcode_name) 
		return

	function_table = {
	'cld' : execute_cld
	}