from Animation import *
from pitchdetect import *
import tkMessageBox

class Tuner(RetainedAnimation):
	## Audio functions: grabs and processes audio data for use. ##
	def initAudio(self):
		self.listener = PitchDetect(channels=1)

	## GUI functions: create buttons and dialogs. ##
	def initGUI(self):
		Button(self.root, text="About", command=self.showHelp).pack()
		Button(self.root, text="Quit", command=self.quitIt).pack()	
		
	def quitIt(self): 
		self.listener.stop()
		self.listener = False
		self.root.destroy()
		
	def showHelp(self):
		micName = self.listener.audio.get_default_input_device_info()['name']
		helpString = """tkTuner is a simple instrument tuner that uses your
computer's microphone to detect how in-tune the pitch it hears is.

Current microphone: %s
Tuning precision: %0.1f Hz""" % (micName, self.tuningPrecision)
						
		tkMessageBox.showinfo("Tuner - Help", helpString)
	
	## Initial draw functions: create new shape instances. ##
	def initScale(self):
		"""Draws the tuner scale."""
		# Note name labels
		numLabels = float(len(Pitch.noteNames))
		self.labelCoords = []
		for i in xrange(int(numLabels)):
			sectionWidth =  (self.width - self.margin) / numLabels 
			# Label position
			labelCx = self.margin + i* sectionWidth
			labelCy = self.height * 0.7
			noteNames = Pitch.noteNames[1:] + [Pitch.noteNames[0]]
			noteName = noteNames[i]
			
			# Store calculated label locations for scale drawing purposes
			self.labelCoords.append((labelCx, labelCy, noteName))			

			# Create label
			label = self.createText( labelCx, labelCy, None, self.labelFont)
			label.text = noteName
			label.anchor = W
			
			# Scale position
			barTop = self.height * 0.33
			barLeft = labelCx - self.width/36  
			barRight = barLeft + (self.width-self.margin)*1.0 / numLabels
			barBottom = self.height * 0.6
			self.scaleNoteWidth = (barRight - barLeft)
			
			# Create scale bar
			barRect = self.createRectangle(barLeft, barTop, barRight, barBottom)
			barRect.fill = self.barColor[ (i % 2 == 1) ]
			barRect.lineWidth = 0

			# Draw ticks
			for step in range(self.scaleSubSections):
				barDiv = ( (1.0*barRight-barLeft) / self.scaleSubSections)
				lineX = barLeft + barDiv * step
				line = self.createLine(lineX, barTop, lineX, barBottom  )
				line.fill = Color(255,255,255)
				topTicks = self.createLine(lineX, barTop-10, lineX, barTop)	
				bottomTicks = self.createLine(lineX, barBottom, lineX, barBottom+10)	
				topTicks.fill, bottomTicks.fill = Color(200, 200, 200), Color(200, 200, 200)
				
				if ( step % 2 == 0 ):
					centsPerTick = 200 / self.scaleSubSections # 200 cents per step
					centMultiplier = step - 4 # middle = in tune = 0 cents
					centLabel = ''.join([c + "\n" for c in str(centsPerTick * centMultiplier)])
					cent = self.createText(lineX, barBottom+30, None, font=self.centFont)
					cent.text = centLabel
				if ( step == self.scaleSubSections/2 ):
					line.width = barDiv / 2 
					line.fill = barRect.fill * 0.8

									   
	def initIndicator(self):
		"""Draws the pitch indicator."""
		self.triTip = (self.width / 2, self.height * 0.35)
		self.triLeft = (self.triTip[0] - self.width*0.01, self.height*.3)
		self.triRight = (self.triTip[0] + self.width*0.01, self.height*.3)
		self.indicatorCoords = ( self.triLeft, self.triTip, self.triRight)
		self.indicator = self.createPolygon( self.indicatorCoords )
		self.indicator.fill = self.indicatorColor[self.inTune]
		self.indicator.line = self.indicator.fill * .5
	
	def initInfo(self):
		"""Draws the accompanying text at the bottom of the screen."""
		infoCx, infoCy = self.width/2, self.height*0.85
		self.pitchText = self.createText( infoCx, infoCy, 
											None, self.pitchTextFont)
		self.pitchText.text = "Currently: No pitch detected."

		self.title = self.createText( infoCx, self.height*0.15, None, self.titleFont)
		self.title.text = "Tuner"
		self.subtitle = self.createText(infoCx, self.height*0.2, None, self.labelFont)
		self.subtitle.text = "(equal temperament)"
		
	## Update functions: update properties of created shapes and audio. ##		
	def updateIndicator(self):
		"""Calculates new indicator position based on current pitch."""
		newIndicatorX = self.getPosFromPitch(self.listener.pitch)
		
		self.triTip = (newIndicatorX, self.triTip[1])
		self.triLeft = (self.triTip[0] - self.width*0.01, self.height*.3)
		self.triRight = (self.triTip[0] + self.width*0.01, self.height*.3)
		self.indicatorCoords = ( self.triLeft, self.triTip, self.triRight)
		self.indicator.points = self.indicatorCoords
		self.indicator.fill = self.indicatorColor[self.inTune]
		
	def getPosFromPitch(self, pitch):
		"""Get screen position of indicator from pitch."""
		# Width of scale: 
		#	self.width - 2*self.margin
		# Width of each individual note: 
		#	width of scale / len(Pitch.noteNames) 
		# Width of each subdivision inside the note: 
		#   width of ind note / self.scaleSubSections
		
		if ( type(self.listener.pitch) == type(None) ):
			self.errorCount += 1
			return self.triTip[0] # don't move
			
		self.errorCount = 0 
		scaleWidth = self.width - 2*self.margin
		scaleNoteSubWidth = self.scaleNoteWidth / self.scaleSubSections
		curMidi = self.listener.pitch.midi
		scaleFraction = (curMidi % 12) + 1
		
		# Distance of scale block from left of screen
		xPos = (self.margin + scaleFraction * 
				self.scaleNoteWidth - (12*scaleNoteSubWidth) )
		if ( self.margin <= xPos ):
			return xPos
		else:	
			return self.triTip[0] # off screen, don't move
		
	def updateInfo(self):
		"""Calculates new info about current pitch to display."""
		if ( self.errorCount == 2 ):
			self.pitchText.text = "Unclear microphone input..."

		curNote = self.listener.pitch.note
		curFreq = self.listener.pitch.freq
		self.tuneDelta, self.tuneNeighbor = self.listener.pitch.inTune()
		tuneText = "%0.2f Hz off from %s (%0.1f Hz)" % (abs(self.tuneDelta), 
												self.tuneNeighbor.note, 
												curFreq)
		self.pitchText.text = tuneText
		
	## Controller functions. ##
	def timerFired(self):
		#self.listener.listen() # New info from microphone - raw
		self.listener.averagePitch() # New info from microphone - moving avg
		if ( self.listener.detectedPitch ):
			self.updateInfo()
			self.updateIndicator()
			if ( self.tuneDelta < self.tuningPrecision / 2):
				self.inTune = 2 # very in-tune: green
			elif ( self.tuneDelta < self.tuningPrecision ):
				self.inTune = 1 # close to in-tune: yellow
			else:
				self.inTune = 0	# not in-tune: red

	## Setup functions. ##
	def init(self):
		# Display settings
		self.root.wm_title("Tuner")
		self.margin = 50 # pixels
		self.scaleSubSections = 8
		self.labelFont = "LucidaGrande 16"
		self.pitchTextFont = "LucidaGrande 21"
		self.titleFont = "LucidaGrande 28 bold"
		self.centFont = "LucidaGrande 6"
		self.barColor = [ Color(245, 245, 245), Color(204, 230, 255) ] 
		self.indicatorColor = [ Color(255, 208, 224), Color(255, 212, 151), 
								Color(194, 255, 189) ] # red yellow green
		
		self.inTune = False
		self.tuningPrecision = 1.5 # Hz
		self.errorCount = 0 
		
		# Call secondary init functions
		self.initAudio()
		self.initScale()
		self.initIndicator()
		self.initInfo()
		self.initGUI()
		self.timerFiredDelay = 1 # milliseconds
		
app = Tuner()		
app.run(800,600)
	