import threading
import tkinter as tk
import speech_recognition as sr
import pyaudio
import wave
import os

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
        self.text_widget.insert("1.0", "defaultRecordingFileName")
        self.text_widget.pack()
        #self.timeLabel.pack()
        self.recording = False
        self.firstTime = True
        self.terminate = False
        self.root.mainloop()
    
    def clickButton(self):
        #If we are recording, then the next press of the button will turn it's colour black otherwise it will become red
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
            self.thread = threading.Thread(target=self.comp).start()

    def recordAudio(self):
        FORMAT = pyaudio.paInt16  #Audio format (16-bit)
        CHANNELS = 1 
        RATE = 44100  #Sample rate (samples per second)
        CHUNK = 1024  #Number of frames per buffer

        audio = pyaudio.PyAudio()
        frames = []
        stream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

        print("Recording audio...")
        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)
        print("Finished recording.")

        stream.stop_stream()
        stream.close()
        audio.terminate()
        wave_file = wave.open("testfilek.wav", "wb")
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b"".join(frames))
        wave_file.close()

    def converSpeechToText(self):
        r = sr.Recognizer()
        with sr.AudioFile("testfilek.wav") as source:
            audio_data = r.record(source)

        text = r.recognize_google(audio_data)
        with open("defaultRecordingFileName.txt", "a") as f:
            f.write(text+"\n")

    def comp(self):
        self.recordAudio()
        self.converSpeechToText()
        os.remove("testfilek.wav")

Recorder()