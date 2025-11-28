#Projet : Nightfall
#Auteurs : Stanislas Gros de Beler, Paul Berenguer, Nael Arras, Sacha Philipps Herbert, Riadh Jouini

import pygame
import threading
import sys
import time

# Initialisation de Pygame
pygame.init()
pygame.font.init()

# Paramètres globaux
audio_settings = {"music_volume": 50, "effects_volume": 50}
dragging_slider = None

def interface():
    # Paramètres de la fenêtre
    largeur_ecran, hauteur_ecran = 1920, 1080
    screen = pygame.display.set_mode((largeur_ecran, hauteur_ecran), pygame.RESIZABLE | pygame.NOFRAME)
    pygame.display.set_caption("Nightfall")

    # Initialisation du mixeur audio
    pygame.mixer.init()

    # Load custom cursor image
    custom_cursor = pygame.image.load("sources/data/image/lampe1.png")
    custom_cursor = pygame.transform.scale(custom_cursor, (80, 80))

    # Hide the default cursor
    pygame.mouse.set_visible(False)

    def get_audio_settings():
        return audio_settings

    def play_music():
        if pygame.mixer.music.get_busy():  # Vérifie si la musique joue déjà
            return  # Si oui, on ne relance pas

        pygame.mixer.music.load("sources/data/Son/Son ambiance/Son_gresillement.mp3")
        pygame.mixer.music.set_volume(audio_settings["music_volume"] / 100)
        pygame.mixer.music.play(-1)

    def stop_music():
        pygame.mixer.music.stop()

    def draw_text(text, font, color, x, y):
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))

    def draw_slider(label, value, x, y, setting_key):
        """Dessine un curseur avec un bouton coulissant."""
        slider_width, slider_height = 200, 10
        knob_radius = 8

        # Barre du curseur
        pygame.draw.rect(screen, (100, 100, 100), (x, y, slider_width, slider_height))

        # Bouton du curseur
        knob_x = x + int((value / 100) * slider_width)
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, y + slider_height // 2), knob_radius)

        # Affichage du texte
        font = pygame.font.Font(None, 30)
        text_surface = font.render(f"{label}: {value}%", True, (255, 255, 255))
        screen.blit(text_surface, (x, y - 30))
        return pygame.Rect(x, y, slider_width, slider_height), setting_key

    def create_button(image_path, rel_x, rel_y, rel_width, rel_height, action=None):
        largeur_ecran, hauteur_ecran = screen.get_size()
        button_width = int(largeur_ecran * rel_width)
        button_height = int(hauteur_ecran * rel_height)
        button_x = int(largeur_ecran * rel_x - button_width / 2)
        button_y = int(hauteur_ecran * rel_y - button_height / 2)

        button_image = pygame.image.load(image_path)
        button_image = pygame.transform.scale(button_image, (button_width, button_height))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height

        if is_hovered:
            button_width = int(button_width * 1.1)
            button_height = int(button_height * 1.1)
            button_x = int(largeur_ecran * rel_x - button_width / 2)
            button_y = int(hauteur_ecran * rel_y - button_height / 2)
            button_image = pygame.transform.scale(button_image, (button_width, button_height))

        screen.blit(button_image, (button_x, button_y))
        
        return pygame.Rect(button_x, button_y, button_width, button_height), action

    game_ready = False

    def load_game(progress_callback):
        global game_ready
        print("Chargement du jeu en arrière-plan...")
        
        # Simulate loading steps
        steps = 10
        for i in range(steps):
            time.sleep(0.5)  # Simulate loading time
            progress_callback((i + 1) / steps * 100)
        
        game_ready = True
        print("Le jeu est prêt à être lancé !")
        
    def fade_in(surface, image, duration=1000):
        clock = pygame.time.Clock()
        alpha = 0
        increment = 255 / (duration / 16)
        while alpha < 255:
            alpha += increment
            image.set_alpha(alpha)
            surface.fill((0, 0, 0))
            surface.blit(image, (0, 0))
            pygame.display.flip()
            clock.tick(100)

    def fade_out(surface, image, duration=1000):
        clock = pygame.time.Clock()
        alpha = 255
        decrement = 255 / (duration / 16)  # Ensure smooth fade

        while alpha > 0:
            alpha -= decrement
            image.set_alpha(int(max(0, alpha)))  # Ensure alpha does not go negative
            surface.fill((0, 0, 0))  # Clear the screen
            surface.blit(image, (0, 0))
            pygame.display.flip()  # <=== Ensure screen updates
            clock.tick(100)

        surface.fill((0, 0, 0))  # Final black screen
        pygame.display.flip()


    def transition(duration=4000):
        start_volume = pygame.mixer.music.get_volume()
        steps = 30
        delay = duration // steps

        for i in range(steps):
            new_volume = start_volume * (1 - (i / steps))
            pygame.mixer.music.set_volume(new_volume)
            pygame.time.wait(delay)

        pygame.mixer.music.set_volume(0)
        
    def draw_gradient_bar(surface, x, y, width, height, start_color, end_color):
        """Draws a horizontal gradient progress bar."""
        for i in range(width):
            progress_ratio = i / width  # Percentage of the progress bar
            r = int(start_color[0] + progress_ratio * (end_color[0] - start_color[0]))
            g = int(start_color[1] + progress_ratio * (end_color[1] - start_color[1]))
            b = int(start_color[2] + progress_ratio * (end_color[2] - start_color[2]))
            pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + height))

    def loading_screen():
        loading_image = pygame.image.load("sources/data/image/chargement.png")
        loading_image = pygame.transform.scale(loading_image, (largeur_ecran, hauteur_ecran))

        fade_in(screen, loading_image, duration=600)

        font = pygame.font.Font("sources/data/Fonts/whoAsksSatan.ttf", 60)
        progress = [0]
        game_finished = [False]

        def progress_callback(p):
            progress.append(p)
            if p >= 100:
                game_finished[0] = True

        threading.Thread(target=load_game, args=(progress_callback,), daemon=True).start()

        loading_texts = ["Chargement", "Chargement.", "Chargement..", "Chargement..."]
        text_index = 0
        text_duration = 500
        last_text_change = pygame.time.get_ticks()

        while not game_finished[0]:
            screen.blit(loading_image, (0, 0))

            current_time = pygame.time.get_ticks()
            if current_time - last_text_change > text_duration:
                text_index = (text_index + 1) % len(loading_texts)
                last_text_change = current_time

            # Draw loading text
            shadow_surface = font.render(loading_texts[text_index], True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(largeur_ecran // 2 + 2, hauteur_ecran - 148))
            screen.blit(shadow_surface, shadow_rect)

            loading_text_surface = font.render(loading_texts[text_index], True, (250, 0, 0))
            text_rect = loading_text_surface.get_rect(center=(largeur_ecran // 2, hauteur_ecran - 150))
            screen.blit(loading_text_surface, text_rect)

            # **Progress Bar with Gradient**
            bar_x = largeur_ecran // 2 - int(largeur_ecran * 0.3)
            bar_y = hauteur_ecran - 100
            bar_width = int((largeur_ecran * 0.6) * (progress[-1] / 100))
            bar_height = 30

            draw_gradient_bar(screen, bar_x, bar_y, bar_width, bar_height, (31, 31, 31), (254, 31, 31))

            # **Border for Progress Bar**
            pygame.draw.rect(screen, (79, 35, 35), (bar_x, bar_y, largeur_ecran * 0.6, bar_height + 1), 3)

            pygame.display.flip()
            pygame.time.wait(100)

            # Process only the QUIT event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        screen.blit(loading_image, (0, 0))
        pygame.display.flip()
        pygame.time.wait(500)

        fade_out(screen, loading_image, duration=600)

        return

    def options_menu():
        fond_img = pygame.image.load("sources/data/image/fond.png")
        fond = pygame.transform.scale(fond_img, (largeur_ecran, hauteur_ecran))
        
        running = True
        while running:
            screen.blit(fond, (0, 0))
            draw_text("Paramètres", pygame.font.Font(None, 150), (255, 255, 255), largeur_ecran // 2 - 300, 150)
            music_slider_rect, music_key = draw_slider("Musique", audio_settings['music_volume'], largeur_ecran // 2 - 100, 350, "music_volume")
            effects_slider_rect, effects_key = draw_slider("Effets", audio_settings['effects_volume'], largeur_ecran // 2 - 100, 450, "effects_volume")
            return_button, _ = create_button("sources/data/image/RETOUR BOUTTON.png", 0.5, 0.85, 0.3, 0.2, main_menu)
            image = pygame.image.load("sources/data/image/touches.png")
            image = pygame.transform.scale(image, (439, 325))
            screen.blit(image, (largeur_ecran // 2 - 250, hauteur_ecran - 550))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if music_slider_rect.collidepoint(event.pos):
                        audio_settings[music_key] = min(max((event.pos[0] - (largeur_ecran // 2 - 100)) // 2, 0), 100)
                    elif effects_slider_rect.collidepoint(event.pos):
                        audio_settings[effects_key] = min(max((event.pos[0] - (largeur_ecran // 2 - 100)) // 2, 0), 100)
                    elif return_button.collidepoint(event.pos):
                        main_menu()
                        return

            # Draw custom cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(custom_cursor, (mouse_x, mouse_y))
            pygame.display.flip()

    def quitter():
        sys.exit()

    def credits_menu():
        fond_img = pygame.image.load("sources/data/image/fond.png")
        fond = pygame.transform.scale(fond_img, (largeur_ecran, hauteur_ecran))
        
        running = True
        while running:
            screen.blit(fond, (0, 0))
            draw_text("Crédits", pygame.font.Font(None, 150), (255, 255, 255), largeur_ecran // 2 - 150, 150)
            
            team = [
                "Stanislas : Développement de l'essentiel du jeu et création des effets sonores",
                "Paul : Développement du jeu et modélisateur 3D",
                "Sacha : Développeur et designer de l'interface",
                "Nael : Développement du système de quêtes, Design et direction artistique",
                "Riadh : Design, modélisation et intégration visuelle du monstre"
            ]

            for i, member in enumerate(team):
                draw_text(member, pygame.font.Font(None, 40), (255, 255, 255), largeur_ecran // 2 - 500, 400 + i * 50)
                
            return_button, _ = create_button("sources/data/image/RETOUR BOUTTON.png", 0.5, 0.9, 0.3, 0.2, main_menu)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and return_button.collidepoint(event.pos):
                    main_menu()
                    return

            # Draw custom cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(custom_cursor, (mouse_x, mouse_y))
            pygame.display.flip()

    def main_menu():
        fond_img = pygame.image.load("sources/data/image/bg.png")
        fond = pygame.transform.scale(fond_img, (largeur_ecran, hauteur_ecran))
        
        overlay_img = pygame.image.load("sources/data/image/bg-dark.png")
        overlay = pygame.transform.scale(overlay_img, (largeur_ecran, hauteur_ecran))
        
        mask_surface = pygame.Surface((1000, 1000), pygame.SRCALPHA)
        for i in range(350, 0, -1):
            alpha = int(255 * (1 - (i / 350)))
            pygame.draw.circle(mask_surface, (0, 0, 0, alpha), (350, 350), i)
        

        # play_music()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            screen.blit(fond, (0, 0))
            buttons = [
                create_button("sources/data/image/JOUER BOUTTON.png",0.25, 0.3, 0.3, 0.3, loading_screen),
                create_button("sources/data/image/PARAMETRES BOUTTON.png", 0.7, 0.4, 0.3, 0.3, options_menu),
                create_button("sources/data/image/CREDITS BOUTTON.png",  0.3, 0.7, 0.3, 0.3, credits_menu),
                create_button("sources/data/image/QUITTER BOUTTON.png", 0.7, 0.8, 0.3, 0.3, quitter)
            ]
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            overlay_surface = pygame.Surface((largeur_ecran, hauteur_ecran), pygame.SRCALPHA)
            overlay_surface.blit(overlay, (0, 0))
            
            overlay_surface.blit(mask_surface, (mouse_x - 350, mouse_y - 350), special_flags=pygame.BLEND_RGBA_SUB)
            
            screen.blit(overlay_surface, (0, 0))
            
            for button_rect, action in buttons:
                pass
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button_rect, action in buttons:
                        if button_rect.collidepoint(event.pos) and action:
                            action()
                            return

            # Draw custom cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(custom_cursor, (mouse_x, mouse_y))
            pygame.display.flip()

    main_menu()
