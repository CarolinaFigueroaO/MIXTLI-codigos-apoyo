''' 
----------------------------
Codigo de seguimiento de linea con el drone DJI Tello
----------------------------
'''
import cv2, time # Importamos las librerias de OpenCV y time
import numpy as np
from djitellopy import Tello


ajuste = 0 # Variable para ajustar el giro del drone
#--------

tiempo = 0 # Variable para el tiempo
lapso = 10
velTiempo = 0.1

#--------
tello = Tello() # Inicializamos el objeto Tello
tello.connect() # Conectamos con el Tello
print("CONECTADO")
print("BATERIA INICIAL: ", tello.get_battery())

tello.streamon() # Iniciamos el streaming de video
cap = tello.get_frame_read() # Obtenemos el frame del video

tello.takeoff() # Despegamos el drone
tello.set_speed(40) # Establecemos la velocidad del drone
time.sleep(3)   # Esperamos 3 segundos
tello.move_down(45) # Movemos el drone hacia abajo
time.sleep(3)  # Esperamos 3 segundos
tello.move_forward(20) # Movemos el drone hacia adelante
time.sleep(3) # Esperamos 3 segundos
#--------

frameWidth = 400 # Ancho del frame
frameHeight = 300 # Alto del frame
ROIwidth = frameWidth # Ancho de la region de interes
ROIheight = frameHeight # Alto de la region de interes
centro_x = ROIwidth//2 # Coordenada x y y del centro de la region de interes
centro_y = ROIheight//2

def deteccion_bordes(ROI): # Funcion para la deteccion de bordes
    # Obtener los contornos de la imagen
    imgGray = cv2.cvtColor(ROI, cv2.COLOR_RGB2GRAY) 
    # Aplica un desenfoque gaussiano para reducir el ruido
    imagen_gris_blur = cv2.GaussianBlur(imgGray, (5, 5), 0) 
    # Aplica el operador Canny para detectar bordes
    bordes = cv2.Canny(imagen_gris_blur, 50, 150) # Aplicamos el detector de bordes Canny a la imagen
    contours, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)   
    contour_image = img.copy() # Creamos una copia de la imagen
    cv2.drawContours(contour_image, contours, -1, (0, 0, 255), 2)  # Rojo (0, 0, 255) para los contornos, grosor 2
    return contours, contour_image  # Retornamos los contornos y la imagen con los contornos dibujados

def ajuste_angulo(contours):
    # Inicializar una lista para almacenar los ángulos de los contornos
    if len(contours) > 0:
        x,y,w,h = cv2.boundingRect(contours[0]) # Obtenemos el rectangulo que encierra el contorno
        box = cv2.minAreaRect(contours[0]) 
        (x_min,y_min),(w_min,h_min),angle = box # Obtenemos el ancho, alto y angulo del rectangulo
        if angle < -45: 
            angle = 90 + angle
        if w_min < h_min and angle > 0:
            angle = (90 - angle) * -1
        if w_min > h_min and angle < 0:
            angle = 90 + angle
        if angle < 0:
            giro = 90 + angle
            giro = int(giro)
            if giro < 10:    # Si el giro es menor a 10 lo consideremos centrado
                print("Centrado")
            else:
                print("Gira a la derecha",  giro) # Si el giro es mayor a 10 lo consideramos un giro a la derecha
                tello.rotate_clockwise(giro)
                time.sleep(4)
                return
        if angle > 0:
            giro = 90 - angle
            giro = int(giro)
            if giro < 10:   # Si el giro es menor a 10 lo consideremos centrado
                print("Centrado")
            else: # Si el giro es mayor a 10 lo consideramos un giro a la izquierda
                print("Gira a la izquierda", giro) 
                tello.rotate_counter_clockwise(giro)
                time.sleep(4)
                return

 
def ajuste_centro(contours): # Funcion para ajustar el centro
        for contour in contours:
            cv2.drawContours(img, [contour], -1, (0, 255, 0), 2)
            puntos = contour.squeeze()
            if len(puntos) > 0:
                cX = int(np.mean(puntos[:, 0]))
                diff_x = centro_x - cX # Diferencia entre el centro y el contorno
                if diff_x < -150: # Si la diferencia es menor a -150 movemos el drone a la derecha
                    print("Mover a la derecha")
                    tello.move_right(20)
                    return
                elif diff_x > 150: # Si la diferencia es mayor a 150 movemos el drone a la izquierda
                    print("Mover a la izquierda")
                    tello.move_left(20)
                    return

                else: # Si la diferencia es menor a 150 y mayor a -150 consideramos que esta centrado
                    print("Centrado")
                cv2.line(img, (centro_x, centro_y), (cX, centro_y), (0, 0, 255), 2)
            else:
                cX = None 


def recuperarLinea(contours): # Funcion para recuperar la linea
    print("No se dectecto linea!")
    print("Recuperando linea...")
    global ajuste
    #Hacemos una secuencia de movimientos para recuperar la linea
    #Si el ajuste realizado no funciona, prueba con el siguiente
    if ajuste == 0: 
        tello.move_left(20)
        ajuste = 1
        return
    elif ajuste == 1:
        tello.move_right(40)
        ajuste = 2
        return
    elif ajuste == 2:
        tello.move_back(20)
        ajuste = 3
        return
    elif ajuste == 3:
        tello.move_forward(40)
        ajuste = 0
        return

def verificarCruce(contours): # Funcion para verificar el cruce
    if len(contours) > 8: # Si el numero de contornos es mayor a 18 consideramos que se detecto un cruce
        print("Se detecto cruce")
        tello.move_forward(20)
        return
    
def detectarAterrizaje(img): # Funcion para detectar el aterrizaje
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Aplicar un umbral para resaltar el círculo (ajusta según sea necesario)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    # Encontrar círculos en la imagen
    circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                               param1=50, param2=30, minRadius=10, maxRadius=100)
    
    if circles is not None: # Si se detecta un circulo aterrizamos el drone
        print("Se detectó un círculo. Aterrizando...")
        tello.land()
        k == 27

while True: 
    k = cv2.waitKey(30)
    frame = cap.frame # Leemos el frame del video
    frame = frame.copy() # Creamos una copia del frame
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convertimos el frame a RGB
    img = cv2.resize(img, (frameWidth, frameHeight)) # Redimensionamos el frame
    img = cv2.flip(img, 0) # Volteamos el frame debido al espejo que se usa para ver el piso

    tiempo += velTiempo # Aumentamos el tiempo
    contours, contour_image = deteccion_bordes(img) # Obtenemos los contornos y la imagen con los contornos dibujados
    if len(contours) <= 0: # Si no se detecta ningun contorno
        recuperarLinea(contours) # Llamamos a la funcion recuperarLinea
    verificarCruce(contours)
    
    #Intervalos de tiempo para realizar ajustes
    if tiempo > lapso and tiempo < lapso+0.1: 
        ajuste_centro(contours)

    if tiempo > 2 and tiempo < 2.1:
        ajuste_angulo(contours)

    if tiempo > lapso + 4 and tiempo< lapso + 4.1:
        tello.move_forward(40)
        
    if tiempo > lapso + 4.1:
        tiempo = 0

    cv2.imshow('Tello camera', img) # Mostramos la imagen en una ventana

    if k == 27: # Si el usuario presiona la tecla ESC salimos del ciclo
        tello.land()
        break
    
tello.streamoff() # Detenemos el streaming de video
print("Bateria final: ", tello.get_battery()) # Mostramos la bateria final
