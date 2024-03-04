import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2

# Leemos la imagen
image = mpimg.imread('carrito/imagen_prueba2.jpg')

def escalaGrises(imagen):
    return cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)

def canny(imagen, bajo, alto):
    return cv2.Canny(imagen, bajo, alto)

def gaussianBlur(imagen, kernel):
    return cv2.GaussianBlur(imagen, (kernel, kernel), 0)

def regionObjetivo(img, vertices):

    mascara = np.zeros_like(img) # Creamos una mas
    
    #definir un color de 3 canales o 1 canal para rellenar la máscara dependiendo de la imagen de entrada
    if len(img.shape) > 2:
        canal_contador = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignorar_mascara = (255,) * canal_contador
    else:
        ignorar_mascara = 255
        
    #Rellena el área de interés con el color  
    cv2.fillPoly(mascara, vertices, ignorar_mascara)
    
    #Regresa la imagen solo donde la máscara es 1, o sea el área de interés
    imagen_mascara = cv2.bitwise_and(img, mascara)
    return imagen_mascara

def dibujarLineas(img, lineas, color=[255, 0, 0], thickness=14):
    # Inicializamos dos matrices vacias ddonde guardaremos las coordenadas de las lineas
    izq = np.empty((0,4), int)
    der = np.empty((0,4), int)

    # Iteramos sobre las lineas detectadas
    for linea in lineas:
        for x1,y1,x2,y2 in linea:
            # Calculamos la pendiente
            m = (y2 - y1) / (x2 - x1)
            # Si la pendiente es negativa, es la linea izquierda
            if m < 0:
                izq = np.append(izq, [[x1, y1, x2, y2]], axis=0)
            # Si la pendiente es positiva, es la linea derecha
            elif m > 0:
                der = np.append(der, [[x1, y1, x2, y2]], axis=0)

    izq_x1 = 0
    izq_y1 = 0
    izq_x2 = 0
    izq_y2 = 0
    der_x1 = 0
    der_y1 = 0
    der_x2 = 0
    der_y2 = 0
    
    top_position_of_region = 330
    extrapolate_times = 10
        
    # calculate average the position of each of the lines, and extrapolate it. for left lane
    if len(izq) != 0:    
        for point in izq:
            izq_x1 += point[0]
            izq_y1 += point[1]
            izq_x2 += point[2]
            izq_y2 += point[3]

        # averaget position
        izq_x1_avg = izq_x1 / len(izq)
        izq_y1_avg = izq_y1 / len(izq)
        izq_x2_avg = izq_x2 / len(izq)
        izq_y2_avg = izq_y2 / len(izq)
        
        x_elm = izq_x2_avg - izq_x1_avg
        y_elm = izq_y2_avg - izq_y1_avg
        extrapolated_x1 = izq_x1_avg - extrapolate_times * x_elm
        extrapolated_y1 =  izq_y1_avg - extrapolate_times * y_elm
        
        grad = y_elm / x_elm
        x_diff = abs((izq_y2_avg - top_position_of_region) / grad)
        cv2.line(img, (int(extrapolated_x1), int(extrapolated_y1)), (int(izq_x2_avg + x_diff), int(top_position_of_region)), color, thickness) 

    # average and extrapolate for right lane
    if len(der) != 0:
        for point in der:
            der_x1 += point[0]
            der_y1 += point[1]
            der_x2 += point[2]
            der_y2 += point[3]

        der_x1_avg = der_x1 / len(der)
        der_y1_avg = der_y1 / len(der)
        der_x2_avg = der_x2 / len(der)
        der_y2_avg = der_y2 / len(der)
        
        x_elm = der_x2_avg - der_x1_avg
        y_elm = der_y2_avg - der_y1_avg
        extrapolated_x2 = der_x2_avg + extrapolate_times * x_elm
        extrapolated_y2 = der_y2_avg + extrapolate_times * y_elm
        
        grad = y_elm / x_elm
        x_diff = abs((der_y1_avg - top_position_of_region) / grad)
        cv2.line(img, (int(der_x1_avg - x_diff), int(top_position_of_region)), (int(extrapolated_x2), int(extrapolated_y2)), color, thickness) 


        


bajo = 50
alto = 150

# Convertimos la imagen a escala de grises
grises = escalaGrises(image)

# Aplicamos Canny
contornos = canny(grises, bajo, alto)

# Aplicamos un filtro gaussiano
gaussian = gaussianBlur(contornos, 5)

# Definimos los vértices del polígono
imshape = image.shape # Obtenemos las dimensiones de la imagen
vertices = np.array([[(80,imshape[0]),(450, 330), (520, 330), (imshape[1] - 50,imshape[0])]], dtype=np.int32) # Definimos los vértices del polígono, en este caso un trapecio
#vertices = np.array([[(0,imshape[0]),(450, 280), (490, 280), (imshape[1],imshape[0])]], dtype=np.int32) # Definimos los vértices del polígono, en este caso un trapecio
region = regionObjetivo(gaussian, vertices) # Aplicamos la máscara y obtenemos el área de interés

# Aplicamos la transformada de Hough
lineas = cv2.HoughLinesP(region, 2, np.pi/180, 100, np.array([]), minLineLength=40, maxLineGap=5)

# Dibujamos las lineas
dibujarLineas(region, lineas)

# Mostramos la imagen
cv2.imshow('Original', region)

cv2.waitKey(0)