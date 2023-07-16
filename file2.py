import os
import wave
import time
import threading
import tkinter as tk
import pyaudio
import speech_recognition as sr
import sys

class Recorder:
    def __init__(self):
        #GUI
        self.root = tk.Tk()
        self.root.geometry("200x200")
        self.root.resizable(False, False)
        self.button = tk.Button(self.root, text="     🎙️", font=("Arial", 55, "bold"), command=self.clickButton)
        self.button.pack()
        #self.timeLabel = tk.Label(text="00:00:00", font=("Arial", 20, "bold"))
        self.label = tk.Label(self.root, text="Enter file name:", font=("Arial", 10, "bold"))
        self.label.pack()
        self.text_widget = tk.Text(self.root, height=1, width=20)
        self.text_widget.pack()
        #self.timeLabel.pack()
        self.recording = False
        self.firstTime = True
        self.terminate = False
        self.root.mainloop()
    
    def clickButton(self):
        #If we are recording, then the next press of the button will turn it's colour black else it will be red
        if self.recording:
            self.recording = False
            self.button.config(fg="black")
            if self.firstTime != True:
                self.terminate = True
                self.root.destroy()
        else:
            self.firstTime = False
            self.recording = True
            self.button.config(fg="red")
            self.thread = threading.Thread(target=self.recordAudio).start()

    def recordAudio(self):
        self.filename = self.text_widget.get("1.0", "end-1c")
        while self.recording:
            #threading.Thread(target=self.record("goofygoobermusic.txt")).start()
            self.record(self.filename)

    def record(self, filename):
        #Recognizer instance
        print("Recording...")
        r = sr.Recognizer()

        with sr.Microphone() as source:
            # Adjust the energy threshold as per your environment and ambient noise level
            r.energy_threshold = 4000

            # Start the continuous listening
            audio = r.listen(source)
        #print("Transcribing...")
        #try:
            text = r.recognize_google(audio)
            with open(filename, "a") as file:
                file.write(text + "\n")
                """
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            pass
        #   print(e)
        #return trueAudioData
        """
Recorder()