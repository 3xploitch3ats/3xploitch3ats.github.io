import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import shutil
import zipfile
import urllib.request
import platform

# Télécharger UPX si nécessaire
def ensure_upx():
    try:
        subprocess.run(["upx", "--version"], check=True, capture_output=True)
        return "upx"
    except FileNotFoundError:
        messagebox.showinfo("UPX manquant", "UPX sera téléchargé automatiquement.")
        system = platform.system()
        if system != "Windows":
            messagebox.showerror("Erreur", "Téléchargement automatique uniquement sur Windows.")
            return None

        url = "https://github.com/upx/upx/releases/download/v4.0.2/upx-4.0.2-win64.zip"
        zip_path = os.path.join(os.getcwd(), "upx.zip")
        extract_path = os.path.join(os.getcwd(), "upx_bin")

        try:
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            os.remove(zip_path)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur téléchargement/extraction UPX: {e}")
            return None

        # Chercher upx.exe dans le dossier extrait
        for root_dir, dirs, files in os.walk(extract_path):
            if "upx.exe" in files:
                return os.path.join(root_dir, "upx.exe")

        messagebox.showerror("Erreur", "Impossible de trouver upx.exe après extraction.")
        return None

# Sélectionner le fichier EXE
def select_exe():
    file_path = filedialog.askopenfilename(title="Sélectionner EXE", filetypes=[("Executable files", "*.exe")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

# Choisir où sauvegarder le nouveau EXE
def save_as():
    orig = entry_file.get()
    if not orig:
        messagebox.showerror("Erreur", "Sélectionner un EXE d'abord.")
        return

    dir_name = os.path.dirname(orig)
    base = os.path.splitext(os.path.basename(orig))[0]
    default_name = base + "_X.exe"

    save_path = filedialog.asksaveasfilename(title="Enregistrer EXE compressé", initialdir=dir_name,
                                             initialfile=default_name, defaultextension=".exe",
                                             filetypes=[("Executable files", "*.exe")])
    if save_path:
        entry_save.delete(0, tk.END)
        entry_save.insert(0, save_path)

# Compresser l'EXE avec UPX
def compress_exe():
    exe_path = entry_file.get()
    save_path = entry_save.get()
    method = compression_var.get()

    if not exe_path or not save_path:
        messagebox.showerror("Erreur", "Fichier EXE et destination requis.")
        return

    upx = ensure_upx()
    if not upx:
        return

    try:
        shutil.copy2(exe_path, save_path)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de copier l'EXE : {e}")
        return

    # Choisir l'option de compression
    if method == "best":
        args = [upx, "--best", "--force", save_path]
    else:  # store
        args = [upx, "--store", save_path]

    try:
        subprocess.run(args, check=True)
        messagebox.showinfo("Succès", f"EXE compressé ({method}) : {save_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur compression : {e}")

# GUI
root = tk.Tk()
root.title("Compresser EXE avec UPX")

tk.Label(root, text="Fichier EXE:").grid(row=0, column=0, padx=5, pady=5)
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Ouvrir", command=select_exe).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Sauvegarder en:").grid(row=1, column=0, padx=5, pady=5)
entry_save = tk.Entry(root, width=50)
entry_save.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Enregistrer sous", command=save_as).grid(row=1, column=2, padx=5, pady=5)

compression_var = tk.StringVar(value="best")
tk.Radiobutton(root, text="Best (max compression, peut échouer)", variable=compression_var, value="best").grid(row=2, column=0, columnspan=3, sticky="w", padx=10)
tk.Radiobutton(root, text="Store (rapide, sûr)", variable=compression_var, value="store").grid(row=3, column=0, columnspan=3, sticky="w", padx=10)

tk.Button(root, text="Compresser EXE", command=compress_exe, bg="green", fg="white").grid(row=4, column=0, columnspan=3, pady=10)

root.mainloop()
