import tkinter as tk
from tkinter import ttk, messagebox
import math

## ----------------------------------------------------
## 1. GEOMETRY CLASSES
## ----------------------------------------------------

class Shape:
    """Base class for geometric shapes."""
    def surface(self):
        return 0
    def volume(self):
        return 0
    def get_params(self):
        return {}
    def __str__(self):
        return self.__class__.__name__

#  2D Shapes 

class Circle(Shape):
    def __init__(self, radius):
        if radius < 0: raise ValueError("Radius must be non-negative.")
        self.r = radius
    def surface(self):
        return math.pi * self.r**2
    def get_params(self):
        return {"Radius": self.r}

class Rectangle(Shape):
    def __init__(self, width, height):
        if width < 0 or height < 0: raise ValueError("Dimensions must be non-negative.")
        self.w = width
        self.h = height
    def surface(self):
        return self.w * self.h
    def get_params(self):
        return {"Width": self.w, "Height": self.h}

class Triangle(Shape):
    def __init__(self, base, height):
        if base < 0 or height < 0: raise ValueError("Dimensions must be non-negative.")
        self.b = base
        self.h = height
    def surface(self):
        return 0.5 * self.b * self.h
    def get_params(self):
        return {"Base": self.b, "Height": self.h}

#  3D Shapes 
class Block(Shape):
    def __init__(self, length, width, height):
        if length < 0 or width < 0 or height < 0: raise ValueError("Dimensions must be non-negative.")
        self.l = length
        self.w = width
        self.h = height
    def surface(self):
        return 2 * (self.l * self.w + self.l * self.h + self.w * self.h)
    def volume(self):
        return self.l * self.w * self.h
    def get_params(self):
        return {"Length": self.l, "Width": self.w, "Height": self.h}

class Sphere(Shape):
    def __init__(self, radius):
        if radius < 0: raise ValueError("Radius must be non-negative.")
        self.r = radius
    def surface(self):
        return 4 * math.pi * self.r**2
    def volume(self):
        return (4/3) * math.pi * self.r**3
    def get_params(self):
        return {"Radius": self.r}

class Tetrahedron(Shape):
    def __init__(self, edge):
        if edge < 0: raise ValueError("Edge length must be non-negative.")
        self.a = edge
    def surface(self):
        return math.sqrt(3) * self.a**2
    def volume(self):
        return self.a**3 / (6 * math.sqrt(2))
    def get_params(self):
        return {"Edge Length": self.a}

## ----------------------------------------------------
## 2. SHAPE MAPPING & PARAMETER DEFINITIONS
## ----------------------------------------------------

SHAPE_MAP = {
    "2D": {
        "Circle": {"class": Circle, "params": ["Radius"]},
        "Rectangle": {"class": Rectangle, "params": ["Width", "Height"]},
        "Triangle": {"class": Triangle, "params": ["Base", "Height"]},
    },
    "3D": {
        "Block": {"class": Block, "params": ["Length", "Width", "Height"]},
        "Sphere": {"class": Sphere, "params": ["Radius"]},
        "Tetrahedron": {"class": Tetrahedron, "params": ["Edge Length"]},
    }
}

## ----------------------------------------------------
## 3. TKINTER GUI
## ----------------------------------------------------

