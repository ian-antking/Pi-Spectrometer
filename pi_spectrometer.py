import tkinter as tk
from tkinter import messagebox
import picamera
import time
from PIL import ImageTk, Image
import os
import subprocess
import io



#camera setting, to be replaced by GUI menu. Use pickle to save settings between uses?
camera = picamera.PiCamera(framerate = 10)
camera.rotation = 270
camera.iso = 1600
camera.shutter_speed = 6000000000
camera.zoom= (0.25, 0.25, 0.5, 0.5)
camera.resolution = (1280,720)

#track if camera preview is running
global preview_active
preview_active = False

#set directories to save images
spectra_directory = '/home/pi/Pictures/pi_spectrometer'
upload_directory = '/home/pi/Pictures/pi_spectrometer/processed_spectra'

#make sure image directories exist. If not, make them
if not os.path.exists(spectra_directory):
    os.makedirs(spectra_directory)

if not os.path.exists(upload_directory):
    os.makedirs(upload_directory) 

def open_pictures():
    subprocess.call(['xdg-open', spectra_directory])

#allow keyboard to initiate camera capture    
def capture_spectrum(event):
    #make sure capture can't be initaited twice before completion.
    global preview_active
    if not preview_active:
        start_preview()

    
def start_preview():
    #check for sample ID, if not throw error window. Add extra validation to check for illegal characters?    
    global o
    global preview_active
    if not sample_input.get():
        messagebox.showerror('error','You must enter a sample ID')
        root.focus_set()
    else:
        #generate crosshair image
        crosshair = Image.new('RGB', (2000,1), color='white')
        camera.start_preview()
        camera.annotate_text = '[esc] to exit, [space] to capture'
        #add crosshair guide to camera preview
        o = camera.add_overlay(crosshair.tobytes(), size=(1280,1), layer=3, alpha=128, format='rgba')
        #camera.preview.alpha = 125 #used during development in case of error during camera preview. Add as setting option?
        #enable spacebar and escape keybidings
        preview_active = True


        
def spacebar(event):
    global preview_active
    global spectra_directory
    global upload_directory
    #check to see if camera is active before attempting image capture
    if preview_active:
        #get sampel name
        sample_name = sample_input.get()
        #open io stream. Need to close afterwards?
        stream=io.BytesIO()
        #capture to stream as png
        camera.capture(stream, format='png')
        #convert stream to PIL image
        img = Image.open(stream)
        #generate save path for finished spectrum
        spectrum_path = '%s/%s.png' % (spectra_directory, sample_name)
        #generate save path for pixel row (for future spectral workbench api uploading. Remove from version until API implimented?)
        upload_path = '%s/%s_upload.png' % (upload_directory, sample_name)
        #get image width (shold be 1280 but may change based on user preference)
        img_width = img.size[0]
        #determine where the middle row of pixels is
        half_height = img.size[1]/2
        #extract middle row of pixels
        img2 = img.crop((0, half_height, img_width, half_height + 1))
        #close original captured image 
        img.close()
        #expand pixel row to user readable spectrum
        img3 = img2.resize((1280,50))
        #save spectrum
        img3.save(spectrum_path)
        #save pixel row for saving data size during uploads
        img2.save(upload_path)
        #close images
        img2.close()
        img3.close()
        #set spectrum to tkinter useable image
        new_spectrum = ImageTk.PhotoImage(Image.open(spectrum_path))
        #display image in main window
        last_image.configure(image = new_spectrum)
        last_image.image = new_spectrum #keep reference
        #stop camera preview and remove overlay
        camera.stop_preview()
        camera.remove_overlay(o)
        #update status bar
        status.configure(text = 'Spectrum saved to: %s' % spectrum_path)
        #disable space and escape keybindings
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

#bind keyboard shortcuts and controls
root.bind('<space>', spacebar)
root.bind('<Escape>', esc_key)
root.bind('<Return>', capture_spectrum)

#define widgets
sample_instruction = tk.Label(sample_controls, text='Sample ID:')
sample_input = tk.Entry(sample_controls)
take_sample = tk.Button(sample_controls, text='Capture Spectrum', command=start_preview)
last_image = tk.Label(image=last_spectrum)
last_image.image = last_spectrum #keep reference
view_spectra = tk.Button(root, text='View Spectra', command = open_pictures)
status = tk.Label(root, text="ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)

#pack widgets
status.pack(side=tk.BOTTOM, expand=1, fill=tk.X, pady=0)
sample_controls.pack(side=tk.TOP, pady=50, padx=10)
sample_instruction.pack(side=tk.LEFT)
sample_input.pack(side=tk.LEFT)
take_sample.pack(side=tk.LEFT)
view_spectra.pack(side=tk.RIGHT, padx=10, pady=10)
last_image.pack()




root.mainloop()
