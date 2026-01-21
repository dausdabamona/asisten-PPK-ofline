"""
Asisten PPK Offline - Aplikasi Desktop
Membantu administrasi Pejabat Pembuat Komitmen
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_generator import (
    generate_daftar_hadir_jamuan,
    generate_daftar_hadir_swakelola
)


class AsistenPPK:
    def __init__(self, root):
        self.root = root
        self.root.title("Asisten PPK Offline")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Set default output directory
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Menu.TButton', font=('Helvetica', 11), padding=10)

        self.create_main_menu()

    def create_main_menu(self):
        """Membuat tampilan menu utama"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="ASISTEN PPK OFFLINE",
                         style='Title.TLabel')
        title.pack(pady=20)

        subtitle = ttk.Label(main_frame,
                            text="Aplikasi Pembantu Administrasi Pejabat Pembuat Komitmen",
                            font=('Helvetica', 10))
        subtitle.pack(pady=5)

        # Menu buttons frame
        menu_frame = ttk.Frame(main_frame)
        menu_frame.pack(pady=40)

        # Menu buttons
        btn_jamuan = ttk.Button(menu_frame, text="Jamuan Tamu / Rapat",
                                style='Menu.TButton', width=30,
                                command=self.show_jamuan_menu)
        btn_jamuan.pack(pady=10)

        btn_swakelola = ttk.Button(menu_frame, text="Swakelola",
                                   style='Menu.TButton', width=30,
                                   command=self.show_swakelola_menu)
        btn_swakelola.pack(pady=10)

        btn_settings = ttk.Button(menu_frame, text="Pengaturan",
                                  style='Menu.TButton', width=30,
                                  command=self.show_settings)
        btn_settings.pack(pady=10)

        # Footer
        footer = ttk.Label(main_frame,
                          text="v1.0.0 - 2024",
                          font=('Helvetica', 8))
        footer.pack(side=tk.BOTTOM, pady=10)

    def show_jamuan_menu(self):
        """Menampilkan menu Jamuan Tamu"""
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="JAMUAN TAMU / RAPAT",
                         style='Title.TLabel')
        title.pack(pady=10)

        # Sub menu frame
        submenu_frame = ttk.Frame(main_frame)
        submenu_frame.pack(pady=20)

        btn_daftar_hadir = ttk.Button(submenu_frame,
                                      text="Generate Daftar Hadir",
                                      style='Menu.TButton', width=30,
                                      command=self.form_daftar_hadir_jamuan)
        btn_daftar_hadir.pack(pady=10)

        # Back button
        btn_back = ttk.Button(main_frame, text="Kembali ke Menu Utama",
                             command=self.create_main_menu)
        btn_back.pack(side=tk.BOTTOM, pady=20)

    def show_swakelola_menu(self):
        """Menampilkan menu Swakelola"""
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="SWAKELOLA",
                         style='Title.TLabel')
        title.pack(pady=10)

        # Sub menu frame
        submenu_frame = ttk.Frame(main_frame)
        submenu_frame.pack(pady=20)

        btn_daftar_hadir = ttk.Button(submenu_frame,
                                      text="Generate Daftar Hadir",
                                      style='Menu.TButton', width=30,
                                      command=self.form_daftar_hadir_swakelola)
        btn_daftar_hadir.pack(pady=10)

        # Back button
        btn_back = ttk.Button(main_frame, text="Kembali ke Menu Utama",
                             command=self.create_main_menu)
        btn_back.pack(side=tk.BOTTOM, pady=20)

    def form_daftar_hadir_jamuan(self):
        """Form untuk generate daftar hadir jamuan"""
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="DAFTAR HADIR - JAMUAN TAMU",
                         style='Header.TLabel')
        title.pack(pady=10)

        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=20, fill=tk.X, padx=50)

        # Form fields
        fields = {}

        row = 0
        ttk.Label(form_frame, text="Nama Kegiatan:").grid(row=row, column=0, sticky='w', pady=5)
        fields['nama_kegiatan'] = ttk.Entry(form_frame, width=50)
        fields['nama_kegiatan'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Tanggal:").grid(row=row, column=0, sticky='w', pady=5)
        fields['tanggal'] = ttk.Entry(form_frame, width=50)
        fields['tanggal'].insert(0, datetime.now().strftime("%d %B %Y"))
        fields['tanggal'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Waktu:").grid(row=row, column=0, sticky='w', pady=5)
        fields['waktu'] = ttk.Entry(form_frame, width=50)
        fields['waktu'].insert(0, "09.00 - Selesai")
        fields['waktu'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Tempat:").grid(row=row, column=0, sticky='w', pady=5)
        fields['tempat'] = ttk.Entry(form_frame, width=50)
        fields['tempat'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Jumlah Peserta:").grid(row=row, column=0, sticky='w', pady=5)
        fields['jumlah_peserta'] = ttk.Spinbox(form_frame, from_=1, to=100, width=10)
        fields['jumlah_peserta'].delete(0, tk.END)
        fields['jumlah_peserta'].insert(0, "10")
        fields['jumlah_peserta'].grid(row=row, column=1, pady=5, padx=10, sticky='w')

        row += 1
        ttk.Separator(form_frame, orient='horizontal').grid(row=row, column=0,
                                                            columnspan=2, sticky='ew', pady=15)

        row += 1
        ttk.Label(form_frame, text="Nama PPK:").grid(row=row, column=0, sticky='w', pady=5)
        fields['nama_ppk'] = ttk.Entry(form_frame, width=50)
        fields['nama_ppk'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="NIP PPK:").grid(row=row, column=0, sticky='w', pady=5)
        fields['nip_ppk'] = ttk.Entry(form_frame, width=50)
        fields['nip_ppk'].grid(row=row, column=1, pady=5, padx=10)

        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        def generate():
            data = {
                'nama_kegiatan': fields['nama_kegiatan'].get(),
                'tanggal': fields['tanggal'].get(),
                'waktu': fields['waktu'].get(),
                'tempat': fields['tempat'].get(),
                'jumlah_peserta': int(fields['jumlah_peserta'].get()),
                'nama_ppk': fields['nama_ppk'].get(),
                'nip_ppk': fields['nip_ppk'].get()
            }
            try:
                filepath = generate_daftar_hadir_jamuan(data, self.output_dir)
                messagebox.showinfo("Berhasil",
                                   f"Dokumen berhasil dibuat!\n\nLokasi: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuat dokumen:\n{str(e)}")

        ttk.Button(btn_frame, text="Generate Dokumen",
                  command=generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Kembali",
                  command=self.show_jamuan_menu).pack(side=tk.LEFT, padx=5)

    def form_daftar_hadir_swakelola(self):
        """Form untuk generate daftar hadir swakelola"""
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="DAFTAR HADIR - SWAKELOLA",
                         style='Header.TLabel')
        title.pack(pady=10)

        # Scrollable form
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form frame
        form_frame = ttk.Frame(scrollable_frame)
        form_frame.pack(pady=20, fill=tk.X, padx=50)

        # Form fields
        fields = {}

        row = 0
        ttk.Label(form_frame, text="Nama Kegiatan:").grid(row=row, column=0, sticky='w', pady=5)
        fields['nama_kegiatan'] = ttk.Entry(form_frame, width=50)
        fields['nama_kegiatan'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Nama Paket:").grid(row=row, column=0, sticky='w', pady=5)
        fields['nama_paket'] = ttk.Entry(form_frame, width=50)
        fields['nama_paket'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Tahun Anggaran:").grid(row=row, column=0, sticky='w', pady=5)
        fields['tahun_anggaran'] = ttk.Entry(form_frame, width=50)
        fields['tahun_anggaran'].insert(0, str(datetime.now().year))
        fields['tahun_anggaran'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Tanggal:").grid(row=row, column=0, sticky='w', pady=5)
        fields['tanggal'] = ttk.Entry(form_frame, width=50)
        fields['tanggal'].insert(0, datetime.now().strftime("%d %B %Y"))
        fields['tanggal'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Waktu:").grid(row=row, column=0, sticky='w', pady=5)
        fields['waktu'] = ttk.Entry(form_frame, width=50)
        fields['waktu'].insert(0, "09.00 - Selesai")
        fields['waktu'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Tempat:").grid(row=row, column=0, sticky='w', pady=5)
        fields['tempat'] = ttk.Entry(form_frame, width=50)
        fields['tempat'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="Jumlah Peserta:").grid(row=row, column=0, sticky='w', pady=5)
        fields['jumlah_peserta'] = ttk.Spinbox(form_frame, from_=1, to=100, width=10)
        fields['jumlah_peserta'].delete(0, tk.END)
        fields['jumlah_peserta'].insert(0, "15")
        fields['jumlah_peserta'].grid(row=row, column=1, pady=5, padx=10, sticky='w')

        row += 1
        ttk.Separator(form_frame, orient='horizontal').grid(row=row, column=0,
                                                            columnspan=2, sticky='ew', pady=15)

        row += 1
        ttk.Label(form_frame, text="Nama PPK:").grid(row=row, column=0, sticky='w', pady=5)
        fields['nama_ppk'] = ttk.Entry(form_frame, width=50)
        fields['nama_ppk'].grid(row=row, column=1, pady=5, padx=10)

        row += 1
        ttk.Label(form_frame, text="NIP PPK:").grid(row=row, column=0, sticky='w', pady=5)
        fields['nip_ppk'] = ttk.Entry(form_frame, width=50)
        fields['nip_ppk'].grid(row=row, column=1, pady=5, padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        def generate():
            data = {
                'nama_kegiatan': fields['nama_kegiatan'].get(),
                'nama_paket': fields['nama_paket'].get(),
                'tahun_anggaran': fields['tahun_anggaran'].get(),
                'tanggal': fields['tanggal'].get(),
                'waktu': fields['waktu'].get(),
                'tempat': fields['tempat'].get(),
                'jumlah_peserta': int(fields['jumlah_peserta'].get()),
                'nama_ppk': fields['nama_ppk'].get(),
                'nip_ppk': fields['nip_ppk'].get()
            }
            try:
                filepath = generate_daftar_hadir_swakelola(data, self.output_dir)
                messagebox.showinfo("Berhasil",
                                   f"Dokumen berhasil dibuat!\n\nLokasi: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuat dokumen:\n{str(e)}")

        ttk.Button(btn_frame, text="Generate Dokumen",
                  command=generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Kembali",
                  command=self.show_swakelola_menu).pack(side=tk.LEFT, padx=5)

    def show_settings(self):
        """Menampilkan halaman pengaturan"""
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="PENGATURAN",
                         style='Title.TLabel')
        title.pack(pady=10)

        # Settings frame
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(pady=20, fill=tk.X, padx=50)

        # Output directory
        ttk.Label(settings_frame, text="Folder Output:").grid(row=0, column=0, sticky='w', pady=5)
        output_entry = ttk.Entry(settings_frame, width=50)
        output_entry.insert(0, self.output_dir)
        output_entry.grid(row=0, column=1, pady=5, padx=10)

        def browse_folder():
            folder = filedialog.askdirectory(initialdir=self.output_dir)
            if folder:
                output_entry.delete(0, tk.END)
                output_entry.insert(0, folder)
                self.output_dir = folder

        ttk.Button(settings_frame, text="Browse",
                  command=browse_folder).grid(row=0, column=2, pady=5)

        # Open output folder button
        def open_output_folder():
            if os.path.exists(self.output_dir):
                if sys.platform == 'win32':
                    os.startfile(self.output_dir)
                elif sys.platform == 'darwin':
                    os.system(f'open "{self.output_dir}"')
                else:
                    os.system(f'xdg-open "{self.output_dir}"')

        ttk.Button(settings_frame, text="Buka Folder Output",
                  command=open_output_folder).grid(row=1, column=1, pady=20, sticky='w')

        # Back button
        btn_back = ttk.Button(main_frame, text="Kembali ke Menu Utama",
                             command=self.create_main_menu)
        btn_back.pack(side=tk.BOTTOM, pady=20)


def main():
    root = tk.Tk()
    app = AsistenPPK(root)
    root.mainloop()


if __name__ == "__main__":
    main()
