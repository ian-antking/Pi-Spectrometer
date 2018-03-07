import picamera
import time
from PIL import Image
from guizero import *
import os
import subprocess
import io

camera = picamera.PiCamera(framerate = 10)

camera.rotation = 270
camera.iso = 1600
camera.shutter_speed = 6000000000
camera.zoom= (0.25, 0.25, 0.5, 0.5)
camera.resolution = (1280,720)

spectra_directory = '/home/pi/Pictures/pi_spectrometer'
upload_directory = '/home/pi/Pictures/pi_spectrometer/processed_spectra'

if not os.path.exists(spectra_directory):
    os.makedirs(spectra_directory)

if not os.path.exists(upload_directory):
    os.makedirs(upload_directory) 

            
def open_pictures():
    subprocess.call(['xdg-open', spectra_directory])

    
def start_preview():
    sample_name = sample_input.value
    if sample_input.value and sample_input.value.strip():

        crosshair = Image.new('RGB', (2000,1), color='white')
        camera.start_preview()
        #camera.annotate_text = '[space] to capture, [esc] to cancel'
    
        o = camera.add_overlay(crosshair.tobytes(), size=(1280,1), layer=3, alpha=128, format='rgba')
        
        #camera.preview.alpha = 70


        stream=io.BytesIO()
        time.sleep(30)
        camera.capture(stream, format='png')
        img = Image.open(stream)
        spectrum_path = '%s/%s.png' % (spectra_directory, sample_name)
        upload_path = '%s/%s_upload.png' % (upload_directory, sample_name)
        img_width = img.size[0]
        half_height = img.size[1]/2
        img2 = img.crop((0, half_height, img_width, half_height + 1))
        img.close() 
        img3 = img2.resize((1280,50))
        img3.save(spectrum_path)
        img2.save(upload_path)
        img2.close()
        img3.close()
        last_image.value = spectrum_path
        last_action.value = 'Spectrum saved to: %s' % spectrum_path
        camera.stop_preview()
        camera.remove_overlay(o)  
        sample_input.clear()
        
       
    else:
        warn("error","Please enter a sample name!")



app = App(title="Pi-Spectrometer", layout="grid", width=1280, height = 155)

welcome = Text(app, text='', grid = [0,0,2,1])

sample_instruction = Text(app, text='Sample ID:', grid=[0,1], align='right')

sample_input = TextBox(app, text="", grid = [1,1], align = 'left',)

sample_input.width = 20

take_image = PushButton(app, command=start_preview, text='Take Reading', grid=[2,1], align='left')

placeholder = Image.new('RGB', (1280, 50), color = 'black')
placeholder.save('%s/placeholder.png' % spectra_directory)
last_image = Picture(app, '%s/placeholder.png' % spectra_directory, grid=[0,3,3,1])


show_files = PushButton(app, text='Show Files', command = open_pictures, grid=[2,4], align='right')
last_action = Text(app, text='Please enter a sample ID', align='left', grid=[0,4])

app.display()

