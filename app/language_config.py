import tkinter as tk
from tkinter import simpledialog, ttk
import sqlite3
from decks_homepage import DecksHomepage

class LanguageConfigFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_language_config_frame()     
        
    ### Create the language configurations window
    def create_language_config_frame(self):
        # Configure the outer rows and columns to absorb extra space
        self.rowconfigure(0, weight=1)
        self.rowconfigure(6, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)

        # Create the label for "Language Configuration" in the center rows/columns
        tk.Label(self, text="Language Configuration", font=("Arial", 16)).grid(row=1, column=1, columnspan=2, pady=10)

        # Create the dropdown (combobox) for language configurations
        self.configuration_var = tk.StringVar(self.controller)
        self.dropdown = ttk.Combobox(self, textvariable=self.configuration_var)
        self.dropdown.grid(row=2, column=1, columnspan=2, pady=10, sticky="ew")

        # Create the "Add New Configuration" button
        tk.Button(self, text="Add New Configuration", command=self.add_new_configuration).grid(row=3, column=1, pady=10)

        # Create the "Delete Configuration" button
        tk.Button(self, text="Delete Configuration", command=self.delete_language_configuration).grid(row=3, column=2, pady=10)

        # Create the "Execute" button
        tk.Button(self, text="Load Decks", command=self.execute_ankiconnect).grid(row=4, column=1, columnspan=2, pady=10)

        # Create the "Back" button to return to the user config screen
        tk.Button(self, text="Back", command=self.back_to_user_config).grid(row=5, column=1, columnspan=2, pady=10)

    ### Go back to User Configuration window
    def back_to_user_config(self):
        self.controller.show_frame(UserConfigFrame)

    def load_language_configurations_to_dropdown(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Access selected_user_id from the MainApp instance
        c.execute("SELECT configuration_name FROM language_configurations WHERE user_id=?", (self.controller.selected_user_id,))
        configurations = [row[0] for row in c.fetchall()]
        self.dropdown["values"] = configurations

        if self.dropdown["values"]:
            self.configuration_var.set(self.dropdown["values"][0])
        else:
            self.configuration_var.set('')

        conn.close()

    def add_new_configuration(self):
        self.new_window = tk.Toplevel(self.controller)
        NewLanguageConfigurationWindow(self.new_window, self.controller, self)

    def delete_language_configuration(self):
        # Confirm the deletion
        answer = tk.messagebox.askyesno("Delete Configuration", "Are you sure you want to delete this language configuration?")
        if answer:
            configuration_name = self.configuration_var.get()
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
    
            try:
                # Delete the selected language configuration from the database
                c.execute("DELETE FROM language_configurations WHERE configuration_name=? AND user_id=?", (configuration_name, self.controller.selected_user_id))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error deleting configuration from database: {e}")
            finally:
                conn.close()
        
        # Refresh the dropdown to reflect the change
        self.load_language_configurations_to_dropdown()

        # Set the selected value of the dropdown to the next available value
        if self.dropdown["values"]:
            self.configuration_var.set(self.dropdown["values"][0])
        else:
            self.configuration_var.set('')
            
    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.load_language_configurations_to_dropdown()
        
    def execute_ankiconnect(self):
        self.controller.configuration_name = self.configuration_var.get() # Store the selected language configuration as a global variable?
        self.controller.show_frame(DecksHomepage)
        self.destroy()  # Closes the current window
            
##### This class implements the logic for adding a new language configuration to a user profile
class NewLanguageConfigurationWindow:
    def __init__(self, root, main_app, lang_config_frame):
        self.root = root
        self.main_app = main_app
        self.lang_config_frame = lang_config_frame  
        self.root.title("Add New Configuration")

        # Learned vocab section
        self.learned_frame = tk.LabelFrame(root, text="Learned Vocab", padx=10, pady=10)
        self.learned_frame.grid(row=0, column=0, padx=10, pady=10)

        tk.Label(self.learned_frame, text="Deck Name").pack(pady=5)
        self.learned_deck_entry = tk.Entry(self.learned_frame, width=30)
        self.learned_deck_entry.pack(pady=5)

        # Dynamic form for learned card types and fields
        self.learned_card_entries = []
        self.learned_field_entries = []
        self.add_learned_card_button = tk.Button(self.learned_frame, text="Add Card Type & Fields", command=self.add_learned_card_field)
        self.add_learned_card_button.pack(pady=10)

        # New vocab section
        self.new_frame = tk.LabelFrame(root, text="New Vocab", padx=10, pady=10)
        self.new_frame.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.new_frame, text="Deck Name").pack(pady=5)
        self.new_deck_entry = tk.Entry(self.new_frame, width=30)
        self.new_deck_entry.pack(pady=5)

        # Dynamic form for new card types and fields
        self.new_card_entries = []
        self.new_field_entries = []
        self.add_new_card_button = tk.Button(self.new_frame, text="Add Card Type & Fields", command=self.add_new_card_field)
        self.add_new_card_button.pack(pady=10)
        
        # Language Selection
        self.language_frame = tk.LabelFrame(root, text="Language Selection", padx=10, pady=10)
        self.language_frame.grid(row=1, columnspan=2, padx=10, pady=10)

        tk.Label(self.language_frame, text="Select Language").pack(pady=5)
        self.language_var = tk.StringVar(value="Arabic")  # Default selection
        self.language_combobox = ttk.Combobox(self.language_frame, textvariable=self.language_var, values=["Arabic", "Hindi", "Mandarin"], state="readonly")
        self.language_combobox.pack(pady=5)

        # Save Button
        tk.Button(root, text="Save Configuration", command=self.save_language_configuration).grid(row=1, columnspan=2, pady=20)

    def add_learned_card_field(self):
        frame = tk.Frame(self.learned_frame)
        frame.pack(pady=5, fill=tk.X)

        tk.Label(frame, text="Card Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        card_entry = tk.Entry(frame, width=20)
        card_entry.grid(row=0, column=1, padx=5, pady=5)
        self.learned_card_entries.append(card_entry)

        tk.Label(frame, text="Fields (comma separated):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        field_entry = tk.Entry(frame, width=20)
        field_entry.grid(row=1, column=1, padx=5, pady=5)
        self.learned_field_entries.append(field_entry)

    def add_new_card_field(self):
        frame = tk.Frame(self.new_frame)
        frame.pack(pady=5, fill=tk.X)

        tk.Label(frame, text="Card Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        card_entry = tk.Entry(frame, width=20)
        card_entry.grid(row=0, column=1, padx=5, pady=5)
        self.new_card_entries.append(card_entry)

        tk.Label(frame, text="Fields (comma separated):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        field_entry = tk.Entry(frame, width=20)
        field_entry.grid(row=1, column=1, padx=5, pady=5)
        self.new_field_entries.append(field_entry)

    def save_language_configuration(self):
        configuration_name = simpledialog.askstring("Input", "Enter name for this configuration:")
        if configuration_name:
            
            # Load all the user inputs
            learned_deck = self.learned_deck_entry.get()
            new_deck = self.new_deck_entry.get()
            configuration_language = self.language_var.get()
            
            # Connect to the database and append all the info
            conn = sqlite3.connect('database.db')
            c = conn.cursor()

        try:
            # Insert into languages table
            c.execute("INSERT INTO language_configurations (user_id, configuration_language, configuration_name, learned_deck, new_deck) VALUES (?, ?, ?, ?, ?)",
                      (self.main_app.selected_user_id, configuration_language, configuration_name, learned_deck, new_deck))
            configuration_id = c.lastrowid  # Get the ID of the newly inserted row

            # Insert card types and fields
            for card_type_entry in self.learned_card_entries:
                card_type = card_type_entry.get()
                c.execute("INSERT INTO card_types (configuration_id, card_type_name) VALUES (?, ?)", (configuration_id, card_type))
                card_type_id = c.lastrowid

                for field_entry in self.learned_field_entries:
                    field = field_entry.get()
                    c.execute("INSERT INTO card_fields (card_type_id, field_name) VALUES (?, ?)", (card_type_id, field))

            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving configuration to database: {e}")
        finally:
            conn.close()
            
        # Refresh dropdown in LanguageConfigFrame
        self.lang_config_frame.load_language_configurations_to_dropdown()

        self.root.destroy()
            