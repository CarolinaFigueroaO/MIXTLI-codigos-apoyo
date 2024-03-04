''' 
----------------------------
Codigo para probar la camara de la laptop con deteccion de bordes
con ayuda de trackbars para ajustar los parametros de la deteccion 
----------------------------
'''

import cv2
import numpy as np
from djitellopy import Tello


frameWidth = 500 # Ancho de la imagen
frameHeight = 350 # Alto de la imagen

img2 = cv2.VideoCapture(0) # Inicializamos la camara de la laptop
deadZone = 100 
global imgContour # Creamos una variable global para los contornos

def empty(a): # Funcion para los trackbars
    pass

cv2.namedWindow("HSV") # Creamos una ventana para los trackbars
cv2.resizeWindow("HSV",640,240) 
cv2.createTrackbar("HUE Min","HSV",19,179,empty) 
cv2.createTrackbar("HUE Max","HSV",35,179,empty)
cv2.createTrackbar("SAT Min","HSV",107,255,empty)
cv2.createTrackbar("SAT Max","HSV",255,255,empty)
cv2.createTrackbar("VALUE Min","HSV",89,255,empty)
cv2.createTrackbar("VALUE Max","HSV",255,255,empty)

cv2.namedWindow("Parameters") 
cv2.resizeWindow("Parameters",640,240)
cv2.createTrackbar("Threshold1","Parameters",166,255,empty)
cv2.createTrackbar("Threshold2","Parameters",171,255,empty)
cv2.createTrackbar("Area","Parameters",3750,30000,empty)




def getContours(img,imgContour): # Funcion para obtener los contornos
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        if area > areaMin:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            x , y , w, h = cv2.boundingRect(approx)
            cv2.rectangle(imgContour, (x , y ), (x + w , y + h ), (0, 255, 0), 5)

            cv2.putText(imgContour, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, .7,
                        (0, 255, 0), 2)
            cv2.putText(imgContour, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        (0, 255, 0), 2)
            cv2.putText(imgContour, " " + str(int(x))+ " "+str(int(y)), (x - 20, y- 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        (0, 255, 0), 2)

            cx = int(x + (w / 2))
            cy = int(y + (h / 2))

            if (cx <int(frameWidth/2)-deadZone): 
                print("GO LEFT")

            elif (cx > int(frameWidth / 2) + deadZone):
                print("GO RIGHT")

            elif (cy < int(frameHeight / 2) - deadZone):
                print("GO UP")

            elif (cy > int(frameHeight / 2) + deadZone):
                print("GO DOWN")

            cv2.line(imgContour, (int(frameWidth/2),int(frameHeight/2)), (cx,cy),
                     (0, 0, 255), 3)

def display(img): # Funcion para mostrar las lineas de referencia
    cv2.line(img,(int(frameWidth/2)-deadZone,0),(int(frameWidth/2)-deadZone,frameHeight),(255,255,0),3)
    cv2.line(img,(int(frameWidth/2)+deadZone,0),(int(frameWidth/2)+deadZone,frameHeight),(255,255,0),3)

    cv2.circle(img,(int(frameWidth/2),int(frameHeight/2)),5,(0,0,255),5)
    cv2.line(img, (0,int(frameHeight / 2) - deadZone), (frameWidth,int(frameHeight / 2) - deadZone), (255, 255, 0), 3)
    cv2.line(img, (0, int(frameHeight / 2) + deadZone), (frameWidth, int(frameHeight / 2) + deadZone), (255, 255, 0), 3)

while True:
    __, img = img2.read() # Leemos la imagen de la camara
    img = cv2.resize(img, (frameWidth, frameHeight)) # Redimensionamos la imagen

    imgContour = img.copy() # Creamos una copia de la imagen
    imgHsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV) # Convertimos la imagen a HSV

    h_min = cv2.getTrackbarPos("HUE Min","HSV") # Obtenemos el valor del trackbar
    h_max = cv2.getTrackbarPos("HUE Max", "HSV")
    s_min = cv2.getTrackbarPos("SAT Min", "HSV")
    s_max = cv2.getTrackbarPos("SAT Max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE Max", "HSV")

    lower = np.array([h_min,s_min,v_min]) # Creamos un arreglo con los valores minimos
    upper = np.array([h_max,s_max,v_max]) # Creamos un arreglo con los valores maximos
    mask = cv2.inRange(imgHsv,lower,upper) # Creamos una mascara con los valores minimos y maximos
    result = cv2.bitwise_and(img,img, mask = mask) # Aplicamos la mascara a la imagen original
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) # Convertimos la mascara a BGR

    imgBlur = cv2.GaussianBlur(result, (7, 7), 1) # Aplicamos un filtro Gaussiano a la imagen
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)     # Convertimos la imagen a escala de grises
    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters") # Obtenemos el valor del trackbar
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")     # Obtenemos el valor del trackbar
    imgCanny = cv2.Canny(imgGray, threshold1, threshold2) # Aplicamos el detector de bordes Canny a la imagen
    kernel = np.ones((5, 5))
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1) # Aplicamos una dilatacion a la imagen
    getContours(imgDil, imgContour) # Obtenemos los contornos de la imagen
    display(imgContour) # Mostramos las lineas de referencia
    
    panel1 = cv2.hconcat([img, mask]) # Concatenamos las imagenes de la primera fila
    pane12 = cv2.hconcat([result,imgContour]) # Concatenamos las imagenes de la segunda fila
    panel = cv2.vconcat([panel1, pane12]) # Concatenamos las imagenes de ambas filas
    cv2.imshow('Deteccion de bordes', panel)
    k = cv2.waitKey(30)
    if k == 27:
        break  

cv2.destroyAllWindows()
