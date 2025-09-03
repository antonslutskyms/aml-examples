import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo
import ctypes
from datetime import datetime
from PIL import Image
import sys

SZ = 1500

gCamAng = 0.
gCamHeight = 3.
vertices = None 
normals = None
faces = None
dropped = 0
modeFlag = 0
look_at_coef = 5    

def look_init():
    global lookat_x, lookat_y, lookat_z, lookfrom_x,lookfrom_y,lookfrom_z
    lookat_x = 0
    lookat_y = 0
    lookat_z = 0

    lookfrom_x,lookfrom_y,lookfrom_z = 5,0,0

look_init()

distanceFromOrigin = 45


def dropCallback(window, paths):
    global vertices, normals, faces, dropped, gVertexArraySeparate
    numberOfFacesWith3Vertices = 0
    numberOfFacesWith4Vertices = 0
    numberOfFacesWithMoreThan4Vertices = 0
    dropped = 1
    fileName = paths[0].split('\\')[-1]
    if(paths[0].split('.')[1].lower() != "obj"):
        print("Invalid File\nPlease provide an .obj file")
        return
    with open(paths[0]) as f:
        lines = f.readlines()
        vStrings = [x.strip('v') for x in lines if x.startswith('v ')]
        vertices = convertVertices(vStrings)
        if np.amax(vertices) <= 1.2:
            vertices /= np.amax(vertices)
        else:
            vertices /= np.amax(vertices)/2
        vnStrings = [x.strip('vn') for x in lines if x.startswith('vn')]
        if not vnStrings: #if There is no normal vectors in the obj file then compute them
            normals = fillNormalsArray(len(vStrings))
        else:
            normals = convertVertices(vnStrings)
        faces = [x.strip('f') for x in lines if x.startswith('f')]
    for face in faces: 
        if len(face.split()) == 3:
            numberOfFacesWith3Vertices +=1
        elif len(face.split()) == 4:
            numberOfFacesWith4Vertices +=1
        else:
            numberOfFacesWithMoreThan4Vertices +=1
    print("File name:",fileName,"\nTotal number of faces:", len(faces),
        "\nNumber of faces with 3 vertices:",numberOfFacesWith3Vertices, 
        "\nNumber of faces with 4 vertices:",numberOfFacesWith4Vertices,
        "\nNumber of faces with more than 4 vertices:",numberOfFacesWithMoreThan4Vertices)
    if(numberOfFacesWith4Vertices > 0 or numberOfFacesWithMoreThan4Vertices > 0):
        faces = triangulate()
    gVertexArraySeparate = createVertexArraySeparate()
    ##########EMPTYING USELESS VARIABLES FOR MEMORY MANAGEMENT##########
    faces = []
    normals = []
    vertices = []
    ####################################################################
def fillNormalsArray(numberOfVertices):
    normals = np.zeros((numberOfVertices, 3))
    i = 0
    for vertice in vertices:
        normals[i] = normalized(vertice)
        i +=1
    return normals
def convertVertices(verticesStrings):
    v = np.zeros((len(verticesStrings), 3))
    i = 0
    for vertice in verticesStrings:
        j = 0
        for t in vertice.split():
            try:
                v[i][j] = (float(t))
            except ValueError:
                pass
            j+=1
        i+=1
    return v
def triangulate():
    facesList = []
    nPolygons = []
    for face in faces:
        if(len(face.split())>=4):
            nPolygons.append(face)
        else:
            facesList.append(face)
    for face in nPolygons:
        for i in range(1, len(face.split())-1):
            seq = [str(face.split()[0]), str(face.split()[i]), str(face.split()[i+1])]
            string = ' '.join(seq)
            facesList.append(string)
    return facesList
def createVertexArraySeparate():
    varr = np.zeros((len(faces)*6,3), 'float32')
    i=0
    normalsIndex = 0
    verticeIndex = 0
    for face in faces:
        for f in face.split():
            if '//' in f: # f v//vn
                verticeIndex = int(f.split('//')[0])-1 
                normalsIndex = int(f.split('//')[1])-1
            elif '/' in f: 
                if len(f.split('/')) == 2: # f v/vt
                    verticeIndex = int(f.split('/')[0])-1 
                    normalsIndex = int(f.split('/')[0])-1
                else: # f v/vt/vn
                    verticeIndex = int(f.split('/')[0])-1 
                    normalsIndex = int(f.split('/')[2])-1
            else: # f v v v
                verticeIndex = int(f.split()[0])-1 
                normalsIndex = int(f.split()[0])-1
            varr[i] = normals[normalsIndex]
            varr[i+1] = vertices[verticeIndex]
            i+=2
    return varr

