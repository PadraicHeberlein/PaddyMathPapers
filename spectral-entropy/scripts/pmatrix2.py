import numpy as np
import sys

def draw_colored_matrix_in_terminal(n):
    if n <= 1:
        print("Error: Please choose an integer n > 1.")
        return

    # 1. Generate the standard modulo multiplication matrix
    p_matrix = np.zeros((n-1, n-1), dtype=int)
    for i in range(1, n):
        for j in range(1, n):
            p_matrix[i-1][j-1] = (i * j) % n

    print(f"\n--- Visualizing Modular Matrix Symmetries with {n} Colors ---\n")

    # 2. Print the canvas row by row using terminal ANSI color escapes
    for row in p_matrix:
        row_chars = []
        for val in row:
            # Map the matrix value linearly into the terminal's 256-color space.
            # We map across the standard vibrant 6x6x6 color cube (indices 16 to 231)
            # or the high-resolution 24-step grayscale ramp (indices 232 to 255).
            # Here, we utilize a clean spectrum cycle across the 216-color cube:
            color_index = 16 + int((val / n) * 215) if n > 1 else 16
            
            # \033[48;5;{color_index}m sets the BACKGROUND color of the character cells
            # Two spaces ("  ") act as a wide pixel block with that background color
            # \033[0m resets the color formatting back to default at the end of the pixel
            pixel = f"\033[48;5;{color_index}m  \033[0m"
            row_chars.append(pixel)
            
        print("".join(row_chars))
        
    print("\n-------------------------------------------------------------")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <integer_n>")
        print("Example: python script_name.py 23")
        sys.exit(1)
        
    try:
        input_n = int(sys.argv[1])
        draw_colored_matrix_in_terminal(input_n)
    except ValueError:
        print("Error: The argument provided must be a valid integer.")
        sys.exit(1)

