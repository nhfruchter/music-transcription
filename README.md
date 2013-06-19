Nathaniel Fruchter / nhf 

Music Transcription: A 112 Term Project
######################################

[A few notes on design]

At the highest level, this project was supposed to be a sort-of Guitar Hero for actual instruments:
load up a MIDI file, play along with it, and find how good you are at playing the song.

From a practicality and design standpoint, this is really three separate elements: pitch detection,
music representation, and music transcription. If those three things were combined into one "all-or-nothing"
application (the final product), it would be pretty difficult to nail down as the three parts would need 
to work together flawlessly.  To that end, my project is split into three modules: an instrument tuner,
a sheet music transcriber, and a somewhat-working approximation of the original idea.

[Running]
Run launcher.py and choose from the menu.

[Modules used]
* Python built-in modules (that we didn't go over in class)
	* threading
		* Documentation: http://docs.python.org/2/library/threading.html
	* itertools
		* Documentation: http://docs.python.org/2/library/itertools.html#itertools.groupby
* PIL (Python Imaging Library) - Image processing and Tkinter wrangling.
	* Version 1.1.7
	* Install: http://www.pythonware.com/products/pil/
	* API / Documentation:
* Music21 - Computational music library, MIDI parser, sheet music rendering interface, and much more.
	* Version 1.4.0
	* Install: http://code.google.com/p/music21/downloads/list
	* API / Documentation: http://mit.edu/music21/doc/html/contents.html
* (app) Lilypond - Sheet music layout and export engine (think LaTeX for sheet music).
	* Version 2.16.2
	* Install: http://lilypond.org/
	* API: Automatically handled by Music21.
* PyGame - Used by Music21 for the sole purpose of its audio engine.
	* Version 1.9.1
	* Install: www.pygame.org
	* API: Automatically handled by Music21.
* NumPy/SciPy - math and number crunching (for audio data, in this case).
	* Version 1.7.0
	* Install: http://scipy.org/Download
	* API / Documentation: http://docs.scipy.org/doc/
* SoundAnalyse - easy pitch detection, implements fast Fourier transforms.
	* Version 0.1.1
	* Install: https://pypi.python.org/pypi/SoundAnalyse
	
Note: numpy + scipy + pygame + PIL + Python is in EPD, a Python distribution: https://www.enthought.com/downloads/	
	
[Citations]	
Code that I reused or got from another source.

* Animation.py (modified slightly)
	* From: http://www.cs.cmu.edu/~112/handouts/Animation.py
* bettertimer.py Timer class 
	* From: http://stackoverflow.com/questions/12435211/python-threading-timer-repeat-function-every-n-seconds
	
	



