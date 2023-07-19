import threading
import speech_recognition as sr
import pyaudio
import wave
import os
import random
from pathlib import Path
import re
import customtkinter as ctk
from CTkScrollableDropdown import *

class Recorder:
    def __init__(self):
        #GUI
        self.root = ctk.CTk()

        #Bringing the main window to the middle of the screen
        window_height = 385
        window_width = 385
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        self.root.resizable(False, False)
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        #List of available languages
        values = ["Albanian / Shqip","Arabic / اللغة العربية","Bengali / বাংলা","Chinese / 普通话","English","German / Deutsch",
                "Greek / Ελληνικά","Hindi / हिन्दी","Italian/ Italiano","Japanese / 日本語","Portuguese / Português","Russian / Русский","Spanish / Español"]
        
        #Match all the languages to their respective code
        self.language_values = {
            "Albanian / Shqip":"sq","Arabic / اللغة العربية":"ar","Bengali / বাংলা":"bn","Chinese / 普通话":"zh-CN","English":"en","German / Deutsch":"de",
            "Greek / Ελληνικά":"el","Hindi / हिन्दी":"hi","Italian/ Italiano":"it","Japanese / 日本語":"ja","Portuguese / Português":"pt-PT",
            "Russian / Русский":"ru","Spanish / Español":"es"
        }

        #Recording button
        self.button = ctk.CTkButton(self.root, text="     🎙️", height=100, font=("Arial", 50, "bold"), corner_radius=50, hover_color="#3b8ed0", command=self.clickButton)
        self.button.pack(pady=10)
        self.value_inside = ctk.StringVar(value="English")

        #Attach to OptionMenu 
        optionmenu = ctk.CTkOptionMenu(self.root, width=220, variable=self.value_inside)
        optionmenu.pack(padx=10, pady=30)
        CTkScrollableDropdown(optionmenu, values=values)

        #Label and text box to enter the files name/path
        self.label = ctk.CTkLabel(self.root, text="Enter file name:", font=("Arial", 15, "bold"), pady=20)
        self.label.pack()
        self.text_widget = ctk.CTkTextbox(self.root, height=10)
        self.text_widget.insert("1.0", "defaultRecordingFileName")
        self.text_widget.pack()

        self.recording = False #Check if the recordign is active
        self.first_click = True
        self.root.mainloop()
    
    def clickButton(self):
        #If we are recording, then the next press of the button will turn it's colour black otherwise it will become red
        if self.recording:
            self.recording = False
            self.button.configure(fg_color="#3b8ed0")
            self.button.configure(hover_color="#3b8ed0")
            #Once the convertion proccess from audio to text begins, we disable the button and enable it again after the proccess is finished
            if self.first_click == False:
                self.button.configure(state="disabled")
        else:
            self.recording = True
            self.first_click = False
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

        #Record as long as the recording is active (the button is grey)
        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)

        #Terminate the stream and save the sound data to a .wav file
        stream.stop_stream()
        stream.close()
        audio.terminate()
        wave_file = wave.open(audioFileName, "wb")
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b"".join(frames))
        wave_file.close()

    def converSpeechToText(self, textFileName, audioFileName, code):
        #Read the sound data, turn it into text and save it into a text file
        r = sr.Recognizer()
        with sr.AudioFile(audioFileName) as source:
            audio_data = r.record(source)

        try:
            text = r.recognize_google(audio_data, language=code)
            file_path = Path(textFileName)
            try:
                with file_path.open(mode="a", encoding="utf-8") as f:
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
        
        #Get the code of the chosen language
        language_code = self.language_values.get(self.value_inside.get())
        
        #We generate a random name for the audio file, so that if 2 recordings occur at almost the same time the file deletion
        #that happens at the end doesn't cause any issues
        SAMPLE = "1234567890qazswxedcvfrtgbnhyujnmkiolpQAZSWXCDERFVBGTYHNMJUIKLOP"
        soundFileName = "soundfile"
        for _ in range(10):
            soundFileName +="".join(random.choice(SAMPLE))
        soundFileName += ".wav"

        self.recordAudio(soundFileName)
        self.loadingScreen()
        self.converSpeechToText(textFileName, soundFileName, language_code)
        self.loadScrn.destroy()
        os.remove(soundFileName) #We dont need the .wav files, so after converting the sound to text, we delete them
        self.button.configure(state="active")

    def loadingScreen(self):
        #GUI of the loading screen
        self.loadScrn = ctk.CTkToplevel(self.root)
        self.loadScrn.geometry("300x150")
        self.loadScrn.resizable(False, False)
        label2 = ctk.CTkLabel(self.loadScrn, text="Please wait while your data is being saved...", font=("Arial", 13, "bold"), pady=30)
        label2.pack()
        progressBar = ctk.CTkProgressBar(self.loadScrn, orientation="horizontal", width=200, mode="indeterminate", progress_color="#3b8ed0",fg_color="#D3D3D3", indeterminate_speed=0.6)
        progressBar.pack()
        progressBar.start()

if __name__ == "__main__":       
    Recorder()
