# main.py

import tkinter as tk
from tkinter import ttk, messagebox
from system_monitor import is_process_running, get_all_processes
from config_manager import load_config, save_config
from vision_detector import get_detection_status


class AutoSolveApp:
    def __init__(self, master):
        self.master = master
        master.title("SpleenDiver Controller")
        self.config = load_config()

        # --- Create Menu Bar ---
        self.create_menu()

        # --- Status Variables ---
        is_running = is_process_running()
        self.process_status_var = tk.StringVar(
            value=f"Game Status: {'Running' if is_running else 'NOT FOUND'}"
        )
        self.region_status_var = tk.StringVar(value="Play Region: UNCHECKED")
        self.grid_status_var = tk.StringVar(value="Grid: UNCHECKED")

        # --- Build GUI Elements ---
        # Status Frame
        status_frame = ttk.LabelFrame(master, text="System Status", padding=10)
        status_frame.pack(pady=10, padx=10, fill=tk.X)

        # 1. Process Status
        process_label = ttk.Label(status_frame, textvariable=self.process_status_var)
        process_label.grid(row=0, column=0, sticky=tk.W, pady=2)

        # 2. Play Region Status
        region_label = ttk.Label(status_frame, textvariable=self.region_status_var)
        region_label.grid(row=1, column=0, sticky=tk.W, pady=2)

        # 3. Grid Status
        grid_label = ttk.Label(status_frame, textvariable=self.grid_status_var)
        grid_label.grid(row=2, column=0, sticky=tk.W, pady=2)

        # Refresh Detection Button
        refresh_btn = ttk.Button(status_frame, text="Refresh Detection",
                                 command=self.refresh_detection)
        refresh_btn.grid(row=3, column=0, pady=5)

        # Control Frame
        control_frame = ttk.Frame(master, padding=10)
        control_frame.pack(pady=5)

        # 4. Main Control Button
        self.start_button = ttk.Button(control_frame, text="Start AutoSolve",
                                       command=self.start_autosolve,
                                       state=tk.NORMAL if is_running else tk.DISABLED)
        self.start_button.pack(pady=5)

        # 5. Configuration Checkbox
        self.skill_use_var = tk.BooleanVar()
        skill_check = ttk.Checkbutton(control_frame, text="Enable Skills (C/D)",
                                      variable=self.skill_use_var,
                                      command=self.update_config_from_ui)
        skill_check.pack(pady=5)

        # Load initial config into the UI
        self.update_ui_from_config()

        # Perform initial detection if process is running
        if is_running:
            self.refresh_detection()

    def create_menu(self):
        """Creates the main menu bar for the application."""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Configuration", command=self.save_config_action)
        file_menu.add_command(label="Load Configuration", command=self.load_config_action)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Show Running Processes", command=self.show_processes_window)
        tools_menu.add_command(label="Refresh Detection", command=self.refresh_detection)

    def refresh_detection(self):
        """Performs play region and grid detection checks."""
        # First check if process is running
        is_running = is_process_running()
        self.process_status_var.set(
            f"Game Status: {'Running' if is_running else 'NOT FOUND'}"
        )

        if not is_running:
            self.region_status_var.set("Play Region: N/A (Game not running)")
            self.grid_status_var.set("Grid: N/A (Game not running)")
            self.start_button.config(state=tk.DISABLED)
            return

        # Update status to show checking
        self.region_status_var.set("Play Region: CHECKING...")
        self.grid_status_var.set("Grid: CHECKING...")
        self.master.update()

        # Perform detection
        region_valid, region_status, grid_found, grid_size, grid_status = get_detection_status()

        # Update status displays
        self.region_status_var.set(region_status)
        self.grid_status_var.set(grid_status)

        # Enable/disable start button based on detection results
        if region_valid and grid_found:
            self.start_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.DISABLED)

    def save_config_action(self):
        """Saves the current configuration to a file and shows a message."""
        self.update_config_from_ui()
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
        messagebox.showinfo("AutoSolve", "AutoSolve engine started!")


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('350x280')
    app = AutoSolveApp(root)
    root.mainloop()