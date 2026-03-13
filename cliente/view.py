import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font
from cliente.dto import ClienteDto

class ClienteView:
    def __init__(self, parent, cliente_service):
        self.parent = parent
        self.cliente_service = cliente_service
        self.frame = ttk.Frame(self.parent)
        self.create_widgets()

    def create_widgets(self):
        """Crea los widgets para la vista de clientes."""
        # Frame para la grilla
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview para la grilla
        self.treeview = ttk.Treeview(self.main_frame, show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Barras de desplazamiento
        self.scroll_y = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.treeview.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_x = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.treeview.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.treeview.configure(xscrollcommand=self.scroll_x.set)

        # Botones de acción
        self.btn_frame = ttk.Frame(self.frame)
        self.btn_frame.pack(fill=tk.X, padx=10, pady=5)

        self.btn_crear = ttk.Button(self.btn_frame, text="Crear Cliente", command=self.open_create_dialog)
        self.btn_crear.pack(side=tk.LEFT, padx=5)

        self.btn_editar = ttk.Button(self.btn_frame, text="Editar Cliente", command=self.open_edit_dialog)
        self.btn_editar.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar = ttk.Button(self.btn_frame, text="Eliminar Cliente", command=self.delete_cliente)
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)

        # Cargar datos iniciales
        self.load_clientes()

    def load_clientes(self):
        """Carga los datos de clientes en el Treeview."""
        clientes, error = self.cliente_service.get_clientes()
        self.display_data(clientes, error)

    def display_data(self, clientes, error=None):
        """Muestra datos en el Treeview o un mensaje de error."""
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if error or not clientes:
            messagebox.showerror("Error", error or "No hay datos para mostrar.")
            self.treeview["columns"] = ["Mensaje"]
            self.treeview.heading("Mensaje", text="Mensaje")
            self.treeview.column("Mensaje", width=200, anchor="center")
            self.treeview.insert("", "end", values=["No hay datos para mostrar"])
            return

        # Configurar columnas
        columns = ["id", "nombre", "email", "telefono"]
        column_headers = {"id": "ID", "nombre": "Nombre", "email": "Email", "telefono": "Teléfono"}
        self.treeview["columns"] = columns
        for col in columns:
            self.treeview.heading(col, text=column_headers[col])
            self.treeview.column(col, width=100, anchor="w")

        # Insertar datos
        for i, cliente in enumerate(clientes):
            values = [cliente.id, cliente.nombre, cliente.email, cliente.telefono]
            self.treeview.insert("", "end", text=str(i + 1), values=values, tags=(cliente.id,))

        # Ajustar ancho de columnas
        tk_font = font.nametofont("TkDefaultFont")
        for col in columns:
            header_width = tk_font.measure(column_headers[col])
            data_widths = [tk_font.measure(str(getattr(cliente, col))) for cliente in clientes]
            max_width = max(data_widths + [header_width], default=100)
            self.treeview.column(col, width=min(max_width + 20, 300))

    def open_create_dialog(self):
        """Abre un diálogo para crear un nuevo cliente."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Crear Cliente")
        self.dialog.geometry("300x200")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Campos del formulario
        ttk.Label(self.dialog, text="Nombre:").pack(pady=5)
        self.entry_nombre = ttk.Entry(self.dialog)
        self.entry_nombre.pack(pady=5)

        ttk.Label(self.dialog, text="Email:").pack(pady=5)
        self.entry_email = ttk.Entry(self.dialog)
        self.entry_email.pack(pady=5)

        ttk.Label(self.dialog, text="Teléfono:").pack(pady=5)
        self.entry_telefono = ttk.Entry(self.dialog)
        self.entry_telefono.pack(pady=5)

        # Botón de guardar
        ttk.Button(self.dialog, text="Guardar", command=self.save_new_cliente).pack(pady=10)

    def save_new_cliente(self):
        """Guarda un nuevo cliente."""
        nombre = self.entry_nombre.get().strip()
        email = self.entry_email.get().strip()
        telefono = self.entry_telefono.get().strip()

        if not nombre or not email:
            messagebox.showerror("Error", "Nombre y email son obligatorios.")
            return

        cliente_dto = ClienteDto(nombre=nombre, email=email, telefono=telefono)
        result, error = self.cliente_service.create_cliente(cliente_dto)
        if error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showinfo("Éxito", "Cliente creado correctamente.")
            self.dialog.destroy()
            self.load_clientes()

    def open_edit_dialog(self):
        """Abre un diálogo para editar un cliente seleccionado."""
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar.")
            return

        item = self.treeview.item(selected_item[0])
        cliente_id = item["tags"][0]
        values = item["values"]

        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Editar Cliente")
        self.dialog.geometry("300x200")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Campos del formulario
        ttk.Label(self.dialog, text="Nombre:").pack(pady=5)
        self.entry_nombre = ttk.Entry(self.dialog)
        self.entry_nombre.insert(0, values[1])  # nombre
        self.entry_nombre.pack(pady=5)

        ttk.Label(self.dialog, text="Email:").pack(pady=5)
        self.entry_email = ttk.Entry(self.dialog)
        self.entry_email.insert(0, values[2])  # email
        self.entry_email.pack(pady=5)

        ttk.Label(self.dialog, text="Teléfono:").pack(pady=5)
        self.entry_telefono = ttk.Entry(self.dialog)
        self.entry_telefono.insert(0, values[3])  # telefono
        self.entry_telefono.pack(pady=5)

        # Botón de guardar
        ttk.Button(self.dialog, text="Guardar", command=lambda: self.save_edited_cliente(cliente_id)).pack(pady=10)

    def save_edited_cliente(self, cliente_id):
        """Guarda los cambios de un cliente editado."""
        nombre = self.entry_nombre.get().strip()
        email = self.entry_email.get().strip()
        telefono = self.entry_telefono.get().strip()

        if not nombre or not email:
            messagebox.showerror("Error", "Nombre y email son obligatorios.")
            return

        cliente_dto = ClienteDto(id=cliente_id, nombre=nombre, email=email, telefono=telefono)
        result, error = self.cliente_service.update_cliente(cliente_dto)
        if error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
            self.dialog.destroy()
            self.load_clientes()

    def delete_cliente(self):
        """Elimina un cliente seleccionado."""
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar.")
            return

        item = self.treeview.item(selected_item[0])
        cliente_id = item["tags"][0]
        cliente_nombre = item["values"][1]

        if not messagebox.askyesno("Confirmar", f"¿Eliminar al cliente {cliente_nombre}?"):
            return

        result, error = self.cliente_service.delete_cliente(cliente_id)
        if error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
            self.load_clientes()

    def show(self):
        """Muestra la vista."""
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.load_clientes()

    def hide(self):
        """Oculta la vista."""
        self.frame.pack_forget()