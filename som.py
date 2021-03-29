# ----------------------------------------------------------------------------------------------------
# Self Organizing Map 
# Idee - unüberwachtes Lernen - Pixel Punkt Zuordnung - basierend darauf Dreiecke bilden
# ----------------------------------------------------------------------------------------------------


import math
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image       #for image input
import os                   #for image input - image path
import drawSvg as draw      #for image output

# ----------------------------------------------------------------------------------------------------
# NN - Klasse
# Soll Gewichte Speichern und sich trainieren lassen

class SOM(object):

    def __init__(self, pic_path, fineness):
        im = Image.open(pic_path)
        self.pic_width, self.pic_height = im.size
        self.pic_width = int(self.pic_width) -1
        self.pic_height = int(self.pic_height) -1
        self.rgb_pic = im.convert('RGB')
        X = np.round(np.linspace(0,self.pic_width -1, fineness))
        Y = np.round(np.linspace(0,self.pic_height -1 , fineness))
        self.weights = np.array([[
                                [x,y,self.rgb_pic.getpixel((x, y))[0],self.rgb_pic.getpixel((x, y))[1],self.rgb_pic.getpixel((x, y))[2]]
                                for x in X] for y in Y])
        self.fineness = fineness

    def get_dist(self, A, B):
        dist = abs(A[0] - B[0]) + abs(A[1]-B[1]) 
        temp = min(abs(B[0]-A[0]), abs(B[1]-A[1]))
        dist = dist - 0.5 * abs(np.sign(B[0]-A[0]) * temp - np.sign(B[1]-A[1])* temp)
        return dist

    def get_winner(self, point):
        k,l = (0,0)
        min = np.linalg.norm(np.subtract(point, self.weights[0][0]))
        for i in range(self.fineness):
            for j in range(self.fineness):
                temp = np.linalg.norm(np.subtract(point, self.weights[i][j]))
                if(temp < min):
                    min = temp
                    k,l = (i,j)
        return (k,l)

    def dist_fct(self, dist, rad):
        if(dist > rad): 
            return 0
        else:
            return 1- dist/rad

    def training(self, max_iteration, learn_rate):
        rad = 3
        max_iteration = max_iteration
        for stepp in range(max_iteration):
            if((stepp/max_iteration *100) % 10 == 0):
                print("Das Training ist zu " + str(stepp/ max_iteration *100) + "% beendet!")
            x = random.randint(0,self.pic_height -1)
            y = random.randint(0, self.pic_width -1)
            r,g,b = self.rgb_pic.getpixel((y,x))
            point = np.array([y,x,r,g,b])
            k,l = self.get_winner(point)
            for i in range(self.fineness):
                for j in range(self.fineness):
                    if(self.dist_fct(self.get_dist([i,j],[k,l]), rad) != 0):
                        self.weights[i][j] += learn_rate * np.subtract( point ,self.weights[i][j]) * self.dist_fct(abs(i-k)+abs(j-l), rad)
                rad = rad * 0.9999
        print("Das Training ist abgeschlossen!")

    def gen_image(self):
        d = draw.Drawing(self.pic_width, self.pic_height, origin='center', displayInline=False)
        w = (self.pic_width -1)/2
        h = (self.pic_height -1)/2
        for y in range(self.fineness -1):
            for x in range(self.fineness -1):
                d.append(draw.Lines(int(w-self.weights[x][y][0]),int(h-self.weights[x][y][1]),
                                    int(w-self.weights[x+1][y][0]),int(h-self.weights[x+1][y][1]),
                                    int(w-self.weights[x][y+1][0]),int(h-self.weights[x][y+1][1]),
                                    int(w-self.weights[x][y][0]),int(h-self.weights[x][y][1]),
                                    close=False,
                                    fill='#%02x%02x%02x' % (int(self.weights[x][y][2]),int(self.weights[x][y][3]),int(self.weights[x][y][4])) ,
                                    ))
        for y in range(1,self.fineness):
            for x in range(1,self.fineness):
                d.append(draw.Lines(int(w-self.weights[x][y][0]),int(h-self.weights[x][y][1]),
                                    int(w-self.weights[x-1][y][0]),int(h-self.weights[x-1][y][1]),
                                    int(w-self.weights[x][y-1][0]),int(h-self.weights[x][y-1][1]),
                                    int(w-self.weights[x][y][0]),int(h-self.weights[x][y][1]),
                                    close=False,
                                    fill='#%02x%02x%02x' % (int(self.weights[x][y][2]),int(self.weights[x][y][3]),int(self.weights[x][y][4])) ,
                                    ))
        d.setPixelScale(1)
        d.saveSvg('test.svg')   #is saved in home directory
        d.savePng('test.png')   #is saved in home directory


            
# ----------------------------------------------------------------------------------------------------
# Interface - Ein paar Abfragen bevor es startet

print('Das Neuronale Netz baut sich auf. Aber vorab brauchen wir noch ein paar Infos.')
rel_path = input('Eingabe von dem Bildpfad - Bsp.: Images/test.jpg : ')
script_dir = os.path.dirname(__file__) 
abs_file_path = os.path.join(script_dir, rel_path)
fineness = int(input('Eingabe von der Netzfeinheit: - Bsp.: 20 : '))
max_iteration = int(input('Eingabe von der Trainingsanzahl - Bsp.: 50000 : '))
lear_rate = float(input('Eingabe von der Lernrate - Bsp.: 0.1 : '))
print('Nun gehts los! :)')

# ----------------------------------------------------------------------------------------------------
# Ausführung

NN = SOM(abs_file_path, fineness)
NN.training(max_iteration, lear_rate)
NN.gen_image()

