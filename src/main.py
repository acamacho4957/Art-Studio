#Painting
from tkinter import *
from tkinter import ttk, colorchooser, PhotoImage
from PIL import Image, ImageTk

import sys, os
sys.path.insert(0, os.path.abspath('..\pyleap'))

from time import sleep
import numpy as np
import random

#Face
import cv2
import keras
from keras.preprocessing import image
from keras.models import Model, load_model

#Gesture
from pyleap.leap import getLeapInfo, getLeapFrame

#Music
import pygame
from pygame import mixer_music

#Speech
import time
import speech_recognition as sr

#Saving
import io
import subprocess
#ghostscript

#Multithreading
import queue


model = load_model('models/emotion_model.h5')
# model = load_model('models/model_3.h5')

emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
emotionsToRGB = {'happy': (252, 252, 0), 'neutral': (40, 180, 252)}

BROWN_PALLETE = '#{:02x}{:02x}{:02x}'.format(232, 208, 132)
RED = "red"
ORANGE = "orange"
YELLOW = "yellow"
GREEN = "green"
BLUE = "blue"
PURPLE = "purple"

class ArtStudioApp(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.bind("<q>", lambda e: self.destroy())
        self.title('Art Studio')
        self.state('zoomed')

        container = Frame(self)

        container.pack(side=TOP, fill=BOTH, expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainPage, CanvasPage, CallibrationPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky = NSEW)

        self.menu = Menu(self)
        self.initializeMenu()

        self.show_frame(MainPage)   

        self.vs = cv2.VideoCapture(0) 

    def show_frame(self, cont, state=None):
        frame = self.frames[cont]

        for F in self.frames.values():
            if F != frame:
                F.deactivate()

        frame.activate()
        if state is "NEW":
            frame.clear() #Activate frame and clear the canvas for new painting
            self.showMenu()
        elif state is "CONTINUE":
            self.showMenu()
        else:
            self.hideMenu()
        frame.tkraise()

    def initializeMenu(self):
        filemenu = Menu(self.menu)
        colormenu = Menu(self.menu)
        self.menu.add_command(label="Home", command=lambda: self.show_frame(MainPage))
        self.menu.add_command(label="Change Custom Color", command=self.frames[CanvasPage].change_fg)
        self.menu.add_command(label="New Suggestion", command=self.frames[CanvasPage].generate_suggestion)
        self.menu.add_command(label="Undo", command=self.frames[CanvasPage].undo)
        self.menu.add_command(label="Clear Canvas", command=self.frames[CanvasPage].clear)
        self.menu.add_command(label="Save", command=self.frames[CanvasPage].save)
        self.menu.add_command(label="Exit", command=self.destroy)

    def hideMenu(self):
        self.config(menu="")

    def showMenu(self):
        self.config(menu=self.menu)

class MainPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.isActive = True
        self.isContinue = False

        self.config(bg='#{:02x}{:02x}{:02x}'.format(40, 180, 252))

        label = Label(self,
                      text="Welcome to Art Studio",
                      font=("Comic Sans MS", 40),
                      fg="white",
                      bg='#{:02x}{:02x}{:02x}'.format(40, 180, 252))

        label.pack(pady=10, padx=10)

        photo = ImageTk.PhotoImage(file="lib/main_image.png")
        label_photo = Label(self, image=photo, bg='#{:02x}{:02x}{:02x}'.format(40, 180, 252))
        label_photo.image = photo
        label_photo.pack(pady=2)

        button1 = Button(self, 
                         text="New Drawing", 
                         font=("Comic Sans MS", 20),
                         bg="white",
                         width=20,
                         command=lambda: controller.show_frame(CanvasPage, state="NEW"))
        button1.pack(pady=2)

        self.button2 = Button(self, 
                         text="Callibrate", 
                         font=("Comic Sans MS", 20),
                         bg="white",
                         width=20,
                         command=lambda: controller.show_frame(CallibrationPage))
        self.button2.pack(pady=2)

    def activate(self):
        self.isActive = True

    def deactivate(self):
        self.isActive = False
        self.showContinue() #Once it's been deactivated, all future viewings of frame will have the continue button
    
    def showContinue(self):
        if not self.isContinue:
            self.button2.destroy()

            button3 = Button(self, 
                             text="Continue Drawing", 
                             font=("Comic Sans MS", 20),
                             bg="white",
                             width=20,
                             command=lambda: self.controller.show_frame(CanvasPage, state="CONTINUE"))
            button3.pack(pady=2)

            self.button2 = Button(self, 
                         text="Callibrate", 
                         font=("Comic Sans MS", 20),
                         bg="white",
                         width=20,
                         command=lambda: self.controller.show_frame(CallibrationPage))
            self.button2.pack(pady=2)

            self.isContinue = True

class CallibrationPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.config(bg='#{:02x}{:02x}{:02x}'.format(40, 180, 252))

        self.isActive = False
        self.current_image = None
        self.i = 0

        self.current_instruction = StringVar()
        self.current_instruction.set("Angry")
        self.banner = Label(self, textvariable = self.current_instruction, font=('arial 20'), bg='#{:02x}{:02x}{:02x}'.format(40, 180, 252))
        self.banner.pack()

        self.panel = Label(self)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        btn = Button(self, text="Capture Image", command=self.capture_image)
        btn.pack(fill="both", expand=True, padx=10, pady=10)

    def capture_image(self, e=None):
        """ Capture image and save it. """
        if self.isActive:
            filenames = ['angry.jpg', 'disgust.jpg', 'fear.jpg', 'happy.jpg','sad.jpg', 'surprise.jpg', 'neutral.jpg']
            filename = filenames[self.i]
            self.current_image.save(filename, "JPEG")  # save image as jpeg file
            if self.i < 6:
                self.i += 1
                titles = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
                self.current_instruction.set(titles[self.i])
            else:
                #TODO TRANSFER LEARNING
                self.controller.show_frame(MainPage)

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        if self.isActive:
            ok, frame = self.controller.vs.read()  # read frame from video stream
            if ok:  # frame captured without any errors
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert colors from BGR to RGB
                self.current_image = Image.fromarray(cv2image)  # convert image for PIL
                imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
                self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
                self.panel.config(image=imgtk)  # show the image
            self.controller.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def activate(self):
        self.isActive = True
        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()

    def deactivate(self):
        self.isActive = False


class CanvasPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.isActive = False
        self.emotion = 'neutral'
        self.rgb = emotionsToRGB[self.emotion]
        self.color_custom = 'gray'
        self.custom_square = None
        self.color_fg = 'black'
        self.color_bg = 'white'
        self.all_lines = []
        self.recent_line = []
        self.old_x = None
        self.old_y = None
        self.cursor = None
        self.cursor_x = 50
        self.cursor_y = 50
        self.entry = None
        self.penwidth = 20
        self.suggestion = StringVar()
        self.suggestion.set("")
        self.suggest_label = None
        self.c = None #painting canvas
        self.p = None #color pallete
        self.drawWidgets()
        self.adaptRGB(self.emotion)
        self.c.bind('<B1-Motion>', self.paint) #drawing the line 
        self.c.bind('<ButtonRelease-1>', self.reset)

    def activate(self):
        self.isActive = True

    def deactivate(self):
        self.isActive = False

    def paint(self, e):
        if self.isActive:
            if self.old_x and self.old_y:
                line_id = self.c.create_line(self.old_x,self.old_y,e.x,e.y,width=int(self.penwidth),fill=self.color_fg,capstyle=ROUND,smooth=True)
                self.recent_line.append(line_id)
            self.old_x = e.x
            self.old_y = e.y


    def gesture_paint(self, x, y):
        if self.isActive:
            if self.old_x and self.old_y:
                line_id = self.c.create_line(self.old_x,self.old_y,x,y,width=int(self.penwidth),fill=self.color_fg,capstyle=ROUND,smooth=True)
                self.recent_line.append(line_id)
            self.old_x = x
            self.old_y = y

    def create_cursor(self):
        dim = int(self.penwidth)//2
        self.cursor = self.c.create_oval(self.cursor_x-dim, self.cursor_y-dim, self.cursor_x + dim, self.cursor_y + dim, outline=self.color_fg, width=4)
    
    def move_cursor_to(self, x, y):
        if self.isActive:
            if self.cursor != None and self.c != None:
                dx = x - self.cursor_x
                dy = y - self.cursor_y
                self.c.move(self.cursor, dx, dy)
                self.c.tag_raise(self.cursor)
                self.cursor_x = x
                self.cursor_y = y
    
    def fill_cursor(self):
        self.c.itemconfig(self.cursor, fill=self.color_fg, outline=self.color_fg, width = 4)

    def empty_cursor(self):
        self.c.itemconfig(self.cursor, fill=self.color_bg, outline=self.color_fg, width = 4)

    def reset(self, e = None): #finishing a stroke
        self.old_x = None
        self.old_y = None
        if len(self.recent_line) > 0:
            self.all_lines.append(self.recent_line)
            self.recent_line = []
    
    def undo(self):
        if self.isActive and len(self.all_lines) > 0:
            undo_line = self.all_lines.pop()
            for id in undo_line:
                self.c.delete(id)
           
    def clear(self):
        if self.isActive:
            self.c.delete(ALL)
            self.create_cursor()
            self.suggestion.set("")

    def change_fg(self, color = None):  #changing the pen color
        if self.isActive:
            if color is None:
                self.color_fg = colorchooser.askcolor(color=self.color_fg)[1]
                self.color_custom = self.color_fg
                self.custom_square.config(bg=self.color_custom, activebackground=self.color_custom)
            else: 
                self.color_fg = color
                self.empty_cursor()

    def change_bg(self):  #changing the background color canvas
        if self.isActive:
            self.color_bg = colorchooser.askcolor(color=self.color_bg)[1]
            self.c['bg'] = self.color_bg

    def adaptRGB(self, emotionName):
        if emotionName == 'happy':
            r, g, b = emotionsToRGB[emotionName] #yellow
        else:
            r, g, b  = emotionsToRGB['neutral'] #deep sky blue 2

        dr, db, dg = 0, 0, 0
        if r != self.rgb[0]:
            dr = 4 if self.rgb[0] < r else -4
        if g != self.rgb[1]:
            dg = 4 if self.rgb[1] < g else -4
        if b != self.rgb[2]:
            db = 4 if self.rgb[2] < b else -4

        red1, green1, blue1, = self.rgb
        red2, green2, blue2 = red1 +  dr, green1 + dg, blue1 + db
        color = '#{:02x}{:02x}{:02x}'.format(red2, green2, blue2)
        self.rgb = (red2, green2, blue2)
        self.config(bg=color)
        self.suggest_label.config(bg=color)

    def adaptMusic(self, emotion):
        if emotion in {'happy', 'neutral'}:
            if self.emotion != emotion:
                self.emotion = emotion
                if mixer_music.get_busy():
                    mixer_music.fadeout(500)
            else:
                if mixer_music.get_volume() <= .95:
                    mixer_music.set_volume(mixer_music.get_volume() + 0.019)
                if not mixer_music.get_busy():
                    mixer_music.set_volume(0)
                    if emotion == 'happy':
                        mixer_music.load("lib/happy.mp3")
                    else:
                        mixer_music.load("lib/neutral.mp3")
                    # mixer_music.play()

    def generate_suggestion(self):
        if self.isActive:
            suggestions = ["Flower", "Happy Face", "Superhero", "Dog", "Cat"]
            new_suggestion = "Draw a " + random.choice(suggestions)
            while new_suggestion == self.suggestion.get():
                new_suggestion = "Draw a " + random.choice(suggestions)
            self.suggestion.set(new_suggestion)

    def save(self):
        if self.isActive:
            self.c.itemconfig(self.cursor, state='hidden')
            ps = self.c.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img.save('drawing.jpg', 'jpeg')
            self.c.itemconfig(self.cursor, state='normal')
            Image.open('drawing.jpg').show()
    
    def change_penwidth(self, e=None, size="20"):
        if self.isActive:
            if e != None:
                self.penwidth = int(self.entry.get())
            else:
                self.penwidth = int(size)
                self.entry.delete(0, END)
                self.entry.insert(0, str(size))
            self.focus()
            self.c.delete(self.cursor)
            self.create_cursor()
            return True

    def drawWidgets(self):
        """ Setting up the canvas and color pallete widgets. """
        c_width = int(self.controller.winfo_screenwidth()*.7)
        c_height = int(self.controller.winfo_screenheight()*.75)
        self.c = Canvas(self, width=c_width, height=c_height, bg=self.color_bg, cursor="circle")
        self.create_cursor()
        self.c.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.suggest_label = Label(self, textvariable = self.suggestion, font=('arial 20'))
        self.suggest_label.pack(side=TOP)

        p_width = int(self.controller.winfo_screenwidth()*.075)
        p_height = int(self.controller.winfo_screenheight()*.75)
        self.p = Frame(self, bg=BROWN_PALLETE, width=p_width, height=p_height)
        square_width = 8
        square_height= 4
        brush_label = Label(self.p,  text="Brush Size", font=('arial 12'), bg=BROWN_PALLETE)
        brush_label.grid(row=0, column=1, pady=2, padx=2)
        self.entry = Entry(self.p, font=('arial 12'), width=3)
        self.entry.insert(0, str(self.penwidth))
        self.entry.bind("<Return>", self.change_penwidth)
        self.entry.grid(row=0, column=2, pady=2, padx=2)
        red_square = Button(self.p, width=square_width, height=square_height, command=lambda: self.change_fg(RED), bg=RED, activebackground=RED, text="Red", font=('arial 12'))
        red_square.grid(row=1, column=1, columnspan=2, pady=2)
        orange_square = Button(self.p, width=square_width, height=square_height, command=lambda: self.change_fg(ORANGE), bg=ORANGE, activebackground=ORANGE, text="Orange", font=('arial 12'))
        orange_square.grid(row=2, column=1, columnspan=2, pady=2)
        yellow_square = Button(self.p, width=square_width, height=square_height, command=lambda: self.change_fg(YELLOW), bg=YELLOW, activebackground=YELLOW, text="Yellow", font=('arial 12'))
        yellow_square.grid(row=3, column=1, columnspan=2, pady=2)
        green_square = Button(self.p, width=square_width, height=square_height, command=lambda: self.change_fg(GREEN), bg=GREEN, activebackground=GREEN, text="Green", font=('arial 12'))
        green_square.grid(row=4, column=1, columnspan=2, pady=2)
        blue_square = Button(self.p, width=square_width, height=square_height, command=lambda: self.change_fg(BLUE), bg=BLUE, activebackground=BLUE, text="Blue", font=('arial 12'))
        blue_square.grid(row=5, column=1, columnspan=2, pady=2)
        purple_square = Button(self.p, width=square_width, height=square_height, command=lambda: self.change_fg(PURPLE), bg=PURPLE, activebackground=PURPLE, text="Purple", font=('arial 12'))
        purple_square.grid(row=6, column=1, columnspan=2, pady=2)
        self.custom_square = Button(self.p, width=square_width, height=square_height, command=lambda: self.change_fg(self.color_custom), bg=self.color_custom, activebackground=self.color_custom, text="Custom", font=('arial 12'))
        self.custom_square.grid(row=7, column=1, columnspan=2, pady=2)
        eraser = Button(self.p, width=square_width, height=square_height, command=lambda: self.change_fg("white"), bg="white", activebackground="white", text="Eraser", font=('arial 12'))
        eraser.grid(row=8, column=1, columnspan=2, pady=2)
        self.p.pack(side=RIGHT)

def label_image(model, img):
    x = np.expand_dims(image.img_to_array(img), axis = 0)/255
    custom = model.predict(x)
    return emotions[custom[0].tolist().index(max(custom[0]))]

def mm_to_px(screenWidth, screenHeight, position):
    x, y, z = position
    x = screenWidth/250*(x+80)
    y = screenHeight - screenHeight/140*(y-50)
    return x, y, z

def is_in_bounds(position):
    return position[0] >= -100 and position[0] <= 150 and position[1] >= 60 and position[1] <= 200

def run():
    app = ArtStudioApp()
    canvasPage = app.frames[CanvasPage]
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    #Setup Speech Multithreading
    speech_callback_queue = queue.Queue()

    def speech_callback(recognizer, audio):
        '''
        Callback function for when audio is heard on separate thread.
        Uses Google Speech recognition to translate audio to text and the text is then
        parsed for keywords.
        '''
        print("Audio received")
        try:
            spoken = recognizer.recognize_google(audio).lower()
            print("You said: " + spoken)
            words = spoken.split()
            if "red" in words:
                func = lambda: canvasPage.change_fg(RED)
                speech_callback_queue.put(func)
            elif "blue" in words:
                func = lambda: canvasPage.change_fg(BLUE)
                speech_callback_queue.put(func)
            elif "orange" in words:
                func = lambda: canvasPage.change_fg(ORANGE)
                speech_callback_queue.put(func)
            elif "green" in words:
                func = lambda: canvasPage.change_fg(GREEN)
                speech_callback_queue.put(func)
            elif "yellow" in words:
                func = lambda: canvasPage.change_fg(YELLOW)
                speech_callback_queue.put(func)
            elif "purple" in words:
                func = lambda: canvasPage.change_fg(PURPLE)
                speech_callback_queue.put(func)
            elif "black" in words:
                func = lambda: canvasPage.change_fg('black')
                speech_callback_queue.put(func)
            elif "eraser" in words:
                func = lambda: canvasPage.change_fg('white')
                speech_callback_queue.put(func)
            elif all(item in ['what', 'should', 'i', 'draw'] for item in words) or \
                    all(item in ['new', 'suggestion'] for item in words):
                func = lambda: canvasPage.generate_suggestion()
                speech_callback_queue.put(func)
            elif "brush" in words and "size" in words:
                prior = words.index("size")
                try:
                    size = words[prior+1]
                    func = lambda: canvasPage.change_penwidth(size=size)
                    speech_callback_queue.put(func)
                except IndexError:
                    pass
            elif "change" in words and "custom" in words and "color" in words:
                func = lambda: canvasPage.change_fg()
                speech_callback_queue.put(func)
            elif "custom" in words:
                func = lambda: canvasPage.change_fg(canvasPage.color_custom)
                speech_callback_queue.put(func)
            elif "clear" in words and "canvas" in words:
                func = lambda: canvasPage.clear()
                speech_callback_queue.put(func)
            elif "undo" in words:
                speech_callback_queue.put(canvasPage.undo)
            elif "save" in words:
                speech_callback_queue.put(canvasPage.save)
            elif "quit" in words or "exit" in words or "close" in words:
                speech_callback_queue.put(canvasPage.master.destroy)
            elif "home" in words:
                speech_callback_queue.put(lambda: app.show_frame(MainPage))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    #Setup Speech Recognition
    r = sr.Recognizer()
    r.energy_threshold = 8000
    m = sr.Microphone()
    with m as source:
        r.adjust_for_ambient_noise(source)
    stop_listening = r.listen_in_background(m, speech_callback, phrase_time_limit=3)
    # stop_listening = listen_in_background(r, m, speech_callback, phrase_time_limit=3)

    #Setup Emotion Recogntion
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    video_capture = app.vs
    emotionStore = {}
    emotionCount = 0

    #Setup Speech Recognition
    store = []

    #Setup Audio
    pygame.init()
    mixer_music.load("lib/neutral.mp3")
    # mixer_music.play()

    #Main loop
    while True:
        try:
            # Capture frame-by-frame
            ret, frame = video_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                
                #Crop, Resize, Gray, & Reshape Image
                cropped_img = frame[y:y+h, x:x+w].copy()
                resized_img = cv2.resize(src=cropped_img, dsize=(48, 48), interpolation=cv2.INTER_AREA)
                grayed_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
                reshaped_img = grayed_img.reshape((48, 48, 1))

                label = label_image(model, reshaped_img)
                emotionStore[label] = emotionStore.get(label, 0) + 1
                emotionCount += 1
                if emotionCount >= 100:
                    prevalent = max(emotionStore, key=lambda key: emotionStore[key])
                    canvasPage.adaptRGB(prevalent)
                    canvasPage.adaptMusic(prevalent)
                    emotionStore = {}
                    emotionCount = 0
                else:
                    canvasPage.adaptRGB(canvasPage.emotion)
                    canvasPage.adaptMusic(canvasPage.emotion)

            #Get Gesture Data each frame
            hand = getLeapFrame().hands[0]
            pointer_position_mm = list(hand.palm_pos)
            
            if pointer_position_mm != [0, 0, 0] and is_in_bounds(pointer_position_mm):
                x, y, z = mm_to_px(screen_width,screen_height,pointer_position_mm)
                store.append((x,y,z))
                if len(store) >= 1:
                    avg_x = sum([a[0] for a in store])/len(store)
                    avg_y = sum([a[1] for a in store])/len(store)
                    avg_z = sum([a[2] for a in store])/len(store)

                    canvasPage.move_cursor_to(avg_x, avg_y)

                    if avg_z <= 0:
                        canvasPage.gesture_paint(avg_x, avg_y)
                        canvasPage.fill_cursor()
                    else:
                        canvasPage.reset()
                        canvasPage.empty_cursor()

                    store = []

            #Try for a callback from speech recognition
            try:
                callback = speech_callback_queue.get(False) #doesn't block
                callback()
            except queue.Empty: #raised when queue is empty
                pass

            #Update App
            app.update_idletasks()
            app.update()

            sleep(0.01)

        except TclError: #Error raised when attempting to quit
            break

    # When everything is done, release the capture
    video_capture.release()
    # cv2.destroyAllWindows()

    #Stop background threads
    stop_listening(wait_for_stop=False)

if __name__ == '__main__':
    run()