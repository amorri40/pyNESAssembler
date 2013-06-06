from bitarray import bitarray

class NesPPU():

	currentX = 0
	current_scan_line = 0 #y position on screen
	end_of_current_frame = False

	pixel_buffer = None

	nmi_counter = 0

	status_register = bitarray('00000000', endian='little')

	vblank_flag = 0

	renderer = None

	#Constants to say which bit in the status register is what
	VBLANK_BIT = 7

	def startFrame(self):
		print ('start frame')

	def execute_cycles_for_instruction(self, cycles):
		cycles *= 3 #for every 1 cpu cycle the ppu has 3
		for i in range (0,cycles):
			if self.end_of_current_frame:
				#self.end_of_current_frame = False
				self.startVBlank()
				return
			self.currentX += 1
			if (self.currentX >= 341): 
				self.endCurrentScanLine()
				self.currentX = 0

	def endCurrentScanLine(self):
		scanline = self.current_scan_line
		if (scanline == 261):
			#last line
			self.current_scan_line = -1 #wrap around (gets incremeneted to 0)
			self.end_of_current_frame = True
			self.setVBlankFlag(1)
			print ('end of frame')
			
		self.current_scan_line += 1

	def getStatusRegister(self):
		status = self.status_register.tobytes()
		self.setVBlankFlag(0)
		return status

	def setVBlankFlag(self, val):		
		self.status_register[self.VBLANK_BIT] = val
		self.vblank_flag = val
		

	def startVBlank(self):
		self.endFrame()

	def endFrame(self):
		#self.renderer.drawPixelsToWindow(self.pixel_buffer)
		return



