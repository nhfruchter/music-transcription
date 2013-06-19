# Graphics
from Tkinter import *
from bettertimer import *
import ImageTk, Image
import tkFileDialog, tkMessageBox

# Audio
from music21 import note, stream, pitch, clef, tempo 
from pitchdetect import *

# Misc
import time
from itertools import groupby
from threading import Thread

class Util(object):
	@classmethod
	def chunks(_class, l, n):
		# CITE: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
	    """ Yield successive n-sized chunks from l.
	    """
	    for i in xrange(0, len(l), n):
	        yield l[i:i+n]
	@classmethod
	def counter(_class, l):
		# CITE: http://docs.python.org/2/library/itertools.html#itertools.groupby
		"""
		Counts the number of occurrences ofn note elements in a list.

		Equivalent to collections.Counter, except it compensates for
		the broken hash representation of music21.note.Note() classes.
		"""
		occurrences = {}
		# Quick explanation:
		# >>> c4_1, c4_2 = note.Note("C4"), c4_2 = note.Note("C4")
		# >>> hash(c4_1) == hash(c4_2) # False (why, I have no idea)
		# >>> hash(c4_1.fullName) == hash(c4_2.fullName) # True

		fixedList = [ "n_"+elem.nameWithOctave if isinstance(elem, note.Note) 
					  else None 
					  for elem in l ]  

		for elem in set(fixedList):
			if ( type(elem) == str and elem[0:2] == "n_" ):
				occurrences[note.Note(elem[2:])] = fixedList.count(elem)
			else:
				occurrences[elem] = l.count(elem)
		return occurrences		
		
	@classmethod
	def stepround(_class, n, step):
		return int( step*round(float(n)/step) )
		
	def test(_class):
		assert ( list(_class.chunks(range(10), 5)) == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]] )
		assert ( list(_class.chunks(range(10), 10)) == [[range(10)]] )
		assert ( list(_class.chunks([], -2) )== [] )


