#!/usr/bin/env python

"""
  ----------------------------- DISCLAIMER --------------------------------
  -------------------------------------------------------------------------
           THIS IS THE ORIGINAL PROTOTYPE OF A WORKING PHOTOCALL,
       USE THIS ON A YOUR OWN RISK, SOME BUGS ARE KNOWN IN THE CODE,
   YOU POTENTIALLY WILL LOSE DATA, DON'T USE IN A PRODUCTION ENVIRONMENT.
            SOME IMPROVEMENT AND COMPLETE REFACTORING IS NEEDED
                 TO ACOMPLISH WITH GOOD PRACTICE STANDARDS.
  -------------------------------------------------------------------------
                     PHOTOCALL_PY BY Jaime Iranzo Ferri
"""

# Base system to render photo carousel
import pygame

# For time calculations
import time
from datetime import datetime

# For calculate memory consumption
import sys

# For manage DSLR cameras
from sh import gphoto2 as gp

# TODO: _______
import signal
import subprocess
# multithread
import threading
import queue

# Import os to work with paths and files
import os
import os.path # <-- ???

# Random number generation
import random


# Initialize all imported pygame modules
pygame.init()


# Directory where the photos will be saved
gallery_path = './gallery/'
save_location = './gallery/'
amount_photo_take_global = 0
max_photo_take = 3


""" Abstraer todo esto para poder reutilizar el código en otra aplicación """
""" --------------------------------------------------------------------- """

#Para leer el arduino button led
import serial, time
arduino = None
if os.path.exists('/dev/ttyUSB0'): # TODO <-- Trasladar a un fichero de configuración o una base de datos
  arduino = serial.Serial('/dev/ttyUSB0', 9600)

rawString = None

last_photo_load = 0

import serial.tools.list_ports
myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
#print(myports)

arduino_port = [port for port in myports if 'FT232R USB UART' in port ][0]

def check_presence(arduino_port, interval=0.1):
  while True:
    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    if arduino_port not in myports:
      print("Arduino has been disconnected!")
      #arduino_queue.put = None #TODO: Create Queue
    time.sleep(interval)


""" --------------------------------------------------------------------- """
""" --------------------------------------------------------------------- """



import threading
port_controller = threading.Thread(target=check_presence, args=(arduino_port, 0.1,))
port_controller.setDaemon(True)
port_controller.start()

#os._exit(0)

#from time import sleep
#from datetime import datetime
#import logging
#from sh import gphoto2 as gp
#import signal, os, subprocess
#import os.path


#Parametros que se le pasan a gphoto2:
#shot_date = datetime.now().strftime("%Y%m%d%H%M%S")
#gphoto2_command = ["--capture-image-and-download", "--force-overwrite", "--filename=" + shot_date + ".JPG"]

#Crea un directorio para guardar las fotos
def createSaveFolder(folder):
  #Comprueba si el directorio existe, si no lo crea
  if not os.path.exists(folder):
    try:
      #https://docs.python.org/2/library/os.html#os.makedir
      os.makedirs(folder, mode=0o755)
    except:
      print("Failed to create directory: " + folder)
      os._exit(1)
  if not os.path.exists(folder):
    #os.chdir(folder)
    os._exit(1)
    
createSaveFolder(gallery_path)




#Para montar el pendrive
#from sh import sudo, mount, umount, mountpoint
import sh

pendrive = '/dev/sda1'

if os.path.exists(pendrive) and os.path.exists(gallery_path):
  try:
    sh.sudo.mountpoint(gallery_path)
    print("El pendrive ya esta montado.")
  except:
    try:
      sh.sudo.mount(pendrive, gallery_path)
    except:
      print("Imposible montar el pendrive!")
      os._exit(-1)





###################################################
##################~~ FICHEROS ~~###################
###################################################

files_found = 0
array_filenames = []
#Lista todos los ficheros de la galeria
def file_load(directory, array_filenames): ##Falta ordenar la salida, es necesario!!
    files_found = 0
    for dirname, dirnames, filenames in os.walk(directory):
        # print path to all subdirectories first.
        #for subdirname in dirnames:
        #    print(os.path.join(dirname, subdirname))

        # print path to all filenames.
        for count, filename in enumerate(filenames):
            array_filenames.append(os.path.join(dirname, filename))
            #Imprime el array de ficheros que ha encontrado:
            print(array_filenames[count])

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.svn' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.svn')

    #Cantidad de ficheros encontrados

    files_found = len(array_filenames)
    print( str(files_found) + " ficheros encontrados." )
