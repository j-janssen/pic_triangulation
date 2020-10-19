# ----------------------------------------------------------------------------------------------------
# Self Organizing Map 
# Idee - unüberwachtes Lernen - Pixel Punkt Zuordnung - basierend darauf Dreiecke bilden
# ----------------------------------------------------------------------------------------------------


import math
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def sgn(x):
    if(x < 0):
        return -1
    else: 
        return 1

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
        self.weights = np.array([[[x,y,self.rgb_pic.getpixel((x, y))[0],self.rgb_pic.getpixel((x, y))[1],self.rgb_pic.getpixel((x, y))[2]] for x in X] for y in Y] )
        self.fineness = fineness

    def plot(self):
        for i in range(self.fineness-1):
            for j in range(self.fineness -1 ):
                plt.plot([self.weights[i][j][0], self.weights[i][j+1][0]], [self.weights[i][j][1], self.weights[i][j+1][1]], 'ro-' , markersize = 2)
                plt.plot([self.weights[i][j][0], self.weights[i+1][j][0]], [self.weights[i][j][1], self.weights[i+1][j][1]], 'ro-' , markersize = 2)
            plt.plot([self.weights[i][self.fineness-1][0], self.weights[i+1][self.fineness-1][0]], [self.weights[i][self.fineness-1][1], self.weights[i+1][self.fineness-1][1]], 'ro-' , markersize = 2)
        for j in range(self.fineness -1 ):
                plt.plot([self.weights[self.fineness-1][j][0], self.weights[self.fineness-1][j+1][0]], [self.weights[self.fineness-1][j][1], self.weights[self.fineness-1][j+1][1]], 'ro-' , markersize = 2)
        for i in range(1,self.fineness): 
            for j in range(i):
                plt.plot([self.weights[i-j][j][0], self.weights[i-(j+1)][j+1][0]], [self.weights[i-j][j][1], self.weights[i-(j+1)][j+1][1]], 'ro-' , markersize = 2)
        for i in range(1,self.fineness): 
            for j in range(self.fineness-1-i):
                plt.plot([self.weights[self.fineness-1-j][i+j][0], self.weights[self.fineness-1-(j+1)][i+j+1][0]], [self.weights[self.fineness-1-j][i+j][1], self.weights[self.fineness-1-(j+1)][i+j+1][1]], 'ro-' , markersize = 2)
        plt.xlabel('x-Achse')
        plt.ylabel('y-Achse')
        plt.title('SOM')
        plt.show()

    def in_triangle(self, point, A, B, C):
        return ((np.dot(np.array([(B-A)[1],(A-B)[0]]), point -A) > 0) and (np.dot(np.array([(C-B)[1],(B-C)[0]]), point -B) > 0) and (np.dot(np.array([(A-C)[1],(C-A)[0]]), point -C) > 0)) or ((np.dot(np.array([(B-A)[1],(A-B)[0]]), point -A) < 0) and (np.dot(np.array([(C-B)[1],(B-C)[0]]), point -B) < 0) and (np.dot(np.array([(A-C)[1],(C-A)[0]]), point -C) < 0)) 

    def get_color(self, point):
        for i in range(self.fineness -2):
            j = 0
            if(self.in_triangle(point, np.array([self.weights[i][j][0],self.weights[i][j][1]]), np.array([self.weights[i][j+1][0],self.weights[i][j+1][1]]), np.array([self.weights[i+1][j][0],self.weights[i+1][j][1]]))):
                return (self.weights[i][j][2],self.weights[i][j][3],self.weights[i][j][4])
            j = self.fineness -2
            if(self.in_triangle(point,  np.array([self.weights[i][j][0],self.weights[i][j][1]]), np.array([self.weights[i+1][j][0],self.weights[i+1][j][1]]) , np.array([self.weights[i+1][j-1][0],self.weights[i+1][j-1][1]]))):
                return (self.weights[i][j][2],self.weights[i][j][3],self.weights[i][j][4])
            for j in range(1,self.fineness -2):
                if(self.in_triangle(point, np.array([self.weights[i][j][0],self.weights[i][j][1]]), np.array([self.weights[i][j+1][0],self.weights[i][j+1][1]]), np.array([self.weights[i+1][j][0],self.weights[i+1][j][1]])) or self.in_triangle(point,  np.array([self.weights[i][j][0],self.weights[i][j][1]]), np.array([self.weights[i+1][j][0],self.weights[i+1][j][1]]) , np.array([self.weights[i+1][j-1][0],self.weights[i+1][j-1][1]]))):
                    return (self.weights[i][j][2],self.weights[i][j][3],self.weights[i][j][4])
        return (0,0,0)

    def gen_image(self):
        data = np.zeros((self.pic_height, self.pic_width, 3), dtype= np.uint8)
        for x in range(self.pic_height -1):
            for y in range(self.pic_width -1):
                data[x][y] = self.get_color(np.array([y,x]))
            if(x/(self.pic_height-1) * 100 % 10 == 0):
                print("Das Bild ist zu " + str(x/(self.pic_height-1) * 100) + "% generiert! ")
        pic = Image.fromarray(data, 'RGB')
        pic.save('my_pic.png')
        pic.show()

    def get_dist(self, A, B):
        dist = abs(A[0] - B[0]) + abs(A[1]-B[1]) 
        temp = min(abs(B[0]-A[0]), abs(B[1]-A[1]))
        dist = dist - 0.5 * abs(sgn(B[0]-A[0]) * temp - sgn(B[1]-A[1])* temp)
        return dist

    def get_winner(self, point):
        k = 0
        l = 0
        min = 3 * 255**2 + self.pic_height**2 + self.pic_width **2
        for i in range(self.fineness):
            for j in range(self.fineness):
                temp = np.linalg.norm(np.subtract(point, self.weights[i][j]))
                if(temp < min):
                    min = temp
                    k = i
                    l = j
        return (k,l)

    def dist_fct(self, dist, rad):
        if(dist > rad): 
            return 0
        else:
            return 1- dist/rad

    def training(self, max_iteration, learn_rate):
        rad = 3
        max_iteration = max_iteration * self.pic_height * self.pic_width
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
            


# ----------------------------------------------------------------------------------------------------
# Test



# ----------------------------------------------------------------------------------------------------
# Bild ist im gleichen Verzeichnis, wie das Python Programm
pic_path = "/home/joerg/Documents/Trainguation/test.jpg"

NN = SOM(pic_path, 20)
NN.training(5, 0.1)
NN.gen_image()
