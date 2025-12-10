import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Peaceful Garden Cat")

# Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
YELLOW = (255, 255, 0)

# Cat class
class Cat:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 40
        self.speed = 2
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False
        self.direction = 1  # 1 for right, -1 for left
        
    def update(self):
        # Move towards target if not at target
        if self.moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 5:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            else:
                self.moving = False
                
        # Change direction occasionally
        if random.random() < 0.01:
            self.direction *= -1
    
    def draw(self, surface):
        # Draw cat body
        pygame.draw.circle(surface, LIGHT_BROWN, (self.x, self.y), self.size//2)
        
        # Draw cat ears
        ear_offset = self.size // 3
        pygame.draw.polygon(surface, LIGHT_BROWN, [
            (self.x - ear_offset, self.y - self.size//2),
            (self.x - ear_offset//2, self.y - self.size),
            (self.x, self.y - self.size//2)
        ])
        pygame.draw.polygon(surface, LIGHT_BROWN, [
            (self.x + ear_offset, self.y - self.size//2),
            (self.x + ear_offset//2, self.y - self.size),
            (self.x, self.y - self.size//2)
        ])
        
        # Draw cat eyes
        eye_size = self.size // 6
        pygame.draw.circle(surface, BLACK, (self.x - eye_size, self.y), eye_size)
        pygame.draw.circle(surface, BLACK, (self.x + eye_size, self.y), eye_size)
        
        # Draw cat nose
        pygame.draw.circle(surface, PINK, (self.x, self.y + eye_size//2), eye_size//2)
        
        # Draw cat mouth
        pygame.draw.arc(surface, BLACK, 
                       (self.x - eye_size, self.y, eye_size*2, eye_size*2),
                       0, math.pi, 2)
        
        # Draw tail
        tail_length = self.size // 2
        tail_x = self.x - self.direction * tail_length if self.direction == -1 else self.x + self.direction * tail_length
        pygame.draw.line(surface, LIGHT_BROWN, (self.x, self.y), (tail_x, self.y + tail_length//2), 5)
    
    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y
        self.moving = True

# Tree class
class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.trunk_width = 20
        self.trunk_height = 60
        self.crown_radius = 40
        
    def draw(self, surface):
        # Draw trunk
        pygame.draw.rect(surface, BROWN, (self.x - self.trunk_width//2, self.y, self.trunk_width, self.trunk_height))
        
        # Draw crown
        pygame.draw.circle(surface, GRASS_GREEN, (self.x, self.y - self.crown_radius//2), self.crown_radius)

# Create game objects
cat = Cat()
trees = []
for i in range(8):
    trees.append(Tree(
        random.randint(50, WIDTH-50),
        random.randint(100, HEIGHT-100)
    ))

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Only move cat when clicking on the window (not on the cat itself)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if click is not on the cat
            distance_to_cat = math.sqrt((mouse_x - cat.x)**2 + (mouse_y - cat.y)**2)
            if distance_to_cat > cat.size:
                cat.set_target(mouse_x, mouse_y)
    
    # Update game objects
    cat.update()
    
    # Draw everything
    screen.fill(SKY_BLUE)
    
    # Draw grass
    pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT//2, WIDTH, HEIGHT//2))
    
    # Draw trees
    for tree in trees:
        tree.draw(screen)
    
    # Draw cat
    cat.draw(screen)
    
    # Draw title
    font = pygame.font.SysFont(None, 36)
    text = font.render("Peaceful Garden", True, BLACK)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
