import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
import sys # Import sys for clean process exit
import math # Used for safe eval in PI handling

# --- Color Constants for Dark Theme ---
BG_DARK = '#2C2C2C'      # Main window background
FG_LIGHT = '#E0E0E0'     # Foreground text color
BG_MID = '#404040'       # Plot/Entry field background
ACCENT_BLUE = '#00AEEF'  # Accent color for buttons/plot lines

# --- Function Definitions and Mappings ---
FUNCTION_MAP = {
    'sin': np.sin,
    'cos': np.cos,
    'tan': np.tan,
    # Safe division for xcos, handling division by zero at x=0
    'xcos': lambda x: np.divide(np.cos(x), x, out=np.full_like(x, np.nan), where=x!=0)
}

# Default limits are always stored in RADIANS
DEFAULT_LIMITS = {
    'sin': (-2 * np.pi, 2 * np.pi),
    'cos': (-2 * np.pi, 2 * np.pi),
    'tan': (-np.pi / 2, np.pi / 2),
    'xcos': (-4 * np.pi, 4 * np.pi)
}

# --- Matplotlib Dark Theme Customization ---
# Settings applied using context manager for cleaner plotting logic
DARK_STYLE = {
    'figure.facecolor': BG_DARK,
    'axes.facecolor': BG_MID,
    'axes.edgecolor': FG_LIGHT,
    'axes.labelcolor': FG_LIGHT,
    'text.color': FG_LIGHT,
    'xtick.color': FG_LIGHT,
    'ytick.color': FG_LIGHT,
    'grid.color': '#707070',
    'legend.facecolor': BG_MID,
    'legend.edgecolor': FG_LIGHT,
    'axes.grid': True,
    'grid.linestyle': '--',
    'axes.linewidth': 0.8
}


