import threading
import tkinter as tk
import speech_recognition as sr
import pyaudio
import wave
import os
import random

class Recorder:
    def __init__(self):
        #GUI
        self.root = tk.Tk()
        self.root.geometry("200x200")
        self.root.resizable(False, False)
        self.button = tk.Button(self.root, text="     🎙️", font=("Arial", 55, "bold"), command=self.clickButton)
        self.button.pack()
        self.label = tk.Label(self.root, text="Enter file name:", font=("Arial", 10, "bold"))
        self.label.pack()
        self.text_widget = tk.Text(self.root, height=1, width=20)
        self.text_widget.insert("1.0", "defaultRecordingFileName")
        self.text_widget.pack()
        self.recording = False
        self.terminate = False
        self.root.mainloop()
    
    def clickButton(self):
        #If we are recording, then the next press of the button will turn it's colour black otherwise it will become red
        if self.recording:
            self.recording = False
            self.button.config(fg="black")
        else:
            self.recording = True
            self.button.config(fg="red")
            self.thread = threading.Thread(target=self.comp)
            self.thread.daemon = True #By setting the daemon property to True we allow the thread to be terminated the moment the "main thread" gets interupted
            self.thread.start()

    def recordAudio(self, audioFileName):
        FORMAT = pyaudio.paInt16  #Audio format (16-bit)
        CHANNELS = 1 
        RATE = 44100  #Sample rate (samples per second)
        CHUNK = 1024  #Number of frames per buffer

        audio = pyaudio.PyAudio()
        frames = []
        stream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

        #Record as long as the button shown is red
        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)

        #Terminate the stream and save the sound data into a .wav file
        stream.stop_stream()
        stream.close()
        audio.terminate()
        wave_file = wave.open(audioFileName, "wb")
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b"".join(frames))
        wave_file.close()

    def converSpeechToText(self, textFileName, audioFileName):
        #Read the sound data, turn it into text and save it into a .txt file
        r = sr.Recognizer()
        with sr.AudioFile(audioFileName) as source:
            audio_data = r.record(source)

        try:
            text = r.recognize_google(audio_data)
            with open(textFileName, "a") as f:
                f.write(text+"\n")
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            pass

    def comp(self):
        #Get the name of the file the text will be stored into
        textFileName = self.text_widget.get("1.0", "end-1c")+".txt"
        if textFileName == ".txt":
            textFileName = "defaultRecordingFileName.txt"
        
        #We generate a random name for the audio file, so that if 2 recordings occur at almost the same time the file deletion
        #that happens at the end doesn't cause any issues
        SAMPLE = "1234567890qazswxedcvfrtgbnhyujnmkiolpQAZSWXCDERFVBGTYHNMJUIKLOP"
        soundFileName = "soundfile"
        for _ in range(10):
            soundFileName +="".join(random.choice(SAMPLE))
        soundFileName += ".wav"
        print(soundFileName)

        self.recordAudio(soundFileName)
        self.converSpeechToText(textFileName, soundFileName)
        os.remove(soundFileName) #We dont need the .wav files, so after converting the sound to text, we delete them

Recorder()
