from tkinter import *
from tkinter import ttk, colorchooser, PhotoImage
import pyautogui

import sys, os
sys.path.insert(0, os.path.abspath('..\pyleap'))

from time import sleep
import numpy as np

from pyleap.leap import getLeapInfo, getLeapFrame

class main:
    def __init__(self, master):
        self.master = master
        self.color_fg = 'black'
        self.color_bg = 'white'
        self.old_x = None
        self.old_y = None
        self.penwidth = 5
        self.drawWidgets()
        self.c.bind('<B1-Motion>', self.paint) #drawing the line 
        self.c.bind('<ButtonRelease-1>', self.reset)

    def paint(self, e):
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x,self.old_y,e.x,e.y,width=self.penwidth,fill=self.color_fg,capstyle=ROUND,smooth=True)
        self.old_x = e.x
        self.old_y = e.y

    def gesture_paint(self, x, y):
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x,self.old_y,x,y,width=self.penwidth,fill=self.color_fg,capstyle=ROUND,smooth=True)
        self.old_x = x
        self.old_y = y

    def reset(self, e):    #reseting or cleaning the canvas 
        self.old_x = None
        self.old_y = None   

    def gesture_reset(self):
        self.old_x = None
        self.old_y = None    

    def changeW(self,e): #change Width of pen through slider
        self.penwidth = e
           
    def clear(self):
        self.c.delete(ALL)

    def change_fg(self):  #changing the pen color
        self.color_fg = colorchooser.askcolor(color=self.color_fg)[1]

    def change_bg(self):  #changing the background color canvas
        self.color_bg = colorchooser.askcolor(color=self.color_bg)[1]
        self.c['bg'] = self.color_bg

    def drawWidgets(self):
        self.controls = Frame(self.master,padx = 5,pady = 5)
        Label(self.controls, text='Pen Width:',font=('arial 18')).grid(row=0,column=0)
        # self.slider = ttk.Scale(self.controls,from_= 5, to = 100,command=self.changeW,orient=VERTICAL)
        # self.slider.set(self.penwidth)
        # self.slider.grid(row=0,column=1,ipadx=30)
        self.controls.pack(side=LEFT)
        
        self.c = Canvas(self.master,width=800,height=600,bg=self.color_bg, cursor="circle")
        self.c.pack(fill=BOTH,expand=True)

        menu = Menu(self.master)
        self.master.config(menu=menu)
        filemenu = Menu(menu)
        colormenu = Menu(menu)
        menu.add_cascade(label='Colors',menu=colormenu)
        colormenu.add_command(label='Brush Color',command=self.change_fg)
        colormenu.add_command(label='Background Color',command=self.change_bg)
        optionmenu = Menu(menu)
        menu.add_cascade(label='Options',menu=optionmenu)
        optionmenu.add_command(label='Clear Canvas',command=self.clear)
        optionmenu.add_command(label='Exit',command=self.master.destroy)

def mm_to_px(screenWidth, screenHeight, position):
    x, y, z = position
    x = screenWidth/400*(x+200)
    y = screenHeight - screenHeight/250*(y-50)
    return x, y, z

def is_in_bounds(position):
    return position[0] >= -200 and position[0] <= 200 and position[1] >= 50 and position[1] <= 300

def run():
    root = Tk()
    activity = main(root)
    root.title('Art Studio')
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    store = []
    # cursor = PhotoImage(file="lib\cursor.jpg")

    while True:
        # get new data each frame
        info = getLeapInfo()
        hand = getLeapFrame().hands[0]
        pointer_position_mm = list(hand.palm_pos)

        # if pointer_position_mm != [0, 0, 0]:
        #     pyautogui.moveTo(x,y)
        if pointer_position_mm != [0, 0, 0] and is_in_bounds(pointer_position_mm):
            print(pointer_position_mm)
            x, y, z = mm_to_px(screen_width,screen_height,pointer_position_mm)
            store.append((x,y,z))
            if len(store) >= 4:
                avg_x = sum([a[0] for a in store])/len(store)
                avg_y = sum([a[1] for a in store])/len(store)
                avg_z = sum([a[2] for a in store])/len(store)

                pyautogui.moveTo(avg_x,avg_y)
                print(avg_x, avg_y, pyautogui.position())
                if avg_z <= -50:
                    activity.gesture_paint(avg_x, avg_y)
                else:
                    activity.gesture_reset()

                store = []

        # status text
        # status = 'service:{} connected:{} focus:{}  '.format(*[('NO ', 'YES')[x] for x in info])
        # print(status)

        #Update canvas
        root.update_idletasks()
        root.update()

        sleep(0.01)

if __name__ == '__main__':
    run()