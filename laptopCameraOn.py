''' 
----------------------------
Codigo base para probar la camara de la laptop 
----------------------------
'''

import cv2 # Importamos la libreria de OpenCV

img = cv2.VideoCapture(0) # Inicializamos la camara de la laptop

while True:
    __, frame = img.read() # Leemos la imagen de la camara

    cv2.imshow("Tello video",frame) # Mostramos la imagen en una ventana

    key = cv2.waitKey(30) # Esperamos 30 milisegundos para que el usuario presione una tecla
    if key == 27: # Si el usuario presiona la tecla ESC salimos del ciclo
        break 

