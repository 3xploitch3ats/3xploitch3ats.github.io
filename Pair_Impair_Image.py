import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

class PixelAdjusterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ajusteur Pixel Pair/Impair")
        self.geometry("500x250")

        self.image_path = None
        self.image = None

        tk.Label(self, text="Image :").pack(pady=5)
        self.path_label = tk.Label(self, text="Aucune image sélectionnée")
        self.path_label.pack()

        tk.Button(self, text="Choisir une image", command=self.choose_image).pack(pady=5)

        tk.Label(self, text="Ajuster largeur et hauteur en :").pack(pady=5)
        self.var_mode = tk.StringVar(value="pair")
        tk.Radiobutton(self, text="Pair", variable=self.var_mode, value="pair").pack()
        tk.Radiobutton(self, text="Impair", variable=self.var_mode, value="impair").pack()

        tk.Button(self, text="Appliquer", command=self.apply_adjustment).pack(pady=10)

    def choose_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if path:
            self.image_path = path
            self.image = Image.open(path).convert("RGBA")  # pour transparence
            self.path_label.config(text=path)

    def apply_adjustment(self):
        if not self.image:
            messagebox.showerror("Erreur", "Veuillez choisir une image")
            return

        width, height = self.image.size
        mode = self.var_mode.get()

        def adjust(value):
            if mode == "pair":
                return value + (value % 2)  # ajoute 1 si impair
            else:
                return value - (1 if value % 2 == 0 else 0)  # enlève 1 si pair

        new_width = adjust(width)
        new_height = adjust(height)

        if new_width == width and new_height == height:
            messagebox.showinfo("Info", "L'image a déjà la dimension désirée")
            return

        # Créer une nouvelle image transparente
        new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
        new_image.paste(self.image, (0, 0))  # coller l'image originale

        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if save_path:
            new_image.save(save_path)
            messagebox.showinfo("Succès", f"Image sauvegardée : {save_path}")

if __name__ == "__main__":
    app = PixelAdjusterApp()
    app.mainloop()
