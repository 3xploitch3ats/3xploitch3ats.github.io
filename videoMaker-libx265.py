import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import tempfile
import json
import threading
import random
import string

CONFIG_FILE = "config.json"

class VideoCreatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Créateur de vidéo H.265 (libx265) - Qualité maximale")
        self.geometry("850x650")

        self.ffmpeg_path = ""
        self.image_files = []

        self.load_config()

        # ---------------- FFmpeg ----------------
        tk.Label(self, text="FFmpeg.exe :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ffmpeg_label = tk.Label(
            self, 
            text=self.ffmpeg_path or "Aucun fichier sélectionné", 
            fg="green" if self.ffmpeg_path else "red", 
            wraplength=650, anchor="w", justify="left"
        )
        self.ffmpeg_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        tk.Button(self, text="Choisir ffmpeg.exe", command=self.choose_ffmpeg).grid(row=0, column=2, padx=5, pady=5)

        # ---------------- Images ----------------
        tk.Label(self, text="Ajouter des images :").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.images_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, width=80, height=10)
        self.images_listbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        tk.Button(btn_frame, text="Ajouter images", command=self.add_images).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Supprimer sélectionnées", command=self.remove_selected_images).grid(row=0, column=1, padx=5)

        # ---------------- Durée par image ----------------
        tk.Label(self, text="Durée par image (secondes) :").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.duration_entry = tk.Entry(self, width=10)
        self.duration_entry.insert(0, "5")
        self.duration_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # ---------------- Nom de sortie ----------------
        tk.Label(self, text="Nom du fichier de sortie :").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.output_entry = tk.Entry(self, width=50)
        self.output_entry.insert(0, "output.mp4")
        self.output_entry.grid(row=5, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        # ---------------- Créer la vidéo ----------------
        tk.Button(self, text="Créer la vidéo", command=self.create_video_thread).grid(row=6, column=0, columnspan=3, pady=10)

        # ---------------- Commande FFmpeg ----------------
        tk.Label(self, text="Commande FFmpeg générée :").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.command_text = tk.Text(self, height=3, width=95)
        self.command_text.grid(row=8, column=0, columnspan=3, padx=5, pady=5)

        # ---------------- Logs FFmpeg ----------------
        tk.Label(self, text="Logs FFmpeg :").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(self, height=10, width=95, state=tk.DISABLED)
        self.log_text.grid(row=10, column=0, columnspan=3, padx=5, pady=5)

    # ---------------- Config ----------------
    def save_config(self):
        config = {"ffmpeg_path": self.ffmpeg_path}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    self.ffmpeg_path = config.get("ffmpeg_path", "")
            except Exception:
                self.ffmpeg_path = ""

    # ---------------- FFmpeg ----------------
    def choose_ffmpeg(self):
        path = filedialog.askopenfilename(title="Choisir ffmpeg.exe", filetypes=[("FFmpeg Executable", "ffmpeg.exe")])
        if path:
            self.ffmpeg_path = path
            self.ffmpeg_label.config(text=path, fg="green")
            self.save_config()

    # ---------------- Images ----------------
    def add_images(self):
        files = filedialog.askopenfilenames(title="Ajouter des images", filetypes=[("Images", "*.png *.jpg *.jpeg")])
        for f in files:
            if f not in self.image_files:
                self.image_files.append(f)
                self.images_listbox.insert(tk.END, os.path.basename(f))

    def remove_selected_images(self):
        selected_indices = list(self.images_listbox.curselection())
        selected_indices.sort(reverse=True)
        for i in selected_indices:
            self.images_listbox.delete(i)
            del self.image_files[i]

    # ---------------- Créer list.txt ----------------
    def create_list_file(self, list_path, duration):
        if os.path.exists(list_path):
            os.remove(list_path)

        with open(list_path, "w", encoding="utf-8") as f:
            for img_path in self.image_files:
                escaped_path = img_path.replace("\\", "/")
                f.write(f"file '{escaped_path}'\n")
                f.write(f"duration {duration}\n")
            # répéter la dernière image pour durée correcte
            if self.image_files:
                last_path = self.image_files[-1].replace("\\", "/")
                f.write(f"file '{last_path}'\n")

    # ---------------- Log ----------------
    def append_log(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ---------------- Construire la commande ----------------
    def build_command(self, list_txt_path, output_file):
        # Codec H.265 (libx265), qualité maximale, conserver taille originale
        cmd = [
            self.ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', list_txt_path,
            '-c:v', 'libx265',
            '-crf', '18',            # meilleure qualité possible
            '-preset', 'slow',       # meilleure compression (mais plus lent)
            '-pix_fmt', 'yuv420p',   # compatibilité vidéo
            output_file
        ]
        return cmd

    # ---------------- Thread pour la vidéo ----------------
    def create_video_thread(self):
        thread = threading.Thread(target=self.create_video)
        thread.start()

    def create_video(self):
        if not self.ffmpeg_path:
            messagebox.showerror("Erreur", "Veuillez choisir le chemin de ffmpeg.exe")
            return
        if not self.image_files:
            messagebox.showerror("Erreur", "Veuillez ajouter au moins une image")
            return

        output_file = self.output_entry.get().strip()
        if not output_file:
            output_file = "output.mp4"

        # Générer un nom aléatoire si le fichier existe
        base, ext = os.path.splitext(output_file)
        while os.path.exists(output_file):
            rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            output_file = f"{base}_{rand_suffix}{ext}"

        try:
            duration = float(self.duration_entry.get())
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la durée (supérieur à 0)")
            return

        temp_dir = tempfile.gettempdir()
        list_txt_path = os.path.join(temp_dir, "list.txt")
        self.create_list_file(list_txt_path, duration)

        cmd = self.build_command(list_txt_path, output_file)

        # Affiche la commande
        self.command_text.config(state=tk.NORMAL)
        self.command_text.delete("1.0", tk.END)
        self.command_text.insert(tk.END, " ".join(f'"{c}"' if " " in c else c for c in cmd))
        self.command_text.config(state=tk.DISABLED)

        # Efface log console
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

        log_filename = "ffmpeg_log.txt"

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
            with open(log_filename, "w", encoding="utf-8") as logfile:
                for line in process.stdout:
                    self.append_log(line)
                    logfile.write(line)
                process.wait()

            if process.returncode != 0:
                messagebox.showerror("Erreur FFmpeg", f"FFmpeg a rencontré une erreur.\nVoir logs pour plus de détails.")
            else:
                messagebox.showinfo("Succès", f"Vidéo créée avec succès :\n{output_file}\n\nLogs enregistrés dans {log_filename}")

        except Exception as e:
            messagebox.showerror("Exception", str(e))

if __name__ == "__main__":
    app = VideoCreatorApp()
    app.mainloop()
