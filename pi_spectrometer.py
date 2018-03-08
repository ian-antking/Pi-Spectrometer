import tkinter as tk
from tkinter import messagebox
import picamera
import time
from PIL import ImageTk, Image
import os
import subprocess
import io
from threading import Thread

camera = picamera.PiCamera(framerate = 10)

camera.rotation = 270
camera.iso = 1600
camera.shutter_speed = 6000000000
camera.zoom= (0.25, 0.25, 0.5, 0.5)
camera.resolution = (1280,720)

global preview_active
preview_active = False

spectra_directory = '/home/pi/Pictures/pi_spectrometer'
upload_directory = '/home/pi/Pictures/pi_spectrometer/processed_spectra'

if not os.path.exists(spectra_directory):
    os.makedirs(spectra_directory)

if not os.path.exists(upload_directory):
    os.makedirs(upload_directory) 

def open_pictures():
    subprocess.call(['xdg-open', spectra_directory])

def capture_spectrum(event):
    start_preview()

def start_preview():
    
    if not sample_input.get():
        messagebox.showerror('error','You must enter a sample ID')
        root.focus_set()
    else:
        crosshair = Image.new('RGB', (2000,1), color='white')
        camera.start_preview(alpha = 128)
        camera.annotate_text = '[esc] to exit, [space] to capture'
        global o
        o = camera.add_overlay(crosshair.tobytes(), size=(1280,1), layer=3, alpha=128, format='rgba')
        #camera.preview.alpha = 125
        global preview_active
        preview_active = True


        
def spacebar(event):
    global preview_active
    if preview_active:
        sample_name = sample_input.get()
        global spectra_directory
        global upload_directory
        stream=io.BytesIO()
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
        new_spectrum = ImageTk.PhotoImage(Image.open(spectrum_path))
        last_image.configure(image = new_spectrum)
        last_image.image = new_spectrum #keep reference
        camera.stop_preview()
        camera.remove_overlay(o)
        status.configure(text = 'Spectrum saved to: %s' % spectrum_path)
        preview_active=False
        
    
def esc_key(event):
    global preview_active
    if preview_active:
        camera.stop_preview()
        camera.remove_overlay(o)
        preview_active=False
        
        
root = tk.Tk()

last_spectrum = ImageTk.PhotoImage(Image.new('RGB', (1280, 50), color = 'black'))


root.title('Pi-Spectrometer')
root.geometry('1280x200')
sample_controls = tk.Frame(root)

root.bind('<space>', spacebar)
root.bind('<Escape>', esc_key)
root.bind('<Return>', capture_spectrum)

sample_instruction = tk.Label(sample_controls, text='Sample ID:')
sample_input = tk.Entry(sample_controls)
take_sample = tk.Button(sample_controls, text='Capture Spectrum', command=start_preview)
last_image = tk.Label(image=last_spectrum)
last_image.image = last_spectrum
view_spectra = tk.Button(root, text='View Spectra', command = open_pictures)
status = tk.Label(root, text="ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)

status.pack(side=tk.BOTTOM, expand=1, fill=tk.X, pady=0)
sample_controls.pack(side=tk.TOP, pady=50, padx=10)
sample_instruction.pack(side=tk.LEFT)
sample_input.pack(side=tk.LEFT)
take_sample.pack(side=tk.LEFT)
view_spectra.pack(side=tk.RIGHT, padx=10, pady=10)
last_image.pack()




root.mainloop()