class AudioTranscription(Frame):
	def __init__(self):
		# Initialize Tkinter
		self.root = Tk()
		self.root.title("Live Transcription")
		Frame.__init__(self, self.root)
		# Override quit to stop threads
		# CITE: http://mail.python.org/pipermail/tkinter-discuss/2009-April/001893.html
		self.root.createcommand('exit', self.quitIt) 
		
		# Initialize timer
		self.timerFiredDelay = 1 / 1000.0 # seconds
		self.timerRecDelay = 0.025 # seconds = 32nd note precision @ 60bpm
		self.timer = Timer(self.timerFiredDelay, self.timerFired)		
		self.recordingTimer = Timer(self.timerRecDelay, lambda: None)

		# Initialize GUI
		self.buttonOptions = {'padx': 10, 'pady': 10 }
		self.refreshInstance = False
		self.justLaunched = True
		self.saveDefault = "Not saved."
		self.saveFileStr = StringVar(self.root, self.saveDefault)
		self.initAudio()
		self.initWidgets()
		self.initSheetDisplay()
		self.timer.start()
		
	def quitIt(self): 
		"""Quit the application after clean up."""
		if ( self.recordingTimer.isAlive() ):
			self.recordingTimer.stop()
			self.recordingTimer.join()
		self.stop()
		self.root.destroy()
		if ( self.timer.isAlive() ):
			self.timer.stop()
			self.timer.join() 
		import sys; sys.exit()

	def getSavePath(self):
		"""Open a save-as dialog and get the file name."""
		self.saveFile = tkFileDialog.asksaveasfilename(title="Save transcribed music...")
		self.saveFileStr.set(self.saveFile)

	def record(self): 
		"""Start recording."""
		# State variables
		self.recording = False
		if ( not self.recording ):
			self.listener.unpause()
			self.recording = True
			self.paused = False
			self.recordingTimer.stopped = False
			self.recordingTimer.seconds = 0
			self.recordBtn.configure({'state': DISABLED})
			self.pauseBtn.configure({'state': NORMAL})
			self.stopBtn.configure({'state': NORMAL})
			
			tempo = int(self.tempo.get())
			quarterNoteSeconds = 60.0 / tempo 
			self.quarterTimerTicks = quarterNoteSeconds / self.timerRecDelay
			self.sixteenthTimerTicks = self.quarterTimerTicks / 4.0
			self.measureTimerTicks = self.quarterTimerTicks * 4

			# Start
			self.noteBuffer = []
			if ( not self.recordingTimer.isAlive() ):
				self.recordingTimer.start()
			self.recordingLabel.configure({"bg": "red", "text":"REC"})
		else:
			tkMessageBox.showerror("Oops", "You're already recording.")
		
	def pause(self): 
		"""Pause recording."""
		# State variables
		if ( self.recording ):		
			self.recording = False
			self.paused = True
			self.recordingTimer.pause()

			self.recordBtn.configure({'state': NORMAL})
			self.pauseBtn.configure({'state': DISABLED})
			self.stopBtn.configure({'state': NORMAL})
			self.recordingLabel.configure({"bg": "orange", "text":"PAUSED"})
		
	def stop(self): 
		"""Stop recording."""
		# State variables
		if ( self.recording ):
			self.recording = False
			self.paused = False		
			self.updateSheetDisplay()
			if ( self.recordingTimer.isAlive() and not self.recordingTimer.paused):
				self.recordingTimer.pause()
				# self.recordingTimer.stop()
				# self.recordingTimer.join()
			# Actually stop
			self.recordingLabel.configure({'bg':'lightblue', "text":"STOPPED"})
			self.recordBtn.configure({'state': NORMAL})
			self.pauseBtn.configure({'state': DISABLED})
			self.stopBtn.configure({'state': DISABLED})
			self.listener.pause() # Close audio input
			
				
	def reset(self):
		"""Reset to a new sheet."""
		areYouSure = "Are you sure you want to clear this transcription?"
		if ( tkMessageBox.askyesno("New file", areYouSure) ):
			self.stop() # Stop if in progress
			self.recordingLabel.configure({'bg':'lightblue', "text":"STOPPED"})
			self.saveFileStr = StringVar(self.root, self.saveDefault) 
			self.initSheetDisplay() # Clear display
			
	def export(self): 
		"""Export the transcribed music."""
		if ( self.saveFileStr.get() not in self.saveDefault ):
			# Set the tempo
			tempoObject = tempo.MetronomeMark( None, 
												int(self.tempo.get()), 
												note.QuarterNote() )
			self.transcribedPart.insert(tempoObject)
			
			# Write to disk
			success = self.transcribedPart.write(fp=self.saveFile)
			if ( success ):
				saveMsg = "Your file has been saved to %s." % success
				tkMessageBox.showinfo("File saved!", saveMsg )
		elif ( self.saveFileStr.get() == "" ):
			self.saveFileStr.set(self.saveDefault)		
			pass
		else:
			# Don't have a save location... should get that
			self.getSavePath()
			self.export()
	
	def timePassed(self, seconds):
		return self.recordingTimer.firedCounter % (15*seconds) == 0

	def timerFired(self):
		if ( self.recording ):
			if ( self.timePassed(1) ):
				self.recordingTimer.seconds += 1
				recText = {"text": "REC: %02d sec" % self.recordingTimer.seconds }
				self.recordingLabel.configure( recText )
			
			if ( len(self.noteBuffer) == self.measureTimerTicks ):
				self.processBuffer(self.noteBuffer)
				self.noteBuffer = [] # Clear the buffer
				
			# Fetch audio
			self.listener.averagePitch()

			# Add to note buffer: 1 measure's worth of audio
			if ( self.listener.detectedPitch ):
				theNote = note.Note(self.listener.pitch.note)
				self.noteBuffer.append(theNote)
			else:
				self.noteBuffer.append(None)	

	def processBuffer(self, noteBuffer):
		"""Process the recorded note buffer and turn it into
		a new music21.stream.Measure() for insertion into the
		transcribed score.
		"""

		measureBySixteenths = Util.chunks(noteBuffer, 
										  int(self.sixteenthTimerTicks))

		# Are the samples for each 16th note chunk predominantly 
		# None (rest) or predominantly a note?
		measureByMaxNote = [max(Util.counter(note16th)) 
							for note16th in measureBySixteenths]
		# Get each note with its corresponding length in terms of 
		# 16th beats.					
		measureByNoteGroup = [ ( elem, len(list(grouper)) ) 
						 for elem, grouper in groupby(measureByMaxNote) ]
		measure = stream.Measure()					
		# Build the new measure
		for (elem, noteLen) in measureByNoteGroup:
			if ( isinstance(elem, note.Note) ):
				# a 16th note is 1/4 a quarter note
				if ( self.heavyFiltering.get() ):
					# smooth to nearest eighth
					noteLen = Util.stepround(noteLen, 2)
				elem.quarterLength = (1.0/4.0) * noteLen					
				measure.insert(elem)
			else:
				rest = note.Rest(quarterLength=noteLen)
				measure.insert(rest)		
				
		measureLength = len(measure)			
		if ( measureLength > 1 and self.heavyFiltering.get() ):
			# Filter out octave jumps
			self.listener.windowLength = 5
			pleasePop = []
			for i in xrange(measureLength):
				current = measure[i]
				if ( i == 0 ):
					next = measure[1]
					prev = None
				elif ( i == measureLength - 1 )	:
					prev = measure[i-1]
					next = None
				else:
					prev = measure[i-1]	
					next = measure[i+1]
				noteSequence = (isinstance(current, note.Note) 
								and isinstance(next, note.Note)
						 		and isinstance(prev, note.Note) )

				if ( noteSequence ):
					octaveJump = ((prev.octave == next.octave) and 
									(current.octave != prev.octave))
					if ( octaveJump ): pleasePop.append(i)
			for i in pleasePop: measure.pop(i)		
				
				
		# You don't want too many ledger lines...
		octaves = [n.octave for n in measure if isinstance(n, note.Note)]
		if ( len(octaves) > 0 and min(octaves) < 4 ): 
			measure.insert(clef.BassClef())
		else:
			measure.insert(clef.TrebleClef())	
			
		self.transcribedPart.insert(measure)	
		self.updateSheetDisplay()

	def initSheetDisplay(self):
		# Initialize transcription container
		self.transcribedPart = stream.Part()
		defaultMeasure = stream.Measure()
		defaultMeasure.append(note.Note(type="whole"))
		self.transcribedPart.insert(defaultMeasure)
		
		# Render image
		self.updateSheetDisplay()
			
	def updateSheetDisplay(self):
		"""Render (or re-render) the transcribed score into sheet music."""
		# Re-render the sheet music
		self.sheetPath = self.transcribedPart.write("lily.png")
		_image = Image.open(self.sheetPath)
		# Scale to fit in window.
		scale = tuple([int(round(dim*0.6)) for dim in _image.size])

		self.sheetImg = ImageTk.PhotoImage(_image.resize(scale, 
															Image.ANTIALIAS))
		# Update the panel
		if ( self.justLaunched ):
			# Pack image and display
			self.panel = Label(self.sheetFrame, image=self.sheetImg)
			self.panel.pack(side=TOP, fill=BOTH, expand=YES)
			self.justLaunched = False
			
		self.panel.configure(image=self.sheetImg)

	def initAudio(self):
		"""Initialize pitch detection and transcription."""
		# Initialize pitch detection
		self.listener = PitchDetect(channels=1)
		self.listener.listen()
		self.recording = False
		self.paused = False

	def initWidgets(self): 	
		"""Define and draw GUI elements."""		
		def initSheetFrame():
			# ...for sheet music display
			self.sheetFrame = Frame(borderwidth=1)
			
		def initControlButtons():
			# Transcription control button container
			self.controlButtons = Frame(relief=SUNKEN, borderwidth=1)
			
			# Define buttons
			self.recordBtn = Button(self.controlButtons, text="Record", 
							command=self.record)
			self.pauseBtn = Button(self.controlButtons, text="Pause", 
							command=self.pause, state=DISABLED)
			self.stopBtn = Button(self.controlButtons, text="Stop", 
							command=self.stop, state=DISABLED)
			self.heavyFiltering = IntVar()
			filtering = Checkbutton(self.controlButtons, 
									text="Smooth Input Audio", 
									variable=self.heavyFiltering)				
			tempoLabel = Label(self.controlButtons, text="Intended tempo: ")
			self.recordingLabel = Label(self.controlButtons, text="STOPPED", 
										fg="white", bg="lightblue")
			self.tempo = Entry(self.controlButtons)
			self.tempo.insert(0, "60")
			
			# Pack buttons
			self.recordBtn.pack(side=LEFT)
			self.pauseBtn.pack(side=LEFT)
			self.stopBtn.pack(side=LEFT)
			filtering.pack(side=LEFT)
			self.recordingLabel.pack(side=LEFT)
			tempoLabel.pack(side=LEFT)
			self.tempo.pack(side=LEFT)
			
		def initBottomButtons():
			# Application control button container
			self.bottomButtons = Frame(relief=SUNKEN, borderwidth=1)
			
			# Define buttons
			fileName = Label(self.bottomButtons, text="Current file: ")
			self.fileLoc = Label(self.bottomButtons, 
									textvariable=self.saveFileStr)
			export = Button(self.bottomButtons, text="Export", 
							command=self.export)
			reset = Button(self.bottomButtons, text="Reset", 
							command=self.reset)
			quit = Button(self.bottomButtons, text="Quit", 
							command=self.quitIt)
		
			# Pack buttons
			fileName.pack(side=LEFT)
			self.fileLoc.pack(side=LEFT)
			export.pack(side=LEFT, **self.buttonOptions)
			reset.pack(side=LEFT, **self.buttonOptions)
			quit.pack(side=LEFT, **self.buttonOptions)
			
		initSheetFrame()
		initControlButtons()	
		initBottomButtons()
	
	def run(self):
		# Pack containers.
		self.pack()
		self.sheetFrame.pack(side=TOP)
		self.bottomButtons.pack(side=BOTTOM)
		self.controlButtons.pack(side=BOTTOM)
		self.root.mainloop()

if __name__ == '__main__':	
	transcription = AudioTranscription()
	transcription.run()
