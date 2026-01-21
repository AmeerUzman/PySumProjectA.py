"""
DOCUMENTATION: MODIFICATIONS MADE
1. Movement Logic: Added coordinate updates (+=, -=) tied to arrow key presses 
   to allow the player square to move around the screen.
2. Collision Detection: Implemented 'colliderect' to check if the player's 
   rectangle overlaps with any star rectangle.
3. List Management: Used 'stars[:]' (a slice copy) to safely remove stars from 
   the list during iteration when a collision occurs.
4. Score Tracking: Added a score counter that increments by 1 for every 
   star collected.
5. UI: Added font rendering to display the real-time score on the screen.
"""

import pygame, sys

# Initialization
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IndieQuest Collector")
clock = pygame.time.Clock()

# Player and Game Variables
player_x, player_y = 100, 100
player_speed = 5
stars = [
    pygame.Rect(300, 200, 20, 20),
    pygame.Rect(500, 400, 20, 20),
    pygame.Rect(200, 350, 20, 20),
]
score = 0
font = pygame.font.SysFont(None, 32)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Movement Logic
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # 2. Collision Detection Logic
    player_rect = pygame.Rect(player_x, player_y, 50, 50)
    for star in stars[:]:
        if player_rect.colliderect(star):
            stars.remove(star)
            score += 1

    # 3. Drawing
    screen.fill((255, 255, 255)) # White background
    
    # Draw Stars (Blue)
    for star in stars:
        pygame.draw.rect(screen, (0, 0, 255), star)
        
    # Draw Player (Black)
    pygame.draw.rect(screen, (0, 0, 0), (player_x, player_y, 50, 50))
    
    # Draw Score Text
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()