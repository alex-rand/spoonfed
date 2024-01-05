import tkinter as tk
from tkinter import simpledialog, ttk
import sqlite3
from language_config import LanguageConfigFrame

class UserConfigFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_user_config_frame()
        self.load_all_saved_users()

    ### Create a window for selecting the user
    def create_user_config_frame(self):
        # Grid configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="User Configuration", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        self.anki_profile_label = tk.Label(self, text="Anki Profile:")
        self.anki_profile_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        # Dropdown for saved user profiles
        self.saved_users_var = tk.StringVar(self.controller)  # Use self.controller here
        self.saved_users_dropdown = ttk.Combobox(self, textvariable=self.saved_users_var)
        self.saved_users_dropdown.grid(row=1, column=1, padx=10, pady=5)

        # Button to select the user and proceed
        tk.Button(self, text="Continue", command=self.proceed_with_selected_user).grid(row=3, column=0, columnspan=2, pady=10)

        # Button to add a new user
        tk.Button(self, text="Add New User", command=self.add_new_user).grid(row=4, column=0, columnspan=2, pady=10)
    
    ### Populate a picklist with all existing user names in the database
    def load_all_saved_users(self):
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT profile_name FROM users")
        user_profiles = [row[0] for row in c.fetchall()]

        self.saved_users_dropdown["values"] = user_profiles   
        self.saved_users_dropdown.current(0) 
        conn.close()

    ### Create a new user and append to the database
    def add_new_user(self):
        new_user = simpledialog.askstring("Input", "Enter new user profile name:")
        if new_user:
            # Update the configurations file immediately
            self.set_user_configuration(new_user)
            # Refresh the dropdown with the updated users list
            self.load_all_saved_users()

    def set_user_configuration(self, user_name):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Insert or ignore (in case of duplicate profile_name)
        c.execute("INSERT OR IGNORE INTO users (profile_name) VALUES (?)", (user_name,))
        conn.commit()

        # Get the user ID of the selected/added user
        c.execute("SELECT id FROM users WHERE profile_name=?", (user_name,))
        self.controller.selected_user_id = c.fetchone()[0]
        
        conn.close()
        
    ### Once a user is selected, proceed to the Configurations window
    def proceed_with_selected_user(self):
        selected_user = self.saved_users_var.get()
        if selected_user:
            # Set the user configuration and proceed to the language config screen
            self.set_user_configuration(selected_user)
            
            # Move to the Language Configuration frame
            self.controller.show_frame(LanguageConfigFrame)