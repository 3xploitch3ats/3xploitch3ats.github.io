import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import time

log_file = "drag_log.txt"

def log_position(x, y):
    message = f"Window position: x={x}, y={y}"
    print(message)
    with open(log_file, "a") as f:
        f.write(message + "\n")

# Open file dialog
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Open Image", filetypes=[("PNG Images", "*.png")])
if not file_path:
    print("No file selected. Exiting...")
    time.sleep(2)
    exit()

# Load image with alpha
img = Image.open(file_path).convert("RGBA")
# Make white fully transparent
datas = img.getdata()
newData = []
for item in datas:
    if item[0] > 240 and item[1] > 240 and item[2] > 240:  # white threshold
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)
img.putdata(newData)
tk_img = ImageTk.PhotoImage(img)

# Transparent borderless window
window = tk.Toplevel()
window.overrideredirect(True)  # no title bar
window.geometry(f"{img.width}x{img.height}+100+100")
window.wm_attributes("-topmost", True)
window.wm_attributes("-transparentcolor", "white")  # treat white as transparent

# Canvas to display image
canvas = tk.Canvas(window, width=img.width, height=img.height, highlightthickness=0, bg="white")
canvas.pack()
img_id = canvas.create_image(0, 0, image=tk_img, anchor="nw")

# Drag window logic
def start_drag(event):
    window.data = {"x": event.x_root, "y": event.y_root, "winx": window.winfo_x(), "winy": window.winfo_y()}

def do_drag(event):
    dx = event.x_root - window.data["x"]
    dy = event.y_root - window.data["y"]
    new_x = window.data["winx"] + dx
    new_y = window.data["winy"] + dy
    window.geometry(f"+{new_x}+{new_y}")
    log_position(new_x, new_y)

canvas.bind("<Button-1>", start_drag)
canvas.bind("<B1-Motion>", do_drag)

print("Drag the image (window moves with it). Close window to exit.")
window.mainloop()
print("Program finished.")
