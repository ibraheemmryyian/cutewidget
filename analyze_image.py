from PIL import Image
import os

img_path = 'assets/cat_sprite_sheet.png'
if os.path.exists(img_path):
    img = Image.open(img_path)
    print(f"Dimensions: {img.size}")
    print(f"Mode: {img.mode}")
    # Sample corners
    print(f"Top-Left: {img.getpixel((0,0))}")
else:
    print("File not found")
