import pygame
import random
import os
import sys
import math

# Configuration
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300
FPS = 60
FIREFLY_COUNT = 15

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Firefly:
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.timer = random.randint(0, 100)
        self.alpha = random.randint(100, 255)
        self.alpha_speed = random.choice([-2, 2])

    def update(self):
        # Movement
        self.x += self.vx
        self.y += self.vy
        
        # Gentle random direction change
        if random.random() < 0.05:
            self.vx += random.uniform(-0.1, 0.1)
            self.vy += random.uniform(-0.1, 0.1)
        
        # Clamp velocity
        self.vx = max(-1.0, min(1.0, self.vx))
        self.vy = max(-1.0, min(1.0, self.vy))

        # Bounce off edges
        if self.x < 0 or self.x > WINDOW_WIDTH: self.vx *= -1
        if self.y < 0 or self.y > WINDOW_HEIGHT: self.vy *= -1
        
        # Keep in bounds
        self.x = max(0, min(WINDOW_WIDTH, self.x))
        self.y = max(0, min(WINDOW_HEIGHT, self.y))
        
        self.rect.center = (int(self.x), int(self.y))

        # Twinkle effect
        self.alpha += self.alpha_speed
        if self.alpha >= 255:
            self.alpha = 255
            self.alpha_speed = -2
        elif self.alpha <= 50:
            self.alpha = 50
            self.alpha_speed = 2
            
        self.image.set_alpha(self.alpha)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

import ctypes
from ctypes import windll, byref, Structure, c_long, c_int, wintypes

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt

def set_window_position(hwnd, x, y, width, height):
    # SWP_NOZORDER (0x0004) | SWP_NOACTIVATE (0x0010)
    windll.user32.SetWindowPos(hwnd, 0, x, y, width, height, 0x0014)

