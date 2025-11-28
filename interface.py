#Projet : Nightfall
#Auteurs : Stanislas Gros de Beler, Paul Berenguer, Nael Arras, Sacha Philipps Herbert, Riadh Jouini
#Interface refaite - Design moderne et immersif

import pygame
import threading
import sys
import time
import math
import random
import os

# Initialisation de Pygame
pygame.init()
pygame.font.init()

# Paramètres globaux
audio_settings = {"music_volume": 50, "effects_volume": 50}
dragging_slider = None

# ═══════════════════════════════════════════════════════════════════════════════
#                              CLASSE PARTICULES
# ═══════════════════════════════════════════════════════════════════════════════

class Particle:
    """Classe pour les particules d'ambiance (brume, poussière, étincelles)"""
    def __init__(self, x, y, particle_type="fog"):
        self.x = x
        self.y = y
        self.type = particle_type
        
        if particle_type == "fog":
            self.size = random.randint(80, 200)
            self.alpha = random.randint(5, 25)
            self.speed_x = random.uniform(-0.3, 0.3)
            self.speed_y = random.uniform(-0.2, 0.1)
            self.color = (150, 150, 170)
            self.life = random.randint(200, 400)
        elif particle_type == "dust":
            self.size = random.randint(2, 5)
            self.alpha = random.randint(30, 80)
            self.speed_x = random.uniform(-0.5, 0.5)
            self.speed_y = random.uniform(-1, -0.3)
            self.color = (200, 180, 150)
            self.life = random.randint(100, 200)
        elif particle_type == "ember":
            self.size = random.randint(2, 6)
            self.alpha = random.randint(150, 255)
            self.speed_x = random.uniform(-1, 1)
            self.speed_y = random.uniform(-2, -0.5)
            self.color = (255, random.randint(80, 150), 0)
            self.life = random.randint(50, 150)
        elif particle_type == "blood":
            self.size = random.randint(3, 8)
            self.alpha = random.randint(100, 200)
            self.speed_x = random.uniform(-0.3, 0.3)
            self.speed_y = random.uniform(0.5, 2)
            self.color = (139, 0, 0)
            self.life = random.randint(80, 150)
            
        self.max_life = self.life
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        
        # Diminuer l'alpha avec le temps
        life_ratio = self.life / self.max_life
        self.current_alpha = int(self.alpha * life_ratio)
        
    def draw(self, surface):
        if self.life > 0 and self.current_alpha > 0:
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            
            if self.type == "fog":
                # Brume avec dégradé circulaire
                for i in range(self.size, 0, -2):
                    alpha = int((self.current_alpha * i) / self.size)
                    pygame.draw.circle(particle_surface, (*self.color, alpha), 
                                     (self.size, self.size), i)
            else:
                pygame.draw.circle(particle_surface, (*self.color, self.current_alpha), 
                                 (self.size, self.size), self.size)
            
            surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))
    
    def is_alive(self):
        return self.life > 0


class ParticleSystem:
    """Gestionnaire de particules"""
    def __init__(self, screen_width, screen_height):
        self.particles = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        
    def emit(self, x, y, particle_type="fog", count=1):
        for _ in range(count):
            self.particles.append(Particle(x, y, particle_type))
            
    def emit_random(self, particle_type="fog", count=1):
        for _ in range(count):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            self.particles.append(Particle(x, y, particle_type))
            
    def update(self):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
            
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


# ═══════════════════════════════════════════════════════════════════════════════
#                              CLASSE EFFETS VISUELS
# ═══════════════════════════════════════════════════════════════════════════════

