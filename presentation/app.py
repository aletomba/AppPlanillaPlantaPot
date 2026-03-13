import tkinter as tk
from tkinter import ttk
from cliente.view import ClienteView
from cliente.service import ClienteService
from libro_entrada.view import LibroDeEntradaView
from libro_entrada.service import LibroDeEntradaService
from libro_fisico.view import FisicoQuimicoView
from libro_fisico.service import FisicoQuimicoService
from libro_bacteriologia.view import BacteriologiaView
from libro_bacteriologia.service import BacteriologiaService
from planilla_diaria.view import PlanillaDiariaView
from planilla_diaria.service import PlanillaDiariaService

class APIViewerApp:
    def __init__(self, root, base_url):
        self.root = root
        self.root.title("Gestión Laboratorio de Agua")
        self.root.geometry("1000x600")

        # Inicializar servicios
        self.cliente_service = ClienteService(base_url)
        self.libro_service = LibroDeEntradaService(base_url)
        self.fisicoquimico_service = FisicoQuimicoService(base_url)

        # Inicializar vistas
        self.cliente_view = ClienteView(self.root, self.cliente_service)
        self.libro_view = LibroDeEntradaView(self.root, self.libro_service)
        # Pasar también el servicio de libros para que la vista de físico‑químico
        # pueda enriquecer los reportes con metadatos del libro y la muestra.
        self.fisicoquimico_view = FisicoQuimicoView(self.root, self.fisicoquimico_service, libro_service=self.libro_service)

        # Bacteriología
        self.bacteriologia_service = BacteriologiaService(base_url)
        self.bacteriologia_view = BacteriologiaView(self.root, self.bacteriologia_service, libro_service=self.libro_service)

        # Planilla Diaria
        self.planilla_service = PlanillaDiariaService(base_url)
        self.planilla_view = PlanillaDiariaView(self.root, self.planilla_service)

        # Crear el layout
        self.create_layout()

    def create_layout(self):
        """Crea la interfaz gráfica con menú lateral."""
        self.menu_frame = ttk.Frame(self.root, width=200)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.url_frame = ttk.Frame(self.menu_frame)
        self.url_frame.pack(fill=tk.X, pady=5)

        # self.label_url = ttk.Label(self.url_frame, text="API URL:", font=("Arial", 12))
        # self.label_url.pack(anchor="w", padx=5)

        # self.entry_url = ttk.Entry(self.url_frame, width=20, font=("Arial", 12))
        # self.entry_url.pack(fill=tk.X, padx=5, pady=5)
        # self.entry_url.insert(0, self.cliente_service.base_url)
        # self.entry_url.bind("<Return>", lambda event: self.update_base_url()) TODO: ver si borrar esto

        self.style = ttk.Style()
        self.style.configure("Menu.TButton", font=("Arial", 12))

        self.btn_clientes = ttk.Button(
            self.menu_frame, text="Clientes", command=self.show_clientes, style="Menu.TButton"
        )
        self.btn_clientes.pack(fill=tk.X, pady=5, padx=5)

        self.btn_libros = ttk.Button(
            self.menu_frame, text="Libros de Entrada", command=self.show_libros, style="Menu.TButton"
        )        
        self.btn_libros.pack(fill=tk.X, pady=5, padx=5)
        self.btn_fisicoquimico = ttk.Button(
        self.menu_frame, text="Fisico Químico", command=self.show_fisicoquimico, style="Menu.TButton"
        )
        self.btn_fisicoquimico.pack(fill=tk.X, pady=5, padx=5)
        self.btn_bacteriologia = ttk.Button(
            self.menu_frame, text="Bacteriología", command=self.show_bacteriologia, style="Menu.TButton"
        )
        self.btn_bacteriologia.pack(fill=tk.X, pady=5, padx=5)

        self.btn_planilla = ttk.Button(
            self.menu_frame, text="Planilla Diaria", command=self.show_planilla_diaria, style="Menu.TButton"
        )
        self.btn_planilla.pack(fill=tk.X, pady=5, padx=5)

    def update_base_url(self):
        """Actualiza la URL base en los servicios."""
        new_url = self.entry_url.get().strip()
        self.cliente_service.update_base_url(new_url)        
        self.libro_service.update_base_url(new_url)
        self.fisicoquimico_service.update_base_url(new_url)
        self.bacteriologia_service.update_base_url(new_url)
        self.show_clientes()        
        self.show_fisicoquimico()

    def show_clientes(self):
        """Muestra la vista de clientes."""
        self.libro_view.hide()
        self.fisicoquimico_view.hide()
        self.bacteriologia_view.hide()
        self.planilla_view.hide()
        self.cliente_view.show()

    def show_libros(self):
        """Muestra la vista de libros de entrada."""
        self.cliente_view.hide()
        self.fisicoquimico_view.hide()
        self.bacteriologia_view.hide()
        self.planilla_view.hide()
        self.libro_view.show()

    def show_fisicoquimico(self):
        self.cliente_view.hide()
        self.libro_view.hide()
        self.bacteriologia_view.hide()
        self.planilla_view.hide()
        self.fisicoquimico_view.show() 

    def show_bacteriologia(self):
        self.cliente_view.hide()
        self.libro_view.hide()
        self.fisicoquimico_view.hide()
        self.planilla_view.hide()
        self.bacteriologia_view.show()

    def show_planilla_diaria(self):
        self.cliente_view.hide()
        self.libro_view.hide()
        self.fisicoquimico_view.hide()
        self.bacteriologia_view.hide()
        self.planilla_view.show()