class GeometryApp:
    def __init__(self, master):
        self.master = master
        master.title("Geometric Calculator")
        master.geometry("600x850")
        master.resizable(True, True)

        # --- Style configuration moved to the top ---
        BG_COLOR = "#2E2E2E"
        FG_COLOR = "#EAEAEA"
        ACCENT_COLOR = "#007ACC"
        FIELD_BG = "#3C3C3C"
        BTN_BG = "#4A4A4A"

        style = ttk.Style(self.master)
        style.theme_use("clam")

        self.master.configure(bg=BG_COLOR)

        style.configure(".",
            background=BG_COLOR,
            foreground=FG_COLOR,
            fieldbackground=FIELD_BG,
            borderwidth=1,
            focuscolor=ACCENT_COLOR
        )

        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, padding=5)

        style.configure("TLabelframe", background=BG_COLOR, labelmargins=10)
        style.configure("TLabelframe.Label", background=BG_COLOR, foreground=FG_COLOR, font=('Arial', 11, 'bold'))

        style.configure("TButton", background=BTN_BG, foreground=FG_COLOR, relief="raised", padding=6)
        style.map("TButton", background=[('active', ACCENT_COLOR), ('pressed', ACCENT_COLOR)], foreground=[('active', 'white'), ('pressed', 'white')])

        style.configure("TRadiobutton", background=BG_COLOR, foreground=FG_COLOR, padding=5)
        style.map("TRadiobutton", indicatorcolor=[('selected', ACCENT_COLOR), ('!selected', BTN_BG)], background=[('active', BG_COLOR)])

        style.configure("TEntry", fieldbackground=FIELD_BG, foreground=FG_COLOR, insertcolor=FG_COLOR)

        # --- Variable and UI setup ---
        self.current_shape_type = tk.StringVar(master, value="")
        self.current_shape_name = tk.StringVar(master, value="")
        self.input_fields = []

        self.main_frame = ttk.Frame(master, padding="15")
        self.main_frame.pack(fill='both', expand=True)

        # --- Widget Creation ---

        self._create_type_selection_widgets()

        self.dynamic_frame = ttk.Frame(self.main_frame)
        self.dynamic_frame.pack(pady=10)

        self.result_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        self.result_frame.pack(pady=10, fill='x')
        self.result_labels = {}

    def _create_type_selection_widgets(self):
        type_frame = ttk.LabelFrame(self.main_frame, text="1. Select Object Type", padding="10")
        type_frame.pack(pady=10, fill='x')

        ttk.Radiobutton(type_frame, text="2D Shapes", variable=self.current_shape_type, value="2D",
                        command=self._show_shape_selection).pack(side=tk.LEFT, padx=10)

        ttk.Radiobutton(type_frame, text="3D Shapes", variable=self.current_shape_type, value="3D",
                        command=self._show_shape_selection).pack(side=tk.LEFT, padx=10)

    def _show_shape_selection(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        self.clear_results()

        shape_type = self.current_shape_type.get()
        shapes = SHAPE_MAP.get(shape_type, {})

        if not shapes: return

        shape_select_frame = ttk.LabelFrame(self.dynamic_frame, text=f"2. Select a {shape_type} Object", padding="10")
        shape_select_frame.pack(fill='x', pady=5)

        button_frame = ttk.Frame(shape_select_frame)
        button_frame.pack(pady=5)

        col, row = 0, 0
        for name in shapes.keys():
            btn = ttk.Button(button_frame, text=name,
                             command=lambda n=name: self._create_input_fields(n))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            col += 1
            if col > 1:
                col = 0
                row += 1

    def _create_input_fields(self, shape_name):
        self.current_shape_name.set(shape_name)
        self.clear_results()

        for widget in self.dynamic_frame.winfo_children():
            if widget.winfo_name() == 'input_frame':
                widget.destroy()

        shape_type = self.current_shape_type.get()
        shape_info = SHAPE_MAP[shape_type][shape_name]
        params = shape_info["params"]

        input_frame = ttk.LabelFrame(self.dynamic_frame, name='input_frame',
                                     text=f"3. Enter Parameters for {shape_name}", padding="10")
        input_frame.pack(fill='x', pady=10)

        self.input_fields = []

        for i, param_name in enumerate(params):
            ttk.Label(input_frame, text=f"{param_name}:").grid(row=i, column=0, padx=5, pady=5, sticky='w')

            entry = ttk.Entry(input_frame, width=15)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            self.input_fields.append(entry)

        ttk.Button(input_frame, text="Calculate",
                   command=self._calculate).grid(row=len(params), column=0, columnspan=2, pady=10)

    def _calculate(self):
        try:
            values = []
            for entry in self.input_fields:
                val_str = entry.get().strip()
                if not val_str:
                    raise ValueError("All fields must be filled.")
                values.append(float(val_str))

            shape_type = self.current_shape_type.get()
            shape_name = self.current_shape_name.get()
            shape_class = SHAPE_MAP[shape_type][shape_name]["class"]

            # Instantiate the class with user values
            shape_instance = shape_class(*values)

            results = {}
            results["Surface Area"] = shape_instance.surface()
            if shape_type == "3D":
                results["Volume"] = shape_instance.volume()

            self._display_results(results)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected error occurred: {e}")

    def clear_results(self):
        for label in self.result_labels.values():
            label.destroy()
        self.result_labels = {}

    def _display_results(self, results):
        self.clear_results()

        row = 0
        for name, value in results.items():
            ttk.Label(self.result_frame, text=f"{name}:").grid(row=row, column=0, padx=5, pady=2, sticky='w')

            val_label = ttk.Label(self.result_frame, text=f"{value:,.4f}", font=('Arial', 10, 'bold'))
            val_label.grid(row=row, column=1, padx=5, pady=2, sticky='e')
            self.result_labels[name] = val_label
            row += 1


if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryApp(root)
    root.mainloop()