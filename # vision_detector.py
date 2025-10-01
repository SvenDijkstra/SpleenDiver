# vision_detector.py

import numpy as np
import cv2
import mss
import time
from config_manager import load_config
from game_controller import pause_game, unpause_game, focus_game_window


def capture_game_window():
    """
    Captures a screenshot of the entire game window area.
    Returns: numpy array (BGR format) or None if capture fails
    """
    config = load_config()
    coords = config.get('play_region_coords', [0, 0, 800, 600])

    # coords format: [x, y, width, height]
    monitor = {
        "left": coords[0],
        "top": coords[1],
        "width": coords[2],
        "height": coords[3]
    }

    try:
        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    except Exception as e:
        print(f"Error capturing game window: {e}")
        return None


def find_play_area(img, debug=False):
    """
    Finds the actual play area (grid) within the game window.
    The play area is the black rectangle with rounded corners inside the grey border.

    Args:
        img: The captured game window image
        debug: If True, saves debug images showing detection steps

    Returns:
        (x, y, width, height) of the play area, or None if not found
    """
    if img is None:
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if debug:
        cv2.imwrite("debug_1_original.png", img)
        cv2.imwrite("debug_2_grayscale.png", gray)

    # The play area is very dark (black), while the border is grey
    # Let's threshold to find the dark play area
    # Values below 10 are the black play area
    _, binary = cv2.threshold(gray, 7, 255, cv2.THRESH_BINARY_INV)

    if debug:
        cv2.imwrite("debug_3_threshold.png", binary)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("No contours found!")
        return None

    # Find the largest contour (should be the play area)
    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)

    print(f"Largest contour area: {area} pixels")

    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(largest_contour)

    print(f"Play area found at: x={x}, y={y}, width={w}, height={h}")

    if debug:
        # Draw the detected play area on the original image
        debug_img = img.copy()
        cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.imwrite("debug_4_detected_area.png", debug_img)

        # Also save just the extracted play area
        play_area_img = img[y:y + h, x:x + w]
        cv2.imwrite("debug_5_play_area_only.png", play_area_img)

    return (x, y, w, h)


def is_game_paused(img, play_area=None, debug=False):
    """
    Detects if the game is paused by looking for the "Paused" text
    and a predominantly black screen.

    Args:
        img: The captured game window image
        play_area: Optional (x, y, w, h) tuple of the play area
        debug: If True, saves debug images

    Returns:
        bool: True if game is paused, False otherwise
    """
    if img is None:
        return False

    # If we have the play area, focus on that region
    if play_area:
        x, y, w, h = play_area
        # Ensure coordinates are within bounds
        h_img, w_img, _ = img.shape
        x = max(0, x)
        y = max(0, y)
        w = min(w_img - x, w)
        h = min(h_img - y, h)
        if w <= 0 or h <= 0:
            return False
        region = img[y:y + h, x:x + w]
    else:
        region = img

    # Convert to grayscale
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    total_pixels = gray.size

    if total_pixels == 0:
        return False

    # --- 1. Check for a Predominantly Black Background ---
    # Black is a value close to 0 in grayscale. Use a low threshold (e.g., 20)
    # The image is pitch black, so we expect a high percentage of pixels to be near 0.
    _, black_mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY_INV)
    black_pixel_count = np.sum(black_mask == 255)
    black_percentage = (black_pixel_count / total_pixels) * 100

    # If the screen is less than 90% black, it's probably not the pause screen.
    is_black_screen = black_percentage > 90.0

    # --- 2. Detect White Text ("Paused") ---
    # Threshold to find white text (high values, 200 is good based on your image)
    _, white_text_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    white_pixel_count = np.sum(white_text_mask == 255)
    white_percentage = (white_pixel_count / total_pixels) * 100

    if debug:
        print(f"Black pixel percentage (<= 20): {black_percentage:.2f}% (Required > 90.0%)")
        print(f"White pixel count (>= 200): {white_pixel_count}")
        print(f"White pixel percentage: {white_percentage:.2f}% (Required > 0.1%)")
        cv2.imwrite("debug_6_pause_white_mask.png", white_text_mask)

    # --- 3. Combined Logic for Pause Detection ---
    # The game is paused if:
    # A) The screen is mostly black (e.g., > 90% black).
    # AND
    # B) A minimum number of white pixels (e.g., > 1000) are present (to account for the 'Paused' text)
    #    AND the white text is a small but meaningful percentage (e.g., > 0.1%)

    is_paused = (
            is_black_screen and
            white_pixel_count > 1000 and  # Ensures actual text is present (adjust based on image size)
            white_percentage > 0.1  # Low percentage for large screens
    )

    return is_paused


