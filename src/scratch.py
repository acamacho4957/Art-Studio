# # # from tkinter import *
# # # import tkinter

# # # top = tkinter.Tk()

# # # B1 = tkinter.Button(top, text ="circle", relief=RAISED,\
# # #                          cursor="circle")
# # # B2 = tkinter.Button(top, text ="plus", relief=RAISED,\
# # #                          cursor="plus")
# # # B1.pack()
# # # B2.pack()
# # # top.mainloop()
# # import pyautogui

# # pyautogui.moveTo(100, 150)
# import sys, os
# sys.path.insert(0, os.path.abspath('..\pyleap'))

# from pydub import AudioSegment
# from pydub.playback import play
# import urllib.request

# # Download an audio file
# urllib.request.urlretrieve("https://tinyurl.com/wx9amev", "metallic-drums.wav")

# # Load into PyDub
# loop = AudioSegment.from_wav("metallic-drums.wav")

# # Repeat 2 times
# loop2 = loop * 2

# # Get length in milliseconds
# length = len(loop2)

# # Set fade time
# fade_time = int(length * 0.5)

# # Fade in and out
# faded = loop2.fade_in(fade_time).fade_out(fade_time)

# # Play the faded loop
# play(faded)

# # import speech_recognition as sr
# # r = sr.Recognizer()
# # mic = sr.Microphone()
# # while(True):
# #     print("ready")
# #     with mic as source:
# #         audio = r.listen_in_background()
# #     print("you said " + r.recognize_google(audio))

# import time

# import speech_recognition as sr

# # this is called from the background thread
# def callback(recognizer, audio):
#     # received audio data, now we'll recognize it using Google Speech Recognition
#     try:
#         # for testing purposes, we're just using the default API key
#         # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
#         # instead of `r.recognize_google(audio)`
#         print("Google Speech Recognition thinks you said " + recognizer.recognize_google(audio))
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand audio")
#     except sr.RequestError as e:
#         print("Could not request results from Google Speech Recognition service; {0}".format(e))


# r = sr.Recognizer()
# m = sr.Microphone()
# with m as source:
#     r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

# # start listening in the background (note that we don't have to do this inside a `with` statement)
# stop_listening = r.listen_in_background(m, callback)
# # `stop_listening` is now a function that, when called, stops background listening

# # do some unrelated computations for 5 seconds
# # for i in range(30): 
# #     print(i)
# #     time.sleep(1)  # we're still listening even though the main thread is doing other things

# # calling this function requests that the background listener stop listening
# # stop_listening(wait_for_stop=False)

# # do some more unrelated things
# while True: time.sleep(0.1)  # we're not listening anymore, even though the background thread might still be running for a second or two while cleaning up and stopping
# from tkinter import *

# win = Tk()
# win.configure(bg='#000')

# red = 0
# blue = 0
# green = 0

# def fadeColour():
#     global win
#     global red
#     global blue
#     global green

#     red += 1
#     blue += 1
#     green += 1

#     if red < 256:
#         colour = '#{:02x}{:02x}{:02x}'.format(red, blue, green)
#         win.configure(bg=colour)

#         win.after(100, fadeColour)
    

# win.after(100, fadeColour)
# win.mainloop()

# import youtube_dl

# options = {
#     'format': 'bestaudio/best',
#     'extractaudio': True,
#     'audioformat': "mp3",
#     'outtmpl': 'happy.mp3',
#     'noplaylist': True,
# }

# with youtube_dl.YoutubeDL(options) as ydl:
#     ydl.download(['https://www.youtube.com/watch?v=TLRpaSq_pOI'])

# options = {
#     'format': 'bestaudio/best',
#     'extractaudio': True,
#     'audioformat': "wav",
#     'outtmpl': 'neutral.wav',
#     'noplaylist': True,
# }

# with youtube_dl.YoutubeDL(options) as ydl:
#     ydl.download(['https://www.youtube.com/watch?v=vMTeA59oOoM'])
# import pygame
# from time import sleep
# from pygame import mixer
# pygame.init()
# # mixer.init()
# mixer.music.load('metallic-drums.wav')
# pygame.mixer.music.play(0)
# while pygame.mixer.music.get_busy():
#     print(1)
#     pygame.time.delay(100)

import pygame
from pygame import mixer

# Intialize the pygame
pygame.init()

# create the screen
screen = pygame.display.set_mode((800, 600))

# Sound
mixer.music.load("Just Lose It.mp3")
mixer.music.play(-1)


# Game Loop
running = True
while running:

    # RGB = Red, Green, Blue
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