class FunctionPlotterApp:
    """Handles the single-window application with inputs and embedded plot."""
    def __init__(self, master):
        self.master = master
        self.master.title("Function Plotter - Single Window")
        # Removed fixed geometry; using minimum size and weights for responsiveness
        self.master.minsize(900, 600)
        self.master.config(bg=BG_DARK)
        
        self._setup_styles()
        self._setup_variables()
        self._setup_ui()
        
        # Plot default 'sin' function on startup
        # Initial plot uses the default 1000 points
        self._update_plot('sin', *DEFAULT_LIMITS['sin'], 1000)
        
        # --- FIX: Bind window close event to ensure clean exit ---
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """Handler for when the user clicks the window's close button."""
        # Cleanly close the Matplotlib figure to release resources
        if self.fig:
            plt.close(self.fig)
        
        # Destroy the Tkinter window
        self.master.destroy()
        
        # Force a clean exit of the Python process.
        sys.exit()


    def _setup_styles(self):
        """Configure Tkinter Ttk styles for the dark theme and high-res display."""
        style = ttk.Style()
        style.theme_use('default') 
        style.configure('TFrame', background=BG_DARK)
        # Increased font size to 18 and set to bold for high-resolution visibility
        style.configure('TLabel', background=BG_DARK, foreground=FG_LIGHT, font=('Arial', 18, 'bold'))
        # Set Entry font to bold
        style.configure('TEntry', fieldbackground=BG_MID, foreground=FG_LIGHT, borderwidth=1, relief='flat', font=('Arial', 18, 'bold'))
        style.configure('TButton', background=ACCENT_BLUE, foreground=BG_DARK, 
                        # Increased font size and padding
                        font=('Arial', 18, 'bold'), borderwidth=0, padding=[20, 10]) 
        style.map('TButton', background=[('active', ACCENT_BLUE)], foreground=[('active', 'white')])

    def _setup_variables(self):
        """Initialize control variables."""
        self.unit_var = tk.StringVar(value='Radians')
        self.func_entry = tk.StringVar(value='sin')
        self.limit_lower = tk.StringVar(value='')
        self.limit_upper = tk.StringVar(value='')
        # New variable for number of points, defaulted to 1000
        self.points_count = tk.StringVar(value='1000') 
        # References for Matplotlib figure and axis
        self.fig = None
        self.ax = None
        self.canvas = None

    def _create_field(self, label_text, var, row):
        """Helper to create and grid a label/entry pair inside the control frame."""
        # Increased pady to 15 for more space
        ttk.Label(self.control_frame, text=label_text).grid(row=row, column=0, sticky='w', pady=15)
        entry = ttk.Entry(self.control_frame, textvariable=var, width=25, style='TEntry')
        entry.grid(row=row, column=1, sticky='ew', pady=15)
        return entry

    def _setup_ui(self):
        """Creates the main two-column layout (Controls and Plot)."""
        
        # Configure the main window grid layout for responsiveness
        # Column 0 (Controls) gets a small weight so it resizes slightly
        self.master.grid_columnconfigure(0, weight=1) 
        # Column 1 (Plot) gets a large weight so it dominates resizing
        self.master.grid_columnconfigure(1, weight=5) 
        self.master.grid_rowconfigure(0, weight=1)

        # 1. Control Frame (Left Column for Input Widgets)
        self.control_frame = ttk.Frame(self.master, padding="100") # Increased padding
        self.control_frame.grid(row=0, column=0, sticky='nsew')
        self.control_frame.columnconfigure(1, weight=1) # Makes the entry widgets stretch
        
        self._create_field("Function (sin, cos, tan, xcos):", self.func_entry, row=0)
        self._create_field("Lower Limit (Optional):", self.limit_lower, row=1)
        self._create_field("Upper Limit (Optional):", self.limit_upper, row=2)
        # New input field for the number of points
        self._create_field("Number of Points (e.g., 1000):", self.points_count, row=3)

        self.unit_btn = ttk.Button(
            self.control_frame, textvariable=self.unit_var, command=self._toggle_units, width=15, style='TButton'
        )
        # Adjusted pady to 25
        self.unit_btn.grid(row=4, column=0, columnspan=2, pady=25)

        self.plot_btn = ttk.Button(
            self.control_frame, text="Plot Function", command=self._validate_and_plot, style='TButton'
        )
        # Adjusted pady to 20
        self.plot_btn.grid(row=5, column=0, columnspan=2, pady=20, sticky='ew')

        # 2. Plot Frame (Right Column for Matplotlib Canvas)
        self.plot_frame = ttk.Frame(self.master, padding="15")
        self.plot_frame.grid(row=0, column=1, sticky='nsew')
        
        self._create_plot_area(self.plot_frame)

    def _create_plot_area(self, master_frame):
        """Initializes the Matplotlib figure and canvas within the plot frame."""
        
        # Initialize figure and axes using the dark style context
        with style.context(DARK_STYLE):
            self.fig, self.ax = plt.subplots(figsize=(8, 6))

        self.ax.set_title("Function Plotter: Enter parameters and click 'Plot'", color=FG_LIGHT)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=master_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(bg=BG_DARK)
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def _toggle_units(self):
        """Toggles the unit between Radians and Degrees."""
        self.unit_var.set('Degrees' if self.unit_var.get() == 'Radians' else 'Radians')

    def _validate_and_plot(self):
        """Validates input, determines limits in the current unit, and converts them to radians for the plot."""
        func_name = self.func_entry.get().strip().lower()
        
        if func_name not in FUNCTION_MAP:
            messagebox.showerror("Input Error", "Function unknown. Please use sin, cos, tan, or xcos.")
            return

        # 1. Validate Number of Points
        points_str = self.points_count.get().strip()
        num_points = 1000 # Default value
        
        if points_str:
            try:
                num_points = int(points_str)
                if num_points <= 0:
                     raise ValueError("Points must be a positive integer.")
            except ValueError:
                messagebox.showerror("Input Error", "Number of points must be a positive integer (e.g., 1000).")
                return

        # 2. Determine raw limits (lower_val, upper_val) based on user input or unit-aware defaults
        try:
            lower_str = self.limit_lower.get().strip()
            upper_str = self.limit_upper.get().strip()
            
            is_degrees_mode = self.unit_var.get() == 'Degrees'

            if lower_str and upper_str:
                # User specified limits (assumed to be in the currently selected unit)
                safe_globals = {'pi': math.pi} 
                # Use eval to handle expressions like '2*pi' in user input
                lower_val = eval(lower_str.lower().replace('pi', 'math.pi'), safe_globals)
                upper_val = eval(upper_str.lower().replace('pi', 'math.pi'), safe_globals)
            else:
                # Use default limits (DEFAULT_LIMITS are in Radians)
                default_rad_lower, default_rad_upper = DEFAULT_LIMITS[func_name]
                
                if is_degrees_mode:
                    # If in Degrees mode, the raw limit value should be the degree equivalent
                    # of the default limits for axis display.
                    lower_val = np.rad2deg(default_rad_lower)
                    upper_val = np.rad2deg(default_rad_upper)
                else: # Radians mode
                    lower_val = default_rad_lower
                    upper_val = default_rad_upper

            # Basic numerical validation
            if not isinstance(lower_val, (int, float)) or not isinstance(upper_val, (int, float)):
                 raise ValueError("Limit expression must resolve to a number.")

            if lower_val >= upper_val:
                messagebox.showerror("Input Error", "Lower limit must be less than upper limit.")
                return

        except Exception as e:
            messagebox.showerror("Input Error", f"Limits must be valid numbers or expressions (e.g., '2*pi'). Error: {e}")
            return

        # 3. CONVERSION TO RADIANS for calculation (only if in degrees mode)
        # NumPy functions require radians for plotting.
        if is_degrees_mode:
            lower_rad = np.deg2rad(lower_val)
            upper_rad = np.deg2rad(upper_val)
        else: # Radians mode
            lower_rad = lower_val
            upper_rad = upper_val
        
        # 4. Pass the RADIAN limits to the plot
        self._update_plot(func_name, lower_rad, upper_rad, num_points)

    def _update_plot(self, func_name, lower, upper, num_points):
        """Updates the existing Matplotlib plot with new data."""
        
        # Use the dark style context for consistent plotting elements
        with style.context(DARK_STYLE):
            # 1. Clear the previous plot
            self.ax.clear()

            # 2. Prepare data
            # x is in RADIANS because it comes from _validate_and_plot as lower_rad/upper_rad
            x = np.linspace(lower, upper, num_points, endpoint=True)
            y = FUNCTION_MAP[func_name](x) # Calculation is correct because x is in radians

            # 3. Determine display units
            is_degrees = self.unit_var.get() == 'Degrees'
            x_display = np.rad2deg(x) if is_degrees else x # Convert x-values back for display
            x_label = 'x (degrees)' if is_degrees else 'x (radians)'
                
            # 4. Plot new data
            self.ax.plot(x_display, y, label=f'$y = {func_name}(x)$', color=ACCENT_BLUE, linewidth=2)
            
            # 5. Set titles and labels
            self.ax.set_title(f"Plot of $y = {func_name}(x)$", fontsize=14, fontweight='bold')
            self.ax.set_xlabel(x_label, fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            
            # --- FIX: Clip Y-axis for the tan function to handle asymptotes ---
            if func_name == 'tan':
                # Manually set Y limits to hide the massive spikes near the asymptotes
                self.ax.set_ylim([-10, 10]) 
            else:
                # Use automatic scaling for all other functions
                self.ax.autoscale(enable=True, axis='y')

            # Re-add legend, axes lines
            self.ax.legend(loc='upper right')
            self.ax.axhline(0, color=FG_LIGHT, linewidth=0.8)
            self.ax.axvline(0, color=FG_LIGHT, linewidth=0.8)
            
            # 6. Redraw the canvas
            self.canvas.draw()


# --- Main Application Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FunctionPlotterApp(root)
    root.mainloop()