#    array_filenames = array_filenames.sort()
#    for count, filename in enumerate(array_filenames):
#        print("Sorted filenames[" + str(count) + "]: " + str(filename))
    return array_filenames, files_found

###################################################
###################################################

try:
  screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
except:
  print("No hay X!")
  os._exit(1)
  
#Esconde el cursor del raton
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
done = False

#Resoluciion de la pantalla (Calculado al arrancar, dinamico)
screen_resolution = screen.get_size()

###################################################
###################################################

###################################################
##############~~ CAPTURAR REFLEX ~~################
###################################################

#shot_date = datetime.now().strftime("%Y%m%d%H%M%S")

# Kill the gphoto process that starts
# whenever we turn on the camera or
# reboot the raspberry pi

def killGphoto2Process():
  p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
  out, err = p.communicate()

  # Search for the process we want to kill
  for line in out.splitlines():
    if b'gvfsd-gphoto2' in line:
      # Kill that process!
      pid = int(line.split(None,1)[0])
      os.kill(pid, signal.SIGKILL)

ready_shot_queue = queue.Queue()
takea_shot_queue = queue.Queue()
array_filenames_queue = queue.Queue()
ready_shot_queue.put(False)
takea_shot_queue.put(False)
def captureImages(ready_shot_queue, takea_shot_queue, array_filenames_queue, files_found, last_photo_load):
  while True:
    try:
      ready_shot = ready_shot_queue.get(timeout=0.01)
    except queue.Empty:
      pass
    if ready_shot:
      shot_date = datetime.now().strftime("%Y%m%d%H%M%S") #TODO: Convertir a numero.
      command = ["--debug", "--debug-logfile=my-logfile.txt", "--capture-image-and-download", "--force-overwrite", "--filename=" + save_location + shot_date + ".JPG"]
      createSaveFolder(save_location)
      try:
        gp(command)
        if not os.path.isfile(save_location + shot_date + ".JPG"):
          print("Failed to locate file: " + save_location + shot_date + ".JPG")
        else:
          print("Saved succesfully: " + save_location + shot_date + ".JPG")
          array_filenames_queue.put(os.path.join(save_location, shot_date + ".JPG"))
          print("Foto: " + save_location + shot_date + ".JPG anadida con exito al array!")
          #files_found = len(array_filenames)
          #last_photo_load = len(array_filenames) - 2
          #print( str(files_found) + " ficheros encontrados." )
          #return array_filenames, files_found, last_photo_load
          takea_shot_queue.put(True)
      except:
        print("Failed to capture command.")
      ready_shot_queue.put(False)
    time.sleep(0.01)
    

camera_controller = threading.Thread(target=captureImages, args=(ready_shot_queue, takea_shot_queue, array_filenames_queue, files_found, last_photo_load,))
camera_controller.setDaemon(True)
camera_controller.start()

#def checkfile(save_location, shot_date):
  #if os.path.isfile(save_location + shot_date + ".JPG"):
    #print("Saved succesfully: " + save_location + shot_date + ".JPG")
    #return 0
  #else:
    #print("Failed to locate file: " + save_location + shot_date + ".JPG")
    #return -1

killGphoto2Process()

#def shottt(save_location, array_filenames):




#lock = threading.Lock()
#def photo_shot(amount_photo_take, done):
    #while not done:
        #if amount_photo_take >= 1:
            #print("Haciendo foto. Sonrie!")
            #if amount_photo_take > max_photo_take:
                #with lock:
                    #amount_photo_take_global = max_photo_take
            #try:
                ##os.chdir("../") #TODO: Esto no mola nada.
                #shot_date = datetime.now().strftime("%Y%m%d%H%M%S")
                #gphoto2_command = ["--capture-image-and-download", "--force-overwrite", "--filename=" + gallery_path + "/" + shot_date + ".JPG"]
                #gp(gphoto2_command)
                #with lock:
                    #amount_photo_take_global -= 1
            #except:
                #print("Failed to take a photo.")

#TODO: Necesario RTC para poder nombrar correctamente:
##thread_shot = threading.Thread(photo_shot(amount_photo_take))
##thread_shot.start()
##thread_shot.join()


###################################################
###################~~ FUENTES ~~################### OK
###################################################

def make_font(fonts, size):
    available = pygame.font.get_fonts()
    # get_fonts() returns a list of lowercase spaceless font names
    choices = map(lambda x:x.lower().replace(' ', ''), fonts)
    for choice in choices:
        if choice in available:
            return pygame.font.SysFont(choice, size)
    return pygame.font.Font(None, size)

