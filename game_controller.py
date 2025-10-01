# game_controller.py

import time
import pyautogui
import pygetwindow as gw
from config_manager import load_config


def focus_game_window():
    """
    Finds and focuses the game window.
    Returns: True if successful, False if window not found
    """
    config = load_config()
    target_name = config.get('target_process_name', 'dota2.exe')

    # Remove .exe extension for window title search
    game_name = target_name.replace('.exe', '')

    try:
        # Get all windows
        windows = gw.getAllTitles()

        # Find window that contains the game name (case-insensitive)
        game_window = None
        for window_title in windows:
            if game_name.lower() in window_title.lower() or 'dota' in window_title.lower():
                game_window = gw.getWindowsWithTitle(window_title)[0]
                break

        if game_window:
            print(f"Focusing game window: {game_window.title}")
            game_window.activate()
            time.sleep(0.2)  # Wait for window to focus
            return True
        else:
            print(f"Could not find game window containing '{game_name}'")
            return False

    except Exception as e:
        print(f"Error focusing game window: {e}")
        return False


def pause_game():
    """
    Focuses the game window and sends F9 key to pause the game.
    Waits a short time for the game to respond.
    """
    if not focus_game_window():
        print("Warning: Could not focus game window, attempting to pause anyway...")

    print("Pausing game (F9)...")
    pyautogui.press('f9')
    time.sleep(0.3)  # Wait for game to pause


def unpause_game():
    """
    Focuses the game window and sends F9 key to unpause the game.
    Waits a short time for the game to respond.
    """
    if not focus_game_window():
        print("Warning: Could not focus game window, attempting to unpause anyway...")

    print("Unpausing game (F9)...")
    pyautogui.press('f9')
    time.sleep(0.3)  # Wait for game to unpause


def click_tile(tile_x, tile_y, play_area_offset):
    """
    Clicks on a specific tile in the grid.

    Args:
        tile_x: Column index of the tile (0-based)
        tile_y: Row index of the tile (0-based)
        play_area_offset: (x, y) tuple of the play area's top-left corner on screen
    """
    # TODO: Calculate actual pixel position from tile coordinates
    # Will need tile size information
    pass


def right_click_tile(tile_x, tile_y, play_area_offset):
    """
    Right-clicks on a specific tile (for flagging).

    Args:
        tile_x: Column index of the tile (0-based)
        tile_y: Row index of the tile (0-based)
        play_area_offset: (x, y) tuple of the play area's top-left corner on screen
    """
    # TODO: Implement right-click for flagging
    pass


def use_skill_c():
    """Uses the C skill."""
    print("Using skill C...")
    pyautogui.press('c')
    time.sleep(0.1)


def use_skill_d():
    """Uses the D skill."""
    print("Using skill D...")
    pyautogui.press('d')
    time.sleep(0.1)


# Test function
if __name__ == "__main__":
    print("Testing game controller functions...")
    print("Make sure the game window is focused!")
    time.sleep(2)

    print("\nTesting pause/unpause...")
    pause_game()
    time.sleep(1)
    unpause_game()

    print("\n✓ Game controller test complete!")