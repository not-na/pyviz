#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pyviz.py
#  
#  Copyright 2016 notna <notna@apparat.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import math
import random
import time

import pyglet
from pyglet.gl import *
from pyglet.window import key

FIELDOFVIEW = 65.0

MOVE_SPEED = 10
VERT_SPEED = 0.15

RES = 1

MIN_X = -10
MAX_X = 10
RES_X = RES

MIN_Z = -10
MAX_Z = 10
RES_Z = RES

COLOR_MIN = 0
COLOR_MAX = 100

WIREFRAME = True
COLORS = False

PRESETS = {"hot_1":"x*z",
           "hot_2":"x+z",
           "hot_3":"x**z",
           "hot_4":"x**2+z**2",
           "hot_5":"x-z",
           "hot_6":"random()",
           "hot_7":"randint(0,10)",
           "hot_8":"sqrt(x**2+z**2)",
           "hot_9":"",
           }

def vec(*args):
    return (GLfloat * len(args))(*args)

def rect_vertices(x,y,sx,sy):
    return [x,y, x+sx,y, x+sx,y+sy, x,y+sy,]

class EqEdit(object):
    def __init__(self,win):
        self.win = win
        self.eq = "x**2+z**2"
        # t= sqrt(x**2+z**2)
        #self.eq = "(1-sqrt(x**2+z**2)**2)*z**(-1/2*sqrt(x**2+z**2)**2)"
        self.eqLabel = pyglet.text.Label(self.eq, font_name='Arial', font_size=18,
            x=100, y=100, anchor_x='center', anchor_y='center',
            color=(0, 0, 0, 255))
        self.batch2d = pyglet.graphics.Batch()
        self.bg = self.batch2d.add(4, GL_QUADS, None,
            "v2f",
            ("c4B/static", [242,241,240,128]*4)
            )
    def on_enter(self):
        #self.eq = ""
        #self.eqLabel.text = self.eq
        self.win.exclusive = False
        self.win.set_exclusive_mouse(self.win.exclusive)
    def on_resize(self,width,height):
        self.bg.vertices = rect_vertices(0,0,width,height)
        self.eqLabel.x = width/2
        self.eqLabel.y = height/2
    def on_text(self,text):
        self.eq+=text
        self.eqLabel.text = self.eq
        print(self.eq)
    def on_text_motion(self,motion):
        if motion == key.MOTION_BACKSPACE:
            self.eq = self.eq[:-1]
            self.eqLabel.text = self.eq
            print(self.eq)
    def draw(self):
        #print("draw2",time.time())
        self.win.graphView.draw()
        self.win.set2d()
        self.batch2d.draw()
        self.eqLabel.draw()

