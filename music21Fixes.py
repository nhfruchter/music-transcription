from music21 import *

def note_Note__hash__(self):
	"""Fix hashing of note.Note() objects so sets work."""
	return hash(self.fullName)

def note_Note__repr__(self):
	"""Better repr() of note.Note() objects."""
	return "note.Note(%r)" % self.nameWithOctave
		
note.Note.__hash__ = note_Note__hash__
note.Note.__repr__ = note_Note__repr__
		
	
			
