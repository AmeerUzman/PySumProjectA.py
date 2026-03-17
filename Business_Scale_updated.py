# Importing necessary Libraries
import pygame
import random
import math
import time  # Added for time.perf_counter()

# CONSTANTS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Physics CONSTANTS
ACCELERATION = 1.0
FRICTION = -0.12
GRAVITY = 0.8
JUMP_FORCE = -17
DOUBLE_JUMP_THRESHOLD = 100 

# Colors
BG_COLOR = (20, 24, 35) 
GRID_COLOR = (40, 50, 65) 
PLAYER_COLOR = (0, 255, 150) 
PLAYER_ACCENT = (255, 255, 255) 
WHITE = (255, 255, 255) 
PLATFORM_COLOR = (70, 130, 180) 
ENEMY_COLOR = (255, 60, 60) 
GOLD_COLOR = (255, 215, 0) 
TEXT_COLOR = (220, 220, 220) 

# --- SFX/Music (Placeholders for logic) ---
pygame.mixer.init()
# Note: Ensure these files exist or wrap in try/except to prevent crashes
try:
    jump_sound = pygame.mixer.Sound("Music/Jump_M.wav")
    lose_life_sound = pygame.mixer.Sound("Music/LoseLife_M.wav")
    lose_sound = pygame.mixer.Sound("Music/Lose_M.wav")
    platform_sound = pygame.mixer.Sound("Music/Platform_M.wav")
    powerup_sound = pygame.mixer.Sound("Music/Powerup_M.wav")
    pygame.mixer.music.load("Music/BG_M.wav")
    pygame.mixer.music.play(-1)