class GraphView(object):
    def __init__(self,win):
        self.win = win
        self.batch2d = pyglet.graphics.Batch()
        self.batch3d = pyglet.graphics.Batch()
        self.coordHelper = self.batch3d.add(6,GL_LINES,None,
            ("v3f/static",[0,0,0, 10,0,0,
                           0,0,0, 0,10,0,
                           0,0,0, 0,0,10,
                           ]),
            ("c3B/static",[255,0,0, 255,0,0,
                           0,255,0, 0,255,0,
                           0,0,255, 0,0,255,
                           ]),
            )
        self.text = pyglet.text.Label("", font_name='Arial', font_size=18,
            x=2, y=20, anchor_x='left', anchor_y='center',
            color=(0, 0, 0, 255))
        #self.arr = [[0 for z in xrange(MIN_Z,MAX_Z,RES_Z)] for x in xrange(MIN_X,MAX_X,RES_X)]
        self.arr = [[random.randint(0,100) for z in xrange(MIN_Z,MAX_Z,RES_Z)] for x in xrange(MIN_X,MAX_X,RES_X)]
        l = len(xrange(MIN_Z,MAX_Z,RES_Z))*len(xrange(MIN_X,MAX_X,RES_X))
        self.mesh = self.batch3d.add(l*4,GL_QUADS,None,
            "v3f/static",
            "c4B/static",
            )
        self.buildMesh()
    def on_enter(self):
        glClearColor(0.5, 0.69, 1.0, 1)
    def on_resize(self,width,height):
        pass
    def draw(self):
        self.win.set3d()
        self.batch3d.draw()
        self.win.set2d()
        self.draw_label()
        self.batch2d.draw()
    def draw_label(self):
        self.text.text = "%.1f FPS pos: (%.2f,%.2f,%.2f) look: (%.2f,%.2f)"%(pyglet.clock.get_fps(),self.win.position[0],self.win.position[1],self.win.position[2],self.win.rotation[0],self.win.rotation[1])
        self.text.draw()
    def calcGraph(self):
        t = time.time()
        g = {}
        g.update(math.__dict__)
        g["random"]=random.random
        g["randint"]=random.randint
        fcompiled = compile(self.win.eqEdit.eq,"<mathematical function>","eval",)
        def f(x,z):
            #try:
            return float(eval(fcompiled,g,{"x":x,"z":z}))
            #except Exception:
            #    return None
        self.arr = [[f(x,z) for z in xrange(MIN_Z,MAX_Z,RES_Z)] for x in xrange(MIN_X,MAX_X,RES_X)]
        tottime = time.time()-t
        print(tottime)
        for r in self.arr:print(r)
        self.buildMesh()
    def buildMesh(self):
        v = []
        c = []
        def color(height):
            if invis:
                return [255,0,0,0]
            elif not COLORS:
                return [0,0,0,255]
            else:
                p = (height-COLOR_MIN)/(COLOR_MAX-COLOR_MIN)
                return [p*255,255-(p*255),0,255]
        def vx(c):
            if c==0:
                return 0.
            elif c>0:
                return float(c*RES_X)
            elif c<0:
                return float(c*RES_X)
        def vz(c):
            if c==0:
                return 0.
            elif c>0:
                return float(c*RES_Z)
            elif c<0:
                return float(c*RES_Z)
        
        for cx in xrange(MIN_X,MAX_X,RES_X):
            for cz in xrange(MIN_Z,MAX_Z,RES_Z):
                x,z = cx,cz
                if self.arr[cx][cz]==None:
                    self.arr[cx][cz]=-1.
                    invis = True
                else:
                    invis = False
                b = [vx(x),self.arr[x][z],vz(z)]
                v.extend(b)
                c.extend(color(b[1]))
                xe = True if x+RES_X<MAX_X else False
                ze = True if z+RES_Z<MAX_Z else False
                if xe:
                    v.extend([vx(x+1),self.arr[x+1][z],vz(z)])
                    c.extend(color(self.arr[x+RES_X][z]))
                else:
                    v.extend(b)
                    c.extend(color(b[1]))
                if xe and ze:
                    v.extend([vx(x+1),self.arr[x+1][z+1],vz(z+1)])
                    c.extend(color(self.arr[x+1][z+1]))
                else:
                    v.extend(b)
                    c.extend(color(b[1]))
                if ze:
                    v.extend([vx(x),self.arr[x][z+1],vz(z+1)])
                    c.extend(color(self.arr[x][z+1]))
                else:
                    v.extend(b)
                    c.extend(color(b[1]))
        print(len(v))
        #print(v)
        self.mesh.vertices = v
        self.mesh.colors = c

