import tkinter as tk
from tkinter import ttk, scrolledtext
import re

class StringCounterApp:
    def __init__(self, master):
        self.master = master
        master.title("String Analyzer")
        master.geometry("650x500")
        
        # --- NIGHT MODE COLOR PALETTE ---
        BG_COLOR = '#202124'      # Dark background
        SURFACE_COLOR = '#313235' # Lighter background for input/containers
        TEXT_COLOR = '#E8EAED'    # Light gray text
        ACCENT_COLOR = '#A0C3FF'  # Soft blue for accent/results
        BUTTON_BG = '#40444C'     # Button default color
        BUTTON_HOVER = '#50545C'  # Button hover color
        
        # Apply theme colors to the main window
        master.config(padx=20, pady=20, bg=BG_COLOR)

        # Configure TTK styles for the dark theme
        style = ttk.Style()
        style.theme_use('clam') 

        # Global/Frame styling
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR)

        # Radiobutton styling
        style.configure('TRadiobutton', 
                        background=BG_COLOR, 
                        foreground=TEXT_COLOR, 
                        indicatorcolor=TEXT_COLOR, 
                        font=('Arial', 10))
        style.map('TRadiobutton', 
                  background=[('active', BG_COLOR)], 
                  foreground=[('active', ACCENT_COLOR)])

        # Button styling (Accent)
        style.configure('Accent.TButton', 
                        font=('Arial', 10, 'bold'), 
                        foreground=TEXT_COLOR, 
                        background=BUTTON_BG,
                        bordercolor=BUTTON_BG,
                        relief='flat',
                        padding=[10, 5])
        style.map('Accent.TButton',
                  background=[('active', BUTTON_HOVER)],
                  foreground=[('active', ACCENT_COLOR)])
        # --- END OF THEME CONFIG ---

        # State variables
        self.count_mode = tk.StringVar(value="Letters")
        self.result_text = tk.StringVar(value="Letters Count: 0")
        self.number_count_text = tk.StringVar(value="Numbers Count: 0")

        # --- Layout Setup using Grid ---
        main_frame = ttk.Frame(master)
        main_frame.pack(fill='both', expand=True)

        # 1. Input Section
        ttk.Label(main_frame, text="Input String:", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 5))

        # ScrolledText for multi-line input
        self.input_text = scrolledtext.ScrolledText(main_frame, 
                                                    wrap=tk.WORD, 
                                                    height=8, 
                                                    width=50, 
                                                    font=('Arial', 10), 
                                                    relief=tk.FLAT, 
                                                    borderwidth=0,
                                                    bg=SURFACE_COLOR, 
                                                    fg=TEXT_COLOR,   
                                                    insertbackground=ACCENT_COLOR 
                                                    )
        self.input_text.grid(row=1, column=0, sticky='nsew', padx=(0, 10))
        self.input_text.bind('<KeyRelease>', self.update_count)

        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=3) 
        main_frame.grid_columnconfigure(1, weight=1)

        # 2. Options and Results Section (Right side)
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=1, column=1, sticky='nsw', padx=10)

        ttk.Label(options_frame, text="Count By:", font=('Arial', 10, 'bold')).pack(pady=(0, 5), anchor='w')

        # Radio Buttons
        modes = [("Letters", "Letters"), ("Words", "Words"), ("Sentences", "Sentences")]
        for text, mode in modes:
            rb = ttk.Radiobutton(options_frame, text=text, variable=self.count_mode, value=mode, command=self.update_count)
            rb.pack(anchor='w', pady=2)

        # --- Results Display ---
        
        # Primary Counter Label
        ttk.Label(options_frame, textvariable=self.result_text, 
                  font=('Arial', 14, 'bold'), 
                  foreground=ACCENT_COLOR).pack(pady=(20, 5), anchor='w')

        # Secondary Number Counter Label
        ttk.Label(options_frame, textvariable=self.number_count_text, 
                  font=('Arial', 10), 
                  foreground=TEXT_COLOR).pack(pady=(5, 0), anchor='w')

        # 3. Action Buttons Section (Bottom)
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)

        # Container for the two side-by-side buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # Revert button
        revert_button = ttk.Button(button_frame, text="Revert String", command=self.revert_string, style='Accent.TButton')
        revert_button.pack(side=tk.LEFT, padx=5)
        
        # Clean button
        clean_button = ttk.Button(button_frame, text="Clean String", command=self.clean_string, style='Accent.TButton')
        clean_button.pack(side=tk.LEFT, padx=5)
        
        # Initial call to populate the count when the app starts
        self.update_count()

    # --- Core Counting Logic ---
    def update_count(self, event=None): 
        """
        Calculates all counts (Letters, Words, Sentences, and Numbers) 
        and updates the displays.
        """
        text = self.input_text.get("1.0", tk.END).strip()
        mode = self.count_mode.get()
        count = 0

        # 1. Number Counting Logic (Counts all individual digits 0-9)
        number_count = len(re.findall(r'\d', text)) 
        self.number_count_text.set(f"Numbers Count: {number_count}")

        # 2. Primary Counting Logic
        if not text:
            count = 0
        elif mode == "Letters":
            # Count only alphabetic characters (a-z and A-Z)
            count = len(re.findall(r'[a-zA-Z]', text))
            
        elif mode == "Words":
            # Split the text into tokens (words)
            words = text.split()
            
            # Filter tokens: only count as a word if the token is NOT purely composed of digits.
            # Tokens containing mixed characters (e.g., "word123") or decimals (e.g., "1.23") are counted.
            # Only tokens matching the pattern of one or more digits (e.g., "123", "45") are excluded.
            valid_words = [word for word in words if not re.fullmatch(r'\d+', word)]
            count = len(valid_words)
            
        elif mode == "Sentences":
            # --- FINAL SENTENCE LOGIC: Handles multiple dots and non-terminated text ---
            
            # 1. Normalize the text: replace any sequence of two or more dots with a single dot. 
            text_normalized = re.sub(r'\.{2,}', '.', text)
            
            # 2. Split the normalized text based on any single sentence terminator (.?!).
            sentences = re.split(r'[.?!]', text_normalized)
            
            # 3. Count the resulting non-empty segments (the valid sentences).
            valid_segments = [s.strip() for s in sentences if s.strip()]
            count = len(valid_segments)
            
            # 4. Correct for incomplete final sentence.
            # Check if the original text ends with a terminator (optionally followed by whitespace).
            text_ends_with_terminator = bool(re.search(r'[.?!]\s*$', text))

            if count > 0:
                if not text_ends_with_terminator:
                    # If the text has segments but does NOT end in punctuation, the last segment is incomplete.
                    # We subtract 1 to remove the final, un-terminated segment from the count.
                    count -= 1
            
            # Ensure count is not negative
            count = max(0, count)


        self.result_text.set(f"{mode} Count: {count}")

    # --- Revert Logic ---
    def revert_string(self):
        """Reverses the order of all characters in the input string and updates the text area."""
        text = self.input_text.get("1.0", tk.END).strip()
        
        if text:
            reversed_text = text[::-1]
            
            # Clear the text area and insert the reversed text
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", reversed_text)
            
            # Immediately trigger a count update after the revert
            self.update_count()

    # --- Clean Logic ---
    def clean_string(self):
        """Clears the entire input text area and updates the counts."""
        self.input_text.delete("1.0", tk.END)
        # Immediately trigger a count update after the clean
        self.update_count()


# Standard boilerplate to run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = StringCounterApp(root)
    root.mainloop()
