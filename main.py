import pygame
import sys
from levels.level1_sanji_vs_queen import Level1
from levels.level2_zoro_vs_king import Level2
from levels.level3_luffy_vs_kaido import Level3

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("One Piece: Wano Showdown")
bg = pygame.image.load("assets/images/intro.png").convert()
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
transition = pygame.image.load("assets/images/transition.png")
bg_music = pygame.mixer.Sound("assets/sounds/game_music.wav") 
bg_music.play(loops = - 1)

clock = pygame.time.Clock()
FPS = 60

def fade_transition(color=(0, 0, 0), duration=1000):
    """Fade to color over `duration` milliseconds"""
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(color)
    for alpha in range(0, 255, 10):  # controls fade speed
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(duration // 25)


def main_menu():
    font = pygame.font.Font(None, 64)
    screen.blit(bg,(0,0))
    start_text = pygame.font.Font(None, 48).render("Press ENTER to Start", True, (230,155,0))
    while True:
        screen.blit(bg, (0, 0))
        screen.blit(start_text, (450, 600))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        pygame.display.flip()
        clock.tick(FPS)

def show_controls():
    font_title = pygame.font.Font(None, 72)
    font_text = pygame.font.Font(None, 42)

    title = font_title.render("Controls", True, (255, 215, 0))

    controls = [
        "  A / D  : Move",
        "  Q       : Short attack",
        "  E       : Long attack",

        "Press ENTER to Begin the Game"
    ]

    while True:
        screen.fill((10, 10, 30))
        screen.blit(title, (420, 80))

        for i, line in enumerate(controls):
            text = font_text.render(line, True, (255, 255, 255))
            screen.blit(text, (200, 180 + i * 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return  # Continue to main game

        pygame.display.flip()
        clock.tick(FPS)

def show_level_title(level_name):
    font = pygame.font.Font(None, 80)
    subfont = pygame.font.Font(None, 50)
    # screen.fill((0, 0, 0))
    title = font.render(level_name, True, (255, 115, 0))
    subtext = subfont.render("Get Ready!", True, (255, 255, 255))
    screen.blit(transition,(0,0))
    screen.blit(title, (400, 300))
    screen.blit(subtext, (530, 400))
    pygame.display.flip()
    pygame.time.wait(2500)


def main():
    main_menu()
    show_controls()

    levels = [
        ("Level 1: Sanji vs Queen", Level1),
        ("Level 2: Zoro vs King", Level2),
        ("Level 3: Luffy vs Kaido", Level3)
    ]

    for name, level in levels:
        fade_transition()
        show_level_title(name)
        current_level = level(screen)
        result = current_level.run()
        if result == "lose":
            return main()

    # Win screen
    fade_transition()
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 80)
    text = font.render("You Won! The Wano Arc is Complete!", True, (255, 255, 255))
    screen.blit(text, (120, 320))
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()



if __name__ == "__main__":
    main()