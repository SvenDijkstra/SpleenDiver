# system_monitor.py

import psutil
from config_manager import load_config

def is_process_running():
    """Checks if the target game process is currently running."""
    config = load_config()
    target_name = config.get('target_process_name')

    if not target_name:
        return False

    # Convert target_name to lowercase once before the loop
    target_name_lower = target_name.lower()

    for proc in psutil.process_iter(['name']):
        # Compare both names in lowercase
        if proc.info['name'].lower() == target_name_lower:
            return True
    return False

def get_all_processes():
    """Retrieves a list of all running processes with their PIDs."""
    process_list = []
    # Iterate over all running processes and get their pid and name
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Format the string as "[PID] Process Name"
            process_list.append(f"[{proc.info['pid']}] {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Some processes may not be accessible, so we skip them
            pass
    return sorted(process_list, key=lambda x: x.lower())

def activate_game_window(x_coord=960, y_coord=540, sleep_time=0.1):
    """
    Activates the game window by simulating a mouse click at a specified
    coordinate (default is the center of a 1920x1080 screen).
    This ensures the game is focused and ready to receive key inputs.

    Args:
        x_coord (int): X-coordinate for the click.
        y_coord (int): Y-coordinate for the click.
        sleep_time (float): Time to wait after the click to allow the OS to switch focus.
    """
    print(f"Activating game window by clicking at ({x_coord}, {y_coord})...")
    # Move the mouse to the coordinate and click
    pyautogui.click(x=x_coord, y=y_coord)
    # Wait briefly for the OS to register the focus change
    time.sleep(sleep_time)

# --- The is_game_paused function, kept exactly as requested ---