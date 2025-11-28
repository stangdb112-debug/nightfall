#Projet : Nightfall
#Auteurs : Stanislas Gros de Beler, Paul Berenguer, Nael Arras, Sacha Philipps Herbert, Riadh Jouini

import pygame


def launch_main():
    pygame.quit()
def run_synopsis():
    pygame.init()
    screen = pygame.display.set_mode((0, 0))
    pygame.display.set_caption("Synopsis")
    clock = pygame.time.Clock()
    
    font = pygame.font.Font(None, 60)
    text_lines = [
        "Nightfall est un jeu d'horreur à la première personne.",
        "Vous incarnez un enquêteur à la recherche de disparus en forêt.",
        "",
        "Votre enquête vous mène à une maison mystérieuse,",
        "qui cache une cave remplie de pièges mortels.",
        "",
        "Une présence inquiétante vous poursuit sans relâche.",
        "",
        "Chaque pas vous rapproche de la vérité,",
        "mais aussi du danger imminent.",
        "",
        "Votre courage sera mis à l'épreuve,",
        "et seul votre instinct pourra vous sauver.",
        "",
        "Survivez à la nuit, échappez à l'entité,",
        "et découvrez les sombres secrets de Nightfall."
    ]
    
    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in text_lines]
    text_positions = [(950 - surface.get_width() // 2, 600 + i * 50) for i, surface in enumerate(text_surfaces)]
    
    running = True
    while running:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False
                launch_main()
                return
        
        for i, pos in enumerate(text_positions):
            text_positions[i] = (pos[0], pos[1] - 1)  # Défilement vers le haut
            screen.blit(text_surfaces[i], text_positions[i])
        
        if text_positions[-1][1] < -50:  # Si le dernier texte sort de l'écran
            running = False
            launch_main()
            return
        
        pygame.display.flip()
        clock.tick(60)


def run_fin_victoire():
    pygame.init()
    screen = pygame.display.set_mode((0, 0))
    pygame.display.set_caption("Synopsis")
    clock = pygame.time.Clock()
    
    font = pygame.font.Font(None, 60)
    text_lines = [
        "Félicitations ! Vous avez réussi à vous échapper du donjon.",
        "",
        "Votre courage et votre détermination ont triomphé.",
        "",
        "Merci d'avoir joué à notre jeu.",
        "",
        "À bientôt pour de nouvelles aventures !"
    ]
    
    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in text_lines]
    text_positions = [(950 - surface.get_width() // 2, 600 + i * 50) for i, surface in enumerate(text_surfaces)]
    
    running = True
    while running:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False
                launch_main()
                return
        
        for i, pos in enumerate(text_positions):
            text_positions[i] = (pos[0], pos[1] - 1)  # Défilement vers le haut
            screen.blit(text_surfaces[i], text_positions[i])
        
        if text_positions[-1][1] < -50:  # Si le dernier texte sort de l'écran
            running = False
            launch_main()
            return
        
        pygame.display.flip()
        clock.tick(60)
def run_croix_detruite():
    pygame.init()
    screen = pygame.display.set_mode((0, 0))
    pygame.display.set_caption("Synopsis")
    clock = pygame.time.Clock()
    
    font = pygame.font.Font(None, 60)
    text_lines = [
        "Vous avez perdu...",
        "",
        "Sans la croix, le monstre a pu dévorer votre esprit et votre âme,",
        "",
        "vous envoyant au paradis.",
        "",
        "Mais vous avez continué jusqu'à la fin.",
        "",
        "retentez votre chance pour vaincre le monstre.",
        "",
        "bonne chance !"
    ]
    
    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in text_lines]
    text_positions = [(950 - surface.get_width() // 2, 600 + i * 50) for i, surface in enumerate(text_surfaces)]
    
    running = True
    while running:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False
                launch_main()
                return
        
        for i, pos in enumerate(text_positions):
            text_positions[i] = (pos[0], pos[1] - 1)  # Défilement vers le haut
            screen.blit(text_surfaces[i], text_positions[i])
        
        if text_positions[-1][1] < -50:  # Si le dernier texte sort de l'écran
            running = False
            launch_main()
            return
        
        pygame.display.flip()
        clock.tick(60)