import struct 
from nes_memory import Memory
from nes_cpu import *

from nes_cpu_instructions import Instructions

class RomFile():
	rom = None
	fields = {}
	
	
	instructions = None

	def openRom(self, filename='mario_bros_original.nes'):
		self.rom = open(filename,'rb')

	def closeRom(self):
		self.rom.close()

	def printRomPosition(self):
		print (self.rom.tell())

	def byteToString(byte, frmt='B'):
		return struct.unpack(frmt, byte)
	def readBytes(self, number_of_bytes):
		return self.rom.read(number_of_bytes)

	def readInt(self, number_of_bytes):
		bytes = self.rom.read(number_of_bytes)
		return int.from_bytes(bytes, byteorder='little')

	def readBytesList(self, number_of_bytes, frmt='B'):
		return_bytes = []
		for i in range (1, number_of_bytes): #read a byte at a time
			byte = self.rom.read(1)
			struct.unpack(frmt, byte)
			return_bytes.append(byte)
		return return_bytes

	def readString(self,length):
		chars = ""
		for i in range (1, length): #read a byte at a time
			byte = self.rom.read(1)
			chars += byte.decode("utf-8")
		return chars

	def setIntFieldFromByte(self, var_name):
		self.fields[var_name] = int(self.readInt(1))

	def printFieldValue(self, var_name):
		print (self.fields[var_name])

	def readCHRSections(self):
		number_of_chr_sections = self.fields['chr_count']
		for i in range(number_of_chr_sections):
			bytes = self.readBytesList(8192)
			Memory.chr_sections.append(bytes)


	def readPRGSections(self, nes_cpu):
		number_of_prg_sections = self.fields['prg_count']
		for i in range(number_of_prg_sections):
			bytes = self.readBytes(16384)
			nes_cpu.memory.program_sections.append(bytes)
			nes_cpu.memory.write_program_to_memory_high(i)
			nes_cpu.memory.write_program_to_memory_low(i)

	def readTrainer(self):
		bytes = self.readBytesList(512)
		print ('ROM has a trainer')

	def readRomHeader(self):
		header = self.readBytes(4)
		if (header != b'NES\x1a'):
			print ("Error rom header is not NES")
			exit()
		self.setIntFieldFromByte('prg_count')
		self.setIntFieldFromByte('chr_count')
		self.setIntFieldFromByte('flags6')
		self.setIntFieldFromByte('flags7')
		self.setIntFieldFromByte('prg_ram_size')
		self.setIntFieldFromByte('flags9')
		self.setIntFieldFromByte('flags10')
		header = self.rom.read(5) # 5 zero bytes

if __name__ == "__main__":

	logging.basicConfig(filename='emulator_log.txt', filemode='w', level=logging.INFO)

	rom = RomFile()
	rom.openRom()
	rom.readRomHeader()
	
	nes_cpu = NesCPU(rom)

	rom.printRomPosition()
	rom.readPRGSections(nes_cpu)
	rom.readCHRSections()
	nes_cpu.run_main_cpu_loop()
	
	rom.closeRom()