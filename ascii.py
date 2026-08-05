# Import the Python Imaging Library to handle image operations
from PIL import Image

# Define ASCII characters arranged from darkest to lightest
# These characters will represent different brightness levels in the final ASCII art
ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=100):
    # Get the current width and height dimensions of the image
    width, height = image.size
    
    # Calculate the aspect ratio (height divided by width) to maintain image proportions
    aspect_ratio = height / width
    
    # Calculate new height based on the aspect ratio and new width
    # The 0.55 factor compensates for terminal font character aspect ratio
    # (characters are taller than they are wide), so we reduce the computed height
    new_height = int(aspect_ratio * new_width * 0.55)
    
    # Resize the image to the new dimensions and return the resized image
    return image.resize((new_width, new_height))

def grayify(image):
    # Convert the image to grayscale using PIL's "L" mode (8-bit luminance)
    # "L" mode stores brightness values from 0 (black) to 255 (white), with many gray levels
    return image.convert("L")

def pixels_to_ascii(image):
    # Extract all pixel brightness values from the grayscale image
    pixels = image.getdata()
    
    # Convert each pixel brightness to an ASCII character
    # Formula: pixel_value * (total_chars - 1) // 255 maps 0-255 brightness to character index
    ascii_chars = [ASCII_CHARS[pixel * (len(ASCII_CHARS) - 1) // 255] for pixel in pixels]
    
    # Join all ASCII characters into one continuous string
    return "".join(ascii_chars)

def image_to_ascii(image_path, output_file="ascii_image.txt", new_width=100):
    # Start a try block to handle potential file opening errors
    try:
        # Attempt to open the image file at the specified path
        image = Image.open(image_path)
    # If opening fails, catch the exception
    except Exception as e:
        # Print an error message with the file path and error details
        print(f"Unable to open image {image_path}. Error: {e}")
        # Exit the function early if image cannot be opened
        return

    # Resize the opened image to the specified width while maintaining aspect ratio
    image = resize_image(image, new_width)
    
    # Convert the resized image to grayscale
    image = grayify(image)

    # Convert all pixels in the grayscale image to ASCII characters
    ascii_str = pixels_to_ascii(image)
    
    # Store the width of the processed image for line breaking
    img_width = image.width

    # Split the long ASCII string into lines that match the image width
    # This creates proper line breaks to maintain the image's rectangular shape
    ascii_img = "\n".join([ascii_str[i:i+img_width] for i in range(0, len(ascii_str), img_width)])

    # Open the output file in write mode
    with open(output_file, "w") as f:
        # Write the formatted ASCII art to the file
        f.write(ascii_img)

    # Print a success message with checkmark emoji
    print(f"🎲 ASCII art written to {output_file}")

def escape_html(text: str) -> str:
    # Replace ampersand characters with HTML entity (must be done first)
    # This prevents conflicts with other HTML entities
    return (
        text.replace("&", "&amp;")
        # Replace less-than symbol with HTML entity
        .replace("<", "&lt;")
        # Replace greater-than symbol with HTML entity
        .replace(">", "&gt;")
        # Replace double quotes with HTML entity
        .replace('"', "&quot;")
        # Replace single quotes with HTML entity
        .replace("'", "&#39;")
    )

def image_to_ascii_color(image_path, output_file_html="ascii_image.html", new_width=100):
    # Start a try block to handle potential file opening errors
    try:
        # Open the image and convert to RGB color mode (red, green, blue values)
        image_rgb = Image.open(image_path).convert("RGB")
    # If opening fails, catch the exception
    except Exception as e:
        # Print an error message with the file path and error details
        print(f"Unable to open image {image_path}. Error: {e}")
        # Exit the function early if image cannot be opened
        return

    # Resize the RGB image to the specified width while maintaining aspect ratio
    image_rgb = resize_image(image_rgb, new_width)
    
    # Create a grayscale version of the resized image for brightness mapping
    image_l = grayify(image_rgb)

    # Get the dimensions of the processed image
    width, height = image_rgb.size
    
    # Extract RGB color values from each pixel as a list of tuples
    rgb_pixels = list(image_rgb.getdata())
    
    # Extract brightness values from the grayscale version as a list
    l_pixels = list(image_l.getdata())

    # Map each brightness value to its corresponding ASCII character
    # Uses the same formula as the grayscale version
    chars = [ASCII_CHARS[l * (len(ASCII_CHARS) - 1) // 255] for l in l_pixels]

    # Initialize an empty list to store HTML lines
    lines_html = []
    
    # Process each row of the image
    for y in range(height):
        # Initialize an empty list to store HTML spans for this row
        spans = []
        
        # Process each column in the current row
        for x in range(width):
            # Calculate the index of the current pixel in the flat pixel array
            idx = y * width + x
            
            # Extract the red, green, and blue values for this pixel
            r, g, b = rgb_pixels[idx]
            
            # Get the ASCII character for this pixel and escape HTML special characters
            ch = escape_html(chars[idx])
            
            # Create an HTML span element with inline CSS for the pixel's color
            spans.append(f"<span style=\"color: rgb({r}, {g}, {b});\">{ch}</span>")
        
        # Join all spans for this row and add to the lines list
        lines_html.append("".join(spans))

    # Create the complete HTML document structure
    html = (
        # HTML5 document declaration
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
        # Set the page title
        "<title>ASCII Image</title>"
        # Add CSS styles: black background, no margins, monospace font
        "<style>body{background:#000;margin:0;padding:16px;min-height:100vh;display:grid;place-items:center}pre{font:10px/10px monospace;letter-spacing:0;margin:0;display:inline-block}</style></head><body><pre>"
        # Insert all the colored ASCII lines
        + "\n".join(lines_html)
        # Close the HTML structure
        + "</pre></body></html>"
    )

    # Open the output HTML file in write mode with UTF-8 encoding
    with open(output_file_html, "w", encoding="utf-8") as f:
        # Write the complete HTML content to the file
        f.write(html)

    # Print a success message with artist palette emoji
    print(f"🎨 Colored ASCII saved to {output_file_html} (HTML)")

# Check if this script is being run directly (not imported as a module)
if __name__ == "__main__":
    # Create a grayscale ASCII art text file from "input.jpg" with width of 120 characters
    image_to_ascii("input.jpg", new_width=120)
    
    # Create a colorized ASCII art HTML file from the same image with width of 120 characters
    image_to_ascii_color("input.jpg", new_width=120)