import tkinter as tk
from tkinter import ttk
from generating_functions import generate

class IPlusOneFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Audio-related widgets sub-frame
        self.audio_frame = tk.Frame(self)
        self.audio_frame.pack(pady=10)

        # Checkbox for 'with audio'
        self.audio_checkbox_var = tk.BooleanVar(value=True)
        self.audio_checkbox = tk.Checkbutton(self.audio_frame, text='with audio', var=self.audio_checkbox_var, command=self.toggle_audio_options)
        self.audio_checkbox.pack(side="top")

        # Label and Picklist for 'choose audio source'
        self.audio_source_label = tk.Label(self.audio_frame, text='Choose audio source:')
        self.audio_source_picklist = ttk.Combobox(self.audio_frame, values=['Narakeet', 'Fake'])
        self.audio_source_picklist.current(0)  # Set default value
        self.toggle_audio_options()  # Initially set the state based on the checkbox

        # Label and Picklist for 'choose model'
        self.model_label = tk.Label(self, text='Choose model:')
        self.model_var = tk.StringVar()
        self.model_picklist = ttk.Combobox(self, textvariable=self.model_var, values=['gpt-4-1106-preview', 'gpt-3.5-turbo-1106', 'gpt-3.5-turbo'])
        self.model_label.pack()
        self.model_picklist.current(0)
        self.model_picklist.pack()
        
        # Label and Picklist for N sentences
        self.nsentences_label = tk.Label(self, text='N sentences to generate:')
        self.nsentences_var = tk.StringVar()
        self.nsentences_picklist = ttk.Combobox(self, textvariable=self.nsentences_var, values=['5', '10', '15', '20', '25', '30', '35', '40', '45', '50',])
        self.nsentences_picklist.current(0)
        self.nsentences_label.pack()
        self.nsentences_picklist.pack()

        # Button for 'Generate'
        self.modify_prompt_button = tk.Button(self, text="Generate Sentences", command=self.on_press_generate)
        self.modify_prompt_button.pack()

        # Scrollable table
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(self.table_frame, columns=("Column1", "Column2", "Column3"), show="headings")
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

    def toggle_audio_options(self):
        if self.audio_checkbox_var.get():
            self.audio_source_label.pack(side="top")
            self.audio_source_picklist.pack(side="top")
        else:
            self.audio_source_label.pack_forget()
            self.audio_source_picklist.pack_forget()
            
    def clear_treeview(self):
        """Clear all entries in the treeview."""
        for item in self.table.get_children():
            self.table.delete(item)

    def create_export_buttons(self):
        """Create 'Export to Anki' buttons."""
        self.export_button_frame = tk.Frame(self)
        self.export_button_frame.pack(fill="x", pady=10)

        self.export_to_anki_button = tk.Button(self.export_button_frame, text="Export to Anki")
        self.export_to_anki_button.pack(side="left", padx=10)

        self.cancel_export_button = tk.Button(self.export_button_frame, text="Cancel")
        self.cancel_export_button.pack(side="left", padx=10)

    def populate_treeview(self, data_frame):
        """Populate the treeview with data from a pandas DataFrame."""
        self.clear_treeview()  # Clear existing data in the treeview
        self.table["columns"] = ["select"] + list(data_frame.columns)
        self.table["show"] = "headings"

        # Setup column headings
        self.table.heading("select", text="Select")
        for col in data_frame.columns:
            self.table.heading(col, text=col)

        # Inserting rows into the treeview with checkboxes
        for row in data_frame.itertuples(index=False, name=None):
            self.table.insert("", "end", values=([0] + list(row)))

        # Create horizontal scrollbar
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.table.xview)
        hsb.pack(side="bottom", fill="x")
        self.table.configure(xscrollcommand=hsb.set)

        # Create 'Export to Anki' buttons
        self.create_export_buttons()
          
    def on_press_generate(self):
        generated_sentences = generate(self.controller, self)
        if generated_sentences is not None:
            self.populate_treeview(generated_sentences)