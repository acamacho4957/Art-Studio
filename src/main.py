#Painting
from tkinter import *
from tkinter import ttk, colorchooser, PhotoImage
from PIL import Image, ImageTk

import sys, os
sys.path.insert(0, os.path.abspath('..\pyleap'))

from time import sleep
import numpy as np

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

        for F in (MainPage, CanvasPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky = NSEW)

        self.menu = Menu(self)
        self.initializeMenu()

        self.show_frame(MainPage)    

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
        self.menu.add_command(label="Undo", command=self.frames[CanvasPage].undo)
        self.menu.add_command(label="Clear Canvas", command=self.frames[CanvasPage].clear)
        self.menu.add_command(label="Save", command=self.frames[CanvasPage].save)
        self.menu.add_command(label="Exit", command=self.destroy)
        # self.menu.add_cascade(label='Colors',menu=colormenu)
        # colormenu.add_command(label='Brush Color',command=self.frames[CanvasPage].change_fg)
        # colormenu.add_command(label='Background Color',command=self.frames[CanvasPage].change_bg)
        # optionmenu = Menu(self.menu)
        # self.menu.add_cascade(label='Options',menu=optionmenu)
        # optionmenu.add_command(label='Clear Canvas',command=self.frames[CanvasPage].clear)
        # optionmenu.add_command(label='Save',command=self.frames[CanvasPage].save)
        # optionmenu.add_command(label='Exit',command=self.destroy)

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

        photo = ImageTk.PhotoImage(file="lib/main_image3.png")
        label_photo = Label(self, image=photo, bg='#{:02x}{:02x}{:02x}'.format(40, 180, 252))
        label_photo.image = photo
        label_photo.pack()

        button1 = Button(self, 
                         text="New Drawing", 
                         font=("Comic Sans MS", 20),
                         bg="white",
                         command=lambda: controller.show_frame(CanvasPage, state="NEW"))
        button1.pack(pady=10)

    def activate(self):
        self.isActive = True

    def deactivate(self):
        self.isActive = False
        self.showContinue() #Once it's been deactivated, all future viewings of frame will have the continue button
    
    def showContinue(self):
        if not self.isContinue:

            button2 = Button(self, 
                             text="Continue Drawing", 
                             font=("Comic Sans MS", 20),
                             bg="white",
                             command=lambda: self.controller.show_frame(CanvasPage, state="CONTINUE"))
            button2.pack()

            self.isContinue = True

class CanvasPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.isActive = False
        self.emotion = 'neutral'
        self.rgb = emotionsToRGB[self.emotion]
        self.color_fg = 'black'
        self.color_bg = 'white'
        self.all_lines = []
        self.recent_line = []
        self.old_x = None
        self.old_y = None
        self.cursor = None
        self.cursor_x = 50
        self.cursor_y = 50
        self.penwidth = 20
        self.controls = None
        self.c = None #painting canvas
        self.p = None #color pallet
        self.drawWidgets()
        self.c.bind('<B1-Motion>', self.paint) #drawing the line 
        self.c.bind('<ButtonRelease-1>', self.reset)

    def activate(self):
        self.isActive = True

    def deactivate(self):
        self.isActive = False

    def paint(self, e):
        if self.isActive:
            if self.old_x and self.old_y:
                line_id = self.c.create_line(self.old_x,self.old_y,e.x,e.y,width=self.penwidth,fill=self.color_fg,capstyle=ROUND,smooth=True)
                self.recent_line.append(line_id)
            else:
                self.recent_line = []
            self.old_x = e.x
            self.old_y = e.y


    def gesture_paint(self, x, y):
        if self.isActive:
            if self.old_x and self.old_y:
                line_id = self.c.create_line(self.old_x,self.old_y,x,y,width=self.penwidth,fill=self.color_fg,capstyle=ROUND,smooth=True)
                self.recent_line.append(line_id)
            else:
                self.recent_line = []
            self.old_x = x
            self.old_y = y

    def create_cursor(self):
        dim = self.penwidth//2
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
    
    def undo(self):
        if self.isActive:
            for id in self.recent_line:
                self.c.delete(id)
            self.recent_line = []

    def changeW(self, e):
        if self.isActive:
            self.penwidth = e
           
    def clear(self):
        if self.isActive:
            self.c.delete(ALL)
            self.create_cursor()

    def change_fg(self, color = None):  #changing the pen color
        if self.isActive:
            if color is None:
                self.color_fg = colorchooser.askcolor(color=self.color_fg)[1]
            else: 
                self.color_fg = color

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

    def save(self):
        if self.isActive:
            self.c.itemconfig(self.cursor, state='hidden')
            ps = self.c.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img.save('drawing.jpg', 'jpeg')
            self.c.itemconfig(self.cursor, state='normal')
            Image.open('drawing.jpg').show()

    def drawWidgets(self):
        # self.controls = Frame(self.master,padx = 5,pady = 5)
        # Label(self.controls, text='Pen Width:',font=('arial 18')).grid(row=0,column=0)
        # # self.slider = ttk.Scale(self.controls,from_= 5, to = 100,command=self.changeW,orient=VERTICAL)
        # # self.slider.set(self.penwidth)
        # # self.slider.grid(row=0,column=1,ipadx=30)
        # self.controls.pack(side=LEFT)
        c_width = int(self.controller.winfo_screenwidth()*.7)
        c_height = int(self.controller.winfo_screenheight()*.75)
        self.c = Canvas(self, width=c_width, height=c_height, bg=self.color_bg, cursor="circle")
        self.create_cursor()
        self.c.place(relx=0.5, rely=0.5, anchor=CENTER)

        p_width = int(self.controller.winfo_screenwidth()*.1)
        p_height = int(self.controller.winfo_screenheight()*.75)
        self.p = Canvas(self, bg=BROWN_PALLETE, width=p_width, height=p_height)
        # red_square = Label(self.p, pady=5, bg=RED)
        # red_square.grid(row=0, column=0, rowspan=2, columnspan=2)
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
    # c_width = int(self.controller.winfo_screenwidth()*.7)
    # c_height = int(self.controller.winfo_screenheight()*.75)
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
                canvasPage.change_fg('red')
            elif "blue" in words:
                canvasPage.change_fg('blue')
            elif "green" in words:
                canvasPage.change_fg('green')
            elif "yellow" in words:
                canvasPage.change_fg('yellow')
            elif "black" in words:
                canvasPage.change_fg('black')
            elif "eraser" in words:
                canvasPage.change_fg('pink')
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
    video_capture = cv2.VideoCapture(0)
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
                print(pointer_position_mm)
                x, y, z = mm_to_px(screen_width,screen_height,pointer_position_mm)
                store.append((x,y,z))
                if len(store) >= 1:
                    avg_x = sum([a[0] for a in store])/len(store)
                    avg_y = sum([a[1] for a in store])/len(store)
                    avg_z = sum([a[2] for a in store])/len(store)

                    canvasPage.move_cursor_to(avg_x, avg_y)

                    if avg_z <= -50:
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