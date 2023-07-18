import threading
import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import pyaudio
import wave
import os
import random
from pathlib import Path
import re
import customtkinter as ctk

class Recorder:
    def __init__(self):
        #GUI
        self.root = ctk.CTk()

        #Bringing the main window at the middle of the screen
        window_height = 200
        window_width = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        self.root.resizable(False, False)
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        
        self.button = ctk.CTkButton(self.root, text="     🎙️", height=100, width=100, font=("Arial", 50, "bold"), hover_color="#3b8ed0", command=self.clickButton)
        self.button.pack()
        self.label = ctk.CTkLabel(self.root, text="Enter file name:", font=("Arial", 15, "bold"), pady=20)
        self.label.pack()
        self.text_widget = ctk.CTkTextbox(self.root, height=1, width=140)
        self.text_widget.insert("1.0", "defaultRecordingFileName")
        self.text_widget.pack()
        self.recording = False
        self.firstClick = True
        self.root.mainloop()
    
    def clickButton(self):
        #If we are recording, then the next press of the button will turn it's colour black otherwise it will become red
        if self.recording:
            self.recording = False
            self.button.configure(fg_color="#3b8ed0")
            self.button.configure(hover_color="#3b8ed0")
            #Once the convertion proccess from audio to text begins, we disable the button and enable it again after the proccess is finished
            if self.firstClick == False:
                self.button.configure(state="disabled")
        else:
            self.recording = True
            self.firstClick = False
            self.button.configure(fg_color="#708090")
            self.button.configure(hover_color="#708090")
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
            file_path = Path(textFileName)
            try:
                with file_path.open(mode="a") as f:
                    f.write(text+"\n")
            except FileNotFoundError:
                print("File not found.")
            except IOError:
                print("Error while opening the file.")
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            pass

    def comp(self):
        #Get the name of the file the text will be stored into
        textFileName = re.sub('\s+','',self.text_widget.get("1.0", "end-1c"))
        if textFileName == "":
            textFileName = "defaultRecordingFileName"
        elif "." in textFileName:
            nameParts = textFileName.split(".")
            if nameParts[-1] != "txt":
                textFileName = textFileName+".txt" 
        
        #We generate a random name for the audio file, so that if 2 recordings occur at almost the same time the file deletion
        #that happens at the end doesn't cause any issues
        SAMPLE = "1234567890qazswxedcvfrtgbnhyujnmkiolpQAZSWXCDERFVBGTYHNMJUIKLOP"
        soundFileName = "soundfile"
        for _ in range(10):
            soundFileName +="".join(random.choice(SAMPLE))
        soundFileName += ".wav"

        self.recordAudio(soundFileName)
        self.loadingScreen()
        self.converSpeechToText(textFileName, soundFileName)
        self.loadScrn.destroy()
        os.remove(soundFileName) #We dont need the .wav files, so after converting the sound to text, we delete them
        self.button.configure(state="active")

    def loadingScreen(self):
        self.loadScrn = ctk.CTkToplevel(self.root)
        self.loadScrn.geometry("300x150")
        self.loadScrn.resizable(False, False)
        label2 = ctk.CTkLabel(self.loadScrn, text="Please wait while your data is being saved...", font=("Arial", 13, "bold"), pady=30)
        label2.pack()
        progressBar = ctk.CTkProgressBar(self.loadScrn, orientation="horizontal", width=200, mode="indeterminate", progress_color="#3b8ed0",fg_color="#D3D3D3", indeterminate_speed=0.6)
        progressBar.pack()
        progressBar.start()
Recorder()