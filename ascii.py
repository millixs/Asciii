from PIL import Image, ImageOps, ImageFilter, ImageFont, ImageDraw
from pathlib import Path

ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def get_downloads_folder():
    downloads = Path.home() / "Downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads


def _load_mono_font(size, font_path=None):
    candidates = [font_path] if font_path else []
    candidates += [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "C:\\Windows\\Fonts\\consola.ttf",
        "C:\\Windows\\Fonts\\cour.ttf",
    ]
    for path in candidates:
        if not path:
            continue
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue

    print("⚠️  No monospace TTF font found - falling back to PIL's built-in "
          "font (lower quality, fixed size). Pass font_path='C:/path/to/font.ttf' "
          "to image_to_ascii()/image_to_ascii_color() for a sharper PNG.")
    return ImageFont.load_default()


def _font_metrics(font, font_size):
    try:
        bbox = font.getbbox("M")
        width = bbox[2] - bbox[0]
        ascent, descent = font.getmetrics()
        height = ascent + descent
        return max(width, 1), max(height, 1)
    except Exception:
        return max(int(font_size * 0.6), 1), max(font_size, 1)


def ascii_to_image(chars_grid, width, height, colors=None, bg_color=(0, 0, 0),
                    fg_color=(255, 255, 255), font_path=None, font_size=14,
                    out_path="ascii_image.png"):
    """
    Rasterizes a flat character grid into a real PNG image.

    chars_grid: string/list of characters, length == width*height, row-major
    colors:     optional flat list of (r, g, b) tuples, same length/order,
                for a colored render. If None, every character is drawn in
                fg_color (monochrome mode).
    """
    font = _load_mono_font(font_size, font_path)
    cell_w, cell_h = _font_metrics(font, font_size)

    canvas = Image.new("RGB", (cell_w * width, cell_h * height), bg_color)
    draw = ImageDraw.Draw(canvas)

    for row in range(height):
        offset = row * width
        y = row * cell_h
        for col in range(width):
            ch = chars_grid[offset + col]
            if ch == " ":
                continue
            color = colors[offset + col] if colors is not None else fg_color
            draw.text((col * cell_w, y), ch, font=font, fill=color)

    canvas.save(out_path)
    return out_path


def resize_image(image, new_width=300):
    width, height = image.size
    aspect_ratio = height / width
    new_height = max(1, int(aspect_ratio * new_width * 0.55))
    return image.resize((new_width, new_height), Image.LANCZOS)


def sharpen(image):
    return image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))


def prep_grayscale(image):
    gray = image.convert("L")
    gray = ImageOps.autocontrast(gray, cutoff=1)
    return gray


def pixels_to_ascii(image, invert=True):
    chars = ASCII_CHARS[::-1] if invert else ASCII_CHARS
    n = len(chars) - 1
    pixels = image.getdata()
    ascii_chars = [chars[pixel * n // 255] for pixel in pixels]
    return "".join(ascii_chars)


def image_to_ascii(image_path, output_file="ascii_image.txt", new_width=300, invert=True,
                    save_image=True, image_name="ascii_image_bw.png", downloads_dir=None,
                    font_path=None, font_size=14):
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Unable to open image {image_path}. Error: {e}")
        return

    image = resize_image(image, new_width)
    image = sharpen(image)
    gray = prep_grayscale(image)
    ascii_str = pixels_to_ascii(gray, invert=invert)
    img_width = gray.width
    img_height = gray.height
    ascii_img = "\n".join(
        ascii_str[i:i + img_width] for i in range(0, len(ascii_str), img_width)
    )

    with open(output_file, "w") as f:
        f.write(ascii_img)

    print(f"🎲 ASCII art written to {output_file}")

    if save_image:
        out_dir = Path(downloads_dir) if downloads_dir else get_downloads_folder()
        out_path = out_dir / image_name
        bg_color = (0, 0, 0) if invert else (255, 255, 255)
        fg_color = (255, 255, 255) if invert else (0, 0, 0)
        ascii_to_image(
            ascii_str, img_width, img_height,
            colors=None, bg_color=bg_color, fg_color=fg_color,
            font_path=font_path, font_size=font_size, out_path=str(out_path),
        )
        print(f"B&W ASCII image saved to {out_path}")


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def image_to_ascii_color(image_path, output_file_html="ascii_image.html", new_width=300, invert=True,
                          save_image=True, image_name="ascii_image_color.png", downloads_dir=None,
                          font_path=None, font_size=14):
    try:
        image_rgb = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Unable to open image {image_path}. Error: {e}")
        return

    image_rgb = resize_image(image_rgb, new_width)
    image_rgb = sharpen(image_rgb)
    image_l = prep_grayscale(image_rgb)

    width, height = image_rgb.size
    rgb_pixels = list(image_rgb.getdata())
    l_pixels = list(image_l.getdata())

    chars_ramp = ASCII_CHARS[::-1] if invert else ASCII_CHARS
    n = len(chars_ramp) - 1
    chars = [chars_ramp[l * n // 255] for l in l_pixels]

    lines_html = []
    for y in range(height):
        spans = []
        for x in range(width):
            idx = y * width + x
            ch = chars[idx]
            if ch == " ":
                spans.append(" ")
                continue
            r, g, b = rgb_pixels[idx]
            ch = escape_html(ch)
            spans.append(f'<span style="color:rgb({r},{g},{b})">{ch}</span>')
        lines_html.append("".join(spans))

    font_px = max(4, min(10, int(2400 / width)))

    html = (
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
        "<title>ASCII Image</title>"
        f"<style>body{{background:#000;margin:0;padding:16px;min-height:100vh;"
        f"display:grid;place-items:center}}"
        f"pre{{font:{font_px}px/{font_px}px monospace;letter-spacing:0;margin:0;"
        f"display:inline-block;white-space:pre}}</style></head><body><pre>"
        + "\n".join(lines_html)
        + "</pre></body></html>"
    )

    with open(output_file_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"🎨 Colored ASCII saved to {output_file_html} (HTML)")

    if save_image:
        out_dir = Path(downloads_dir) if downloads_dir else get_downloads_folder()
        out_path = out_dir / image_name
        ascii_to_image(
            chars, width, height,
            colors=rgb_pixels, bg_color=(0, 0, 0),
            font_path=font_path, font_size=font_size, out_path=str(out_path),
        )
        print(f"Colored ASCII image saved to {out_path}")


if __name__ == "__main__":
    image_to_ascii("input.jpg", new_width=300, invert=True)
    image_to_ascii_color("input.jpg", new_width=300, invert=True)
