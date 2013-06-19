import time
from threading import Thread

class Timer(Thread):
	# CITE: http://stackoverflow.com/questions/12435211/python-threading-timer-repeat-function-every-n-seconds
	"""A (slightly) better timer for Tkinter. At the millisecond level, 
	Tk.after() is very jittery and this seems to work a lot better.
	
	timer = Timer(delay_seconds, function_to_call)
	
	Example:
	from bettertimer import *
	timer = Timer(0.001, self.timerFired )
	timer.run()
	"""
	def __init__(self, delay, function):
		self.stopped = False
		self.paused = False
		self.delay = delay # seconds
		self.function = function
		self.firedCounter = 0 # how many times the timer has fired
		Thread.__init__(self)

	def stop(self):
		self.stopped = True	
		
	def pause(self):
		self.paused = not self.paused	

	def run(self):
		"""Implementation of threading.Thread() run function, which is the
		thread's main loop."""
		while not self.stopped:
			if ( not self.paused ):
				self.firedCounter += 1
				self.function()
				time.sleep(self.delay)
			else:
				continue	



