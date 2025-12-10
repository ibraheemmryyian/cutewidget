import pygame
import random
import os
import sys

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
        for name in ['cat_idle_1.png', 'cat_idle_2.png', 'cat_sleep.png']:
            img = pygame.image.load(os.path.join(asset_dir, name)).convert()
            img.set_colorkey((0, 255, 0))
            cat_images_orig.append(img)
            
        firefly_orig = pygame.image.load(os.path.join(asset_dir, 'firefly.png')).convert()
        firefly_orig.set_colorkey(firefly_orig.get_at((0,0))) 
        firefly_img = pygame.transform.scale(firefly_orig, (10, 10))
        
    except FileNotFoundError as e:
        print(f"Error loading assets: {e}")
        return

    # Helper to rescale assets
    def scale_assets(w, h):
        bg = pygame.transform.scale(bg_orig, (w, h))
        cats = [pygame.transform.scale(img, (60, 60)) for img in cat_images_orig]
        return bg, cats

    bg_img, cat_images = scale_assets(current_w, current_h)

    # Cat Class
    class Cat:
        def __init__(self, images):
            self.images = images
            self.current_idx = 0
            self.image = self.images[self.current_idx]
            self.rect = self.image.get_rect()
            self.update_pos(current_w, current_h)
            
            self.state = "idle"
            self.timer = 0
            self.duration = random.randint(60, 180)

        def update_pos(self, w, h):
            self.rect.bottomright = (w - 20, h - 20)
            
        def update_images(self, new_images):
            self.images = new_images
            self.image = self.images[self.current_idx]

        def update(self):
            self.timer += 1
            if self.timer >= self.duration:
                self.timer = 0
                self.duration = random.randint(120, 300)
                choice = random.choice([0, 0, 1, 2, 2])
                self.current_idx = choice
                self.image = self.images[self.current_idx]

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