_cached_fonts = {}
def get_font(font_preferences, size):
    global _cached_fonts
    key = str(font_preferences) + '|' + str(size)
    font = _cached_fonts.get(key, None)
    if font == None:
        font = make_font(font_preferences, size)
        _cached_fonts[key] = font
    return font

_cached_text = {}
def create_text(text, fonts, size, color):
    global _cached_text
    key = '|'.join(map(str, (fonts, size, color, text)))
    image = _cached_text.get(key, None)
    if image == None:
        font = get_font(fonts, size)
        image = font.render(text, True, color)
        _cached_text[key] = image
    return image

##pygame.init()
##screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
##done = False

font_preferences = [
        "Bizarre-Ass Font Sans Serif",
        "They definitely dont have this installed Gothic",
        "Papyrus",
        "Comic Sans MS"]

#text = create_text("W:" + str(screen.get_width()) + ", H:" + str(screen.get_height()) + ", S:" + str(screen.get_size()), font_preferences, 72, (0, 128, 0))

###################################################
###################################################

###################################################
###############~~ CARGA DINAMICA ~~################
###################################################

#Setea las dos posiciones y asi no hay desbordamiento de memoria
image = [0, 0]
sizeof_image = [0, 0]
#array_fotos = [0, 0]

save_location_error = './gallery_error/'

#Carga una foto:
def photo_load(image, array_filenames, photo_number, files_found):
  for count in [0, 1]:
    #Revisamos si el array contiene datos en esa posicion
    gotdata = ""
    try:
      print("Cargando foto...")
      gotdata = array_filenames[photo_number]
    except IndexError:
      print("ERROR: list index out of range, next!")
      gotdata = ""
    if gotdata:
      #Comprobamos si se puede cargar la foto
      try:
        image[count] = pygame.image.load(array_filenames[photo_number])

        #Escalado de foto encajado al ancho y respetando la relacion de aspecto de la foto, para no deformar ni excluir a nadie, jj
        photo_resolution = image[count].get_rect().size
        photo_aspect_ratio = photo_resolution[0] / photo_resolution[1]

        photo_new_resolution_width = int(screen_resolution[0] + fact)
        photo_new_resolution_height = int(photo_resolution[1] * (screen_resolution[0] + fact) / photo_resolution[0])

        photo_new_resolution = [ photo_new_resolution_width, photo_new_resolution_height ]

        ##image[count] = pygame.transform.scale(image[count], photo_new_resolution) #---------------------> Probar rendimiento
        image[count] = pygame.transform.smoothscale(image[count], photo_new_resolution).convert()

        #Lo que ocupa en memoria cada elemento de la lista
        sizeof_image[count] = sys.getsizeof(image[count])

        #Imprimiendo informacion relevante
        print(str(photo_number) + " - Loading[" + array_filenames[photo_number] + "] - " + str(photo_resolution[0]) + "x" + str(photo_resolution[1]) + " --> " + str(photo_new_resolution[0]) + "x" + str(photo_new_resolution[1]) + " - " + str(sizeof_image[count]) + " bytes")
      except:
        #Si no se puede cargar por lo que sea, se mueve a otro directorio
        createSaveFolder(save_location_error)
        print(str(photo_number) + " - ERROR[" + array_filenames[photo_number] + "]")
        try:
          if not os.path.isfile(save_location_error + os.path.basename(array_filenames[photo_number])):
            os.rename(array_filenames[photo_number], save_location_error + os.path.basename(array_filenames[photo_number]))
          else:
            random_name = random.randint(1000,9999)
            os.rename(array_filenames[photo_number], save_location_error + str(random_name) + os.path.basename(array_filenames[photo_number]))
          array_filenames.remove(array_filenames[photo_number])
        except:
          print("Failed to move photo ERROR: " + save_location_error + str(os.path.basename(array_filenames[photo_number])))
      if photo_number == (files_found - 1):
        photo_number = 0
      else:
        photo_number += 1


##Descarga una foto:
#def photo_unload(image, last_photo_load):
#    print("Unloading[" + str(last_photo_load - 1) + "]: ")
#    del image[last_photo_load - 1]

###################################################
###################################################

##Tiempo de visualizacion de cada foto
time_photo = 1000

##Escaneo inicial de ficheros en la galeria
#array_filenames, files_found = file_load(gallery_path, array_filenames)

recent_photo = None

x_pos = 0
y_pos = 0
screen_width = screen.get_width()
screen_height = screen.get_height()
vel = 120 #Recomendado: 90
fact = -0.5

current_millis = int(round(time.time() * 1000))
current_millis_now = lambda: int(round(time.time() * 1000))

count_frames = 0
fps = 120