def render(ang):
    global gCamAng, gCamHeight, distanceFromOrigin, dropped, look_at_coef, lookat_x, lookat_y, lookat_z, lookfrom_x,lookfrom_y,lookfrom_z
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION) # use projection matrix stack for projection transformation for correct lighting
    glLoadIdentity()
    gluPerspective(distanceFromOrigin, 1, 1,10)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #gluLookAt(5*np.sin(gCamAng),gCamHeight,5*np.cos(gCamAng), 0,0,0, 0,1,0)
    
    #gluLookAt(look_at_coef*np.sin(gCamAng),gCamHeight,look_at_coef*np.cos(gCamAng), lookat_x,lookat_y,lookat_z, 0,1,0)

    gluLookAt(lookfrom_x,lookfrom_y,lookfrom_z, lookat_x,lookat_y,lookat_z, 0,1,0)
    
    #gluLookAt(lookfrom_x,lookfrom_y,lookfrom_z, look_at_coef*np.sin(lookat_x),lookat_y,look_at_coef*np.cos(lookat_z), 0,1,0)

    drawFrame()
    glEnable(GL_LIGHTING)   #comment: no lighting
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    # light position
    glPushMatrix()
    lightPos0 = (1.,2.,3.,1.)    # try to change 4th element to 0. or 1.
    lightPos1 = (3.,2.,1.,1.)
    lightPos2 = (2.,3.,1.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos1)
    glLightfv(GL_LIGHT2, GL_POSITION, lightPos2)
    glPopMatrix()

    # light intensity for each color channel
    ambientLightColor0 = (.1,.1,.1,1.)
    diffuseLightColor0 = (1.,1.,1.,1.)
    specularLightColor0 = (1.,1.,1.,1.)
    ambientLightColor1 = (.075,.075,.075,1.)
    diffuseLightColor1 = (0.75,0.75,0.75,0.75)
    specularLightColor1 = (0.75,0.75,0.75,0.75)
    ambientLightColor2 = (.05,.05,.05,1.)
    diffuseLightColor2 = (0.5,0.5,0.,0.5)
    specularLightColor2 = (0.5,0.5,0.,0.5)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLightColor0)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specularLightColor0)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor1)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuseLightColor1)
    glLightfv(GL_LIGHT1, GL_SPECULAR, specularLightColor1)
    glLightfv(GL_LIGHT2, GL_AMBIENT, ambientLightColor2)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, diffuseLightColor2)
    glLightfv(GL_LIGHT2, GL_SPECULAR, specularLightColor2)
    # material reflectance for each color channel
    diffuseObjectColor = (0.4,0.6,0.5,1.)
    specularObjectColor = (0.6,0.3,0.3,.5)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, diffuseObjectColor)
    #glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    glPushMatrix()
    if dropped == 1:
        draw_glDrawArray()
    glPopMatrix()

    glDisable(GL_LIGHTING)
    #print("CamAng:",np.degrees(gCamAng), "CamHeight:", gCamHeight, "Distance:", distanceFromOrigin, end='\r')



def draw_glDrawArray():
    global gVertexArraySeparate
    varr = gVertexArraySeparate
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([10.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,10.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,10.]))
    glEnd()


capture_video_on = False
do_capture_screenshot = False

def generate_key_action(window, scancode, action, mods):
    key_callback(window, glfw.KEY_3, scancode, action, mods)

def move(op):
    global lookfrom_x,lookfrom_y,lookfrom_z, lookat_x, lookat_y, lookat_z
    lookfrom_x +=  op*((lookat_x - lookfrom_x)/50.)
    lookfrom_y +=  op*((lookat_y - lookfrom_y)/50.)
    lookfrom_z +=  op*((lookat_z - lookfrom_z)/50.)

