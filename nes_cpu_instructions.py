import nes_memory
import struct
from nes_byte_utils import *
import logging

class Instructions:

	cpu = None
	memory = None

	def __init__(self, cpu):
		self.cpu = cpu
		self.memory = self.cpu.memory

	loggingi = 0
	def logOpcode(self, message):
		pc = self.cpu.get_program_counter()
		if (pc <= 0xc007): return
		if (self.loggingi > 19000 and self.loggingi < 25000 ):
			logging.info ('pc:'+self.cpu.get_program_counter_as_str()+' x:'+str(self.cpu.x_register)+' y:'+str(self.cpu.y_register)+' acc:'+str(self.cpu.accumulator)+' zero:'+str(self.cpu.zero_flag)+' carry:'+str(self.cpu.carry_flag)+' negative:'+str(self.cpu.negative_flag)+' m:'+message) #+' cycles:'+str(self.cpu.total_cycles)
		self.loggingi += 1
	

	#####################################
	# Register opcodes
	#####################################

	def execute_cld(self, addr):
		self.cpu.decimal_flag = 0

	def execute_clc(self, addr):
		self.cpu.carry_flag = 0

	# compare the accumulator to the memory at addr
	def execute_cmp(self, addr):
		memory_bytes = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		difference_between_acc_and_memory = self.cpu.accumulator - memory_bytes
		self.setZeroFlagForValue(difference_between_acc_and_memory)
		self.setNegativeFlagForValue(difference_between_acc_and_memory)
		self.setCarryFlagForValue( negative_byte_wrap(difference_between_acc_and_memory) )

	# compare the x register to the memory at addr
	def execute_cpx(self, addr):
		memory_bytes = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		difference_between_x_and_memory = self.cpu.x_register - memory_bytes
		self.setZeroFlagForValue(difference_between_x_and_memory)
		self.setNegativeFlagForValue(difference_between_x_and_memory)
		self.setCarryFlagForValue( negative_byte_wrap(difference_between_x_and_memory) )

	def execute_sei(self, addr):
		self.cpu.interrupt_flag = 1

	#####################################
	# Storage opcodes
	#####################################

	def execute_lda(self, addr):
		self.logOpcode('Before LDA:'+str(addr))
		value = self.cpu.memory.read_byte_from_memory(addr)
		self.cpu.accumulator = byte_to_signed_int(value)
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode(str(value)+'After LDA\n')

	def execute_ldx(self, addr):
		self.logOpcode('Before LDX')
		value = self.cpu.x_register = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode('After LDX\n')

	def execute_ldy(self, addr):
		self.logOpcode('Before LDY')
		value = self.cpu.y_register = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode('After LDY\n')

	def execute_sta(self, addr):
		self.logOpcode('Before STA:'+str(addr))
		self.cpu.memory.write_int_to_memory(addr, self.cpu.accumulator)
		self.logOpcode('After STA\n')
		

	def execute_stx(self, addr):
		self.logOpcode('Before STX:'+str(addr))
		self.cpu.memory.write_int_to_memory(addr, self.cpu.x_register)
		self.logOpcode('After STX\n')

	def execute_sty(self, addr):
		self.logOpcode('Before STY:'+str(addr))
		self.cpu.memory.write_int_to_memory(addr, self.cpu.y_register)
		self.logOpcode('After STY\n')

	def execute_txs(self, addr):
		value  = self.cpu.stack_pointer = self.cpu.x_register#+0x0100
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		print ('Transfer '+str(self.cpu.x_register)+' to stack pointer')


	# Transfer X to accumulator
	def execute_txa(self, addr):
		value = self.cpu.accumulator = self.cpu.x_register
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	# Transfer Accumulator to Y
	def execute_tay(self, addr):
		self.logOpcode('Before TAY')
		value = self.cpu.y_register = self.cpu.accumulator
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode('After TAY\n')

	# Transfer Accumulator to X
	def execute_tax(self, addr):
		self.logOpcode('Before TAX')
		value = self.cpu.x_register = self.cpu.accumulator
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode('After TAX\n')

	#####################################
	# Math opcodes
	#####################################

	def execute_dex(self, addr):
		self.logOpcode('Before DEX')
		self.cpu.x_register -= 1
		value = self.cpu.x_register
		self.cpu.x_register = negative_byte_wrap(self.cpu.x_register)
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode('After DEX\n')

	def execute_dey(self, addr):
		self.logOpcode('Before DEY')

		#value = self.cpu.y_register = (self.cpu.y_register-1)&0xFF
        #this.F_SIGN = (this.REG_Y>>7)&1;

		self.cpu.y_register -= 1
		value = self.cpu.y_register &0xFF
		self.cpu.y_register = value
		#self.cpu.y_register = abs(value)#negative_byte_wrap(self.cpu.y_register)
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode('After DEY\n')

	def execute_dec(self, addr):
		value = byte_to_unsigned_int(self.cpu.memory.read_byte_from_memory(addr))
		value -= 1
		self.cpu.memory.write_int_to_memory(addr, negative_byte_wrap(value))
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	def execute_inx(self, addr):
		self.logOpcode('Before INX')
		self.cpu.x_register += 1
		value = self.cpu.x_register
		self.cpu.x_register = negative_byte_wrap(self.cpu.x_register)
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode('After INX\n')

	def execute_iny(self, addr):
		self.logOpcode('Before INY')
		self.cpu.y_register += 1
		value = self.cpu.y_register
		self.cpu.y_register = negative_byte_wrap(self.cpu.y_register)
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.logOpcode('After INY\n')

	def execute_adc(self, addr):
		memory_value = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		value = self.cpu.accumulator + memory_value + self.cpu.carry_flag
		
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.setCarryFlagForValue(value)
		self.setOverflowFlagForValue(self.cpu.accumulator, memory_value, value)
		self.cpu.accumulator = value # need to set accumulator after set overflow

	#####################################
	# Branch opcodes
	#####################################

	# BPL: Branch on PLus (negative clear)
	def execute_bpl(self, addr):
		self.logOpcode('Before BPL')
		if (self.cpu.negative_flag == 0):
			self.cpu.program_counter = addr
		self.logOpcode('After BPL\n')

	# Branch on not zero
	def execute_bne(self, addr):
		self.logOpcode('Before BNE')
		if (self.cpu.zero_flag == 0):
			self.cpu.program_counter = addr
		self.logOpcode('After BNE\n')

	# Branch on equal to zero (zero flag set)
	def execute_beq(self, addr):
		self.logOpcode('Before BEQ')
		if (self.cpu.zero_flag == 1):
			self.cpu.program_counter = addr
		self.logOpcode('After BEQ\n')

	# Branch on carry set
	def execute_bcs(self, addr):
		self.logOpcode('Before BCS')
		if (self.cpu.carry_flag == 1):
			self.cpu.program_counter = addr
		self.logOpcode('After BCS\n')

	#####################################
	# Jump opcodes
	#####################################
	
	def execute_jmp(self, addr):
		self.logOpcode('Before JMP')
		self.cpu.program_counter = addr
		self.logOpcode('After JMP\n')

	def execute_jsr(self, addr):
		self.logOpcode('Before JSR')
		self.push_short_to_stack(self.cpu.program_counter)
		self.cpu.program_counter = addr
		self.logOpcode('After JSR\n')

	def execute_rts(self, addr):
		self.logOpcode('Before RTS')
		self.cpu.program_counter = self.pop_short_from_stack()
		self.logOpcode('After RTS\n')

	#####################################
	# Bitwise opcodes
	#####################################

	def execute_and(self, addr):
		value = self.cpu.accumulator & byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))
		self.cpu.accumulator = value
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)

	def execute_asl(self, addr):
		if (addr == -1):
			value = self.cpu.accumulator
		else:
			value = byte_to_signed_int(self.cpu.memory.read_byte_from_memory(addr))

		value = negative_byte_wrap(value << 1) #shift 1 bit left
		
		
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.setCarryFlagForValue(value)

		#write value back to either accumulator or memory
		if (addr == -1):
			self.cpu.accumulator = value
		else:
			self.cpu.memory.write_int_to_memory(addr, value)


	#####################################
	# Stack opcodes
	#####################################

	# Pull Accumulator from Stack
	def execute_pla(self, addr):
		value = self.pop_byte_from_stack()
		self.setZeroFlagForValue(value)
		self.setNegativeFlagForValue(value)
		self.cpu.accumulator = value


	def execute_instruction(self, opcode_name, addr):
		#print ('execute: '+opcode_name)
		#try:
		if opcode_name in self.function_table:
			self.function_table[opcode_name](self, addr)
		else:
			print ('Error at pc='+get_program_counter_as_str(self.cpu.program_counter))
			print ('Missing instruction:'+opcode_name + ' '+str(addr))
			raise KeyError
		#except Exception as e:
		#	print (e)
		#	print ('execute: '+opcode_name) 
		return 2

	####################################
	# Stack handeling helper methods
	#####################################

	def push_short_to_stack(self, val):
		self.cpu.stack_pointer -= 2 #stack starts at 0xFF and shrinks
		addr = 0x0100 + self.cpu.stack_pointer
		self.cpu.memory.write_short_to_memory(addr, val)
		print ('pushed:'+str(val)+' to stack ( at location:'+str(addr)+' in mem)')
		return

	def pop_short_from_stack(self):
		#get the value pointed at by the stack pointer then increment stack pointer
		addr = 0x0100 + self.cpu.stack_pointer
		value = self.cpu.memory.read_short_from_memory(addr)
		self.cpu.stack_pointer += 2
		print ('poped: '+str(value)+' from stack')
		return value

	def pop_byte_from_stack(self):
		#get the value pointed at by the stack pointer then increment stack pointer back up
		addr = 0x0100 + self.cpu.stack_pointer
		value = self.cpu.memory.read_byte_from_memory(addr)
		self.cpu.stack_pointer += 1
		print ('poped: '+str(value)+' from stack')
		return value

	####################################
	# Flag setting helper methods
	#####################################
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
		if value < 0: return 1 #unsigned value is negative when below 0
		elif value > 127: return 1 #signed value is actually negative when over 127
		else: return 0

	function_table = {
	'adc' : execute_adc,
	'and' : execute_and,
	'asl' : execute_asl,
	'clc' : execute_clc,
	'cld' : execute_cld,
	'cmp' : execute_cmp,
	'cpx' : execute_cpx,
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
	'inx' : execute_inx,
	'iny' : execute_iny,
	'txs' : execute_txs,
	'txa' : execute_txa,
	'tay' : execute_tay,
	'tax' : execute_tax,
	'jmp' : execute_jmp,
	'jsr' : execute_jsr,
	'rts' : execute_rts,
	'pla' : execute_pla,
	'bne' : execute_bne,
	'beq' : execute_beq,
	'bcs' : execute_bcs,
	'bpl' : execute_bpl
	}