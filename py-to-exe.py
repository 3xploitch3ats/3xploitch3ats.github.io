import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
import shutil

def ensure_pyinstaller():
    """Installe PyInstaller si nécessaire."""
    try:
        import PyInstaller
        return True
    except ImportError:
        response = messagebox.askyesno(
            "PyInstaller manquant",
            "PyInstaller n'est pas installé. Voulez-vous l'installer maintenant ?"
        )
        if response:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"])
                return True
            except subprocess.CalledProcessError:
                messagebox.showerror("Erreur", "Échec de l'installation de PyInstaller.")
                return False
        else:
            return False

def select_python_file():
    file_path = filedialog.askopenfilename(
        title="Sélectionner un fichier Python",
        filetypes=[("Python files", "*.py")]
    )
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def save_as_exe():
    save_path = filedialog.asksaveasfilename(
        title="Nom du fichier EXE",
        defaultextension=".exe",
        filetypes=[("Executable files", "*.exe")]
    )
    if save_path:
        entry_save.delete(0, tk.END)
        entry_save.insert(0, save_path)

def convert_to_exe():
    if not ensure_pyinstaller():
        return

    py_file = entry_file.get()
    exe_file = entry_save.get()

    if not py_file or not exe_file:
        messagebox.showerror("Erreur", "Sélectionnez le fichier Python et le nom du fichier EXE.")
        return

    dist_dir = os.path.dirname(exe_file)
    exe_name = os.path.splitext(os.path.basename(exe_file))[0]

    # Commande PyInstaller
    command = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--distpath", dist_dir,
        "--name", exe_name,
        py_file
    ]

    try:
        subprocess.run(command, check=True)

        # Nettoyage des fichiers temporaires
        spec_file = os.path.splitext(py_file)[0] + ".spec"
        build_dir = os.path.join(os.getcwd(), "build")
        if os.path.exists(spec_file):
            os.remove(spec_file)
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        messagebox.showinfo("Succès", f"EXE créé avec succès dans : {dist_dir}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Échec de la création de l'EXE :\n{e}")

# Fenêtre Tkinter
root = tk.Tk()
root.title("Python → EXE")

tk.Label(root, text="Fichier Python:").grid(row=0, column=0, padx=5, pady=5)
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Parcourir", command=select_python_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Sauvegarder en EXE:").grid(row=1, column=0, padx=5, pady=5)
entry_save = tk.Entry(root, width=50)
entry_save.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Parcourir", command=save_as_exe).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Convertir en EXE", command=convert_to_exe, bg="green", fg="white").grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()
