import asyncio
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defender - Enhanced")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (200, 0, 255)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)
GOLD = (255, 215, 0)

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
        self.shield = 0
        self.max_shield = 50
        self.weapon_level = 1
        
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
        # Shield effect
        if self.shield > 0:
            pygame.draw.circle(screen, (0, 200, 255, 100), 
                             (self.x + self.w // 2, self.y + self.h // 2), 
                             self.w, 2)
        
        # Ship body
        pygame.draw.polygon(screen, CYAN, [
            (self.x + self.w // 2, self.y),
            (self.x, self.y + self.h),
            (self.x + self.w, self.y + self.h)
        ])
        # Cockpit
        pygame.draw.circle(screen, BLUE, (self.x + self.w // 2, self.y + 15), 8)
        
        # Weapon indicator
        if self.weapon_level > 1:
            for i in range(self.weapon_level - 1):
                pygame.draw.circle(screen, GOLD, 
                                 (self.x + 10 + i * 10, self.y + self.h - 5), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def take_damage(self, damage):
        if self.shield > 0:
            self.shield -= damage
            if self.shield < 0:
                self.health += self.shield
                self.shield = 0
        else:
            self.health -= damage

class Bullet:
    def __init__(self, x, y, angle=0, damage=1):
        self.x = x
        self.y = y
        self.speed = 8
        self.w = 4
        self.h = 15
        self.angle = angle
        self.damage = damage
        
    def update(self):
        self.y -= self.speed * math.cos(math.radians(self.angle))
        self.x += self.speed * math.sin(math.radians(self.angle))
    
    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.w, self.h))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Enemy:
    def __init__(self, enemy_type='normal'):
        self.x = random.randint(0, WIDTH - 40)
        self.y = random.randint(-100, -40)
        self.w = 35
        self.h = 35
        self.type = enemy_type
        
        if enemy_type == 'fast':
            self.speed = random.uniform(3.5, 5.0)
            self.health = 1
            self.color = PINK
            self.points = 15
        elif enemy_type == 'tank':
            self.speed = random.uniform(1.0, 2.0)
            self.health = 5
            self.color = (100, 0, 100)
            self.points = 30
            self.w = 45
            self.h = 45
        else:
            self.speed = random.uniform(1.5, 3.5)
            self.health = 2
            self.color = RED
            self.points = 10
            
        self.max_health = self.health
        
    def update(self):
        self.y += self.speed
    
    def draw(self):
        # Enemy ship
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.polygon(screen, tuple(c // 2 for c in self.color), [
            (self.x, self.y),
            (self.x + self.w // 2, self.y - 10),
            (self.x + self.w, self.y)
        ])
        
        # Health bar for tanks
        if self.type == 'tank':
            bar_w = self.w
            health_ratio = self.health / self.max_health
            pygame.draw.rect(screen, RED, (self.x, self.y - 8, bar_w, 4))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 8, int(bar_w * health_ratio), 4))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Boss:
    def __init__(self):
        self.x = WIDTH // 2 - 50
        self.y = -150
        self.w = 100
        self.h = 100
        self.health = 100
        self.max_health = 100
        self.speed = 1
        self.direction = 1
        self.shoot_timer = 0
        self.phase = 1
        
    def update(self):
        # Move boss
        if self.y < 80:
            self.y += self.speed
        else:
            self.x += self.direction * 2
            if self.x <= 0 or self.x >= WIDTH - self.w:
                self.direction *= -1
                
        # Change phase based on health
        if self.health < self.max_health * 0.5:
            self.phase = 2
    
    def draw(self):
        # Boss body
        color = RED if self.phase == 1 else PURPLE
        pygame.draw.rect(screen, color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(screen, ORANGE, (self.x + 10, self.y + 10, self.w - 20, self.h - 20))
        
        # Eyes
        pygame.draw.circle(screen, YELLOW, (self.x + 30, self.y + 40), 10)
        pygame.draw.circle(screen, YELLOW, (self.x + 70, self.y + 40), 10)
        pygame.draw.circle(screen, RED, (self.x + 30, self.y + 40), 5)
        pygame.draw.circle(screen, RED, (self.x + 70, self.y + 40), 5)
        
        # Health bar
        bar_w = self.w
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y - 15, bar_w, 8))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 15, int(bar_w * health_ratio), 8))
        pygame.draw.rect(screen, WHITE, (self.x, self.y - 15, bar_w, 8), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def shoot(self):
        bullets = []
        if self.phase == 1:
            # Simple shot pattern
            bullets.append(EnemyBullet(self.x + self.w // 2, self.y + self.h))
        else:
            # Triple shot pattern
            for angle in [-20, 0, 20]:
                bullets.append(EnemyBullet(self.x + self.w // 2, self.y + self.h, angle))
        return bullets

class EnemyBullet:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.speed = 5
        self.angle = angle
        
    def update(self):
        self.y += self.speed * math.cos(math.radians(self.angle))
        self.x += self.speed * math.sin(math.radians(self.angle))
    
    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 5)
    
    def get_rect(self):
        return pygame.Rect(self.x - 5, self.y - 5, 10, 10)

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
    def __init__(self, x=None, y=None, ptype=None):
        self.x = x if x is not None else random.randint(0, WIDTH - 30)
        self.y = y if y is not None else -30
        self.w = 30
        self.h = 30
        self.speed = 2
        self.type = ptype if ptype else random.choice(['health', 'rapid_fire', 'shield', 'weapon_up'])
    
    def update(self):
        self.y += self.speed
    
    def draw(self):
        colors = {
            'health': GREEN,
            'rapid_fire': PURPLE,
            'shield': CYAN,
            'weapon_up': GOLD
        }
        color = colors.get(self.type, WHITE)
        pygame.draw.circle(screen, color, (self.x + self.w // 2, self.y + self.h // 2), self.w // 2)
        pygame.draw.circle(screen, WHITE, (self.x + self.w // 2, self.y + self.h // 2), self.w // 4)
        
        # Icon
        center_x = self.x + self.w // 2
        center_y = self.y + self.h // 2
        if self.type == 'health':
            pygame.draw.line(screen, WHITE, (center_x - 5, center_y), (center_x + 5, center_y), 2)
            pygame.draw.line(screen, WHITE, (center_x, center_y - 5), (center_x, center_y + 5), 2)
        elif self.type == 'weapon_up':
            pygame.draw.polygon(screen, WHITE, [
                (center_x, center_y - 5),
                (center_x - 4, center_y + 5),
                (center_x + 4, center_y + 5)
            ])
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

async def main():
    running = True
    player = Player()
    bullets = []
    enemies = []
    enemy_bullets = []
    particles = []
    powerups = []
    boss = None
    
    score = 0
    combo = 0
    combo_timer = 0
    wave = 1
    kills_this_wave = 0
    
    enemy_spawn_timer = 0
    powerup_spawn_timer = 0
    shoot_cooldown = 0
    rapid_fire_timer = 0
    boss_active = False
    
    game_over = False
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    tiny_font = pygame.font.Font(None, 18)
    
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
                    enemy_bullets = []
                    particles = []
                    powerups = []
                    boss = None
                    score = 0
                    combo = 0
                    wave = 1
                    kills_this_wave = 0
                    boss_active = False
                    game_over = False
        
        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            # Shooting
            shoot_cooldown -= 1
            fire_rate = 5 if rapid_fire_timer > 0 else 15
            
            if (keys[pygame.K_SPACE] or keys[pygame.K_j]) and shoot_cooldown <= 0:
                if player.weapon_level == 1:
                    bullets.append(Bullet(player.x + player.w // 2 - 2, player.y))
                elif player.weapon_level == 2:
                    bullets.append(Bullet(player.x + player.w // 2 - 10, player.y))
                    bullets.append(Bullet(player.x + player.w // 2 + 6, player.y))
                elif player.weapon_level >= 3:
                    bullets.append(Bullet(player.x + player.w // 2 - 10, player.y))
                    bullets.append(Bullet(player.x + player.w // 2 - 2, player.y))
                    bullets.append(Bullet(player.x + player.w // 2 + 6, player.y))
                
                shoot_cooldown = fire_rate
            
            rapid_fire_timer = max(0, rapid_fire_timer - 1)
            combo_timer = max(0, combo_timer - 1)
            if combo_timer == 0:
                combo = 0
            
            # Boss wave every 5 waves
            if wave % 5 == 0 and kills_this_wave >= 20 and not boss_active:
                boss = Boss()
                boss_active = True
                enemies.clear()
            
            # Spawn enemies
            if not boss_active:
                enemy_spawn_timer += 1
                spawn_rate = max(20, 40 - wave * 2)
                
                if enemy_spawn_timer > spawn_rate:
                    # Random enemy type based on wave
                    rand = random.random()
                    if wave >= 3 and rand < 0.2:
                        enemies.append(Enemy('tank'))
                    elif wave >= 2 and rand < 0.5:
                        enemies.append(Enemy('fast'))
                    else:
                        enemies.append(Enemy('normal'))
                    enemy_spawn_timer = 0
            
            # Spawn powerups
            powerup_spawn_timer += 1
            if powerup_spawn_timer > 600:
                powerups.append(PowerUp())
                powerup_spawn_timer = 0
            
            # Update boss
            if boss_active and boss:
                boss.update()
                boss.shoot_timer += 1
                
                shoot_rate = 30 if boss.phase == 1 else 20
                if boss.shoot_timer > shoot_rate:
                    enemy_bullets.extend(boss.shoot())
                    boss.shoot_timer = 0
                
                # Check boss collision with bullets
                for b in bullets[:]:
                    if boss.get_rect().colliderect(b.get_rect()):
                        boss.health -= 1
                        if b in bullets:
                            bullets.remove(b)
                        for _ in range(5):
                            particles.append(Particle(b.x, b.y, ORANGE))
                
                if boss.health <= 0:
                    score += 500
                    boss_active = False
                    wave += 1
                    kills_this_wave = 0
                    for _ in range(50):
                        particles.append(Particle(boss.x + boss.w // 2, boss.y + boss.h // 2, 
                                                 random.choice([YELLOW, ORANGE, RED, PURPLE])))
                    powerups.append(PowerUp(boss.x + boss.w // 2, boss.y + boss.h // 2, 'weapon_up'))
                    boss = None
            
            # Update enemy bullets
            for eb in enemy_bullets[:]:
                eb.update()
                if eb.y > HEIGHT or eb.x < 0 or eb.x > WIDTH:
                    enemy_bullets.remove(eb)
                elif eb.get_rect().colliderect(player.get_rect()):
                    player.take_damage(10)
                    enemy_bullets.remove(eb)
                    for _ in range(8):
                        particles.append(Particle(eb.x, eb.y, RED))
            
            # Update bullets
            for b in bullets[:]:
                b.update()
                if b.y < 0 or b.x < 0 or b.x > WIDTH:
                    bullets.remove(b)
            
            # Update enemies
            for e in enemies[:]:
                e.update()
                if e.y > HEIGHT:
                    enemies.remove(e)
                    combo = 0
                
                # Check collision with player
                if e.get_rect().colliderect(player.get_rect()):
                    player.take_damage(20)
                    enemies.remove(e)
                    combo = 0
                    for _ in range(15):
                        particles.append(Particle(e.x + e.w // 2, e.y + e.h // 2, RED))
                
                # Check collision with bullets
                for b in bullets[:]:
                    if e.get_rect().colliderect(b.get_rect()):
                        e.health -= 1
                        if b in bullets:
                            bullets.remove(b)
                        
                        if e.health <= 0:
                            combo += 1
                            combo_timer = 120
                            combo_bonus = combo * 2
                            score += e.points + combo_bonus
                            kills_this_wave += 1
                            
                            if e in enemies:
                                enemies.remove(e)
                            for _ in range(20):
                                particles.append(Particle(e.x + e.w // 2, e.y + e.h // 2, 
                                                        random.choice([YELLOW, ORANGE, RED])))
                            
                            # Check for wave completion
                            if kills_this_wave >= 30 and not boss_active and wave % 5 != 0:
                                wave += 1
                                kills_this_wave = 0
            
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
                    elif p.type == 'shield':
                        player.shield = min(player.max_shield, player.shield + 30)
                    elif p.type == 'weapon_up':
                        player.weapon_level = min(3, player.weapon_level + 1)
                    
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
        
        for eb in enemy_bullets:
            eb.draw()
        
        for e in enemies:
            e.draw()
        
        if boss_active and boss:
            boss.draw()
        
        for p in particles:
            p.draw()
        
        for pw in powerups:
            pw.draw()
        
        # Draw UI
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        wave_text = small_font.render(f"Wave: {wave}", True, WHITE)
        screen.blit(wave_text, (WIDTH - 120, 10))
        
        if combo > 1:
            combo_text = font.render(f"x{combo} COMBO!", True, GOLD)
            screen.blit(combo_text, (WIDTH // 2 - 80, 50))
        
        # Health bar
        pygame.draw.rect(screen, RED, (10, 40, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, 40, int(200 * player.health / player.max_health), 20))
        pygame.draw.rect(screen, WHITE, (10, 40, 200, 20), 2)
        
        # Shield bar
        if player.shield > 0:
            pygame.draw.rect(screen, (0, 100, 150), (10, 65, 200, 15))
            pygame.draw.rect(screen, CYAN, (10, 65, int(200 * player.shield / player.max_shield), 15))
            pygame.draw.rect(screen, WHITE, (10, 65, 200, 15), 2)
        
        if rapid_fire_timer > 0:
            rapid_text = small_font.render("RAPID FIRE!", True, PURPLE)
            screen.blit(rapid_text, (10, 85))
        
        if boss_active:
            boss_text = font.render("BOSS BATTLE!", True, RED)
            screen.blit(boss_text, (WIDTH // 2 - 100, 10))
        
        if game_over:
            game_over_text = font.render("GAME OVER", True, RED)
            score_text = font.render(f"Final Score: {score}", True, WHITE)
            wave_text_final = small_font.render(f"Reached Wave: {wave}", True, WHITE)
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 80))
            screen.blit(score_text, (WIDTH // 2 - 120, HEIGHT // 2 - 30))
            screen.blit(wave_text_final, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
            screen.blit(restart_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
        
        pygame.display.flip()
        await asyncio.sleep(0)
    
    pygame.quit()

asyncio.run(main())
