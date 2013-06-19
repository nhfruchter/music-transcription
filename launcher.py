from Tkinter import *
import subprocess, threading

class ThreadedCall(threading.Thread):
	"""
	Because object oriented Tkinter is hard.
	Creates a newthread with a subprocess (the application being launched) 
	inside.
	
	Example:
	app = ThreadedCall(["python", "TkinterApp.py"])
	app.start() # open a new copy of TkinterApp
	"""
	def __init__(self, command):
		self.command = command
		threading.Thread.__init__(self)
	 
	def run(self):
		process = subprocess.Popen(self.command)

class Launcher(Frame):
	"""Launcher/menu screen for project components."""
	
	def __init__(self):
		self.root = Tk()
		self.root.title("Launcher")
		Frame.__init__(self, self.root)
		self.buttonOptions = {'fill': BOTH, 'padx': 10, 'pady': 10 }
		self.drawText()
		self.drawButtons()
		
	def launchTuner(self):
		tuner = ThreadedCall(["python", "tkTuner.py"])
		tuner.start()
		
	def launchMIDI(self):
		midi = ThreadedCall(["python", "playalong.py"])
		midi.start()

	def launchTranscription(self):
		transcribeapp = ThreadedCall(["python", "transcribe.py"])
		transcribeapp.start()

	def quitIt(self):
		import sys 
		self.root.destroy(); sys.exit()
		
	def drawButtons(self):
		buttons = []
		buttons += [Button(self, text="Instrument Tuner", 
				command=self.launchTuner)] 
		buttons += [Button(self, text="Audio to Sheet Music Transcription", 
				command=self.launchTranscription)]
		buttons += [Button(self, text="Play Along With MIDI File (Kinda-working demo)",
				command=self.launchMIDI)]
		buttons += [Button(self, text="Quit", command=self.quitIt)]
		for button in buttons:
			button.pack(**self.buttonOptions)
			
	def drawText(self): 
		Label(self, text="Music Transcription\nChoose an app to launch.").pack(side=TOP)
		
	
	def run(self):
		self.pack()
		self.root.mainloop()
		
if __name__ == '__main__':	
	launcher = Launcher()
	launcher.run()