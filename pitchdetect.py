from microphone import *
from pitch import *
from numpy import fromstring, int16, average, mean, std, array, append, sqrt
import analyse, struct

class PitchDetect(Microphone):
	"""A pitch detection class that supports detection of individual pitches
	as well as a moving-window average of pitches with outliers removed.
	
	Example:
	from pitchdetect import *
	listener = PitchDetect(channels=1)
	while True:
		listener.averagePitch()
		print listener.pitch
	"""
	def __init__(self, **kwargs):
		super(PitchDetect, self).__init__(**kwargs)
		# Amplitude in terms of RMS amplitude
		# Rules of thumb, gained through empirical testing:
		# 	Silence / background jitter: RMS < 1
		# 	Someone talking next to laptop: 0.5 - 5
		# 	String instrument: 3-15
		self.amplitudeThreshold = 0.5
		self.windowLength = 3 # samples per window

	def averagePitch(self):	
		"""Gets the moving average of input pitches."""
		self.detectedPitch = False

		def removeOutliers(a):
			deviations = 2
			mu = mean(a)
			s = std(a)
			return filter(lambda x: mu-deviations*s < x < mu+deviations*s, a)

		samples = []
		for i in xrange(self.windowLength):
			self.listen()
			if ( self.detectedNoise ):
				samples.append(self.pitch)
		freqs = [sample.freq for sample in samples if isinstance(sample, Pitch)]				
		cleaned = removeOutliers(freqs)		
		if ( len(cleaned) > 0 ):
			self.detectedPitch = True
			self.pitch = Pitch(sum(cleaned) / len(cleaned))

	def getAmplitude(self, block):
		"""Get the RMS (root-mean-square) amplitude of a block."""
		# CITE https://en.wikipedia.org/wiki/Root_mean_square
		count = len(block) / 2
		format = "%dh" % (count)
		wavBlock = struct.unpack(format, block)

		sumOfSquares = 0.0
		for sample in wavBlock:
			# normalize
			n = sample / float(self.rate)
			sumOfSquares += n*n

		return sqrt(sumOfSquares/count)
	

	def processAudio(self, block):
		try: 
			samples = fromstring(block, dtype=int16)
			freq = analyse.detect_pitch(samples) 
			amplitude = self.getAmplitude(block) * 1000
			self.detectedNoise = type(freq) != type(None)		
			if ( self.detectedNoise and amplitude >= self.amplitudeThreshold):
				self.pitch = Pitch(freq)
			else:
				self.pitch = None	
		except:
			# Not best practices, but good for failing silently if PyAudio
			# feeds you garbage audio data (which happens)
			pass