def detect_grid_with_auto_pause(img, max_attempts=3):
    """
    Attempts to detect the grid size, automatically pausing the game if needed.

    Args:
        img: The initial captured game window image
        max_attempts: Maximum number of attempts to detect the grid

    Returns:
        tuple: (grid_info dict, play_area tuple, was_paused_initially bool)
               Returns (None, None, False) if detection fails
    """
    # First attempt - check current state
    play_area = find_play_area(img, debug=False)

    if play_area:
        x, y, w, h = play_area
        grid_info = detect_grid_size((w, h))

        if grid_info:
            # Successfully detected without intervention
            was_paused = is_game_paused(img, play_area, debug=False)
            return grid_info, play_area, was_paused

    # Grid not detected - game is probably not paused
    print("Grid not detected in current state. Attempting to pause game...")

    # Check if already paused
    was_initially_paused = False
    if play_area:
        was_initially_paused = is_game_paused(img, play_area, debug=False)

    if was_initially_paused:
        print("Game is already paused but grid not detected. Checking again...")
        return None, None, was_initially_paused

    # Try pausing and detecting
    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1}/{max_attempts}...")

        # Pause the game
        pause_game()

        # Capture new screenshot
        img = capture_game_window()
        if img is None:
            continue

        # Try to find play area
        play_area = find_play_area(img, debug=False)
        if not play_area:
            continue

        # Check if actually paused
        x, y, w, h = play_area
        if not is_game_paused(img, play_area, debug=False):
            print("Game did not pause properly, retrying...")
            continue

        # Try to detect grid
        grid_info = detect_grid_size((w, h))

        if grid_info:
            print("✓ Grid detected successfully after pausing!")
            return grid_info, play_area, False  # Was not initially paused

    print("✗ Failed to detect grid after multiple attempts")
    return None, None, False


def detect_grid_size(play_area_dimensions):
    """
    Determines the grid size based on the play area dimensions.
    The game has 5 stages with different grid sizes:
    - Stage 1: 9x9 (10 bombs)
    - Stage 2: 12x11 (19 bombs)
    - Stage 3: 15x13 (32 bombs)
    - Stage 4: 18x14 (47 bombs)
    - Stage 5: 20x16 (66 bombs)

    Each tile is approximately 48x48 pixels.

    Args:
        play_area_dimensions: (width, height) tuple of the play area in pixels

    Returns:
        dict with 'cols', 'rows', 'stage', 'bombs' or None if unknown
    """
    if not play_area_dimensions:
        return None

    width, height = play_area_dimensions

    print(f"Play area dimensions: {width}x{height} pixels")

    # Known grid configurations (cols, rows, stage, bombs)
    KNOWN_GRIDS = [
        {'cols': 9, 'rows': 9, 'stage': 1, 'bombs': 10},
        {'cols': 12, 'rows': 11, 'stage': 2, 'bombs': 19},
        {'cols': 15, 'rows': 13, 'stage': 3, 'bombs': 32},
        {'cols': 18, 'rows': 14, 'stage': 4, 'bombs': 47},
        {'cols': 20, 'rows': 16, 'stage': 5, 'bombs': 66},
    ]

    # Approximate tile size
    TILE_SIZE = 48

    # Calculate how many tiles fit in the play area
    estimated_cols = round(width / TILE_SIZE)
    estimated_rows = round(height / TILE_SIZE)

    print(f"Estimated grid from dimensions: {estimated_cols}x{estimated_rows}")

    # Find the closest matching grid
    best_match = None
    min_difference = float('inf')

    for grid in KNOWN_GRIDS:
        # Calculate difference from estimated size
        col_diff = abs(grid['cols'] - estimated_cols)
        row_diff = abs(grid['rows'] - estimated_rows)
        total_diff = col_diff + row_diff

        if total_diff < min_difference:
            min_difference = total_diff
            best_match = grid

    if best_match and min_difference <= 2:  # Allow small variance
        print(
            f"✓ Matched to Stage {best_match['stage']}: {best_match['cols']}x{best_match['rows']} grid ({best_match['bombs']} bombs)")
        return best_match
    else:
        print(f"✗ Could not confidently match grid size (difference: {min_difference})")
        return None


# Test and analysis
if __name__ == "__main__":
    print("=== Focusing game window ===")
    if not focus_game_window():
        print("⚠ Warning: Could not focus game window")
        print("The script will continue, but key presses may not work\n")
    else:
        print("✓ Game window focused\n")

    print("=== Capturing game window ===")
    img = capture_game_window()

    if img is None:
        print("✗ Capture failed!")
        exit(1)

    print(f"✓ Capture successful! Image shape: {img.shape}\n")

    print("=== Auto-detecting grid with pause if needed ===")
    grid_info, play_area, was_paused = detect_grid_with_auto_pause(img)

    if grid_info and play_area:
        x, y, w, h = play_area
        print(f"\n✓ Detection successful!")
        print(f"  Stage: {grid_info['stage']}")
        print(f"  Grid: {grid_info['cols']}x{grid_info['rows']}")
        print(f"  Bombs: {grid_info['bombs']}")
        print(f"  Play area: x={x}, y={y}, w={w}, h={h}")
        print(f"  Was initially paused: {was_paused}")

        # If we paused the game, ask if user wants to unpause
        if not was_paused:
            user_input = input("\nGame was paused for detection. Unpause now? (y/n): ")
            if user_input.lower() == 'y':
                unpause_game()
                print("Game unpaused!")
    else:
        print("\n✗ Grid detection failed!")

    print("\n" + "=" * 50)
    print("Grid detection with auto-pause complete!")