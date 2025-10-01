# main.py

import tkinter as tk
from tkinter import ttk, messagebox  # Import messagebox for dialogs
from system_monitor import is_process_running, get_all_processes
from config_manager import load_config, save_config


class AutoSolveApp:
    def __init__(self, master):
        self.master = master
        master.title("SpleenDiver Controller")
        self.config = load_config()

        # --- Create Menu Bar ---
        self.create_menu()

        # --- Status Bar Check (Immediate Action) ---
        is_running = is_process_running()
        self.process_status_var = tk.StringVar(value=f"Game Status: {'Running' if is_running else 'NOT FOUND'}")

        # --- Build GUI Elements ---
        # 1. Status Bar
        status_label = ttk.Label(master, textvariable=self.process_status_var)
        status_label.pack(pady=10)

        # 2. Main Control Button
        self.start_button = ttk.Button(master, text="Start AutoSolve",
                                       command=self.start_autosolve,
                                       state=tk.NORMAL if is_running else tk.DISABLED)
        self.start_button.pack(pady=5)

        # 3. Configuration Checkbox (Example)
        self.skill_use_var = tk.BooleanVar() # Value set by update_ui_from_config
        skill_check = ttk.Checkbutton(master, text="Enable Skills (C/D)",
                                      variable=self.skill_use_var,
                                      command=self.update_config_from_ui)
        skill_check.pack(pady=5)

        # Load initial config into the UI
        self.update_ui_from_config()


    def create_menu(self):
        """Creates the main menu bar for the application."""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        # --- ADDED SAVE/LOAD OPTIONS ---
        file_menu.add_command(label="Save Configuration", command=self.save_config_action)
        file_menu.add_command(label="Load Configuration", command=self.load_config_action)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Show Running Processes", command=self.show_processes_window)

    def save_config_action(self):
        """Saves the current configuration to a file and shows a message."""
        self.update_config_from_ui() # Ensure current UI state is captured
        save_config(self.config)
        messagebox.showinfo("Success", "Configuration has been saved to config.json")

    def load_config_action(self):
        """Loads the configuration from a file and updates the UI."""
        self.config = load_config()
        self.update_ui_from_config()
        messagebox.showinfo("Success", "Configuration has been loaded from config.json")

    def update_config_from_ui(self):
        """Updates the internal config dictionary from the UI elements' state."""
        self.config['auto_solve_enabled'] = self.skill_use_var.get()
        print("Internal config updated from UI.")

    def update_ui_from_config(self):
        """Updates the UI elements to reflect the current internal config."""
        self.skill_use_var.set(self.config.get('auto_solve_enabled', False))

    def show_processes_window(self):
        """Creates a new window to display all running processes."""
        proc_window = tk.Toplevel(self.master)
        proc_window.title("Running Processes")
        proc_window.geometry("450x600")

        frame = ttk.Frame(proc_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        processes = get_all_processes()
        for process in processes:
            listbox.insert(tk.END, process)

    def start_autosolve(self):
        """Placeholder for starting the main solving thread."""
        print("AutoSolve started!")


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('300x150')
    app = AutoSolveApp(root)
    root.mainloop()