class VisualEffects:
    """Effets visuels avancés pour l'interface"""
    
    @staticmethod
    def create_vignette(width, height, intensity=100):
        """Crée un effet vignette (coins sombres)"""
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for x in range(0, width, 4):
            for y in range(0, height, 4):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                alpha = int((dist / max_dist) * intensity)
                alpha = min(alpha, 255)
                pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, 4, 4))
        
        return vignette
    
    @staticmethod
    def create_scanlines(width, height, spacing=3, alpha=30):
        """Crée un effet de lignes de scan (style CRT)"""
        scanlines = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, spacing):
            pygame.draw.line(scanlines, (0, 0, 0, alpha), (0, y), (width, y))
        return scanlines
    
    @staticmethod
    def create_noise_overlay(width, height, intensity=15):
        """Crée un overlay de bruit"""
        noise = pygame.Surface((width, height), pygame.SRCALPHA)
        for _ in range(int(width * height * 0.01)):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            alpha = random.randint(5, intensity)
            noise.set_at((x, y), (255, 255, 255, alpha))
        return noise
    
    @staticmethod
    def draw_glowing_text(surface, text, font, x, y, main_color, glow_color, glow_size=3):
        """Dessine du texte avec effet de lueur"""
        # Dessiner le glow
        for offset in range(glow_size, 0, -1):
            alpha = int(50 / offset)
            glow_surface = font.render(text, True, glow_color)
            glow_surface.set_alpha(alpha)
            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    surface.blit(glow_surface, (x + dx, y + dy))
        
        # Dessiner le texte principal
        text_surface = font.render(text, True, main_color)
        surface.blit(text_surface, (x, y))
        
    @staticmethod
    def draw_blood_drip(surface, x, start_y, length, time_offset=0):
        """Dessine une coulure de sang animée"""
        drip_color = (139, 0, 0)
        wave = math.sin(time.time() * 2 + time_offset) * 2
        
        for i in range(length):
            y = start_y + i
            alpha = max(0, 255 - (i * 3))
            width = max(1, 4 - i // 20)
            
            drip_surface = pygame.Surface((width * 2, 1), pygame.SRCALPHA)
            pygame.draw.line(drip_surface, (*drip_color, alpha), (0, 0), (width, 0), 1)
            surface.blit(drip_surface, (x + wave, y))


# ═══════════════════════════════════════════════════════════════════════════════
#                              CLASSE BOUTON ANIMÉ
# ═══════════════════════════════════════════════════════════════════════════════

class AnimatedButton:
    """Bouton avec animations et effets"""
    def __init__(self, x, y, width, height, text, font, 
                 base_color=(40, 10, 10), hover_color=(80, 20, 20),
                 text_color=(200, 200, 200), border_color=(100, 30, 30)):
        self.rect = pygame.Rect(x - width//2, y - height//2, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        
        self.is_hovered = False
        self.hover_progress = 0
        self.click_animation = 0
        self.pulse_time = random.random() * math.pi * 2
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Animation de hover smooth
        if self.is_hovered:
            self.hover_progress = min(1, self.hover_progress + 0.1)
        else:
            self.hover_progress = max(0, self.hover_progress - 0.1)
            
        # Animation de clic
        if self.click_animation > 0:
            self.click_animation -= 0.1
            
        self.pulse_time += 0.05
        
    def draw(self, surface):
        # Calcul des couleurs interpolées
        current_color = self._lerp_color(self.base_color, self.hover_color, self.hover_progress)
        
        # Effet de pulsation subtile
        pulse = math.sin(self.pulse_time) * 0.1 + 0.9
        
        # Effet de clic (réduction de taille)
        scale = 1 - (self.click_animation * 0.05)
        
        # Rectangle avec effet de profondeur
        button_rect = self.rect.copy()
        if scale != 1:
            button_rect.width = int(button_rect.width * scale)
            button_rect.height = int(button_rect.height * scale)
            button_rect.center = self.rect.center
            
        # Ombre
        shadow_rect = button_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # Fond du bouton avec dégradé
        self._draw_gradient_rect(surface, button_rect, current_color, 
                                 self._darken_color(current_color, 0.5))
        
        # Bordure lumineuse
        border_glow = int(self.hover_progress * 50)
        border_color = tuple(min(255, c + border_glow) for c in self.border_color)
        pygame.draw.rect(surface, border_color, button_rect, 2, border_radius=8)
        
        # Effet de lueur interne au hover
        if self.hover_progress > 0:
            glow_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            glow_alpha = int(30 * self.hover_progress)
            pygame.draw.rect(glow_surface, (255, 100, 100, glow_alpha), 
                           glow_surface.get_rect(), border_radius=8)
            surface.blit(glow_surface, button_rect.topleft)
        
        # Texte
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        
        # Ombre du texte
        shadow_surface = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(shadow_surface, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text_surface, text_rect)
        
    def _draw_gradient_rect(self, surface, rect, color_top, color_bottom):
        """Dessine un rectangle avec dégradé vertical"""
        for i in range(rect.height):
            ratio = i / rect.height
            color = self._lerp_color(color_top, color_bottom, ratio)
            pygame.draw.line(surface, color, 
                           (rect.x, rect.y + i), 
                           (rect.x + rect.width, rect.y + i))
        pygame.draw.rect(surface, color_top, rect, border_radius=8)
        
    def _lerp_color(self, color1, color2, t):
        """Interpolation linéaire entre deux couleurs"""
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))
    
    def _darken_color(self, color, factor):
        """Assombrit une couleur"""
        return tuple(int(c * factor) for c in color)
    
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.click_animation = 1
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
#                              CLASSE SLIDER STYLISÉ
# ═══════════════════════════════════════════════════════════════════════════════

