import tkinter as tk
import ctypes


# Function to refresh the widget
def close():
    root.destroy()


def set_background(img):
    if img:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, img, 0)
    else:
        print('Image not found!')

# Function to display JSON data in the widget
def display_data():
    pass


# Create the root window
root = tk.Tk()
root.attributes('-alpha', 0.9)
root.overrideredirect(True)

# Call function to display JSON data
display_data()

root.mainloop()