class MainWindow(pyglet.window.Window):
    def __init__(self,*args,**kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setup()
        self.position = [0,0,0]
        self.rotation = [0,0]
        self.move = [0,0]
        self.vert = 0
        self.exclusive = False
        self.menu = "edit"
        self.eqEdit = EqEdit(self)
        self.graphView = GraphView(self)
        self.setup()
        self.loadPreset("hot_1")
        self.graphView.calcGraph()
        self.menuEdit()
        self.on_resize(self.width,self.height)
        pyglet.clock.schedule_interval(self.update, 1.0 / 60)
    
    def loadPreset(self,key):
        self.menuEdit()
        self.eqEdit.eq = PRESETS[key]
        self.eqEdit.eqLabel.text = self.eqEdit.eq
        #self.menuMain()
        #self.graphView.calcGraph()
    
    def menuEdit(self):
        print("Enter menu edit")
        self.menu = "edit"
        self.eqEdit.on_enter()
    def menuMain(self):
        print("Enter menu main")
        self.menu = "main"
        self.graphView.on_enter()
    
    def draw_menuMain(self):
        self.graphView.draw()
    def draw_menuEdit(self):
        self.eqEdit.draw()
    
    def on_draw(self):
        self.clear()
        #print("draw",time.time())
        if self.menu == "main":
            self.draw_menuMain()
        elif self.menu == "edit":
            self.draw_menuEdit()
    def on_key_press(self, symbol, modifiers):
        if symbol == key.W and self.menu == "main":
            self.move[0]-=1
        elif symbol == key.S and self.menu == "main":
            self.move[0]+=1
        elif symbol == key.A and self.menu == "main":
            self.move[1]-=1
        elif symbol == key.D and self.menu == "main":
            self.move[1]+=1
        elif symbol == key.LSHIFT and self.menu == "main":
            self.vert-=1
        elif symbol == key.SPACE and self.menu == "main":
            self.vert+=1
        elif symbol == key.TAB and self.menu=="main":
            self.exclusive = not self.exclusive
            self.set_exclusive_mouse(self.exclusive)
        elif symbol == key.ENTER and self.menu=="edit":
            self.menuMain()
            self.graphView.calcGraph()
        elif symbol == key.ESCAPE:
            if self.menu == "main":
                self.menuEdit()
            elif self.menu == "edit":
                self.menuMain()
        if modifiers & key.MOD_ACCEL:
            if symbol == key._1:
                self.loadPreset("hot_1")
            elif symbol == key._2:
                self.loadPreset("hot_2")
            elif symbol == key._3:
                self.loadPreset("hot_3")
            elif symbol == key._4:
                self.loadPreset("hot_4")
            elif symbol == key._5:
                self.loadPreset("hot_5")
            elif symbol == key._6:
                self.loadPreset("hot_6")
            elif symbol == key._7:
                self.loadPreset("hot_7")
            elif symbol == key._8:
                self.loadPreset("hot_8")
            elif symbol == key._9:
                self.loadPreset("hot_9")
            elif symbol == key._0:
                self.loadPreset("hot_0")
            elif symbol == key.C:
                if not self.cinematic:
                    self.startCinematic()
                else:
                    self.stopCinematic()
    def on_text(self,text):
        if self.menu == "edit":
            self.eqEdit.on_text(text)
    def on_text_motion(self,motion):
        if self.menu == "edit":
            self.eqEdit.on_text_motion(motion)
    def on_key_release(self, symbol, modifiers):
        if symbol == key.W and self.move[0]!=0:
            self.move[0] += 1
        elif symbol == key.S and self.move[0]!=0:
            self.move[0] -= 1
        elif symbol == key.A and self.move[1]!=0:
            self.move[1] += 1
        elif symbol == key.D and self.move[1]!=0:
            self.move[1] -= 1
        elif symbol == key.LSHIFT and self.vert!=0:
            self.vert+=1
        elif symbol == key.SPACE and self.vert!=0:
            self.vert-=1
    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive and self.menu == "main":
            m = 0.15
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            x %= 360
            newrot = (x,y)
            self.rotation = newrot
    def on_mouse_drag(self,x,y,dx,dy,buttons,modifiers):
        self.on_mouse_motion(x,y,dx,dy)
    def on_resize(self, width, height):
        self.eqEdit.on_resize(width,height)
        self.graphView.on_resize(width,height)
    
    def update(self,dt):
        speed = MOVE_SPEED
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        dy+=self.vert*VERT_SPEED
        x,y,z = self.position
        newpos = dx+x, dy+y, dz+z
        self.position = newpos
    def get_motion_vector(self):
        if any(self.move):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.move))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if False and self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.move[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.move[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)
    
    def setup(self):
        glClearColor(0.5, 0.69, 1.0, 1)
        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        
        glShadeModel(GL_SMOOTH)
        
        # Shaders
        
        #self.shader = Shader([VERTEX_SHADER],[FRAG_SHADER])
        
        #glBindAttribLocation(self.shader.handle, 9, "mixFactor")
        
        #print(self.shader.linked)
        #self.shader.uniformf("outColor",1.,0.,0.,1.)
        #location = glGetUniformLocation(self.shader.handle,"color_out")
        #glBindFragDataLocation(self.shader.handle, 0, "color_out");
        #glUniform4f(0,1.,0.,0.,1.)
        
        #self.shader.link()
        
        self.lightSetup()
        
        #self.fogSetup()
        return
    def lightSetup(self):
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, vec(0.5,0.5,0.5,1.0))
        
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        
        glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, .5, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
        
        glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
        glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

        #glMaterialfv(GL_FRONT, GL_DIFFUSE, vec(0.8, 0.8, 0.8, 1))
        #glMaterialfv(GL_FRONT, GL_SPECULAR, vec(1, 1, 1, 1))
        #glMaterialfv(GL_FRONT, GL_AMBIENT, vec(0.8,0.8,0.8,1))
        #glMaterialf(GL_FRONT, GL_SHININESS, 50)
        
        #glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(1, 0, 0, 1))
        #glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(0, 1, 0, 1))
        #glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
        
        
        glDisable(GL_LIGHTING) # To avoid interfering with 2d rendering
    def fogSetup(self):
        glEnable(GL_FOG)
        # Set the fog color.
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
        # Say we have no preference between rendering speed and quality.
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        # Specify the equation used to compute the blending factor.
        glFogi(GL_FOG_MODE, GL_LINEAR)
        # How close and far away fog starts and ends. The closer the start and end,
        # the denser the fog in the fog range.
        glFogf(GL_FOG_START, 20.0)
        glFogf(GL_FOG_END, 60.0)
    def set2d(self):
        """ Configure OpenGL to draw in 2d.
        """
        # Light
        
        glDisable(GL_LIGHTING)
        
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL)
        
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    def set3d(self):
        """ Configure OpenGL to draw in 3d.
        """
        
        # Light
        
        #glEnable(GL_LIGHTING)
        
        if WIREFRAME:glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FIELDOFVIEW, width / float(height), 0.1, 6000.0) # default 60
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

window = MainWindow(caption="PyViz",resizable=True,vsync=True)

pyglet.app.run()
