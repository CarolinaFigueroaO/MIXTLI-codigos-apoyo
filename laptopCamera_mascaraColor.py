''' 
----------------------------
Codigo base para filtrar colores de video 
----------------------------
'''

import cv2 # Importamos la libreria de OpenCV
import numpy as np

img = cv2.VideoCapture(0) # Inicializamos la camara de la laptop
font = cv2.FONT_HERSHEY_SIMPLEX

# Definir el rango de color que quieres filtrar (en este caso, verde)
verde_min = np.array([40, 50, 50])
verde_max = np.array([80, 255, 255])

while True:
    __, frame = img.read() # Leemos la imagen de la camara

    frame = cv2.resize(frame, (500, 380)) # Redimensionamos la imagen

    frameHSV= cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
    mascaraHSV = cv2.inRange(frameHSV, verde_min, verde_max)

    contornos, jerarquia = cv2.findContours(mascaraHSV, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    frameContornos = frame.copy() # Creamos una copia de la imagen
    cv2.drawContours(frameContornos, contornos, -1, (255, 0, 0), 2) # Dibujar contornos en la copia de la imagen original

    cv2.putText(frame, "Imagen original", (10, 30), font, 1, (0,0,0), 2, cv2.LINE_AA)
    cv2.putText(frameHSV, "HSV filtro", (10, 30), font, 1, (0,0,0), 2, cv2.LINE_AA)
    cv2.putText(frameContornos, "Contornos de la mascara", (10, 30), font, 1, (0,0,0), 2, cv2.LINE_AA)

    listaVideos = cv2.hconcat([frame, frameHSV, frameContornos]) # Concatenamos las imagenes de la primera fila
    cv2.imshow("Video laptop", listaVideos) # Mostramos la imagen en una ventana

    key = cv2.waitKey(30) # Esperamos 30 milisegundos para que el usuario presione una tecla
    if key == 27: # Si el usuario presiona la tecla ESC salimos del ciclo
        break 

