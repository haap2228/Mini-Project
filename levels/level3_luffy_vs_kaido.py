import pygame
import random

class Level3:
    def __init__(self, screen):
        self.screen = screen
        self.bg = pygame.image.load("assets/images/bg_onigashima.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))

        def crop_surface(surface):
            mask = pygame.mask.from_surface(surface)
            rects = mask.get_bounding_rects()
            if rects:
                rect = rects[0]
                cropped = surface.subsurface(rect)
                return cropped
            return surface

        # === Power-up (meat) ===
        self.powerup_active = False
        self.powerup_img = pygame.transform.scale(
            pygame.image.load("assets/images/meat.png").convert_alpha(), (50, 50)
        )
        self.powerup_timer = 0
        self.powerup_pos = (0, 0)

        # === Kaido (Boss) setup ===
        kaido1 = crop_surface(pygame.image.load("assets/images/kaido2.png").convert_alpha())
        kaido2 = crop_surface(pygame.image.load("assets/images/kaido2.png").convert_alpha())
        scale = 0.1
        self.kaido_walk = [
            pygame.transform.rotozoom(kaido1, 0, scale),
            pygame.transform.rotozoom(kaido2, 0, scale),
        ]
        self.kaido_index = 0
        self.kaido = self.kaido_walk[self.kaido_index]
        self.kaido_rect = self.kaido.get_rect(midbottom=(1100, 600))

        # === Luffy setup ===
        def load_luffy(path, scale):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.rotozoom(img, 0, scale)
            

        scale = 0.3
        self.luffy_walk = [
            crop_surface(load_luffy("assets/images/luffy/luffy_walk1.png", scale)),
            crop_surface(load_luffy("assets/images/luffy/luffy_walk2.png", scale)),
            crop_surface(load_luffy("assets/images/luffy/luffy_walk3.png", scale))
        ]
        self.luffy_punch = load_luffy("assets/images/luffy/luffy_punch.png", scale)
        self.luffy_projectile_img = load_luffy("assets/images/luffy/luffy_projectile.png", 0.25)
        self.luffy_rect = self.luffy_walk[0].get_rect(midbottom=(200, 560))

        self.projectiles = []
        self.slash_active = False
        self.gravity = 0

        # === Stats ===
        self.health_luffy = 100
        self.health_kaido = 100
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # === Kaido attacks ===
        self.kaido_attack_img = pygame.transform.rotozoom(
            pygame.image.load("assets/images/fire.png").convert_alpha(), 0, 0.1)
        self.kaido_projectiles = []
        self.last_attack_time = 0

        # === Sounds ===
        self.sound_punch = pygame.mixer.Sound("assets/sounds/luffy_punch.wav")
        self.sound_fire = pygame.mixer.Sound("assets/sounds/fire.wav")
        self.sound_hit_luffy = pygame.mixer.Sound("assets/sounds/sanji_damage.wav")
        self.sound_hit_kaido = pygame.mixer.Sound("assets/sounds/queen_damage.wav")
        self.sound_powerup = pygame.mixer.Sound("assets/sounds/power_up.wav")
        self.sound_jump = pygame.mixer.Sound("assets/sounds/jump.wav")

    def draw_healthbar(self, x, y, hp, color):
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, 200, 20))
        pygame.draw.rect(self.screen, color, (x, y, 2 * max(hp, 0), 20))

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

            if remaining_time <= 0:
                return "lose"

            # === Movement ===
            if keys[pygame.K_a]:
                self.luffy_rect.x -= 5
            if keys[pygame.K_d]:
                self.luffy_rect.x += 5
            if keys[pygame.K_SPACE] and self.luffy_rect.bottom >= 560:
                self.gravity = -20
                self.sound_jump.play()

            self.gravity += 1
            self.luffy_rect.y += self.gravity
            if self.luffy_rect.bottom >= 560:
                self.luffy_rect.bottom = 560

            # === Power-up ===
            if not self.powerup_active and random.randint(0, 400) == 1:
                self.powerup_pos = (random.randint(200, 1000), 500)
                self.powerup_active = True
                self.powerup_timer = pygame.time.get_ticks()

            if self.powerup_active:
                self.screen.blit(self.powerup_img, self.powerup_pos)
                meat_rect = self.powerup_img.get_rect(topleft=self.powerup_pos)
                if pygame.time.get_ticks() - self.powerup_timer > 5000:
                    self.powerup_active = False
                if self.luffy_rect.colliderect(meat_rect):
                    self.health_luffy = min(self.health_luffy + 25, 100)
                    self.powerup_active = False
                    self.sound_powerup.play()

            # === Luffy animation ===
            self.kaido_index = (self.kaido_index + 0.1) % len(self.kaido_walk)
            self.kaido = self.kaido_walk[int(self.kaido_index)]
            self.luffy_index = (getattr(self, "luffy_index", 0) + 0.1) % len(self.luffy_walk)
            luffy_img = self.luffy_walk[int(self.luffy_index)]

            # === Kaido attacks with cooldown ===
            now = pygame.time.get_ticks()
            cooldown = 1800
            if now - self.last_attack_time > cooldown:
                atk_type = random.choice(["ground", "air"])
                rect = self.kaido_attack_img.get_rect(midright=self.kaido_rect.midleft)
                rect.y = 420 if atk_type == "ground" else 150
                self.kaido_projectiles.append((atk_type, rect))
                self.sound_fire.play()
                self.last_attack_time = now

            # === Move Kaido projectiles ===
            for atk_type, rect in self.kaido_projectiles[:]:
                rect.x -= 9 if atk_type == "air" else 11
                self.screen.blit(self.kaido_attack_img, rect)
                if rect.colliderect(self.luffy_rect):
                    self.health_luffy -= 6
                    self.sound_hit_luffy.play()
                    self.kaido_projectiles.remove((atk_type, rect))
                elif rect.right < 0:
                    self.kaido_projectiles.remove((atk_type, rect))

            # === Luffy Punch (close attack) ===
            if keys[pygame.K_q] and self.luffy_rect.colliderect(self.kaido_rect):
                luffy_img = self.luffy_punch
                self.health_kaido -= 0.6
                self.sound_punch.play()
                self.sound_hit_kaido.play()

            # === Luffy Long Attack (projectile) ===
            if keys[pygame.K_e] and not self.slash_active:
                proj_rect = self.luffy_projectile_img.get_rect(midleft=self.luffy_rect.midright)
                self.projectiles.append(proj_rect)
                self.slash_active = True
                self.sound_punch.play()

            for proj_rect in self.projectiles[:]:
                proj_rect.x += 12
                self.screen.blit(self.luffy_projectile_img, proj_rect)
                if proj_rect.colliderect(self.kaido_rect):
                    self.health_kaido -= 1.2
                    self.sound_hit_kaido.play()
                    self.projectiles.remove(proj_rect)
                    self.slash_active = False
                elif proj_rect.x > 1300:
                    self.projectiles.remove(proj_rect)
                    self.slash_active = False

            # === Collision damage if too close ===
            if self.luffy_rect.colliderect(self.kaido_rect):
                self.health_luffy -= 0.6

            # === Draw ===
            self.screen.blit(self.kaido, self.kaido_rect)
            self.screen.blit(luffy_img, self.luffy_rect)
            self.draw_healthbar(50, 50, self.health_luffy, (0, 255, 0))
            self.draw_healthbar(900, 50, self.health_kaido, (255, 0, 0))

            # === Win / Lose conditions ===
            if self.health_luffy <= 0:
                return "lose"
            if self.health_kaido <= 0:
                return "win"

            # === Events ===
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYUP and event.key == pygame.K_k:
                    self.slash_active = False

            pygame.display.flip()
            self.clock.tick(self.FPS)