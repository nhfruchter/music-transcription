# CITE http://people.csail.mit.edu/hubert/pyaudio/
import pyaudio, time

class Microphone(object):
	"""Sets up an instance of a microphone recording stream using PyAudio."""
	def __init__(self, format=None, channels=None, rate=None):
		self.format = format or pyaudio.paInt16 # records in WAV format; 16-bit integers
		self.channels = channels or 2 # channels (i.e. stereo, mono, more if available)
		self.rate = rate or 44100 # audio sampling rate
		self.audio = pyaudio.PyAudio() # new pyAudio root instance
		self.micStream = self.newMicStream() # new pyAudio stream instance
		self.framesPerBuffer = 2**10 # number of samples per block (1024)
		self.isRunning = True
		self.timer = 0
		self.secondTimer = 0
		self.debug = False
		
	def debug(self, obj, excludedKeys=[]):
		"""
		Prints canvas.data.__dict__, minus any keys in excludedKeys.
		Handy for debugging classes and stuff.
		"""
		print "#"*20
		print "Printing current state:"
		for key in obj.__dict__:
			if ( key in excludedKeys ): continue
			print "%s: %s" % (str(key), str(obj.__dict__[key]))
		print "#"*20
	
	def stop(self):
		"""Stop a mic stream."""
		self.micStream.close()
		self.isRunning = False

	def pause(self):
		"""Pause recording from a mic stream."""
		if ( self.isRunning ):
			self.isRunning = False

	def unpause(self):
		"""Unpause recording from a mic stream."""
		if ( not self.isRunning ):
			self.isRunning = True

	def newMicStream(self):
		"""Creates a new instance of the microphone data strem."""
		stream = self.audio.open( format = self.format,
								  channels = self.channels,
								  rate = self.rate,
								  input = True
								)
		return stream
					
	def readAudio(self):
		"""A wrapper for reading raw audio data from the microphone data stream.
		Reads in blocks of length self.framesPerBuffer.
		"""
		try:
			audioBlock = self.micStream.read(self.framesPerBuffer)
			return audioBlock	
		except IOError:
			if ( self.debug ): self.debug(self.micStream)
			return False
			
	def listen(self):
		"""Listens and hands off audio to processing function(s)."""
		audioBlock = self.readAudio()	
		self.processAudio(audioBlock)
			
	def processAudio(self, block):
		error = "Please define your own version of this function in your subclass."
		raise NotImplementedError(error)

	def display(self, block):
		error = "Please define your own version of this function in your subclass."
		raise NotImplementedError(error)
	
	def run(self): 
		"""Listens until paused or stopped."""
		while self.isRunning:
			self.listen()
			self.display()
		
		