def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT
    pygame.init()
    
    # Initial dimensions
    current_w = WINDOW_WIDTH
    current_h = WINDOW_HEIGHT
    
    # Setup window - No frame for widget look
    screen = pygame.display.set_mode((current_w, current_h), pygame.NOFRAME)
    pygame.display.set_caption("Cozy Widget")
    clock = pygame.time.Clock()
    
    # Get Window Handle
    hwnd = pygame.display.get_wm_info()['window']

    # Load Assets
    if getattr(sys, 'frozen', False):
        asset_dir = os.path.join(sys._MEIPASS, 'assets')
    else:
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets')
    
    try:
        # Load originals
        bg_orig = pygame.image.load(os.path.join(asset_dir, 'background.png')).convert()
        
        cat_images_orig = []
        # Load cleaned sprite sheet (already has alpha)
        sheet = pygame.image.load(os.path.join(asset_dir, 'cat_sprites_clean.png')).convert_alpha()
        sheet_w = sheet.get_width()
        sheet_h = sheet.get_height()
        # Assuming 3 horizontal sprites
        sprite_w = sheet_w // 3
        
        for i in range(3):
            # Create surface for each sprite (needs SRCALPHA to keep transparency)
            surf = pygame.Surface((sprite_w, sheet_h), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), (i * sprite_w, 0, sprite_w, sheet_h))
            cat_images_orig.append(surf)

        # Removed individual loads
            
        firefly_orig = pygame.image.load(os.path.join(asset_dir, 'firefly.png')).convert()
        firefly_orig.set_colorkey(firefly_orig.get_at((0,0))) 
        firefly_img = pygame.transform.scale(firefly_orig, (10, 10))
        
    except FileNotFoundError as e:
        print(f"Error loading assets: {e}")
        return

    def crop_to_content(surf):
        mask = pygame.mask.from_surface(surf)
        rects = mask.get_bounding_rects()
        if rects:
            # Union all rects to get the full bounding box
            r = rects[0].unionall(rects)
            return surf.subsurface(r).copy()
        return surf

    # Rescale assets
    def scale_assets(w, h):
        bg = pygame.transform.scale(bg_orig, (w, h))
        cats = []
        for img in cat_images_orig:
            # Crop first (remove empty space from spritesheet slice)
            cropped = crop_to_content(img)
            
            # Constant Height Scaling (maintain aspect ratio)
            target_h = 70
            aspect = cropped.get_width() / cropped.get_height()
            target_w = int(target_h * aspect)
            
            cats.append(pygame.transform.scale(cropped, (target_w, target_h)))
        return bg, cats

    bg_img, cat_images = scale_assets(current_w, current_h)

    # Cat Class
    class Cat:
        def __init__(self, images):
            self.images = images
            self.current_idx = 0
            self.image = self.images[self.current_idx]
            self.rect = self.image.get_rect()
            
            # Position
            self.x = current_w - 90
            self.y = current_h - 80
            self.rect.topleft = (int(self.x), int(self.y))
            
            # Movement / State
            self.state = "idle" # idle, walk
            self.target_x = self.x
            self.timer = 0
            # 15-35 minutes idle (at 60 FPS)
            # 15 * 60 * 60 = 54000
            # 35 * 60 * 60 = 126000
            self.duration = random.randint(54000, 126000) 
            self.speed = 1.6 # A bit faster to match bobbing

        def update_pos(self, w, h):
            # Keep relative scale or just clamp?
            # Let's just ensure it remains on screen
            self.y = h - 70
            self.x = min(self.x, w - 60)
            self.rect.topleft = (int(self.x), int(self.y))

        def update_images(self, new_images):
            self.images = new_images
            self.image = self.images[self.current_idx]

        def update(self):
            # State Management
            self.timer += 1
            
            if self.state == "idle":
                # Switch pose occasionally
                if self.timer >= self.duration:
                    self.timer = 0
                    # Keep the long duration consistent!
                    self.duration = random.randint(54000, 126000)
                    
                    # 50% chance to start walking, 50% chance to change idle pose
                    if random.random() < 0.5:
                        self.state = "walk"
                        self.target_x = random.randint(0, WINDOW_WIDTH - 60)
                        # Switch to walking pose (using idx 1 'licking' as makeshift walk cycle or just sit)
                        # Ideally we'd have a walk anim, but we'll hop/slide with pose 0
                        self.current_idx = 0 
                    else:
                        # Change idle pose
                        # 0 = sit (hate), 1 = lick (love), 2 = sleep (love)
                        # Weights: Sit EXTREMELY low (User hates it), Lick/Sleep high
                        # 1 instance of '0', 25 instances of '1' and '2'
                        pool = [0] + [1]*25 + [2]*25
                        choice = random.choice(pool)
                        self.current_idx = choice
            
            elif self.state == "walk":
                # Move towards target
                dx = self.target_x - self.x
                if abs(dx) < self.speed:
                    self.x = self.target_x
                    self.state = "idle"
                    self.timer = 0
                    self.rect.y = int(self.y) # Reset height
                else:
                    self.x += self.speed if dx > 0 else -self.speed
                    
                    # Bobbing motion (Walk cycle simulation)
                    # Bob up and down every 10 pixels or so
                    bob_offset = math.sin(pygame.time.get_ticks() * 0.015) * 3
                    self.rect.y = int(self.y + bob_offset)
                    
                    # Switch sprites for rudimentary animation if we had them, 
                    # for now sticking to the 'sit' or 'lick' pose but purely the bobbing helps "floatiness"
                    self.current_idx = 0 
            
            # Update Image and Rect x (y is handled in walk or idle)
            self.image = self.images[self.current_idx]
            self.rect.x = int(self.x)
            if self.state == "idle":
                 self.rect.y = int(self.y)
            
            # Flip if moving left
            if self.state == "walk" and self.target_x < self.x:
                 self.image = pygame.transform.flip(self.image, True, False)

        def draw(self, surface):
            surface.blit(self.image, self.rect)

    fireflies = [Firefly(firefly_img) for _ in range(FIREFLY_COUNT)]
    cat = Cat(cat_images)

    # Interactive state
    dragging = False
    resizing = False
    drag_start_pos = (0, 0) # Mouse pos relative to screen
    window_start_pos = (0, 0) # Window pos
    
    # To track window position without relying on unreliable pygame get_window_position
    # We will use WinAPI to get rect
    rect = ctypes.wintypes.RECT()
    
    running = True
    while running:
        # Event Handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # Key Handler
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Mouse Handler
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    mx, my = pygame.mouse.get_pos()
                    
                    # Check for Resize grip (bottom right 20x20)
                    if mx > current_w - 20 and my > current_h - 20:
                        resizing = True
                        drag_start_pos = queryMousePosition() # Global
                        # Store start size
                        window_start_pos = (current_w, current_h)
                    else:
                        dragging = True
                        pt = queryMousePosition() # Global screen pos
                        drag_start_pos = (pt.x, pt.y)
                        
                        # Get current window pos
                        windll.user32.GetWindowRect(hwnd, byref(rect))
                        window_start_pos = (rect.left, rect.top)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    if resizing:
                        resizing = False
                        # Finalize size if needed, but we do it live
                        pass

        # Handle Dragging/Resizing logic outside event loop for smoothness
        if dragging:
            pt = queryMousePosition()
            dx = pt.x - drag_start_pos[0]
            dy = pt.y - drag_start_pos[1]
            new_x = window_start_pos[0] + dx
            new_y = window_start_pos[1] + dy
            set_window_position(hwnd, new_x, new_y, current_w, current_h)
            
        if resizing:
            pt = queryMousePosition() 
            # This is tricky because dx/dy is global.
            dx = pt.x - drag_start_pos.x
            dy = pt.y - drag_start_pos.y
            
            new_w = max(100, window_start_pos[0] + dx)
            new_h = max(100, window_start_pos[1] + dy)
            
            if new_w != current_w or new_h != current_h:
                current_w = new_w
                current_h = new_h
                # Re-init screen
                screen = pygame.display.set_mode((current_w, current_h), pygame.NOFRAME)
                # Rescale assets
                bg_img, cat_images = scale_assets(current_w, current_h)
                cat.update_images(cat_images)
                cat.update_pos(current_w, current_h)
                
                # Update global for Firefly class
                WINDOW_WIDTH = current_w
                WINDOW_HEIGHT = current_h
                
                # Update fireflies bounds (they might go out of bounds, let's pull them in)
                for f in fireflies:
                    f.x = min(f.x, current_w)
                    f.y = min(f.y, current_h)

        # Update
        cat.update()
        
        # Change cursor near corner
        mx, my = pygame.mouse.get_pos()
        if not resizing and not dragging:
            if mx > current_w - 20 and my > current_h - 20:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Draw
        screen.blit(bg_img, (0, 0))
        cat.draw(screen)
        
        for f in fireflies:
            f.draw(screen)

        # Draw subtle resize handle
        pygame.draw.line(screen, (200, 200, 200), (current_w-10, current_h-2), (current_w-2, current_h-10), 1)
        pygame.draw.line(screen, (200, 200, 200), (current_w-6, current_h-2), (current_w-2, current_h-6), 1)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
