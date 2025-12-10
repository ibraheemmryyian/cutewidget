import pygame
import os

pygame.init()
screen = pygame.display.set_mode((100, 100)) # Init display for convert support

img_path = 'assets/cat_sprite_sheet.png'
save_path = 'assets/cat_sprites_clean.png'

if os.path.exists(img_path):
    img = pygame.image.load(img_path).convert()
    w, h = img.get_size()
    print(f"Original Size: {w}x{h}")
    
    # Create new surface with alpha
    clean_img = pygame.Surface((w, h), pygame.SRCALPHA)
    clean_img.fill((0,0,0,0))
    
    # Iterate and copy (slow but fine for one-time offline processing)
    # Actually, let's just use Pygame's efficient array manipulation if possible, 
    # OR since it's small, per-pixel is instant.
    
    # Target color: Magenta
    target = (255, 0, 255)
    threshold = 50 # Tolerance
    
    for y in range(h):
        for x in range(w):
            color = img.get_at((x, y))
            # Distance from magenta
            dist = max(abs(color.r - target[0]), abs(color.g - target[1]), abs(color.b - target[2]))
            
            if dist > threshold:
                # Keep pixel
                clean_img.set_at((x, y), color)
            # Else transparent
            
    pygame.image.save(clean_img, save_path)
    print(f"Saved cleaned image to {save_path}")
    
    # Suggest sprite dimensions
    print(f"Suggested sprite width: {w//3}")
    print(f"Suggested sprite height: {h}")
    
else:
    print("File not found")
