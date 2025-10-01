# game_controller.py

import time
import pyautogui
from config_manager import load_config


def pause_game():
    """
    Sends F9 key to pause the game.
    Waits a short time for the game to respond.
    """
    print("Pausing game (F9)...")
    pyautogui.press('f9')
    time.sleep(0.3)  # Wait for game to pause


def unpause_game():
    """
    Sends F9 key to unpause the game.
    Waits a short time for the game to respond.
    """
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