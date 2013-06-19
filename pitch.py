from numbers import Number
from math import log

class Util(object):
	@classmethod
	def freqOrNumber(_class, other):
		"""Returns the correct type to operate on."""
		if ( isinstance(other, Number) ):
			otherPart = other
		elif ( isinstance(other, Pitch) ):
			otherPart = other.freq
		else:
			otherPart = None	
		return otherPart

class Pitch(object):
	"""A class that represents a given pitch in terms of frequency and its
	associated MIDI and note-name values. Provides conversion functions
	to convert between note names, MIDI values, and frequencies, as well as
	basic math and pitch math (i.e. tuning, harmonic equivalency).
	"""
	
	# noteNames = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
	noteNames = ["C", "C#", "D", "E-", "E", "F", "F#", "G", "A-", "A", "B-", "B"]

	def __init__(self, frequency):
		self.precision = 3
		self.freq = round(float(frequency), self.precision) 
		self.midi = Pitch.freqToMidi(self.freq)
		self.note = Pitch.midiToNote(self.midi)
	
	# Type representations
	def __repr__(self): return "Pitch(%0.3f)" % self.freq
	def __str__(self): return "%s (%0.3f Hz)" % (self.note, self.freq)
	def __int__(self): return int(self.freq)
	def __float__(self): return float(self.freq)
				
	# Math		
	def __cmp__(self, other): return (self.freq - Util.freqOrNumber(other))
	def __div__(self, other): return Pitch(self.freq/Util.freqOrNumber(other))
	def __mul__(self, other): 
		result = self.freq*Util.freqOrNumber(other)
		if ( result > 0 ):
			return Pitch(result)

	def __add__(self, other): 
		result = self.freq+Util.freqOrNumber(other)
		if ( result > 0 ):
			return Pitch( result )
		else:
			raise ValueError("Can't have a zero or negative pitch.")	

	def __sub__(self, other):
		result = self.freq - Util.freqOrNumber(other)
		if ( result > 0 ):
			return Pitch(result)
		else:
			raise ValueError("Can't have a zero or negative pitch.")					
	
	# Hashing 
	def __hash__(self): return hash(self.__repr__())
		
	def roughlyEqual(self, other, tolerance=0.1):
		"""Returns equality between two pitches given a tolerance."""
		return abs(self.pitch - other) < tolerance

	def roughlyEqualHarmonically(self, other, tolerance=0.009):
		"""Tests equality of two pitches regardless of harmonic difference.
		For example, Pitch(440) != Pitch (220) (A4 != A3), but
		Pitch(440).roughlyEqualHarmonically(Pitch(220)) == True since (A == A).
		"""
		this = self.freq
		that = float(Util.freqOrNumber(other))
		
		if ( this > that ):
			trueOctaveDiff = this / float(that)
		elif ( this < that ):
			trueOctaveDiff = float(that) / this
		else:
			return True
			
		roughOctaveDiff = round(trueOctaveDiff)
		return abs ( trueOctaveDiff - roughOctaveDiff ) < tolerance

	def inTune(self):
		"""Returns the difference between a pitch and the nearest 
		whole note. (Whole as in whole number, not as in time signature.)
		For example, Pitch(438.500).inTune() == -1.500 Hz as it's 
		3 away from 440 Hz, its nearest neighbor.
		"""
		nearestNeighbor = Pitch(self.noteToFreq(self.note))
		pitchDelta = self.freq - nearestNeighbor.freq 
		return (pitchDelta, nearestNeighbor)
	
	@classmethod
	def freqToMidi(_class, freq):
		"""Converts a pitch into its corresponding MIDI note representation.
		MIDI notes go from 0 to 127 and map frequencies to that range. 
		60 is middle C (C4) and 69 is middle A (A4 = 440 Hz).
		An octave is represented as 12 semitones.
		""" 
		# CITE: http://www.phys.unsw.edu.au/jw/notes.html
		midiNote = 69 + 12 * log(freq / 440.0, 2)
		return round(midiNote, 2)

	@classmethod
	def freqToNote(_class, freq):
		"""Converts a frequency value to a note name."""
		return _class.midiToNote(_class.freqToMidi(freq))
		
	@classmethod
	def midiToFreq(_class, midi):
		"""Converts a MIDI note value to a frequency."""
		midiFreq = 2**((midi-69)/12.0) * 440.0
		return midiFreq
		
	@classmethod	
	def midiToNote(_class, midi):
		"""Get the standard written representation of a pitch (note + octave)
		from a MIDI note representation."""
		octave = (int(midi) / 12) - 1
		name = _class.noteNames[ int(round(midi)) % 12  ]
		return "%s%d" % (name, octave)
		
	@classmethod
	def noteToMidi(_class, note):
		"""Takes a note in the form of C4 of F#3 and returns its MIDI value."""
		return int(round(_class.freqToMidi(_class.noteToFreq(note))))

	@classmethod
	def noteToFreq(_class, note, precision=3):
		"""Takes a note in the form of C4 of F#3 and returns its frequency."""
		# Useful constants
		# CITE: http://www.booki.cc/csound/pitch-and-frequency/
		aToCTuningOffset = 9
		semitoneRatio = 2**(1.0/12)
				
		# Takes a note in the form A(-/#)N. 
		letter = note[0:len(note)-1]
		octave = note[-1]
		offsetNoteIndex = _class.noteNames.index(letter) - aToCTuningOffset
		
		octaveComponent = 2**int(octave)
		noteComponent = semitoneRatio**offsetNoteIndex
		frequency = round((275*octaveComponent*noteComponent/10.0), precision)

		return frequency
	
	@classmethod
	def test(_class):
		"""Tests for the Pitch class."""
		import random
		notes = ["A4", "B-4", "C3", "F2"]
		midis = [69, 70, 48, 41]
		freqs = [440.0, 466.16, 130.81, 87.307]
		A0 = 27
		C8 = 4186
		
		def almostEq(a, b, tolerance=0.01): return abs(b-a) < tolerance
		
		for i in xrange(len(freqs)):
			assert( _class.freqToMidi(freqs[i]) == float(midis[i]) )
			assert( _class.freqToNote(freqs[i]) == notes[i] )
		
		for i in xrange(len(midis)):
			assert( almostEq(_class.midiToFreq(midis[i]), freqs[i]) )
			assert ( _class.midiToNote(midis[i]) == notes[i] )
		
		for i in xrange(len(notes)):
			assert( _class.noteToMidi(notes[i]) == midis[i] )
			assert( almostEq(_class.noteToFreq(notes[i]), freqs[i]) )
			
		assert( Pitch(440) + Pitch(20) == Pitch(440+20) )
		assert( Pitch(440) != Pitch(220) )
		assert( Pitch(440).roughlyEqualHarmonically(Pitch(440)*3) )
		assert( Pitch(440) / 2.3 == Pitch(191.304) )
		assert( Pitch(440)*0 == None )
		assert( hash(Pitch(440)) == hash(Pitch(440)) )				
		assert( hash(Pitch(333)) != hash(Pitch(333.01)))
		
if __name__ == '__main__':
	Pitch.test()