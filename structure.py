import struct
from collections import namedtuple

from matplotlib.ft2font import GLYPH_NAMES

V2 = namedtuple('Point2', ['x', 'y'])

def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    #1 word
    return struct.pack('=h', w)

def dword(d):
    #2 word
    return struct.pack('=l', d)

def color(r, g, b):
    '''
        Función para crear un color.
        La imagen se pone en bgr (o sea al revés).
        Se multiplica para pasarle de parámetro un valor de 0 a 1.
    '''
    return bytes([int(b * 255),
                  int(g * 255),
                  int(r * 255)])

class Renderer(object):
    def __init__(self, w, h):
        '''
            h: alto
            w: ancho
        '''
        self.width = w
        self.height = h
        self.clearColor = color(0,0,0) # Color predeterminado
        self.currColor = color(1,1,1)

        self.glViewport(0, 0, self.width, self.height) #Viewport predeterminado (del tamaño de la window)
        self.glClear()


    def glViewport(self, posX, posY, width, height):
        self.vpX = posX
        self.vpY = posY
        self.vpWidth = width
        self.vpHeight = height


    def glClearColor (self, r, g, b):
        self.clearColor = color(r,g,b)

    def glColor (self, r, g, b):
        self.currColor = color(r,g,b) 

    def glClearViewport (self, clr=None):
        for x in range(self.vpX, self.vpX + self.vpWidth):
            for y in range(self.vpY, self.vpY + self.vpHeight):
                self.glPoint(x,y,clr)

    # Array de pixeles
    def glClear(self):
        '''
            Para determinar el color del fondo. 
            Borra todos lo que está en la pantalla.
            Esto se hace para poder crear los arrays de los pixeles.
        '''
        # Array de pixeles
        self.pixels = [[self.clearColor for y in range(self.height)]
                        for x in range (self.width)] # Array de ancho x altura, list comprehension

    def glPoint (self, x, y, clr = None):
        '''
            Función para trazar un punto en la pantalla con cordenadas
        '''
        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[x][y] = clr or self.currColor # Falta validar que x y y no supere el tamaño

    def glPoint_vp(self, ndcX, ndcY, clr = None):
        '''
            Función para trazar un punto en la pantalla con coordenadas normalizadas.
        '''
        if ndcX < -1 or ndcX > 1 or ndcY < -1 or ndcY > 1:
            return

        x = (ndcX + 1) * (self.vpWidth / 2) + self.vpX
        y = (ndcY + 1) * (self.vpHeight / 2) + self.vpY

        x = int(x)
        y = int(y)

        self.glPoint(x, y, clr)

    def glLine(self, v0, v1, clr=None):
        '''
            Bresenham line algorithm.
            Utilizando la librería nametuple para facilitar la lectura del código.
            Tomar en cuenta: y = m * x + b
            v0: Vector inicial
            v1: Vector final
        '''
        x0 = int(v0.x)
        x1 = int(v1.x)
        y0 = int(v0.y)
        y1 = int(v1.y)

        # Si el punto 0 es igual al punto 1, solo se tiene que dibujar un punto.
        if x0 == x1 and y0 == y1:
            self.glPoint(x0,y0,clr)
            return

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        steep = dy > dx # Si es true es que la línea está muy inclinada. Entonces ahora voy a querer recorrerlo de forma vertical.

        if steep:
            # Para recorrer de forma vertical
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            # Significa ue el punto inicial está del lado derecho -> Lo tengo que dibujar de derecha a izquierda.
            # Pero quiero que siempre lo haga de iz a der, entonces le tengo que dar la vuelta.
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        # Por si cambiaron de valor. (Está más inclinado)
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        # Para fillearlo busco el punto central de cada pixel. 
        # Determino si me paso al otro pixel si ya superó la mitad del pixel actual
        offset = 0
        limit = 0.5 # Representa el punto central del pixel
        m = dy / dx
        y = y0

        for x in range (x0, x1 + 1):
            # Si está muy inclinado, dibujo de forma vertical
            if steep:
                # Vertical
                self.glPoint(y, x, clr)
            else:
                # Dibujado de forma horizontal.
                self.glPoint(x, y, clr)

            offset += m
            
            # Prácticamente tengo que revizar si el pixel llegó a la mitad del pixel. Si no llegó pinto el de abajo.
            if offset >= limit:
                if y0 < y1:
                    # De abajo para arriba. La pendiente es positiva.
                    y += 1
                else:
                    # La pendiente es negativa. De arriba para abajo.
                    y -= 1

                limit += 1


        # m = dy / dx
        # y = y0

        # # Leer primero de foma horizontal
        # for x in range(x0, x1 + 1):
        #     y += m
        #     y = int(y)
        #     self.glPoint(x,y)

    def glFillPoli (self):
        '''
            Recorrer cada uno de los pixeles. Si el color es diferente al del fondo y es True la variable temp rellenar.
            Siempre va verificando el siguiente del que rellenó y si el color es diferente al del fondo cambiar a False
            la variable temp.
        '''
        for y in range(self.height):
            for x in range(self.width):
                print(self.pixels[x][y])

                # if self.currColor != (self.pixels[x][y]):
            

    # Función para crear el bitmap/frame buffer
    def glFinish (self, filename):
        '''
        BMP FILE ESQUEME
            File header: Se dan las propiedades de la imagen. 
            filename: El nombre del archivo
        '''
        # Escritura en bytes -> wb
        with open(filename, "wb") as file:

            # Crear el FILE HEADER
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            # Para decirle el tamaño del archivo en bytes.
            # Usualmente son 40 bytes (offset),
            # 14 del header
            # y luego lo de los colores que es w*h*3 por los 3 colores.
            file.write(dword( 14 + 40 + (self.width * self.height * 3))) 
            file.write(dword(0))
            file.write(dword(14 + 40))

            # Crear INFORMATION HEADER
            # Ocupa 40 bytes
            file.write(dword(40))
            file.write(dword(self.width)) 
            file.write(dword(self.height))
            file.write(word(1)) # Planes
            # bits por pixel. Cuanta memoria voy a ocupar por cada pixel.
            file.write(word(24)) # 24 bits por pixel
            file.write(dword(0)) # Compression
            file.write(dword(self.width * self.height * 3)) # Image size
            # El resto se pueden quedar vacías
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # COLOR TABLE
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y])
