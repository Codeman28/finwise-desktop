"""
tools_make_icon.py - Draws the app icon (assets/icon.ico) with Pillow.

Run once before building (from the project folder):   python toolsmake_icon.py
It draws a deep-green circle with a white "F" and a small coral coin,
using the same palette as the app.
"""

from PIL import Image, ImageDraw, ImageFont

GREEN = (0, 91, 76, 255)
CORAL = (253, 123, 100, 255)
WHITE = (255, 255, 255, 255)

SIZE = 512
image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Big green circle
draw.ellipse((16, 16, SIZE - 16, SIZE - 16), fill=GREEN)

# White letter "F" - try a bold Windows font, fall back to Pillow's default
try:
    font = ImageFont.truetype("segoeuib.ttf", 320)
except OSError:
    font = ImageFont.load_default(size=320)
draw.text((SIZE / 2 - 20, SIZE / 2 + 6), "F", font=font, fill=WHITE, anchor="mm")

# Small coral "coin" in the top-right
draw.ellipse((330, 90, 430, 190), fill=CORAL, outline=WHITE, width=10)

image.save("assets/icon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
image.save("assets/icon.png")
print("Icon written to assets/icon.ico")