def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight, modeFlag, distanceFromOrigin, look_at_coef, lookat_x, lookat_y, lookat_z, lookfrom_x,lookfrom_y,lookfrom_z, do_capture_screenshot
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_1:
            gCamAng += np.radians(10%360)
        elif key==glfw.KEY_3:
            gCamAng += np.radians(-10%360)
        elif key==glfw.KEY_2:
            if gCamHeight < 9:
                gCamHeight += .1
        elif key==glfw.KEY_W:
            if gCamHeight > -9:
                gCamHeight += -.1
        elif key==glfw.KEY_Z:
            if modeFlag == 0:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                modeFlag = 1
            else:
                glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
                modeFlag = 0
        elif key==glfw.KEY_A:
            if distanceFromOrigin > 0:
                distanceFromOrigin -= 1
        elif key==glfw.KEY_S:
            if distanceFromOrigin < 180:
                distanceFromOrigin +=1
        elif key==glfw.KEY_N:
            look_at_coef +=.3
        elif key==glfw.KEY_M:
            look_at_coef -=.3
        elif key==glfw.KEY_RIGHT:
            lookat_z -= max( lookat_z/10., .3)
            #lookat_z = max(-16, lookat_z)
            print("R-Looking at:", lookat_x, lookat_y, lookat_z)
        elif key==glfw.KEY_LEFT:
            lookat_z +=max( lookat_z/10., .3)
            #lookat_z = min(16, lookat_z)
            print("L-Looking at:", lookat_x, lookat_y, lookat_z)
        elif key==glfw.KEY_UP:
            lookat_y +=.1
        elif key==glfw.KEY_DOWN:
            lookat_y -=.1
        elif key==glfw.KEY_U:
            lookfrom_y +=.1
        elif key==glfw.KEY_D:
            lookfrom_y -=.1
        
        elif key==glfw.KEY_L:
            lookat_z -=.1
        elif key==glfw.KEY_R:
            lookat_z +=.1
        elif key==glfw.KEY_X:

            ###########################
            
            capture_screenshot(window, 0, out_dir=output_dir)
            
            #print("Toggling video capture...")
            #do_capture_screenshot = True
            ###########################


        elif key==glfw.KEY_V:
            look_init()
            # gCamAng = 0.
            # gCamHeight = 1.
            # distanceFromOrigin = 45
        elif key==glfw.KEY_SPACE:
            print("Space key is pressed. Generating next steps for flyby path...")
            move(1.)
        elif key==glfw.KEY_B:
            print("Space key is pressed. Generating next steps for flyby path...")
            move(-1.)


        


def capture_screenshot(window, i, out_dir='.'):
    width, height = glfw.get_framebuffer_size(window)
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    pixels = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (width, height), pixels)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)  # Flip vertically
    image.save(f"{out_dir}/image{str(i).zfill(10)}.png")
    print("Screenshot saved as 'screenshot.png'")

gVertexArraySeparate = np.zeros((3, 3))

output_dir = "."

def main():
    input_obj_file = sys.argv[1] if len(sys.argv) > 1 else None

    global output_dir
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    global gVertexArraySeparate
    if not glfw.init():
        return
    window = glfw.create_window(SZ,SZ,'3D Obj File Viewer', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_drop_callback(window, dropCallback)

    if input_obj_file:
        dropCallback(window, [input_obj_file])  # Load the initial OBJ file if provided

    glfw.swap_interval(1)
    count = 0
    image_count = 0
    while not glfw.window_should_close(window):
        global do_capture_screenshot
        glfw.poll_events()
        count+=1
        ang = count % 360
        render(ang)
        count += 1
        glfw.swap_buffers(window)


        #####################################
        #print("do_capture_screenshot", do_capture_screenshot)
#        global do_capture_screenshot
        if do_capture_screenshot:
            if capture_video_on:
                print("Capturing screenshot...", output_dir)
                capture_screenshot(window, image_count, output_dir)
            image_count += 1
            do_capture_screenshot = False
        #####################################

    glfw.terminate()
def l2norm(v):
    return np.sqrt(np.dot(v, v))
def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)
if __name__ == "__main__":
    main()
			