class StylizedSlider:
    """Slider avec design horrifique"""
    def __init__(self, x, y, width, label, value, setting_key):
        self.x = x
        self.y = y
        self.width = width
        self.height = 12
        self.label = label
        self.value = value
        self.setting_key = setting_key
        self.dragging = False
        self.hover = False
        
        self.knob_radius = 10
        self.track_rect = pygame.Rect(x, y, width, self.height)
        
    def update(self, mouse_pos, mouse_pressed):
        # Vérifier le hover
        knob_x = self.x + int((self.value / 100) * self.width)
        knob_rect = pygame.Rect(knob_x - self.knob_radius, 
                               self.y - self.knob_radius + self.height//2,
                               self.knob_radius * 2, self.knob_radius * 2)
        
        self.hover = self.track_rect.collidepoint(mouse_pos) or knob_rect.collidepoint(mouse_pos)
        
        # Gestion du drag
        if mouse_pressed[0] and self.hover:
            self.dragging = True
            
        if not mouse_pressed[0]:
            self.dragging = False
            
        if self.dragging:
            relative_x = mouse_pos[0] - self.x
            self.value = max(0, min(100, int((relative_x / self.width) * 100)))
            audio_settings[self.setting_key] = self.value
            
    def draw(self, surface, font):
        # Label avec effet
        label_text = f"{self.label}: {self.value}%"
        VisualEffects.draw_glowing_text(surface, label_text, font, 
                                        self.x, self.y - 35,
                                        (200, 200, 200), (100, 30, 30), 2)
        
        # Track background (rainure sombre)
        track_bg = pygame.Rect(self.x - 2, self.y - 2, self.width + 4, self.height + 4)
        pygame.draw.rect(surface, (20, 5, 5), track_bg, border_radius=6)
        
        # Track principal
        pygame.draw.rect(surface, (40, 15, 15), self.track_rect, border_radius=5)
        
        # Partie remplie avec dégradé rouge
        filled_width = int((self.value / 100) * self.width)
        if filled_width > 0:
            filled_rect = pygame.Rect(self.x, self.y, filled_width, self.height)
            # Dégradé rouge sang
            for i in range(filled_width):
                ratio = i / max(1, self.width)
                r = int(80 + ratio * 100)
                g = int(10 + ratio * 20)
                b = int(10 + ratio * 20)
                pygame.draw.line(surface, (r, g, b),
                               (self.x + i, self.y),
                               (self.x + i, self.y + self.height))
        
        # Bordure
        border_color = (150, 50, 50) if self.hover else (80, 30, 30)
        pygame.draw.rect(surface, border_color, self.track_rect, 2, border_radius=5)
        
        # Knob (bouton coulissant)
        knob_x = self.x + int((self.value / 100) * self.width)
        knob_y = self.y + self.height // 2
        
        # Ombre du knob
        pygame.draw.circle(surface, (0, 0, 0), (knob_x + 2, knob_y + 2), self.knob_radius)
        
        # Knob principal avec dégradé
        knob_color = (180, 50, 50) if self.hover or self.dragging else (120, 40, 40)
        pygame.draw.circle(surface, knob_color, (knob_x, knob_y), self.knob_radius)
        pygame.draw.circle(surface, (200, 80, 80), (knob_x, knob_y), self.knob_radius - 3)
        
        # Highlight
        if self.hover or self.dragging:
            glow_surface = pygame.Surface((self.knob_radius * 4, self.knob_radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 100, 100, 50), 
                             (self.knob_radius * 2, self.knob_radius * 2), self.knob_radius * 2)
            surface.blit(glow_surface, (knob_x - self.knob_radius * 2, knob_y - self.knob_radius * 2))


# ═══════════════════════════════════════════════════════════════════════════════
#                              INTERFACE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

