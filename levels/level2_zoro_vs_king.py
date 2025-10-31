import pygame
import random
        
class Level2:          
    def __init__(self, screen):
        self.screen = screen
        self.bg = pygame.image.load("assets/images/bg_onigashima.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))

        # Power-up
        self.powerup_collected = False
        self.powerup_image = pygame.image.load("assets/images/power_up.png").convert_alpha()
        self.powerup_image = pygame.transform.scale(self.powerup_image, (40, 40))
        self.powerup_timer = 0
        self.powerup_pos = (0, 0)        

        # === King setup ===
        king_1 = pygame.image.load("assets/images/king1.png").convert_alpha()
        king_2 = pygame.image.load("assets/images/king2.png").convert_alpha()

        def crop_surface(surface):
            mask = pygame.mask.from_surface(surface)
            rects = mask.get_bounding_rects()
            if rects:
                rect = rects[0]
                cropped = surface.subsurface(rect)
                return cropped
            return surface

        king_1 = crop_surface(king_1)
        king_2 = crop_surface(king_2)

        scale_factor = 0.12
        king_1 = pygame.transform.rotozoom(king_1, 0, scale_factor)
        king_2 = pygame.transform.rotozoom(king_2, 0, scale_factor)

        self.king_walk = [king_1, king_2]
        self.kwalk_index = 0
        self.king = self.king_walk[self.kwalk_index]
        self.king_rect = self.king.get_rect(midbottom=(1100, 600))

        # === zoro setup ===
        def load_zoro(path, scale):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.rotozoom(img, 0, scale)

        scale = 0.3
        self.zoro_hit = crop_surface(load_zoro('assets/images/sanji/sanji_hit1.png', scale))
        self.zoro_walk = [
            crop_surface(load_zoro('assets/images/zoro/zoro_walk1.png', scale)),
            crop_surface(load_zoro('assets/images/zoro/zoro_walk2.png', scale)),
            crop_surface(load_zoro('assets/images/zoro/zoro_walk3.png', scale))
        ]
        self.walk_index = 0
        self.image = self.zoro_walk[self.walk_index]
        self.zoro_rect = self.image.get_rect(midbottom=(560, 300))

        self.zoro_cslash = load_zoro('assets/images/zoro/zoro_cslash.png', scale)
        self.slash_image = load_zoro('assets/images/sanji/sanji_slash.png', 0.25)
        self.slashes = []

        self.health_zoro = 100
        self.health_king = 100
        self.slash = False
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # === King attacks ===
        self.king_attack = pygame.image.load("assets/images/fire.png").convert_alpha()
        self.king_attack = pygame.transform.rotozoom(self.king_attack, 0, 0.1)
        self.king_projectiles = []
        
        self.gravity = 0
        
        # == Sounds ==
        self.sound_kick = pygame.mixer.Sound("assets/sounds/kick.wav")
        self.sound_slash = pygame.mixer.Sound("assets/sounds/sanji_slash.wav")
        self.sound_jump = pygame.mixer.Sound("assets/sounds/jump.wav")
        self.sound_queen_attack = pygame.mixer.Sound("assets/sounds/queen_attack.wav")
        self.sound_powerup = pygame.mixer.Sound("assets/sounds/power_up.wav")
        self.sound_qhit = pygame.mixer.Sound("assets/sounds/queen_damage.wav")
        self.sound_shit = pygame.mixer.Sound("assets/sounds/sanji_damage.wav")
       

    def draw_healthbar(self, x, y, hp, color):
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, 200, 20))
        pygame.draw.rect(self.screen, color, (x, y, 2 * hp, 20))

    def run(self):
        running = True
        start_time = pygame.time.get_ticks()
        level_duration = 90000
         
        while running:
            self.screen.blit(self.bg, (0, 0))
            keys = pygame.key.get_pressed()

            self.screen.blit(self.bg, (0, 0))
            keys = pygame.key.get_pressed()

                        # === TIMER ===
            elapsed_time = pygame.time.get_ticks() - start_time
            remaining_time = max(0, (level_duration - elapsed_time) // 1000)  # in seconds

            # Display timer on screen
            font = pygame.font.Font(None, 48)
            timer_text = font.render(f"Time: {remaining_time}", True, (255, 255, 255))
            self.screen.blit(timer_text, (570, 50))

            # If time runs out → lose
            if remaining_time <= 0:
                return "lose"

            # === Zoro movement ===
            if keys[pygame.K_a]:
                self.zoro_rect.x -= 5
            if keys[pygame.K_d]:
                self.zoro_rect.x += 5
            if keys[pygame.K_SPACE] and self.zoro_rect.bottom >= 560:
                self.gravity = -20
                self.sound_jump.play()

            self.gravity += 1
            self.zoro_rect.y += self.gravity
            if self.zoro_rect.bottom >= 560:
                self.zoro_rect.bottom = 560

            # Power-up spawn
            if not self.powerup_collected and random.randint(0, 400) == 1:
                self.powerup_pos = (random.randint(200, 1000), 500)
                self.powerup_collected = True
                self.powerup_timer = pygame.time.get_ticks()

            # Power-up logic
            if self.powerup_collected:
                self.screen.blit(self.powerup_image, self.powerup_pos)
                powerup_rect = self.powerup_image.get_rect(topleft=self.powerup_pos)
                if pygame.time.get_ticks() - self.powerup_timer > 5000:
                    self.powerup_collected = False
                if self.zoro_rect.colliderect(powerup_rect):
                    self.health_zoro = min(self.health_zoro + 20, 100)
                    self.powerup_collected = False                

            # === Walking animation ===
            self.walk_index += 0.1
            if self.walk_index >= len(self.zoro_walk):
                self.walk_index = 0
            self.image = self.zoro_walk[int(self.walk_index)]

            # === King animation ===
            self.kwalk_index += 0.1
            if self.kwalk_index >= len(self.king_walk):
                self.kwalk_index = 0
            self.king = self.king_walk[int(self.kwalk_index)]

            # === King random attacks with cooldown ===
            current_time = pygame.time.get_ticks()
            if not hasattr(self, "last_king_attack_time"):
                self.last_king_attack_time = 0

            attack_cooldown = 2000  # King can attack every 2 seconds
            if current_time - self.last_king_attack_time > attack_cooldown:
                attack_type = random.choice(["ground", "air"])

                if attack_type == "ground":
                    rect = self.king_attack.get_rect(midright=self.king_rect.midleft)
                    self.sound_queen_attack.play()
                    rect.y = 420  # near ground level
                else:
                    rect = self.king_attack.get_rect(midright=self.king_rect.midleft)
                    self.sound_queen_attack.play()
                    rect.y = 150  # air level

                self.king_projectiles.append((attack_type, rect))
                self.last_king_attack_time = current_time

            # === Move & draw king projectiles ===
            for attack_type, rect in self.king_projectiles[:]:
                # Move attack
                if attack_type == "ground":
                    rect.x -= 10
                else:
                    rect.x -= 8

                # Draw attack
                self.screen.blit(self.king_attack, rect)

                # Collision with Zoro
                if rect.colliderect(self.zoro_rect):
                    self.health_zoro -= 5
                    self.king_projectiles.remove((attack_type, rect))
                    self.image = self.zoro_hit
                    self.sound_shit.play()
                else:
                    self.image = self.zoro_walk[int(self.walk_index)]
                continue

                # Remove off-screen attacks
                if rect.right < 0 or rect.top > 720:
                    self.king_projectiles.remove((attack_type, rect))

            # === Zoro short attack ===
            if keys[pygame.K_q] and self.zoro_rect.colliderect(self.king_rect):
                self.image = self.zoro_cslash
                self.health_king -= 0.4
                self.sound_kick.play()

            # === Zoro long attack ===
            if keys[pygame.K_e]:
                slash_rect = self.slash_image.get_rect(midleft=self.zoro_rect.midright)
                self.sound_slash.play()
                if not self.slash:
                    self.slashes.append(slash_rect)
                    self.slash = True

            for slash_rect in self.slashes[:]:
                slash_rect.x += 12
                self.screen.blit(self.slash_image, slash_rect)
                if slash_rect.colliderect(self.king_rect):
                    self.health_king -= 0.8
                    self.sound_qhit.play()
                    self.slashes.remove(slash_rect)
                    self.slash = False
                    continue
                if slash_rect.x > 1300:
                    self.slashes.remove(slash_rect)

            # === Collision ===
            if self.zoro_rect.colliderect(self.king_rect):
                self.health_zoro -= 0.6
                self.sound_shit.play()

            # === Draw ===
            self.screen.blit(self.king, self.king_rect)
            self.screen.blit(self.image, self.zoro_rect)

            self.draw_healthbar(50, 50, self.health_zoro, (0, 255, 0))
            self.draw_healthbar(900, 50, self.health_king, (255, 0, 0))

            # === End conditions ===
            if self.health_zoro <= 0:
                return "lose"
            if self.health_king <= 0:
                return "win"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_s:
                        self.slash = False

            pygame.display.flip()
            self.clock.tick(self.FPS)