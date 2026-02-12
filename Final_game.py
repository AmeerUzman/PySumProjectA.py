import pygame
import random
import math

# --- CONFIGURATION & CONSTANTS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Physics Constants
ACCELERATION = 1.0
FRICTION = -0.12
GRAVITY = 0.8
JUMP_FORCE = -17
DOUBLE_JUMP_THRESHOLD = 100  # LOWERED TO 100 SO YOU CAN TEST IT SOONER!

# Colors (Dashboard Palette)
BG_COLOR = (20, 24, 35)      # Dark Navy/Grey
GRID_COLOR = (40, 50, 65)
PLAYER_COLOR = (0, 255, 150) # Neon Green
PLAYER_ACCENT = (255, 255, 255)
WHITE = (255, 255, 255)
PLATFORM_COLOR = (70, 130, 180) # Steel Blue
ENEMY_COLOR = (255, 60, 60)  # Volatility Red
GOLD_COLOR = (255, 215, 0)   # Multiplier Gold
TEXT_COLOR = (220, 220, 220)

class Particle(pygame.sprite.Sprite):
    """ Little squares that explode when things happen """
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = random.uniform(-4, 4)
        self.vel_y = random.uniform(-4, 4)
        self.life = 30 # Frames to live

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life -= 1
        if self.life <= 0:
            self.kill()
        self.image.set_alpha(int((self.life / 30) * 255))

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((40, 40))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        
        # Physics vectors
        self.pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        # State
        self.jump_count = 0  # <--- NEW: Tracks jumps (0, 1, or 2)
        self.multiplier_timer = 0
        self.lives = 3
        self.score = 0

    def reset(self):
        """Reset player state for game restart"""
        self.pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.jump_count = 0  # Reset jumps
        self.multiplier_timer = 0
        self.lives = 3
        self.score = 0

    def update(self):
        # 1. Physics Calculation
        self.acc = pygame.math.Vector2(0, GRAVITY)
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.acc.x = -ACCELERATION
        if keys[pygame.K_RIGHT]:
            self.acc.x = ACCELERATION

        # Apply Friction
        self.acc.x += self.vel.x * FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Wrap around screen
        if self.pos.x > SCREEN_WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = SCREEN_WIDTH

        # Update Rect
        self.rect.midbottom = self.pos

        # Multiplier Timer (5 seconds = 300 frames) 
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer % 10 < 5:
                self.image.fill(GOLD_COLOR)
            else:
                self.image.fill(PLAYER_COLOR)
        else:
            self.image.fill(PLAYER_COLOR)

    def jump(self):
        # Check collision with ground just to see if we are grounded
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        
        # Logic: If on ground, reset count. 
        if hits:
            self.jump_count = 0

        # JUMP 1: Normal Jump
        if self.jump_count == 0:
            self.vel.y = JUMP_FORCE
            self.jump_count = 1
            
        # JUMP 2: Double Jump (Only if unlocked)
        elif self.jump_count == 1 and self.score >= DOUBLE_JUMP_THRESHOLD:
            self.vel.y = JUMP_FORCE
            self.jump_count = 2 # Mark as used
            
            # Create particle effect for double jump (White explosion)
            for _ in range(15):
                self.game.particles.add(Particle(self.rect.centerx, self.rect.bottom, WHITE))

    def bounce(self):
        """ Used when stomping enemies """
        self.vel.y = -20 # Small hop
        self.multiplier_timer = 300 # 5 Seconds
        
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.Surface((width, 18))
        self.image.fill(PLATFORM_COLOR)
        # Add a "tech" line on top
        pygame.draw.rect(self.image, (150, 200, 255), (0,0,width, 4))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.passed = False

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Draw a "Spiky" Enemy (Market Volatility)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, ENEMY_COLOR, [(20,0), (40,20), (20,40), (0,20)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - 40)
        self.rect.y = -50
        self.speed_y = random.randint(3, 7)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("KPI Dashboard: Market Action Platformer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.running = True
        self.game_state = "PLAYING"  # "PLAYING" or "GAMEOVER"
        
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        self.shake_timer = 0
        self.spawn_timer = 0
        self.start_game()

    def start_game(self):
        # Clear existing sprites first (for restart)
        self.platforms.empty()
        self.enemies.empty()
        self.particles.empty()
        self.all_sprites.empty()
        
        # Re-add player
        self.all_sprites.add(self.player)
        
        # Initial Platforms
        p = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH)
        self.platforms.add(p)
        self.all_sprites.add(p)
        for i in range(1, 8):
            p = Platform(random.randrange(0, SCREEN_WIDTH - 100), SCREEN_HEIGHT - (i * 100), 120)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def reset_game(self):
        """Fully reset game state for restart"""
        self.player.reset()
        self.start_game()
        self.spawn_timer = 0
        self.shake_timer = 0
        self.game_state = "PLAYING"

    def draw_grid(self):
        # Draw faint grid lines to look like a chart
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

    def screen_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            return offset_x, offset_y
        return 0, 0

    def run(self):
        while self.running:
            self.events()
            if self.game_state == "PLAYING":
                self.update()
            self.draw()
            self.clock.tick(FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_state == "PLAYING" and event.key == pygame.K_SPACE:
                    self.player.jump()
                if self.game_state == "GAMEOVER" and event.key == pygame.K_r:
                    self.reset_game()

    def update(self):
        self.all_sprites.update()
        self.particles.update()

        # 1. Camera Scroll (Infinite Climb)
        if self.player.rect.top <= SCREEN_HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)
            for p in self.platforms:
                p.rect.y += abs(self.player.vel.y)
                if p.rect.top >= SCREEN_HEIGHT:
                    p.kill()
            for e in self.enemies:
                e.rect.y += abs(self.player.vel.y)
            
            # Spawn new platforms
            while len(self.platforms) < 8:
                width = random.randint(80, 150)
                p = Platform(random.randint(0, SCREEN_WIDTH - width), -30, width)
                self.platforms.add(p)
                self.all_sprites.add(p)

        # 2. Platform Collisions (Landing)
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                for platform in hits:
                    if (self.player.rect.bottom >= platform.rect.top and 
                        self.player.rect.bottom <= platform.rect.top + 15 and
                        self.player.vel.y > 0):
                        
                        self.player.pos.y = platform.rect.top
                        self.player.vel.y = 0
                        self.player.jump_count = 0  # <--- RESET JUMP COUNT ON LANDING
                        
                        if not platform.passed:
                            mult = 2 if self.player.multiplier_timer > 0 else 1
                            self.player.score += (10 * mult)
                            platform.passed = True
                        break 

        # 3. Enemy "Stomp" Logic
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            # Check if hitting from TOP (Stomp)
            if self.player.vel.y > 0 and self.player.rect.bottom < enemy.rect.centery + 10:
                enemy.kill()
                self.player.bounce()
                for _ in range(15):
                    self.particles.add(Particle(enemy.rect.centerx, enemy.rect.centery, ENEMY_COLOR))
            else:
                self.player.lives -= 1
                self.shake_timer = 10
                self.player.pos = pygame.math.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                self.player.vel = pygame.math.Vector2(0, 0)
                self.enemies.empty() 

        # 4. Spawning Enemies
        self.spawn_timer += 1
        if self.spawn_timer >= 110:
            e = Enemy()
            self.enemies.add(e)
            self.all_sprites.add(e)
            self.spawn_timer = 0

        # 5. Fall off screen
        if self.player.rect.top > SCREEN_HEIGHT:
            self.player.lives -= 1
            self.shake_timer = 10
            self.player.pos = pygame.math.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            self.player.vel = pygame.math.Vector2(0, 0)
            p = Platform(self.player.rect.x - 50, self.player.rect.y + 60, 200)
            self.platforms.add(p)
            self.all_sprites.add(p)

        # 6. Check Game Over
        if self.player.lives <= 0:
            self.game_state = "GAMEOVER"

    def draw(self):
        ox, oy = self.screen_shake()
        self.screen.fill(BG_COLOR)
        self.draw_grid()

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x + ox, sprite.rect.y + oy))
        for p in self.particles:
            self.screen.blit(p.image, (p.rect.x + ox, p.rect.y + oy))

        # UI
        pygame.draw.rect(self.screen, (30, 30, 40), (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(self.screen, WHITE, (0, 60), (SCREEN_WIDTH, 60), 2)

        score_surf = self.font.render(f"REVENUE (SCORE): ${self.player.score}k", True, PLAYER_ACCENT)
        self.screen.blit(score_surf, (20, 20))

        lives_color = PLAYER_ACCENT if self.player.lives > 1 else ENEMY_COLOR
        lives_surf = self.font.render(f"CAPITAL (LIVES): {self.player.lives}", True, lives_color)
        self.screen.blit(lives_surf, (300, 20))

        # Show if Double Jump is unlocked
        if self.player.score >= DOUBLE_JUMP_THRESHOLD:
            dj_status = "UNLOCKED"
            dj_color = GOLD_COLOR
        else:
            dj_status = f"LOCKED (<{DOUBLE_JUMP_THRESHOLD})"
            dj_color = (100, 100, 100)
            
        dj_surf = self.font.render(f"DOUBLE JUMP: {dj_status}", True, dj_color)
        self.screen.blit(dj_surf, (550, 40)) # Positioned below multiplier

        if self.player.multiplier_timer > 0:
            mult_surf = self.font.render("MARKET BOOM: 2X ACTIVE!", True, GOLD_COLOR)
            self.screen.blit(mult_surf, (550, 10))

        if self.game_state == "GAMEOVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            go_surf = self.font.render("INSOLVENT! GAME OVER", True, ENEMY_COLOR)
            restart_surf = self.font.render("PRESS 'R' TO RESTART", True, WHITE)
            self.screen.blit(go_surf, (SCREEN_WIDTH//2 - go_surf.get_width()//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(restart_surf, (SCREEN_WIDTH//2 - restart_surf.get_width()//2, SCREEN_HEIGHT//2 + 10))

        pygame.display.flip()

# Run the game
if __name__ == "__main__":
    g = Game()
    g.run()
    pygame.quit()