def interface():
    global audio_settings, dragging_slider
    
    # Paramètres de la fenêtre
    info = pygame.display.Info()
    largeur_ecran, hauteur_ecran = info.current_w, info.current_h
    screen = pygame.display.set_mode((largeur_ecran, hauteur_ecran), pygame.RESIZABLE | pygame.NOFRAME)
    pygame.display.set_caption("NIGHTFALL")

    # Initialisation du mixeur audio
    pygame.mixer.init()

    # Chargement du curseur personnalisé
    try:
        custom_cursor = pygame.image.load("sources/data/image/lampe1.png")
        custom_cursor = pygame.transform.scale(custom_cursor, (80, 80))
    except:
        # Créer un curseur de secours si l'image n'existe pas
        custom_cursor = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(custom_cursor, (255, 200, 100, 200), (20, 20), 15)
        pygame.draw.circle(custom_cursor, (255, 255, 200, 255), (20, 20), 8)

    pygame.mouse.set_visible(False)

    # ═══════════════════════════════════════════════════════════════════════════
    #                              CHARGEMENT RESSOURCES
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Polices
    try:
        title_font = pygame.font.Font("sources/data/Fonts/whoAsksSatan.ttf", 120)
        subtitle_font = pygame.font.Font("sources/data/Fonts/whoAsksSatan.ttf", 60)
        button_font = pygame.font.Font("sources/data/Fonts/whoAsksSatan.ttf", 45)
        text_font = pygame.font.Font("sources/data/Fonts/whoAsksSatan.ttf", 35)
        small_font = pygame.font.Font("sources/data/Fonts/whoAsksSatan.ttf", 28)
    except:
        title_font = pygame.font.Font(None, 120)
        subtitle_font = pygame.font.Font(None, 60)
        button_font = pygame.font.Font(None, 50)
        text_font = pygame.font.Font(None, 40)
        small_font = pygame.font.Font(None, 30)

    # Chargement des images de fond
    try:
        bg_image = pygame.image.load("sources/data/image/bg.png")
        bg_image = pygame.transform.scale(bg_image, (largeur_ecran, hauteur_ecran))
    except:
        bg_image = pygame.Surface((largeur_ecran, hauteur_ecran))
        bg_image.fill((10, 5, 15))
        
    try:
        bg_dark = pygame.image.load("sources/data/image/bg-dark.png")
        bg_dark = pygame.transform.scale(bg_dark, (largeur_ecran, hauteur_ecran))
    except:
        bg_dark = pygame.Surface((largeur_ecran, hauteur_ecran), pygame.SRCALPHA)
        bg_dark.fill((0, 0, 0, 200))
        
    try:
        fond_img = pygame.image.load("sources/data/image/fond.png")
        fond_img = pygame.transform.scale(fond_img, (largeur_ecran, hauteur_ecran))
    except:
        fond_img = pygame.Surface((largeur_ecran, hauteur_ecran))
        fond_img.fill((15, 5, 20))

    # ═══════════════════════════════════════════════════════════════════════════
    #                              SYSTÈMES D'EFFETS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Système de particules
    particle_system = ParticleSystem(largeur_ecran, hauteur_ecran)
    
    # Effets visuels précalculés
    vignette = VisualEffects.create_vignette(largeur_ecran, hauteur_ecran, 150)
    scanlines = VisualEffects.create_scanlines(largeur_ecran, hauteur_ecran, 3, 20)
    
    # Masque de lampe torche amélioré
    mask_size = 800
    mask_surface = pygame.Surface((mask_size, mask_size), pygame.SRCALPHA)
    for i in range(mask_size // 2, 0, -1):
        alpha = int(255 * (1 - (i / (mask_size // 2))) ** 1.5)
        pygame.draw.circle(mask_surface, (0, 0, 0, alpha), (mask_size // 2, mask_size // 2), i)

    # ═══════════════════════════════════════════════════════════════════════════
    #                              FONCTIONS UTILITAIRES
    # ═══════════════════════════════════════════════════════════════════════════

    def get_audio_settings():
        return audio_settings

    def play_music():
        if pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.load("sources/data/Son/Son ambiance/Son_gresillement.mp3")
            pygame.mixer.music.set_volume(audio_settings["music_volume"] / 100)
            pygame.mixer.music.play(-1)
        except:
            pass

    def stop_music():
        pygame.mixer.music.stop()

    def draw_animated_title(surface, text, font, x, y, time_val):
        """Dessine le titre avec effet de tremblement et lueur"""
        # Effet de tremblement subtil
        shake_x = math.sin(time_val * 3) * 2
        shake_y = math.cos(time_val * 2.5) * 1
        
        # Lueur rouge derrière
        for i in range(5, 0, -1):
            glow_alpha = int(30 / i)
            glow_surface = font.render(text, True, (150, 0, 0))
            glow_surface.set_alpha(glow_alpha)
            surface.blit(glow_surface, (x - i + shake_x, y - i + shake_y))
            surface.blit(glow_surface, (x + i + shake_x, y + i + shake_y))
        
        # Texte principal
        text_surface = font.render(text, True, (200, 30, 30))
        surface.blit(text_surface, (x + shake_x, y + shake_y))
        
        # Highlight
        highlight = font.render(text, True, (255, 100, 100))
        highlight.set_alpha(int(50 + math.sin(time_val * 4) * 30))
        surface.blit(highlight, (x + shake_x, y + shake_y - 2))

    # ═══════════════════════════════════════════════════════════════════════════
    #                              VARIABLES D'ÉTAT
    # ═══════════════════════════════════════════════════════════════════════════
    
    game_ready = False
    start_time = time.time()

    def load_game(progress_callback):
        nonlocal game_ready
        print("Chargement du jeu en arrière-plan...")
        steps = 10
        for i in range(steps):
            time.sleep(0.5)
            progress_callback((i + 1) / steps * 100)
        game_ready = True
        print("Le jeu est prêt à être lancé !")

    # ═══════════════════════════════════════════════════════════════════════════
    #                              TRANSITIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def fade_in(surface, image, duration=1000):
        clock = pygame.time.Clock()
        alpha = 0
        increment = 255 / (duration / 16)
        while alpha < 255:
            alpha += increment
            temp_image = image.copy()
            temp_image.set_alpha(int(min(255, alpha)))
            surface.fill((0, 0, 0))
            surface.blit(temp_image, (0, 0))
            pygame.display.flip()
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def fade_out(surface, image, duration=1000):
        clock = pygame.time.Clock()
        alpha = 255
        decrement = 255 / (duration / 16)
        while alpha > 0:
            alpha -= decrement
            temp_image = image.copy()
            temp_image.set_alpha(int(max(0, alpha)))
            surface.fill((0, 0, 0))
            surface.blit(temp_image, (0, 0))
            pygame.display.flip()
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
        surface.fill((0, 0, 0))
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

    # ═══════════════════════════════════════════════════════════════════════════
    #                              ÉCRAN DE CHARGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    def loading_screen():
        nonlocal game_ready
        
        # Créer un fond de chargement
        try:
            loading_bg = pygame.image.load("sources/data/image/chargement.png")
            loading_bg = pygame.transform.scale(loading_bg, (largeur_ecran, hauteur_ecran))
        except:
            loading_bg = pygame.Surface((largeur_ecran, hauteur_ecran))
            loading_bg.fill((5, 0, 10))
        
        fade_in(screen, loading_bg, duration=600)
        
        progress = [0]
        game_finished = [False]
        loading_particles = ParticleSystem(largeur_ecran, hauteur_ecran)
        
        def progress_callback(p):
            progress.append(p)
            if p >= 100:
                game_finished[0] = True
        
        threading.Thread(target=load_game, args=(progress_callback,), daemon=True).start()
        
        loading_texts = ["CHARGEMENT", "CHARGEMENT.", "CHARGEMENT..", "CHARGEMENT..."]
        text_index = 0
        text_duration = 400
        last_text_change = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        
        while not game_finished[0]:
            current_time = pygame.time.get_ticks()
            dt = clock.tick(60) / 1000
            
            # Mise à jour du texte animé
            if current_time - last_text_change > text_duration:
                text_index = (text_index + 1) % len(loading_texts)
                last_text_change = current_time
            
            # Émettre des particules
            if random.random() < 0.3:
                loading_particles.emit_random("ember", 1)
            if random.random() < 0.1:
                loading_particles.emit_random("dust", 1)
            
            loading_particles.update()
            
            # Dessin
            screen.blit(loading_bg, (0, 0))
            loading_particles.draw(screen)
            
            # Titre "NIGHTFALL" animé
            title_y = hauteur_ecran // 4
            title_text = title_font.render("NIGHTFALL", True, (150, 20, 20))
            title_rect = title_text.get_rect(center=(largeur_ecran // 2, title_y))
            
            # Lueur du titre
            glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (100, 0, 0, 30), glow_surface.get_rect(), border_radius=20)
            screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
            screen.blit(title_text, title_rect)
            
            # Texte de chargement
            loading_text = subtitle_font.render(loading_texts[text_index], True, (180, 180, 180))
            text_rect = loading_text.get_rect(center=(largeur_ecran // 2, hauteur_ecran - 180))
            screen.blit(loading_text, text_rect)
            
            # Barre de progression stylisée
            bar_width = int(largeur_ecran * 0.5)
            bar_height = 20
            bar_x = (largeur_ecran - bar_width) // 2
            bar_y = hauteur_ecran - 120
            
            # Fond de la barre
            pygame.draw.rect(screen, (20, 5, 5), (bar_x - 3, bar_y - 3, bar_width + 6, bar_height + 6), border_radius=10)
            pygame.draw.rect(screen, (40, 10, 10), (bar_x, bar_y, bar_width, bar_height), border_radius=8)
            
            # Progression avec dégradé
            fill_width = int(bar_width * (progress[-1] / 100))
            if fill_width > 0:
                for i in range(fill_width):
                    ratio = i / bar_width
                    r = int(80 + ratio * 120)
                    g = int(10 + ratio * 20)
                    b = 10
                    pygame.draw.line(screen, (r, g, b), (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height))
            
            # Bordure de la barre
            pygame.draw.rect(screen, (100, 30, 30), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=8)
            
            # Pourcentage
            percent_text = small_font.render(f"{int(progress[-1])}%", True, (200, 200, 200))
            percent_rect = percent_text.get_rect(center=(largeur_ecran // 2, bar_y + bar_height + 30))
            screen.blit(percent_text, percent_rect)
            
            # Effets
            screen.blit(vignette, (0, 0))
            screen.blit(scanlines, (0, 0))
            
            # Curseur
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(custom_cursor, (mouse_x, mouse_y))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
        pygame.time.wait(500)
        fade_out(screen, loading_bg, duration=600)

    # ═══════════════════════════════════════════════════════════════════════════
    #                              MENU OPTIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def options_menu():
        # Sliders
        music_slider = StylizedSlider(largeur_ecran // 2 - 150, hauteur_ecran // 2 - 100, 
                                      300, "MUSIQUE", audio_settings['music_volume'], "music_volume")
        effects_slider = StylizedSlider(largeur_ecran // 2 - 150, hauteur_ecran // 2, 
                                        300, "EFFETS", audio_settings['effects_volume'], "effects_volume")
        
        # Bouton retour
        return_button = AnimatedButton(largeur_ecran // 2, hauteur_ecran - 150, 
                                       300, 70, "RETOUR", button_font)
        
        options_particles = ParticleSystem(largeur_ecran, hauteur_ecran)
        clock = pygame.time.Clock()
        running = True
        
        # Charger l'image des touches si disponible
        try:
            touches_img = pygame.image.load("sources/data/image/touches.png")
            touches_img = pygame.transform.scale(touches_img, (350, 260))
        except:
            touches_img = None
        
        while running:
            dt = clock.tick(60) / 1000
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            
            # Particules d'ambiance
            if random.random() < 0.05:
                options_particles.emit_random("fog", 1)
            options_particles.update()
            
            # Dessin
            screen.blit(fond_img, (0, 0))
            options_particles.draw(screen)
            
            # Titre
            title_text = title_font.render("PARAMÈTRES", True, (180, 30, 30))
            title_rect = title_text.get_rect(center=(largeur_ecran // 2, 120))
            
            # Ombre du titre
            shadow_text = title_font.render("PARAMÈTRES", True, (0, 0, 0))
            screen.blit(shadow_text, (title_rect.x + 3, title_rect.y + 3))
            screen.blit(title_text, title_rect)
            
            # Ligne décorative sous le titre
            line_width = 400
            pygame.draw.line(screen, (100, 30, 30), 
                           (largeur_ecran // 2 - line_width // 2, 180),
                           (largeur_ecran // 2 + line_width // 2, 180), 2)
            
            # Sliders
            music_slider.update(mouse_pos, mouse_pressed)
            effects_slider.update(mouse_pos, mouse_pressed)
            music_slider.draw(screen, text_font)
            effects_slider.draw(screen, text_font)
            
            # Appliquer le volume
            pygame.mixer.music.set_volume(audio_settings["music_volume"] / 100)
            
            # Image des contrôles
            if touches_img:
                controls_x = largeur_ecran // 2 - touches_img.get_width() // 2
                controls_y = hauteur_ecran // 2 + 100
                
                # Cadre autour de l'image
                frame_rect = pygame.Rect(controls_x - 10, controls_y - 10, 
                                        touches_img.get_width() + 20, touches_img.get_height() + 20)
                pygame.draw.rect(screen, (40, 15, 15), frame_rect, border_radius=10)
                pygame.draw.rect(screen, (80, 30, 30), frame_rect, 2, border_radius=10)
                
                screen.blit(touches_img, (controls_x, controls_y))
            
            # Bouton retour
            return_button.update(mouse_pos)
            return_button.draw(screen)
            
            # Effets
            screen.blit(vignette, (0, 0))
            screen.blit(scanlines, (0, 0))
            
            # Curseur
            screen.blit(custom_cursor, (mouse_pos[0], mouse_pos[1]))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if return_button.is_clicked(event):
                    return

    # ═══════════════════════════════════════════════════════════════════════════
    #                              MENU CRÉDITS
    # ═══════════════════════════════════════════════════════════════════════════

    def credits_menu():
        return_button = AnimatedButton(largeur_ecran // 2, hauteur_ecran - 100, 
                                       300, 70, "RETOUR", button_font)
        
        team = [
            ("Stanislas", "Développement principal & Effets sonores"),
            ("Paul", "Développement & Modélisation 3D"),
            ("Sacha", "Design & Interface"),
            ("Nael", "Système de quêtes & Direction artistique"),
            ("Riadh", "Design & Modélisation du monstre")
        ]
        
        credits_particles = ParticleSystem(largeur_ecran, hauteur_ecran)
        clock = pygame.time.Clock()
        running = True
        scroll_y = 0
        
        while running:
            dt = clock.tick(60) / 1000
            mouse_pos = pygame.mouse.get_pos()
            
            # Particules
            if random.random() < 0.03:
                credits_particles.emit_random("fog", 1)
            if random.random() < 0.02:
                credits_particles.emit(random.randint(0, largeur_ecran), 0, "blood", 1)
            credits_particles.update()
            
            # Dessin
            screen.blit(fond_img, (0, 0))
            credits_particles.draw(screen)
            
            # Titre
            title_text = title_font.render("CRÉDITS", True, (180, 30, 30))
            title_rect = title_text.get_rect(center=(largeur_ecran // 2, 100))
            shadow_text = title_font.render("CRÉDITS", True, (0, 0, 0))
            screen.blit(shadow_text, (title_rect.x + 3, title_rect.y + 3))
            screen.blit(title_text, title_rect)
            
            # Ligne décorative
            pygame.draw.line(screen, (100, 30, 30), 
                           (largeur_ecran // 2 - 200, 160),
                           (largeur_ecran // 2 + 200, 160), 2)
            
            # Sous-titre
            subtitle = small_font.render("L'ÉQUIPE DE DÉVELOPPEMENT", True, (150, 150, 150))
            subtitle_rect = subtitle.get_rect(center=(largeur_ecran // 2, 200))
            screen.blit(subtitle, subtitle_rect)
            
            # Membres de l'équipe
            start_y = 280
            for i, (name, role) in enumerate(team):
                y_pos = start_y + i * 100
                
                # Cadre
                card_width, card_height = 600, 80
                card_x = largeur_ecran // 2 - card_width // 2
                card_rect = pygame.Rect(card_x, y_pos, card_width, card_height)
                
                # Fond du cadre avec transparence
                card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                pygame.draw.rect(card_surface, (30, 10, 10, 200), card_surface.get_rect(), border_radius=10)
                screen.blit(card_surface, (card_x, y_pos))
                
                # Bordure
                pygame.draw.rect(screen, (80, 30, 30), card_rect, 2, border_radius=10)
                
                # Nom
                name_text = text_font.render(name.upper(), True, (200, 60, 60))
                name_rect = name_text.get_rect(midleft=(card_x + 30, y_pos + 25))
                screen.blit(name_text, name_rect)
                
                # Rôle
                role_text = small_font.render(role, True, (150, 150, 150))
                role_rect = role_text.get_rect(midleft=(card_x + 30, y_pos + 55))
                screen.blit(role_text, role_rect)
            
            # Bouton retour
            return_button.update(mouse_pos)
            return_button.draw(screen)
            
            # Effets
            screen.blit(vignette, (0, 0))
            screen.blit(scanlines, (0, 0))
            
            # Curseur
            screen.blit(custom_cursor, (mouse_pos[0], mouse_pos[1]))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if return_button.is_clicked(event):
                    return

    # ═══════════════════════════════════════════════════════════════════════════
    #                              MENU PRINCIPAL
    # ═══════════════════════════════════════════════════════════════════════════

    def main_menu():
        nonlocal start_time
        
        # Boutons du menu
        buttons = [
            AnimatedButton(largeur_ecran // 4, hauteur_ecran // 2 - 80, 
                          350, 80, "JOUER", button_font,
                          base_color=(50, 15, 15), hover_color=(100, 30, 30)),
            AnimatedButton(largeur_ecran // 4, hauteur_ecran // 2 + 40, 
                          350, 80, "PARAMÈTRES", button_font,
                          base_color=(40, 12, 12), hover_color=(90, 25, 25)),
            AnimatedButton(largeur_ecran // 4, hauteur_ecran // 2 + 160, 
                          350, 80, "CRÉDITS", button_font,
                          base_color=(35, 10, 10), hover_color=(80, 22, 22)),
            AnimatedButton(largeur_ecran // 4, hauteur_ecran // 2 + 280, 
                          350, 80, "QUITTER", button_font,
                          base_color=(30, 8, 8), hover_color=(70, 20, 20))
        ]
        
        actions = [loading_screen, options_menu, credits_menu, sys.exit]
        
        menu_particles = ParticleSystem(largeur_ecran, hauteur_ecran)
        clock = pygame.time.Clock()
        
        # Initialiser avec quelques particules de brume
        for _ in range(20):
            menu_particles.emit_random("fog", 1)
        
        # play_music()
        running = True
        
        while running:
            current_time = time.time() - start_time
            dt = clock.tick(60) / 1000
            mouse_pos = pygame.mouse.get_pos()
            
            # Émettre des particules
            if random.random() < 0.1:
                menu_particles.emit_random("fog", 1)
            if random.random() < 0.02:
                menu_particles.emit_random("dust", 1)
            
            menu_particles.update()
            
            # Dessin du fond
            screen.blit(bg_image, (0, 0))
            
            # Overlay sombre avec effet de lampe torche
            overlay_surface = pygame.Surface((largeur_ecran, hauteur_ecran), pygame.SRCALPHA)
            overlay_surface.blit(bg_dark, (0, 0))
            
            # Effet lampe torche (révèle le fond sous le curseur)
            mask_x = mouse_pos[0] - mask_size // 2
            mask_y = mouse_pos[1] - mask_size // 2
            overlay_surface.blit(mask_surface, (mask_x, mask_y), special_flags=pygame.BLEND_RGBA_SUB)
            
            screen.blit(overlay_surface, (0, 0))
            
            # Particules
            menu_particles.draw(screen)
            
            # Titre "NIGHTFALL" avec effets
            title_x = largeur_ecran * 3 // 4
            title_y = hauteur_ecran // 4
            
            draw_animated_title(screen, "NIGHTFALL", title_font, 
                              title_x - title_font.size("NIGHTFALL")[0] // 2, 
                              title_y, current_time)
            
            # Sous-titre
            subtitle_text = "Survivez à la nuit..."
            subtitle_surface = small_font.render(subtitle_text, True, (120, 120, 120))
            subtitle_alpha = int(150 + math.sin(current_time * 2) * 50)
            subtitle_surface.set_alpha(subtitle_alpha)
            subtitle_rect = subtitle_surface.get_rect(center=(title_x, title_y + 100))
            screen.blit(subtitle_surface, subtitle_rect)
            
            # Mise à jour et dessin des boutons
            for button in buttons:
                button.update(mouse_pos)
                button.draw(screen)
            
            # Indicateurs décoratifs (coins)
            corner_size = 30
            corner_color = (80, 20, 20)
            # Coin supérieur gauche
            pygame.draw.line(screen, corner_color, (20, 20), (20, 20 + corner_size), 2)
            pygame.draw.line(screen, corner_color, (20, 20), (20 + corner_size, 20), 2)
            # Coin supérieur droit
            pygame.draw.line(screen, corner_color, (largeur_ecran - 20, 20), (largeur_ecran - 20, 20 + corner_size), 2)
            pygame.draw.line(screen, corner_color, (largeur_ecran - 20, 20), (largeur_ecran - 20 - corner_size, 20), 2)
            # Coin inférieur gauche
            pygame.draw.line(screen, corner_color, (20, hauteur_ecran - 20), (20, hauteur_ecran - 20 - corner_size), 2)
            pygame.draw.line(screen, corner_color, (20, hauteur_ecran - 20), (20 + corner_size, hauteur_ecran - 20), 2)
            # Coin inférieur droit
            pygame.draw.line(screen, corner_color, (largeur_ecran - 20, hauteur_ecran - 20), (largeur_ecran - 20, hauteur_ecran - 20 - corner_size), 2)
            pygame.draw.line(screen, corner_color, (largeur_ecran - 20, hauteur_ecran - 20), (largeur_ecran - 20 - corner_size, hauteur_ecran - 20), 2)
            
            # Version
            version_text = small_font.render("v1.0", True, (60, 60, 60))
            screen.blit(version_text, (largeur_ecran - 80, hauteur_ecran - 40))
            
            # Effets finaux
            screen.blit(vignette, (0, 0))
            screen.blit(scanlines, (0, 0))
            
            # Curseur personnalisé
            screen.blit(custom_cursor, (mouse_pos[0], mouse_pos[1]))
            
            pygame.display.flip()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                
                for i, button in enumerate(buttons):
                    if button.is_clicked(event):
                        if i == 3:  # Quitter
                            pygame.quit()
                            sys.exit()
                        else:
                            actions[i]()
                            if i == 0:  # Jouer - sortir du menu
                                return

    # Lancer le menu principal
    main_menu()
