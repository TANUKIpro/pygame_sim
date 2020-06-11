# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, "..")
from socket import socket, AF_INET, SOCK_STREAM
import pygame
from pygame.locals import *
from pgu import gui

class Communicater:
    def __init__(self):
        self.HOST        = 'localhost'
        self.PORT        = 51000
        self.MAX_MESSAGE = 2048
        self.NUM_THREAD  = 4

        self.CHR_CAN     = '\18'
        self.CHR_EOT     = '\04'

    def com_send(self, message):
            try:
                sock = socket(AF_INET, SOCK_STREAM)
                sock.connect((self.HOST, self.PORT))
                sock.send(message.encode('utf-8'))
                #sock.send(self.mess)
                print("SEND MESSAGE:",message)
                sock.close()
            except:
                print ("ERROR :: The receiving process is not started.")

    def exit(self):
        self.com_send("SEND:EXIT")
        self.com_send(self.CHR_EOT)

    def cancel(self):
        self.com_send(self.CHR_CAN)

comm = Communicater()
class Counter:
    def __init__(self, num):
        self.num=num
        self.n = 0
    def swc_cb(self):
        self.n += 1
        if self.n%2==0:
            msg = str(self.num)+"_False"
            comm.com_send(msg)
            print(msg)
        else:
            msg = str(self.num)+"_True"
            comm.com_send(msg)
            print(msg)

class GUI_drawer:
    def __init__(self):
        self.app = gui.Desktop()
        self.app.connect(gui.QUIT, self.app.quit,None)
        self.c = gui.Table()

    def check_box(self, box_name, num):
        self.c.tr()
        self.c.td(gui.Label(box_name))
        swc = gui.Switch(False)

        self.c.td(swc, colspan=10)
        counter = Counter(num)
        swc.connect(gui.CLICK, counter.swc_cb)

    def gui_draw(self, box_names):
        self.c.tr()
        self.c.td(gui.Label("Gui Widgets"),colspan=4)

        for num, name in enumerate(box_names):
            self.check_box(name, num)

    def run(self):
        self.app.run(self.c)

names_list = ["Index.Metacarpal", "Index.Proximal_Phalanx", "Index.Middle_Phalanxh", "Index.Distal_Phalanxh"]
def main():
    ch_gui = GUI_drawer()
    ch_gui.gui_draw(names_list)
    ch_gui.run()
    
    comm.exit()

if __name__=="__main__":
    main()
