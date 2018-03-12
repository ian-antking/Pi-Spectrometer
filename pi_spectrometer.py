import tkinter as tk
from tkinter import messagebox
import picamera
import time
from PIL import ImageTk, Image
import os
import subprocess
import io
import webbrowser


#camera settings, to be replaced by GUI menu. Use pickle to save settings between uses?
camera = picamera.PiCamera()

camera_settings = [10, 270, 1600, 6000000000]

camera.framerate= camera_settings[0]
camera.rotation = camera_settings[1]
camera.iso = camera_settings[2]
camera.shutter_speed = camera_settings[3]
camera.zoom= (0.25, 0.25, 0.5, 0.5)


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

def open_pictures_shortcut(event):
    open_pictures()

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
        sample_name = sample_input.get().strip()
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

def show_about():
    #define About window
    about = tk.Toplevel()
    about.title("about")
    about.geometry('300x300')
    name = tk.Label(about, text="Pi-Spectrometer")
    name.config(font= ('Helvetica', 28, 'bold'))
    instruction = tk.Label(about, text='For use with Raspberry Pi \n and Raspberry Pi Camera Module')

    instruction2 = tk.Label(about, text='Lego Spectrometer plans available at:')
    instruction2.configure(font='bold')
    public_lab_link = tk.Label(about, text='Public Lab', fg='blue', cursor='hand2')
    public_lab_link.configure(font='bold')

    instruction3 = tk.Label(about, text='Analyse captured spectra at:')
    instruction3.configure(font='bold')
    spectral_workbench_link = tk.Label(about, text='Spectral Workbench', fg='blue', cursor='hand2')
    spectral_workbench_link.configure(font='bold')
    
    version = tk.Label(about, text='Version: 2.1')
    author = tk.Label(about, text='Coded by Ian King')
    code = tk.Label(about, text='Powered by Python')
    ok = tk.Button(about, text='OK', command=about.destroy)
    
    name.pack()
    
    version.pack()

    instruction.pack(pady=10)

    instruction2.pack()
    public_lab_link.pack(pady=5)
    public_lab_link.bind('<Button-1>', lambda event: webbrowser.open_new(r'https://publiclab.org/w/lego-spectrometer'))

    instruction3.pack()
    spectral_workbench_link.pack(pady=5)
    spectral_workbench_link.bind('<Button-1>', lambda event: webbrowser.open_new(r'https://spectralworkbench.org'))
    author.pack()
    code.pack() 
    ok.pack()



def update_settings():
    global settings
    global entries
    global camera_settings
    
    for i in range(0, len(camera_settings)):
        camera_settings[i] = entries[i].get()

    camera.framerate = int(camera_settings[0])
    camera.rotation = int(camera_settings[1])
    camera.iso = int(camera_settings[2])
    camera.shutter_speed = int(camera_settings[3])

    status.configure(text='Camera settings updated.')
    settings.destroy()

def update_shortcut(event):
    update_settings()
    
def show_settings():
    global settings
    global entries
    global camera_settings
    settings = tk.Toplevel()
    settings.title('Settings')
    entries = []

    fields = ['Framerate (fps):', 'Rotation:', 'ISO:', 'Shutter Speed (ns):']
    #defaults = ['10', '6', '1600', '(1280, 720)', '270']

    for i in range(0,len(fields)):
        row = tk.Frame(settings)
        lab = tk.Label(row, width=15, text=fields[i], anchor=tk.W)
        ent = tk.Entry(row)
        ent.insert(tk.END, camera_settings[i])
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT)
        entries.append(ent)

    button_row = tk.Frame(settings)
    apply_settings = tk.Button(button_row, text='Apply', command = update_settings)
    cancel = tk.Button(button_row, text='Close', command = settings.destroy)

    button_row.pack(side=tk.BOTTOM, pady=5, padx=5, fill=tk.X)
    cancel.pack(side=tk.RIGHT)
    apply_settings.pack(side=tk.RIGHT)

    settings.bind('<Return>', update_shortcut)
    
root = tk.Tk()

last_spectrum = ImageTk.PhotoImage(Image.new('RGB', (1280, 50), color = 'black'))


root.title('Pi-Spectrometer')
root.geometry('1280x200')
sample_controls = tk.Frame(root)
#root.resizable(width=False, height=False)

#bind keyboard shortcuts and controls
root.bind('<space>', spacebar)
root.bind('<Escape>', esc_key)
root.bind('<Return>', capture_spectrum)

#define menubar
menubar = tk.Menu(root)

main_menu = tk.Menu(menubar, tearoff=0)
main_menu.add_command(label = "View Spectra", command=open_pictures)

main_menu.add_command(label = "Settings", command=show_settings)
main_menu.add_command(label = "About", command=show_about)
main_menu.add_separator()
main_menu.add_command(label = "Exit", command=root.destroy)

menubar.add_cascade(label='Menu', menu=main_menu)
root.configure(menu=menubar)

#define widgets
sample_instruction = tk.Label(sample_controls, text='Sample ID:')
sample_input = tk.Entry(sample_controls)
take_sample = tk.Button(sample_controls, text='Capture Spectrum', command=start_preview)
last_image = tk.Label(image=last_spectrum, cursor='hand2')
last_image.image = last_spectrum #keep reference
last_image.bind('<Button-1>', open_pictures_shortcut)
#view_spectra = tk.Button(root, text='View Spectra', command = open_pictures) #moved to cascade menu
status = tk.Label(root, text="ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)

#pack widgets
status.pack(side=tk.BOTTOM, expand=1, fill=tk.X, pady=0)
sample_controls.pack(side=tk.TOP, pady=50, padx=10)
sample_instruction.pack(side=tk.LEFT)
sample_input.pack(side=tk.LEFT)
take_sample.pack(side=tk.LEFT)
#view_spectra.pack(side=tk.RIGHT, padx=10, pady=10) #moved to cascade menu
last_image.pack()


root.mainloop()
