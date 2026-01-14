import asyncio
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defender")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (200, 0, 255)

# Clock
clock = pygame.time.Clock()
FPS = 60

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 80
        self.w = 40
        self.h = 40
        self.speed = 5
        self.health = 100
        self.max_health = 100
        
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        self.x = max(0, min(WIDTH - self.w, self.x))
        self.y = max(0, min(HEIGHT - self.h, self.y))
    
    def draw(self):
        # Ship body
        pygame.draw.polygon(screen, CYAN, [
            (self.x + self.w // 2, self.y),
            (self.x, self.y + self.h),
            (self.x + self.w, self.y + self.h)
        ])
        # Cockpit
        pygame.draw.circle(screen, BLUE, (self.x + self.w // 2, self.y + 15), 8)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8
        self.w = 4
        self.h = 15
        
    def update(self):
        self.y -= self.speed
        
    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.w, self.h))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Enemy:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 40)
        self.y = random.randint(-100, -40)
        self.w = 35
        self.h = 35
        self.speed = random.uniform(1.5, 3.5)
        self.health = 2
        
    def update(self):
        self.y += self.speed
        
    def draw(self):
        # Enemy ship
        pygame.draw.rect(screen, RED, (self.x, self.y, self.w, self.h))
        pygame.draw.polygon(screen, (150, 0, 0), [
            (self.x, self.y),
            (self.x + self.w // 2, self.y - 10),
            (self.x + self.w, self.y)
        ])
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.color = color
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(1, self.size - 0.1)
        
    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class PowerUp:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 30)
        self.y = -30
        self.w = 30
        self.h = 30
        self.speed = 2
        self.type = random.choice(['health', 'rapid_fire'])
        
    def update(self):
        self.y += self.speed
        
    def draw(self):
        color = GREEN if self.type == 'health' else PURPLE
        pygame.draw.circle(screen, color, (self.x + self.w // 2, self.y + self.h // 2), self.w // 2)
        pygame.draw.circle(screen, WHITE, (self.x + self.w // 2, self.y + self.h // 2), self.w // 4)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

async def main():
    running = True
    player = Player()
    bullets = []
    enemies = []
    particles = []
    powerups = []
    score = 0
    enemy_spawn_timer = 0
    powerup_spawn_timer = 0
    shoot_cooldown = 0
    rapid_fire_timer = 0
    game_over = False
    
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    # Restart game
                    player = Player()
                    bullets = []
                    enemies = []
                    particles = []
                    powerups = []
                    score = 0
                    game_over = False
        
        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            # Shooting
            shoot_cooldown -= 1
            fire_rate = 5 if rapid_fire_timer > 0 else 15
            if (keys[pygame.K_SPACE] or keys[pygame.K_j]) and shoot_cooldown <= 0:
                bullets.append(Bullet(player.x + player.w // 2 - 2, player.y))
                shoot_cooldown = fire_rate
            
            rapid_fire_timer = max(0, rapid_fire_timer - 1)
            
            # Spawn enemies
            enemy_spawn_timer += 1
            if enemy_spawn_timer > 40:
                enemies.append(Enemy())
                enemy_spawn_timer = 0
            
            # Spawn powerups
            powerup_spawn_timer += 1
            if powerup_spawn_timer > 600:
                powerups.append(PowerUp())
                powerup_spawn_timer = 0
            
            # Update bullets
            for b in bullets[:]:
                b.update()
                if b.y < 0:
                    bullets.remove(b)
            
            # Update enemies
            for e in enemies[:]:
                e.update()
                if e.y > HEIGHT:
                    enemies.remove(e)
                    
                # Check collision with player
                if e.get_rect().colliderect(player.get_rect()):
                    player.health -= 20
                    enemies.remove(e)
                    for _ in range(15):
                        particles.append(Particle(e.x + e.w // 2, e.y + e.h // 2, RED))
                    
                # Check collision with bullets
                for b in bullets[:]:
                    if e.get_rect().colliderect(b.get_rect()):
                        e.health -= 1
                        if b in bullets:
                            bullets.remove(b)
                        if e.health <= 0:
                            score += 10
                            if e in enemies:
                                enemies.remove(e)
                            for _ in range(20):
                                particles.append(Particle(e.x + e.w // 2, e.y + e.h // 2, random.choice([YELLOW, ORANGE := (255, 165, 0), RED])))
            
            # Update powerups
            for p in powerups[:]:
                p.update()
                if p.y > HEIGHT:
                    powerups.remove(p)
                if p.get_rect().colliderect(player.get_rect()):
                    if p.type == 'health':
                        player.health = min(player.max_health, player.health + 30)
                    elif p.type == 'rapid_fire':
                        rapid_fire_timer = 300
                    powerups.remove(p)
                    for _ in range(10):
                        particles.append(Particle(p.x, p.y, GREEN))
            
            # Update particles
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)
            
            # Check game over
            if player.health <= 0:
                game_over = True
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw stars
        for i in range(50):
            x = (i * 123) % WIDTH
            y = (i * 456 + pygame.time.get_ticks() // 10) % HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        player.draw()
        
        for b in bullets:
            b.draw()
        
        for e in enemies:
            e.draw()
        
        for p in particles:
            p.draw()
            
        for pw in powerups:
            pw.draw()
        
        # Draw UI
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Health bar
        pygame.draw.rect(screen, RED, (10, 40, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, 40, int(200 * player.health / player.max_health), 20))
        pygame.draw.rect(screen, WHITE, (10, 40, 200, 20), 2)
        
        if rapid_fire_timer > 0:
            rapid_text = small_font.render("RAPID FIRE!", True, PURPLE)
            screen.blit(rapid_text, (10, 70))
        
        if game_over:
            game_over_text = font.render("GAME OVER", True, RED)
            score_text = font.render(f"Final Score: {score}", True, WHITE)
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 60))
            screen.blit(score_text, (WIDTH // 2 - 120, HEIGHT // 2 - 10))
            screen.blit(restart_text, (WIDTH // 2 - 100, HEIGHT // 2 + 40))
        
        pygame.display.flip()
        await asyncio.sleep(0)
    
    pygame.quit()

asyncio.run(main())