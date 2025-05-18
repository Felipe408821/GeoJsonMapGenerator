import tkinter as tk
from tkinter import ttk, messagebox

from PIL.Image import Resampling

from map import map as mapa
from routes import routes as route
from PIL import Image, ImageTk

BG_COLOR       = "#F5F5F7"   # fondo general
ENTRY_BG_COLOR = "#FFFFFF"   # fondo de los Entry
FG_COLOR       = "#1C1C1E"   # texto oscuro
ACCENT_COLOR   = "#007AFF"   # azul
ACCENT_ACTIVE  = "#005BBB"   # azul al pulsar

class MapRouteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GeoJson Map Generator")
        self.root.configure(bg=BG_COLOR)

        # Centramos la ventana
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        ww, hh = int(w*0.45), int(h*0.55)
        x, y = (w-ww)//2, (h-hh)//2
        root.geometry(f"{ww}x{hh}+{x}+{y}")

        # Variables
        self.generate_map   = tk.BooleanVar(value=True)
        self.generate_route = tk.BooleanVar(value=True)
        self.show_map       = tk.BooleanVar()
        self.save_map       = tk.BooleanVar()

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style(self.root)

        # Fondos
        style.configure("TFrame",    background=BG_COLOR)
        style.configure("TLabel",    background=BG_COLOR, foreground=FG_COLOR, font=("Helvetica Neue", 14))
        style.configure("TCheckbutton",
                        background=BG_COLOR,
                        foreground=FG_COLOR,
                        font=("Helvetica Neue", 14),
                        relief="flat")
        style.configure("TEntry",
                        fieldbackground=ENTRY_BG_COLOR,
                        font=("Helvetica Neue", 14),
                        background=BG_COLOR,
                        foreground=FG_COLOR,
                        relief="flat")

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(expand=True, fill="both")

        # ---------- Barra superior con crédito ----------
        top_bar = tk.Frame(container, bg="#ededed")
        top_bar.pack(fill="x", pady=(0, 5))

        # Texto "Powered by:" alineado a la izquierda
        tk.Label(top_bar, text="Felipe Camacho", bg="#ededed",
                 fg="#1C1C1E", font=("Helvetica Neue", 10)).pack(side="left")

        # Cargar imagen y mostrarla alineada a la derecha
        img_path = "images/logo.png"  # <-- actualiza con tu ruta real
        image = Image.open(img_path).resize((49, 15), Resampling.LANCZOS)
        self.logo_img = ImageTk.PhotoImage(image)  # mantener referencia

        tk.Label(top_bar, image=self.logo_img, bg="#ededed").pack(side="right")

        # Título
        ttk.Label(container, text="Opciones de generación", font=("Helvetica Neue", 20, "bold")).pack(pady=(0,20))

        # Secciones
        self._make_section(container, "Mapa",   self.generate_map,   self._map_options)
        self._make_section(container, "Rutas",  self.generate_route, self._route_options)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)

        # Botón Ejecutar
        self.execute_btn = tk.Label(container, text="Ejecutar",
                                    font=("Helvetica Neue", 14, "bold"),
                                    fg="white", bg=ACCENT_COLOR,
                                    padx=5, pady=5)

        self.execute_btn.pack(fill="x")

        self.execute_btn.bind("<Button-1>", lambda e: self.execute_operations())
        self.execute_btn.bind("<Enter>", lambda e: self.execute_btn.config(bg=ACCENT_ACTIVE))
        self.execute_btn.bind("<Leave>", lambda e: self.execute_btn.config(bg=ACCENT_COLOR))

    def _make_section(self, parent, name, var, build_fn):
        section = ttk.Frame(parent)
        section.pack(fill="x", pady=10)

        # Check para activar/desactivar
        chk = ttk.Checkbutton(section, text=f"Generar {name}", variable=var,
                              command=lambda f=section, v=var: self._toggle(f, v))
        chk.pack(anchor="w")

        # Contenido
        content = ttk.Frame(section)
        content.pack(fill="x", padx=10, pady=5)
        build_fn(content)

        # Estado inicial
        self._toggle(section, var)

    def _toggle(self, section_frame, var):
        # el content es siempre el segundo hijo:
        content = section_frame.winfo_children()[1]
        if var.get():
            content.pack(fill="x", padx=10, pady=5)
        else:
            content.forget()

    def _map_options(self, frame):
        ttk.Checkbutton(frame, text="Guardar mapa como imagen", variable=self.show_map).grid(row=0, column=0,
                                                                                              columnspan=2, sticky="w",
                                                                                              pady=2)
        ttk.Checkbutton(frame, text="Guardar mapa como GeoJson", variable=self.save_map).grid(row=1, column=0,
                                                                                             columnspan=2, sticky="w",
                                                                                             pady=2)

        ttk.Label(frame, text="Ubicación del mapa:").grid(row=2, column=0, sticky="w", pady=8, padx=(0, 10))
        self.location_entry = tk.Entry(frame, font=("Helvetica Neue", 14), bg="#FFFFFF", relief="flat")
        self.location_entry.insert(0, "Majadahonda, Spain")
        self.location_entry.grid(row=2, column=1, sticky="ew")

        frame.columnconfigure(1, weight=1)  # permite expandir columna 1

    def _route_options(self, frame):
        ttk.Label(frame, text="Input:").grid(row=0, column=0, sticky="w", pady=(8, 2), padx=(0, 10))
        self.route1_entry = tk.Entry(frame, font=("Helvetica Neue", 14), bg="#FFFFFF", relief="flat")
        self.route1_entry.insert(0, "652_vuelta.json")
        self.route1_entry.grid(row=0, column=1, sticky="ew", pady=(8, 2))

        ttk.Label(frame, text="Output:").grid(row=1, column=0, sticky="w", pady=(8, 2), padx=(0, 10))
        self.route2_entry = tk.Entry(frame, font=("Helvetica Neue", 14), bg="#FFFFFF", relief="flat")
        self.route2_entry.insert(0, "652B.json")
        self.route2_entry.grid(row=1, column=1, sticky="ew", pady=(8, 2))

        frame.columnconfigure(1, weight=1)

    def execute_operations(self):
        try:
            if self.generate_map.get():
                mapa.create_map(self.location_entry.get(),
                                self.show_map.get(),
                                self.save_map.get())
            if self.generate_route.get():
                route.create_route(self.route1_entry.get(),
                                   self.route2_entry.get())
            messagebox.showinfo("Éxito", "Operaciones completadas correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = MapRouteApp(root)
    root.mainloop()
