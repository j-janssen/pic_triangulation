import Triangulation
import math
import random
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image       #for image input
import os                   #for image input - image path
import drawSvg as draw      #for image output

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
        t_pts_X = np.round(np.linspace(0,self.pic_width -1, 100)) 
        t_pts_Y = np.round(np.linspace(0,self.pic_height -1, 100))
        self.train_pts = np.array([[
                                [int(x),int(y),self.rgb_pic.getpixel((x, y))[0],self.rgb_pic.getpixel((x, y))[1],self.rgb_pic.getpixel((x, y))[2]]
                                for x in t_pts_X] for y in t_pts_Y])
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
        for stepp in tqdm(range(max_iteration)):
            x = random.randint(0,99)
            y = random.randint(0,99)
            self.train_pts[y][x]
            k,l = self.get_winner(self.train_pts[y][x])
            for i in range(1,self.fineness-1):
                for j in range(1,self.fineness-1):
                    if(self.dist_fct(self.get_dist([i,j],[k,l]), rad) != 0):
                        self.weights[i][j] += learn_rate * np.subtract( self.train_pts[y][x] ,self.weights[i][j]) * self.dist_fct(abs(i-k)+abs(j-l), rad)
                rad = rad * 0.9999

    def gen_image(self,abs_file_path):
        D = Triangulation.Triangle(-1, -1, self.pic_width +1, self.pic_height+1, -1, self.pic_height+1)
        D.initialize(D, self.pic_height, self.pic_width)
        D.re_delaunay_prop(D)
        for i in range(0,99,10):
            for j in range(0,99,10):
                if(self.get_winner(self.train_pts[i][j]) != self.get_winner(self.train_pts[i][j+1])):
                    D.add_point(self.train_pts[i][j][0],self.train_pts[i][j][1],D)
                    D.re_delaunay_prop(D)
                if(self.get_winner(self.train_pts[j][i]) != self.get_winner(self.train_pts[j+1][i])):
                    D.add_point(self.train_pts[j][i][0],self.train_pts[j][i][1],D)
                    D.re_delaunay_prop(D)

        d = draw.Drawing(self.pic_width, self.pic_height, origin='center', displayInline=False)
        w = (self.pic_width -1)/2
        h = (self.pic_height -1)/2
        for y in range(99):
            for x in range(99):
                if(D.get_triangle_via_point(self.train_pts[x][y][0]+1,self.train_pts[x][y][1]+1 ,D)):
                    x1, x2, y1,y2, z1,z2 = D.get_triangle_via_point(self.train_pts[x][y][0]+1,self.train_pts[x][y][1]+1 ,D)
                    k,l = self.get_winner(self.train_pts[x][y])
                    if(x1 < 0):
                        x1 = 0
                    if(y1 < 0):
                        y1 = 0
                    if(z1 < 0):
                        z1 = 0
                    if(x2 < 0):
                        x2 = 0
                    if(y2 < 0):
                        y2 = 0
                    if(z2 < 0):
                        z2 = 0
                    if(x1 > self.pic_width):
                        x1 = self.pic_width
                    if(y1 > self.pic_width):
                        y1 = self.pic_width
                    if(z1 > self.pic_width):
                        z1 = self.pic_width
                    if(x2 > self.pic_height):
                        x2 = self.pic_height
                    if(y2 > self.pic_height):
                        y2 = self.pic_height
                    if(z2 > self.pic_height):
                        z2 = self.pic_height
                    d.append(draw.Lines(int(x1-w),int(h-x2),
                                        int(y1-w),int(h-y2),
                                        int(z1-w),int(h-z2),
                                        int(x1-w),int(h-x2),
                                        close=False,
                                        fill='#%02x%02x%02x' % (int(self.weights[k][l][2]),int(self.weights[k][l][3]),int(self.weights[k][l][4])) ,
                                        ))
        d.setPixelScale(1)
        d.saveSvg(abs_file_path[0:-4] + '_pt.svg')   #is saved in home directory
        d.savePng(abs_file_path[0:-4] + '_pt.png')   #is saved in home directory

            
rel_path = input('Please type your relative path of your picture! Exp: Images/test_pic_01.jpg : ')
script_dir = os.path.dirname(__file__) 
abs_file_path = os.path.join(script_dir, rel_path)
fineness = 10
max_iteration = 100000
lear_rate = 0.001
print('Preprocessing starts!')


NN = SOM(abs_file_path, fineness)
NN.training(max_iteration, lear_rate)
NN.gen_image(abs_file_path)

