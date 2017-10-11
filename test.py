from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image as Image
import os
import math
import numpy

time_dic = {}
id_dic = {}
speed_dic = {}
time_stamp = -1
interval = 40
width = 0
height = 0
internal_width = 90
internal_height = 50
fps = 25.0
start_stamp = 13
location_file_path = "res.txt"
background_path = "b1.jpg"
interpolate_interval = 5
texture_id = None

def read_texture(filename):
    global texture_id

    img = Image.open(filename)
    width, height = img.size
    img_data = numpy.array(list(img.getdata()), numpy.int8)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)

def refresh2d_custom(width, height, internal_width, internal_height):
    #glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, internal_width, 0.0, internal_height, -10.0, 10.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def drawPoint(x, y):
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(5.0)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def drawSpeed(x, y, speed):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x - 2, y - 2)
    speed_str = str(speed)
    if speed == 0.0:
        for ch in speed_str:
            glutBitmapCharacter(OpenGL.GLUT.GLUT_BITMAP_HELVETICA_18, ord(ch))
    else:
        for i in range(5):
            glutBitmapCharacter(OpenGL.GLUT.GLUT_BITMAP_HELVETICA_18, ord(speed_str[i]))

def drawID(x, y, speed):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x - 1, y + 1)
    speed = str(speed)
    for ch in speed:
        glutBitmapCharacter(OpenGL.GLUT.GLUT_BITMAP_HELVETICA_18, ord(ch))

def draw_back():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION);
    glPushMatrix()
    glLoadIdentity();
    gluOrtho2D(0, width, height, 0);
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    #glEnable(GL_TEXTURE_GEN_S)
    #glEnable(GL_TEXTURE_GEN_T)
    #glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    #glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glBegin(GL_POLYGON);
    glTexCoord2f(0.0, 0.0); glVertex2f(0, 0);
    glTexCoord2f(0.0, 1.0); glVertex2f(0, height)
    glTexCoord2f(1.0, 1.0); glVertex2f(width, height);
    glTexCoord2f(1.0, 0.0); glVertex2f(width, 0);
    glEnd();
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()
    return

def drawFunc():
    global time_stamp

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()                                   # reset position
    draw_back()
    #glLoadIdentity()
    refresh2d_custom(width, height, internal_width, internal_height)

    for person in time_dic[time_stamp]:
        if len(id_dic[person][time_stamp]) == 3:
            speed_dic[person] = id_dic[person][time_stamp][2]
        if person in speed_dic:
            speed = speed_dic[person]
        else:
            speed = 0.0
        #print(float(time_dic[time_stamp][person][0]), float(time_dic[time_stamp][person][1]))
        #if (time_stamp - 13) % 5 == 0:
        #print(id_dic[person][time_stamp][0], id_dic[person][time_stamp][1])
        drawPoint(id_dic[person][time_stamp][0], id_dic[person][time_stamp][1])
        drawSpeed(id_dic[person][time_stamp][0], id_dic[person][time_stamp][1], speed)
        drawID(id_dic[person][time_stamp][0], id_dic[person][time_stamp][1], person)

    glutSwapBuffers()

def update(value):
    global  time_stamp
    time_stamp = time_stamp + 1
    if time_stamp == len(time_dic):
        exit()
    glutTimerFunc(interval, update, value)

def cal_speed(x, y, time, id):
    previous_time = time - fps
    ride = 1.0
    if previous_time not in id_dic[id]:
        while previous_time not in id_dic[id]:
            previous_time += 1
            #print(previous_time)
            if previous_time == time: return 0.0
        ride = (time - previous_time)/fps

    last_occur = id_dic[id][previous_time]
    last_x = last_occur[0]
    last_y = last_occur[1]
    dx = x - last_x
    dy = y - last_y
    speed = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))/ride
    return speed

def do_interpolation():
    for id in id_dic:
        for time in id_dic[id]:
            start_time = time - interpolate_interval
            while start_time not in id_dic[id]:
                start_time += 1
            end_time = time + interpolate_interval
            while end_time not in id_dic[id]:
                end_time -= 1
            sum_x = 0.0
            sum_y = 0.0
            count = 0
            for t in range(start_time, end_time + 1):
                if t not in id_dic[id]:
                    continue
                sum_x += id_dic[id][t][0]
                sum_y += id_dic[id][t][1]
                count += 1

            id_dic[id][time][0] = sum_x / count
            id_dic[id][time][1] = sum_y / count

def read_location(location_file_path):
    global time_stamp
    last_time_stamp = 0
    with open(location_file_path, 'r') as location:
        for line in location:
            identity = line.strip().split(',')
            identity[0] = int(identity[0])
            identity[1] = int(identity[1])
            identity[7] = float(identity[7])
            identity[8] = float(identity[8])
            id_dic.setdefault(identity[1], {})
            time_dic.setdefault(identity[0], [])
            if time_stamp == -1:
                time_stamp = identity[0]
                last_time_stamp = identity[0]

            if identity[0] % fps == time_stamp and identity[0] != time_stamp:
                speed = cal_speed(identity[7], identity[8], identity[0], identity[1])
                id_dic[identity[1]][identity[0]] = [identity[7], identity[8], speed]
            else:
                id_dic[identity[1]][identity[0]] = [identity[7], identity[8]]
            time_dic[identity[0]].append(identity[1])

if __name__ == "__main__":
    read_location(location_file_path)
    img = Image.open(background_path)
    width, height = img.size
    do_interpolation()
    glutInit()
    glutInitWindowPosition(0, 0)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow(b'Pedestrian tracking visualization')
    read_texture(background_path)
    glutDisplayFunc(drawFunc)
    glutIdleFunc(drawFunc)
    glutTimerFunc(interval, update, start_stamp)
    glutMainLoop()