except:
    print("Sound files not found, running in silent mode.")

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = random.uniform(-4, 4)
        self.vel_y = random.uniform(-4, 4)
        self.life = 30 

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
        self.pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.jump_count = 0 
        self.multiplier_timer = 0
        self.lives = 3
        self.score = 0

    def reset(self):
        self.pos = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.jump_count = 0 
        self.multiplier_timer = 0
        self.lives = 3
        self.score = 0

    def update(self):
        self.acc = pygame.math.Vector2(0, GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.acc.x = -ACCELERATION
        if keys[pygame.K_RIGHT]: self.acc.x = ACCELERATION

        self.acc.x += self.vel.x * FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > SCREEN_WIDTH: self.pos.x = SCREEN_WIDTH
        if self.pos.x < 0: self.pos.x = 0
        self.rect.midbottom = self.pos

        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            self.image.fill(GOLD_COLOR if self.multiplier_timer % 10 < 5 else PLAYER_COLOR)
        else:
            self.image.fill(PLAYER_COLOR)

    def jump(self):
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if hits: self.jump_count = 0

        if self.jump_count == 0:
            try: jump_sound.play()
            except: pass
            self.vel.y = JUMP_FORCE
            self.jump_count = 1
        elif self.jump_count == 1 and self.score >= DOUBLE_JUMP_THRESHOLD:
            try: jump_sound.play()
            except: pass
            self.vel.y = JUMP_FORCE
            self.jump_count = 2 
            for _ in range(15):
                self.game.particles.add(Particle(self.rect.centerx, self.rect.bottom, WHITE))

    def bounce(self):
        try:
            jump_sound.play()
            powerup_sound.play()
        except: pass
        self.vel.y = -20 
        self.multiplier_timer = 300 

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.Surface((width, 18))
        self.image.fill(PLATFORM_COLOR)
        pygame.draw.rect(self.image, (150, 200, 255), (0,0,width, 4))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.passed = False

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, ENEMY_COLOR, [(20,0), (40,20), (20,40), (0,20)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - 40)
        self.rect.y = -50
        self.speed_y = random.randint(3, 7)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT: self.kill()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Business Scale (KPI Dashboard)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 18, bold=True)
        self.running = True
        self.game_state = "PLAYING"
        
        # Performance Tracking Variables
        self.frame_compute_time = 0
        
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
        self.platforms.empty()
        self.enemies.empty()
        self.particles.empty()
        self.all_sprites.empty()
        self.all_sprites.add(self.player)
        p = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH)
        self.platforms.add(p)
        self.all_sprites.add(p)
        for i in range(1, 8):
            p = Platform(random.randrange(0, SCREEN_WIDTH - 100), SCREEN_HEIGHT - (i * 100), 120)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def reset_game(self):
        self.player.reset()
        self.start_game()
        self.game_state = "PLAYING"

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

    def run(self):
        while self.running:
            # 1. Start High Precision Timer
            start_tick = time.perf_counter()
            
            self.events()
            if self.game_state == "PLAYING":
                self.update()
            self.draw()
            
            # 2. End Timer and calculate in milliseconds
            end_tick = time.perf_counter()
            self.frame_compute_time = (end_tick - start_tick) * 1000
            
            self.clock.tick(FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_state == "PLAYING" and event.key == pygame.K_SPACE:
                    self.player.jump()
                if self.game_state == "GAMEOVER" and event.key == pygame.K_r:
                    self.reset_game()

    def update(self):
        self.all_sprites.update()
        self.particles.update()

        # Infinite Scroll
        if self.player.rect.top <= SCREEN_HEIGHT / 4:
            shift = abs(self.player.vel.y)
            self.player.pos.y += shift
            for p in self.platforms:
                p.rect.y += shift
                if p.rect.top >= SCREEN_HEIGHT: p.kill()
            for e in self.enemies:
                e.rect.y += shift
            while len(self.platforms) < 8:
                w = random.randint(80, 150)
                p = Platform(random.randint(0, SCREEN_WIDTH - w), -30, w)
                self.platforms.add(p)
                self.all_sprites.add(p)

        # Platform Collision
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            for platform in hits:
                if self.player.rect.bottom <= platform.rect.top + 15:
                    self.player.pos.y = platform.rect.top
                    self.player.vel.y = 0
                    self.player.jump_count = 0
                    if not platform.passed:
                        mult = 2 if self.player.multiplier_timer > 0 else 1
                        self.player.score += (10 * mult)
                        try: platform_sound.play()
                        except: pass
                        platform.passed = True
                    break

        # Combat
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            if self.player.vel.y > 0 and self.player.rect.bottom < enemy.rect.centery + 10:
                enemy.kill()
                self.player.bounce()
                for _ in range(15): self.particles.add(Particle(enemy.rect.centerx, enemy.rect.centery, ENEMY_COLOR))
            else:
                self.player.lives -= 1
                self.player.pos = pygame.math.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                self.enemies.empty() 

        self.spawn_timer += 1
        if self.spawn_timer >= 110:
            e = Enemy(); self.enemies.add(e); self.all_sprites.add(e)
            self.spawn_timer = 0

        if self.player.rect.top > SCREEN_HEIGHT:
            try: lose_life_sound.play()
            except: pass
            self.player.lives -= 1
            self.player.pos = pygame.math.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            self.player.vel = pygame.math.Vector2(0, 0)

        if self.player.lives <= 0:
            try: lose_sound.play()
            except: pass
            self.game_state = "GAMEOVER"

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_grid()

        for sprite in self.all_sprites: self.screen.blit(sprite.image, sprite.rect)
        for p in self.particles: self.screen.blit(p.image, p.rect)

        # UI Overlay
        pygame.draw.rect(self.screen, (30, 30, 40), (0, 0, SCREEN_WIDTH, 65))
        pygame.draw.line(self.screen, WHITE, (0, 65), (SCREEN_WIDTH, 65), 2)

        # KPIs
        score_surf = self.font.render(f"REVENUE: ${self.player.score}k", True, PLAYER_ACCENT)
        self.screen.blit(score_surf, (20, 10))
        
        lives_surf = self.font.render(f"CAPITAL: {self.player.lives}", True, ENEMY_COLOR if self.player.lives == 1 else WHITE)
        self.screen.blit(lives_surf, (200, 10))

        # --- PERFORMANCE MONITORING (The new bits) ---
        # Using clock.get_fps()
        fps_val = int(self.clock.get_fps())
        fps_surf = self.font.render(f"STABILITY: {fps_val} FPS", True, (0, 255, 0) if fps_val > 50 else (255, 0, 0))
        self.screen.blit(fps_surf, (400, 10))

        # Using time.perf_counter() data
        perf_surf = self.font.render(f"LATENCY: {self.frame_compute_time:.2f}ms", True, (200, 200, 200))
        self.screen.blit(perf_surf, (400, 35))

        if self.player.score >= DOUBLE_JUMP_THRESHOLD:
            dj_surf = self.font.render("DOUBLE JUMP: ACTIVE", True, GOLD_COLOR)
            self.screen.blit(dj_surf, (20, 35))

        if self.game_state == "GAMEOVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(180); overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            go_surf = self.font.render("INSOLVENT! PRESS 'R' TO RESTART", True, ENEMY_COLOR)
            self.screen.blit(go_surf, (SCREEN_WIDTH//2 - go_surf.get_width()//2, SCREEN_HEIGHT//2))

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()



    #--------------------
#README Paragraph:
#Business Scale is a Finance-themed Infinite Climber we built.
#You climb a Market Grid to grow your Score (Revenue) while not losing your Lives (Capital). 
#Avoid or Stomp on Red Enemies to survive, and jumping on Enemies triggers a Market Boom for Double Points!
#Reaching 100 (100K Revenue) points unlocks a Double Jump.
#The goal is to scale the business as high as possible until you lose all your Lives (Capital).
#--------------------



#--------------------
#Resources:
#Audio from "scratch.mit.edu"
#--------------------



#--------------------
#Student Reflections:
#I thought that Coming into this project, I didn't have much experience with Python, so I used AI to help me structure the code and explain how the different parts work.
#I thought that connecting the business KPIs to the actual gameplay was the most interesting part.
#While the AI did the hard parts, I learned how small changes in the constants (like gravity or friction) completely change how the game feels to play.
#Also I learned how AI can be utilized to do amazing stuff.
#What I did which I found most intriguing was the sound effect and music finding songs from scratch and using sounds.play to play the sounds.
#My partner was also super herlpful as he codded the player to fix collisions, add polish, enemy speed, double jump and fixed some of the UI.
#--------------------