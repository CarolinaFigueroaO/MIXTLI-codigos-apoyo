''' 
----------------------------
Codigo base para probar la camara del drone DJI Tello 
----------------------------
'''

from djitellopy import Tello # Importamos la libreria de DJI Tello
import cv2 # Importamos la libreria de OpenCV


tello = Tello() # Inicializamos el objeto Tello
tello.connect() # Conectamos con el Tello

tello.streamon() # Iniciamos el streaming de video
cap = tello.get_frame_read() # Obtenemos el frame del video

while True:
    frame = cap.frame  # Leemos el frame del video

    cv2.imshow("Tello video", frame) # Mostramos la imagen en una ventana

    key = cv2.waitKey(30) # Esperamos 30 milisegundos para que el usuario presione una tecla
    if key == 27: # Si el usuario presiona la tecla ESC salimos del ciclo
        break