###################################################
#####################~~ MAIN ~~####################
###################################################
#def event_handler(current_millis, done):
    #while not done:
        #for event in pygame.event.get():
            #if event.type == pygame.QUIT:
                #done = True
            #elif event.type == pygame.KEYDOWN:
                #if event.key == pygame.K_ESCAPE:
                    #done = True
                #if event.key == pygame.K_SPACE:
                    #current_millis = current_millis_now()
        #time.sleep(0.2)
    #return done

#event_thread = threading.Thread(target=event_handler, args=(current_millis, done,))
#event_thread.start()

#thread_shot = threading.Thread(target=photo_shot, args=(amount_photo_take_global, done,))
#thread_shot.start()

print("READY!")
#Escaneo inicial de ficheros en la galeria
array_filenames, files_found = file_load(gallery_path, array_filenames)

while not done:
    while not done:
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            done = True
          elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
              done = True
            if event.key == pygame.K_SPACE:
              current_millis = current_millis_now()
            if event.key == pygame.K_RETURN:
              #shottt(save_location, array_filenames)
              print("[Keyboard] Nueva solicitud! Capturas pendientes:")
                #with lock:
                    #amount_photo_take_global += 1
                    #print("[Keyboard] Nueva solicitud! Capturas pendientes:" + str(amount_photo_take_global))
                    
        # FOTO ARDUINO BUTTON LED
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if arduino:
          try:
            takea_shot = takea_shot_queue.get(timeout=0.01)
          except queue.Empty:
            pass
          while arduino.in_waiting:
            white = (255,255,255)
            screen.fill((white))
            pygame.display.update()
            rawString = arduino.readline()
          if rawString:
            print("Arduino button led dice: " + str(rawString))
            ready_shot_queue.put(True)
          if takea_shot:
            takea_shot_queue.put(False)
            try:
              recent_photo = array_filenames_queue.get(timeout=0.01)
            except:
              pass
            if recent_photo:
              array_filenames.append(recent_photo)
              files_found = len(array_filenames)
              last_photo_load = len(array_filenames) - 2
              print( str(files_found) + " ficheros encontrados." )
              photo_load(image, array_filenames, last_photo_load, files_found)
              last_photo_load += 1
              x_pos = screen_width
              current_millis = int(round(time.time() * 1000)) + time_photo
              fact = 0.2
            else:
              print("Foto: " + save_location + shot_date + ".JPG no anadida al array!")
          rawString = None
          
        #Momento de descargar una foto y cargar nueva:
        if current_millis_now() >= current_millis:
            print("Siguiente diapositiva a cargar: " + str(last_photo_load))
            photo_load(image, array_filenames, last_photo_load, files_found)
            ##TODO: Manejar error
            last_photo_load += 1
            x_pos = screen_width
            current_millis = int(round(time.time() * 1000)) + time_photo
            fact = 0.2

    #    #text = create_text("LOOP: " + str(str(count_frames)), font_preferences, 30, (0, 128, 0))
    #    text = create_text("[" + str(int(clock.get_fps())) + "]", font_preferences, 30, (255, 255, 0))

        #Momento de resetear el carrete, llego a su fin
        if last_photo_load >= files_found:
            last_photo_load = 0
            x_pos = screen_width

        #Movimiento en el eje x
        if x_pos > 0:
            x_pos -= vel
            #fact += fact
        #La posicion no puede ser menor a 0
        if x_pos < 0:
            x_pos = 0

        #print("Loop: " + str(count_frames))
        #print("loaded_photos_total: " + str(loaded_photos_total))
        count_frames += 1

        #Actualizamos el display
        screen.blit(image[0], ((x_pos - screen_width),y_pos))
        screen.blit(image[1], (x_pos, y_pos))
        #screen.blit(text, (320 - text.get_width() // 2, 240 - text.get_height() // 2))
        ##  pygame.display.flip() #O .update, hacer pruebas.

        pygame.display.update()

        #Limitador de FPS
        clock.tick(fps)


#Saliendo de todo
print("Bye bye!")

#thread_shot.join()
if arduino:
  arduino.close()
pygame.quit()

##emerge -av dev-python/sh

# Fuente - Principal:              https://www.pygame.org
# Fuente - Cycling between JPEGs:  https://www.raspberrypi.org/forums/viewtopic.php?t=11990
# Fuente - Fonts and Text:         https://nerdparadise.com/programming/pygame/part5
# Fuente - Threads:                https://pymotw.com/2/threading/
# Fuente - Events:                 https://stackoverflow.com/questions/42215932/two-for-event-in-pygame-event-get
