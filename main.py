#Projet : Nightfall
#Auteurs : Stanislas Gros de Beler, Paul Berenguer, Nael Arras, Sacha Philipps Herbert, Riadh Jouini

import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.lights import DirectionalLight, AmbientLight
from ursina.shaders import basic_lighting_shader,unlit_shader
from environement import setup_environnement_foret
from environement import charger_donjon
import time
from ursina import window
from synopsis import run_synopsis, run_fin_victoire,run_croix_detruite
from interface import interface


def crouch(personnage:any, target_height:int):
    '''hyp: La fonction prend en entrée les informations du joueur, la hauteur voulue du personnage. Elle renvoie un mouvement fluide de la caméra sur l'axe y de la hauteur initiale à la hauteur voulue'''
    personnage.height = lerp(personnage.height, target_height, time.dt * 5)
    personnage.camera_pivot.y = personnage.height
    return personnage.camera_pivot.y

def accélération(perso:any, vitesse_visée:int):
    '''hyp: La fonction prend en entrée les informations du 'player' et la vitesse voulue. Elle renvoie une transition fluide entre la vitesse initiale et la vitesse voulue'''
    perso.speed = lerp(perso.speed, vitesse_visée, time.dt * 11)
    return perso.speed
interface()
run_synopsis()
#lancement de Ursina
app = Ursina()

window.exit_button.visible = False
window.fps_counter.enabled = False
window.fullscreen = True 





class Quete:
    def __init__(self, nom, description, objectif, completed=False):
        """hyp : La fonction renvoie le nom de la quête, se description, la condition de complétion et l'avancement de la quête, initialement False"""
        assert type(nom)==str, 'Le nom doit être une chaîne de caractères.'
        assert type(description)==str, 'La description doit être une chaîne de caractères'
        self.nom = nom
        self.description = description
        self.objectif = objectif  # Condition pour compléter la quête
        self.completed = completed

    def verifier_completion(self):
        """hyp : Vérifie si l'objectif est atteint."""
        return self.objectif()

class QueteManager:
    def __init__(self):
        """hyp : renvoie la liste des quêtes disponibles, initialement vide, indique si la quête est actuellement suivie, initialement sur None, compte les quêtes terminées, initialement à 0 et affiche l'image de la quête."""
        self.quetes = []
        self.quete_active = None
        self.compteur = 0

        # Image fixe "Quête"
        self.interface_titre = Entity(
            parent=camera.ui,
            model='quad',
            texture='data/image/quete.png',
            scale=(0.2, 0.2),  # Taille de l'image
            position=(0.7, 0.4)  # En haut à droite
        )

        # Image de la quête active (changeable)
        self.interface_quete = Entity(
            parent=camera.ui,
            model='quad',
            texture=None,  # Vide au départ
            scale=(0.4, 0.3),
            position=(0.7, 0.295),  # Juste en dessous de l'image "Quête"
            visible=False  # Caché au début
        )

    def ajouter_quete(self, quete):
        """hyp : la fonction renvoie une liste de toutes les quêtes, et une quête devient la première quête ajoutée si aucune autre n'est active"""
        self.quetes.append(quete)
        if not self.quete_active:
            self.quete_active = quete  # Active la première quête
            self.afficher_quete_active()

    def verifier_quetes(self):
        """hyp : la fonction indique si la quête activée est terminée. Si oui, elle renvoie True et passe à la suivante"""
        if self.quete_active and not self.quete_active.completed:
            if self.quete_active.verifier_completion():
                print(f" Quête complétée : {self.quete_active.nom}")
                self.quete_active.completed = True
                self.passer_a_quete_suivante()
    def passer_a_quete_suivante(self):
        """Passe à la quête suivante si disponible, sinon désactive l'affichage des quêtes."""
        quetes_restantes = [q for q in self.quetes if not q.completed]
        print(f" Quêtes restantes: {[q.nom for q in quetes_restantes]}")  # Debugging

        if self.compteur >= len(quetes_restantes):  # Vérifier que l'index ne dépasse pas
            print(" Toutes les quêtes sont terminées")
            self.interface_quete.visible = False  # Cacher l'affichage des quêtes
            self.quete_active = None  # Désactiver la quête active
            return  

    # Assigne la nouvelle quête et l'affiche
        self.quete_active = quetes_restantes[self.compteur]
        print(f" Nouvelle quête active : {self.quete_active.nom}")  # Debugging
        self.afficher_quete_active()

        self.compteur += 1  # Incrémente le compteur SEULEMENT après l'affectation
    
    def afficher_quete_active(self):
        """hyp : la fonction affiche l'image de la quête si celle-ci est active à l'aide du chemin de l'image associée."""
        if self.quete_active:
            # Charger l'image associée à la quête (doit être dans data/image/)
            image_path = f"data/image/{self.quete_active.nom.replace(' ', '_')}.png"
            self.interface_quete.texture = image_path
            self.interface_quete.visible = True  # Afficher l'image

# 🔹Gestionnaire de quêtes
quete_manager = QueteManager()

#  Ajout de quêtes avec leurs images
def objectif_lampe_torche():
    return "Lampe_torche_inventaire" in inventory  # Vérifie si l'objet est dans l'inventaire

def objectif_trouver_maison():
    global etat_jeu
    return etat_jeu=='maison_interior'

def objectif_trouver_3objets():
    return 'crane' in inventory and 'os' in inventory and 'bougie' in inventory

def objectif_trouver_portail():
    global etat_jeu
    return etat_jeu=='donjon'
victoire=False
def objectif_final():
    return victoire


quete_lampe = Quete("retrouver la lampe torche", "Récupérez la lampe torche quelque part dans la forêt.", objectif_lampe_torche)
quete_manager.ajouter_quete(quete_lampe)

quete_maison= Quete("trouver la maison", "trouver la maison.", objectif_trouver_maison)
quete_manager.ajouter_quete(quete_maison)

quete_objets1= Quete("trouver_3_objets", "trouver les objets.", objectif_trouver_3objets)
quete_manager.ajouter_quete(quete_objets1)

quete_objets2= Quete("trouver_3_objets", "trouver les objets.", objectif_trouver_3objets)
quete_manager.ajouter_quete(quete_objets2)

quete_portail= Quete("chercher_le_portail", "trouver le portail et l'activer.", objectif_trouver_portail)
quete_manager.ajouter_quete(quete_portail)

quete_portail1= Quete("chercher_le_portail", "trouver le portail et l'activer.", objectif_trouver_portail)
quete_manager.ajouter_quete(quete_portail1)

quete_final= Quete("survivre_et_s'échapper", "s'echapper du donjon et survivre en fuyant le monstre.", objectif_final)
quete_manager.ajouter_quete(quete_final)

quete_final1= Quete("survivre_et_s'échapper", "s'echapper du donjon et survivre en fuyant le monstre.", objectif_final)
quete_manager.ajouter_quete(quete_final1)





# _____ _   _   ____      _    ____  ____   ___  ____ _____      ___     _______ ____   _     _____ ____     ___  ____      _ _____ _____ ____  
#| ____| \ | | |  _ \    / \  |  _ \|  _ \ / _ \|  _ \_   _|    / \ \   / / ____/ ___| | |   | ____/ ___|   / _ \| __ )    | | ____|_   _/ ___| 
#|  _| |  \| | | |_) |  / _ \ | |_) | |_) | | | | |_) || |     / _ \ \ / /|  _|| |     | |   |  _| \___ \  | | | |  _ \ _  | |  _|   | | \___ \ 
#| |___| |\  | |  _ <  / ___ \|  __/|  __/| |_| |  _ < | |    / ___ \ V / | |__| |___  | |___| |___ ___) | | |_| | |_) | |_| | |___  | |  ___) |
#|_____|_| \_| |_| \_\/_/   \_\_|   |_|    \___/|_| \_\|_|   /_/   \_\_/  |_____\____| |_____|_____|____/   \___/|____/ \___/|_____| |_| |____/ 
                                                                                                                                               

#INVENTAIRE


slots=[]
icons=[]
for i in range(4):
    slot = Entity(
        model='quad',
        texture='data/image/inventaire.png', 
        color=color.rgba(255,255,255,128),
        scale=(0.125, 0.1, 1),  
        position=(-0.2+i * 0.13, -0.45, 0), 
        parent=camera.ui  
    )
    slots.append(slot)
    icon = Entity(
        model='quad',
        texture=None,  # Pas d'image au départ
        scale=(0.1, 0.1),
        position=slot.position,
        parent=camera.ui,
        visible=False
    )
    icons.append(icon)

inventaire_slot= Entity(
    model='quad',
    texture='data/image/inventaire_slot_choisi.jpeg',
    color=color.rgba(255,255,255,128),
    scale=(0.140, 0.115, 1.015),
    position=slots[0].position,
    parent=camera.ui
)
#gestion inventaire
nb_slot=0
inventory = [None] * len(slots)

icon_textures = {
    "Lampe_torche_inventaire": load_texture('data/image/Lampe_torche_inventaire.png'),
    "crane": load_texture('data/image/crane.png'),
    "bougie": load_texture('data/image/bougie.png'),
    "os": load_texture('data/image/os.png'),
    "croix": load_texture('data/image/croix.png')
}

def ajoute_a_inventaire(entity, icon_chemin):
    """hyp : la fonction vérifie l'objet n'est pas dans l'inventaire. S'il ne l'est pas, il l'ajoute en associant le nom de l'objet à une texture visible dans un emplacement précis de l'inventaire."""
    global inventory

    if entity.name in inventory:
        return None

    for i in range(len(inventory)):
        if inventory[i] is None:
            # Ajouter immédiatement à l'inventaire
            inventory[i] = entity.name
            entity.disable()  # Désactiver immédiatement l'objet
            icons[i].texture = icon_textures.get(entity.name, icon_chemin)  # Appliquer la texture préchargée
            icons[i].visible = True  # Rendre visible l'icône
            return





def input(key):
    """hyp : la fonction renvoie la position du joueur si la touche k est pressée, et permet de naviguer dans les slots de l'inventaire avec la molette, ou de naviguer plus précisemment avec les touches 1,2,3,4.
    La touche tab renvoie au menu pause."""
    global nb_slot
    if key == 'k':
        print(player.position,',')

    # Passer au slot suivant (molette vers le haut)
    if key == 'scroll down':
        nb_slot= (nb_slot + 1) % len(slots)
        inventaire_slot.position = slots[nb_slot].position

    # Passer au slot précédent (molette vers le bas)
    if key == 'scroll up':
        nb_slot = (nb_slot - 1) % len(slots)
        inventaire_slot.position = slots[nb_slot].position
    
    if key == '1':
        nb_slot = 0
        inventaire_slot.position = slots[nb_slot].position
    if key == '2':
        nb_slot = 1
        inventaire_slot.position = slots[nb_slot].position
    if key == '3':
        nb_slot = 2
        inventaire_slot.position = slots[nb_slot].position
    if key == '4' :
        nb_slot = 3
        inventaire_slot.position = slots[nb_slot].position
    
    if key == 'tab':
        toggle_pause()

    if key == 'escape':
        fermer_image_livre()







#  ___  ____      _ _____ _____ ____  
# / _ \| __ )    | | ____|_   _/ ___| 
#| | | |  _ \ _  | |  _|   | | \___ \ 
#| |_| | |_) | |_| | |___  | |  ___) |
# \___/|____/ \___/|_____| |_| |____/ 




# On crée une lumière nommée lampe_torche
lampe_torche_lumière=SpotLight(
    parent=camera, # Suivre la caméra
    position=(0.65, -0.4, 0.4),# Même endroit que le modèle 3D de la lampe torche, pour que ce soit plus 'réel'
    rotation=(0, 0, 0),
    color=color.black,
    shadows=False,# pas d'ombre crée par la lampe torche, ce sont des calcules inutiles
    cone_angle=150# taille du cone de lumière
    )




#  ___  ____      _ _____ _____      _      __  __ _____ _____ _____ ____  _____   ____    _    _   _ ____    _        _      __  __    _    ____  
# / _ \| __ )    | | ____|_   _|    / \    |  \/  | ____|_   _|_   _|  _ \| ____| |  _ \  / \  | \ | / ___|  | |      / \    |  \/  |  / \  |  _ \ 
#| | | |  _ \ _  | |  _|   | |     / _ \   | |\/| |  _|   | |   | | | |_) |  _|   | | | |/ _ \ |  \| \___ \  | |     / _ \   | |\/| | / _ \ | |_) |
#| |_| | |_) | |_| | |___  | |    / ___ \  | |  | | |___  | |   | | |  _ <| |___  | |_| / ___ \| |\  |___) | | |___ / ___ \  | |  | |/ ___ \|  __/ 
# \___/|____/ \___/|_____| |_|   /_/   \_\ |_|  |_|_____| |_|   |_| |_| \_\_____| |____/_/   \_\_| \_|____/  |_____/_/   \_\ |_|  |_/_/   \_\_|    


# VARIABLES
porte_ouverte = {}
rotation_targets = {}
cooldown_timer = 0.0  # Temporisateur pour éviter les doubles interactions

# MAISON 
maison_interior = Entity(    position=Vec3(70, 0.1, 70),scale=0.3)
maison_interior1=Entity(    position=Vec3(70, 0.1, 70),scale=0.3)
# PIVOTS
pivots = [
    Entity(position=(-6.16, 0.92, 22.95)),  # Pivot pour porte1
    Entity(parent=maison_interior1, position=(-1.8,0,10)),  # Pivot pour porte_interieur1
    Entity(parent=maison_interior1, position=(25.7, 0, 10)),  # Pivot pour porte_interieur2
    Entity(parent=maison_interior1, position=(-19.43, 0, 20.7)),  # Pivot pour porte_interieur3
    Entity(position=Vec3(43.55, 0.5203226, 10.288113))

]
portes=[]
portes_donjon=[]
# OBJETS INTERACTIFS (lampe + portes)
objects = [
    # Lampe torche
    Entity(
        model='data/modele_3D/flashlight/flashlight.glb',
        color=color.rgba(255, 255, 255, 255),
        position=Vec3(14.645611, 0.8, -15.204462),
        rotation=(0, -30, 0),
        scale=0.15,
        collider='box',
        name='Lampe_torche_inventaire',
        icon='data/image/Lampe_torche_inventaire.png'
    ),
    Entity(
        model='data/modele_3D/collectible/crane.glb',
        color=color.rgba(255, 255, 255, 255),
        position=Vec3(58.4107, 0.1, 73.376754) ,
        rotation=(0,45,0),
        scale=0.15,
        collider='box',
        name='crane',
        icon='data/image/crane.png'
    ),
        Entity(
        model='data/modele_3D/collectible/bougie.glb',
        color=color.rgba(255, 255, 255, 255),
        position=Vec3(62.767845, 0.1, 61.869682) ,
        scale=0.15,
        collider='box',
        name='bougie',
        icon='data/image/bougie.png'
    ),
        Entity(
        model='data/modele_3D/collectible/os.glb',
        color=color.rgba(255, 255, 255, 255),
        position=Vec3(77.2486, 0.1, 79.45972) ,
        scale=0.15,
        collider='box',
        name='os',
        icon='data/image/os.png'
    ),
        Entity(
        model='data/modele_3D/collectible/croix.glb',
        color=color.rgba(255, 255, 255, 255),
        position=Vec3(52.65, 1.45, 13.442674),
        scale=0.4,
        collider='box',
        name='croix',
        icon='data/image/croix.png'
            ),
        Entity(
        model='data/modele_3D/collectible/graal.glb',
        scale=1,
        color=color.rgba(255,255,255,255),
        position=Vec3(97.03792, 1.4, 54.73767),
        collider='box',
        name='graal',
        icon='data/image/graal.png'
),       Entity(
        model='data/modele_3D/collectible/cle.glb',
        color=color.rgba(255, 255, 255, 255),
        position=Vec3(43.67408, 0.5203226, -5.3729243),
        scale=1.2,
        rotation=Vec3(90, 0, 0),
        collider='box',
        name='clef',
        icon='data/image/clef.png'
            ),
        Entity(
        model='data/modele_3D/collectible/livre.glb',
        color=color.rgba(255, 255, 255, 255),
        position=Vec3(43.632472, 1.4, -6.7273173),
        scale=0.5,
        collider='box',
        name='livre',
            )
]

objets_cercle=[
    Entity(
            model='cube',
            visible=False,
            name ='object_cercle1',
            position=Vec3(59.556522, -5.9, 51.443515) ,
            scale=(0.5,0.5,0.5),
            collider='box'
        ),
        Entity(
            model='cube',
            visible=False,
            name ='object_cercle1',
            position=Vec3(59.556522, -5.9, 51.443515) ,
            scale=(0.5,0.5,0.5),
            collider='box'
        ),
        Entity(
            model='cube',
            visible=False,
            name ='object_cercle1',
            position=Vec3(59.556522, -5.9, 51.443515) ,
            scale=(0.5,0.5,0.5),
            collider='box'
        ),
        Entity(
            model='cube',
            visible=False,
            name ='object_cercle1',
            position=Vec3(50.113101, 0.803226, 31.754013) ,
            scale=(3.5,3.5,3.5),
            collider='box'
        )
]

# PORTES (intégrées dans `objects`)
for i, pivot in enumerate(pivots):
    if i == 4:
        porte = Entity(
            model='data/modele_3D/Porte/portev4.glb',
            parent=pivot,
            scale=1.4,
            color=color.white * 2,
            position=Vec3(0.7, 0, 0),
            collider=None,
            name=f'porte_{i}',
            pivot_index=i  # Stocke l'index du pivot dans l'entité
        )
    else:
        porte = Entity(
            model='data/modele_3D/Porte/portev4.glb' if i == 0 else 'data/modele_3D/interieurMaison/porteInterieur.glb',
            parent=pivot,
            position=(-0.7, 0, 0) if i == 0 else (-0.13, 0, -2.6) if i == 3 else (-3.2, 0, 0),
            rotation=(0, 0, 0) if i == 0 else (0, -47.5, 0) if i == 3 else (0, 44, 0),
            scale=1.1 if i == 0 else 1,
            color=color.white * 2,
            collider='box',
            name=f'porte_{i}',
            pivot_index=i  # Stocke l'index du pivot dans l'entité
        )
    portes.append(porte)
    porte_ouverte[i] = False
    rotation_targets[i] = 0  # Initialise chaque porte avec un angle cible à 0°

lumiere_de_la_lampe=SpotLight(
    parent=objects[0],  # Attaché à l'objet principal
    position=(0, 10, -1),  # Position légèrement au-dessus de l'objet
    rotation=(90, 0, 0),  # Oriente la lumière vers l'avant
    color=color.black,  # Couleur de la lueur
    shadows=False,  # Pas d'ombres pour une lueur douce
    cone_angle=40  # Angle large pour couvrir l'objet

)
lampe_torche=   Entity(
        model='data/modele_3D/flashlight/flashlight.glb',#chemin du fichier de la lampe torche
        parent=camera,  
        position=(0.55, -0.3, 0.6),  # Position en bas à droite de l'écran
        rotation=(0, 200, 0),  # Rotation de la lampe torche pour qu'elle soit bien orientée dans la direction que l'on veut
        scale=0.1,  # échelle du modèle 3D
        name='lampe_torche',
        visible=False
    )

croix_inventaire=    Entity(
        model='data/modele_3D/collectible/croix.glb',#chemin du fichier de la lampe torche
        parent=camera,  
        position=(0.5, -0.22, 0.6),  # Position en bas à droite de l'écran
        rotation=(0, 120, 0),  # Rotation de la lampe torche pour qu'elle soit bien orientée dans la direction que l'on veut
        scale=0.25,  # échelle du modèle 3D
        name='croix_inventaire',
        visible=False
    )

lampe_torche.shader = basic_lighting_shader
objects[0].shader=basic_lighting_shader






#      _  ___  _   _ _____ _   _ ____  
#    | |/ _ \| | | | ____| | | |  _ \ 
# _  | | | | | | | |  _| | | | | |_) |
#| |_| | |_| | |_| | |___| |_| |  _ < 
# \___/ \___/ \___/|_____|\___/|_| \_\





player = FirstPersonController()  # On initialise le joueur et la caméra, avec les touches par défaut de la bibliothèque
player.position = Vec3(60.556522, -6.25, 52.443515)  # Position initiale du joueur à l'endroit où l'objet graal est censé se poser
player.cursor.visible = True
player.cursor.color = color.red
player.speed = 5
player.jump_height = 1.55
player.jump_duration = 0.4
player.collider = 'box'
player.crouching = False
player.target_height = player.height
player.vitesse_visée = 5
lampe_active = False
f_pressed = False

player.gravity = 0.5  
spam_duree = 30  # Durée totale du spam (secondes)
spam_fin = time.time() + spam_duree  # Calcul du temps de fin

def spammer_position():
    """Hyp: Empêche le joueur de bouger pendant les 30 premières secondes en le téléportant constamment."""
    global spam_fin
    if time.time() < spam_fin:  # Vérifie si le délai n'est pas écoulé
        player.position = Vec3(1.1259576, 0.1, -22.242361)  # Téléporte le joueur
        invoke(spammer_position, delay=0.1)  # Rappelle la fonction toutes les 50ms
    else:
        print("Spam terminé, le joueur peut bouger librement.")

# Lancer le spam au début du jeu
spammer_position()

for p in range(10):
    attenuation_sphere = Entity(
        model='sphere', 
        scale=25-p*0.9,  
        double_sided=True,  
        color=color.rgba(0,0,0,255-p*25.4), 
        parent= player,  
        shader=basic_lighting_shader  
        )





# _____ _   ___     _____ ____   ___  _   _ _   _ _____ __  __ _____ _   _ _____ 
#| ____| \ | \ \   / /_ _|  _ \ / _ \| \ | | \ | | ____|  \/  | ____| \ | |_   _|
#|  _| |  \| |\ \ / / | || |_) | | | |  \| |  \| |  _| | |\/| |  _| |  \| | | |  
#| |___| |\  | \ V /  | ||  _ <| |_| | |\  | |\  | |___| |  | | |___| |\  | | |  
#|_____|_| \_|  \_/  |___|_| \_\\___/|_| \_|_| \_|_____|_|  |_|_____|_| \_| |_|  





#HITBOX DE LA FORET
# Variables pour stocker les éléments de chaque zone
foret_elements = []
maison_elements = []

etat_jeu = "foret" 

def charger_foret():
    foret =Entity(
        model='data/modele_3D/free_low_poly_forest/Mapv1.gltf',
        position=(0, 0, 0),
        scale=0.6,
        skip=1,
        collider='box',
        color=color.rgb(255, 255, 255),
        visible=True
    )
    foret_elements.append(foret)

    trees, little_rock, middle_rocks, high_rocks, white_rocks, barriers, maison =setup_environnement_foret(tree_positions = [
    Vec3(-2.9526941, 0.04799992, 19.720874),
    Vec3(-9.854335, 0.04799992, 18.702577),
    Vec3(-15.250536, 0.04799992, 12.549754),
    Vec3(-10.790384, 0.04799992, 13.048348),
    Vec3(-3.8831462, 0.04799992, 14.175954),
    Vec3(1.3916058, 0.04799992, 16.906),
    Vec3(3.3835375, 0.04799992, 13.862),
    Vec3(-3.0350682, 0.04799992, 10.49115),
    Vec3(-8.154051, 0.04799992, 7.290462),
    Vec3(-17.420255, 0.04799992, -0.84036213),
    Vec3(-9.828607, 0.04799992, -1.6098047),
    Vec3(-13.853688, 0.04799992, -4.818714),
    Vec3(-13.588303, 0.04799992, -9.871969),
    Vec3(-17.037031, 0.04799992, -9.226057),
    Vec3(-14.82344, 0.04799992, -17.305727),
    Vec3(-11.581169, 0.04799992, -18.189361),
    Vec3(-8.267964, 0.04799992, -12.0002164),
    Vec3(-5.399496, 0.04799992, -8.580153),
    Vec3(-0.43676751, 0.04799992, -13.432328),
    Vec3(4.6637635, 0.04799992, -12.635011),
    Vec3(-2.5674147, 0.04799992, 3.8516685),
    Vec3(-0.27386218, 0.04799992, 6.2923245),
    Vec3(-2.5075902, 0.04799992, 3.679463),
    Vec3(-7.2964067, 0.04799992, 2.999939),
    Vec3(0.14083057, 0.04799992, -2.5104591),
    Vec3(6.731105, 0.04799992, -2.092569),
    Vec3(9.980322, 0.04799992, -6.623657),
    Vec3(12.626253, 0.04799992, -8.781404),
    Vec3(17.47311, 0.04799992, -4.528522),
    Vec3(20.56239, 0.04799992, -0.8373769),
    Vec3(17.40762, 0.04799992, 9.911573),
    Vec3(11.4570875, 0.04799992, 9.279459),
    Vec3(6.014631, 0.04799992, 3.0351057),
    Vec3(-11.647994, 0.04799992, 10.203972),
    Vec3(-17.30256, 0.04799992, 8.992241),
    Vec3(7.5685544, 0.04799992, 12.089983),
    Vec3(-0.26369097, 0.04799992, 19.936111),
    Vec3(-13.251878, 0.04799992, 18.586355),
    Vec3(-11.679618, 0.04799992, 10.173381),
    Vec3(-17.301826, 0.04799992, 9.033962),
    Vec3(-6.9325833, 0.04799992, -17.201822),
    Vec3(-5.427629, 0.04799992, -20.2679),
    Vec3(7.7581825, 0.04799992, 12.085086),
    Vec3(13.042545, 0.04799992, 1.6552733),
    Vec3(15.080036, 0.04799992, 2.9740195),
    Vec3(20.44454, 0.04799992, -11.649143),
    Vec3(19.617792, 0.04799992, -16.845491),
    Vec3(15.680487, 0.04799992, -20.229677),
    Vec3(12.822047, 0.04799992, -21.62651)
    ],
    little_rock_position=[
    Vec3(-3.347238, 0.04799992, -21.254064) ,
    Vec3(-7.83839, 0.04799992, -1.5068688) ,
    Vec3(-3.3807654, 0.04799992, -11.98956) ,
    Vec3(19.837764, 0.04799992, 2.95436) ,
    Vec3(18.516626, 0.04799992, 0.25448235) ,
    Vec3(21.357954, 0.04799992, -8.381998) ,
    Vec3(14.563205, 0.04799992, -9.651172) ,
    ]
    ,
    middle_rock_position=[
    Vec3(-3.197343, 0.04799992, -22.381362) ,
    Vec3(-14.5151205, 0.04799992, -11.787062) ,
    Vec3(-9.4366254, 0.04799992, -5.1947307) ,
    Vec3(-3.2670733, 0.04799992, -12.985057) ,
    Vec3(-2.3490474, 0.04799992, -3.1828291) ,
    Vec3(4.364517, 0.04799992, 5.762631) ,
    Vec3(14.602225, 0.04799992, -10.644111) ,
    ]
    ,
    high_rock_position=[
    Vec3(-11.948373, 0.04799992, -21.656314) ,
    Vec3(-14.07094, 0.04799992, 6.272238) ,
    Vec3(14.245182, 0.04799992, 12.649508) ,
    Vec3(7.53287, 0.04799992, -18.088623) ,
    Vec3(5.411991, 0.04799992, -6.4442834) ,
    ],
    white_rock_position=[
    Vec3(-9.144624, 0.04799992, -19.318147) ,
    Vec3(-13.700636, 0.04799992, -1.0371945) ,
    Vec3(-1.9555882, 0.04799992, -8.590938) ,
    Vec3(1.1037786, 0.04799992, 0.80254536) ,
    Vec3(2.44347, 0.04799992, 2.3884732) ,
    Vec3(-10.958722, 0.04799992, 6.5622272) ,
    Vec3(-14.09876, 0.04799992, 15.299037) ,
    Vec3(1.1259088, 0.04799992, 12.566655) ,
    Vec3(15.275531, 0.04799992, 10.032349) ,
    Vec3(15.302321, 0.04799992, -2.5281546) ,
    Vec3(18.705843, 0.04799992, -14.627413) ,
    Vec3(10.942856, 0.04799992, -13.246193) ,
    Vec3(8.730364, 0.04799974, -10.8074045) ,
    ],  barrier_points = [
    (Vec3(16.538578, 0.04799992, -23.372364) ,Vec3(-16.346176, 0.04799992, -23.260311)) ,
    (Vec3(16.376867, 0.04799992, -18.367046) ,Vec3(23.251195, 0.04799992, -22.880924) ,) ,
    (Vec3(22.599155, 0.04799992, -7.0748343) ,Vec3(25.767095, 0.04799992, -19.6393)  ) ,
    (Vec3(25.778148, 0.04799992, 1.6810791) ,Vec3(25.986196, 0.04799992, -14.25192)),
    (Vec3(19.936801, 0.04799992, -10.559186) ,Vec3(26.598283, 0.04799992, 13.409483)),
    (Vec3(12.652037, 0.04799992, 9.734656) ,Vec3(22.059309, 0.04799992, 16.504978)),
    (Vec3(14.884506, 0.04799992, 15.697063) ,Vec3(4.110244, 0.04799992, 15.39427)),
    (Vec3(0.037605267, 0.04799992, 14.701565) ,Vec3(4.6997303, 0.04799992, 22.409778)),
    (Vec3(-14.709718, 0.04799992, -15.517832) ,Vec3(-22.167717, 0.04799992, -25.938434)),
    (Vec3(-19.750383, 0.04799992, -16.273668) ,Vec3(-17.891737, 0.04799992, -20.525386) ),
    (Vec3(-18.923488, 0.04799992, -17.139877) ,Vec3(-19.150556, 0.04799992, -9.6890134)),
    (Vec3(-19.822805, 0.04799992, -4.7708792) ,Vec3(-18.336944, 0.04799992, -13.609533) ),
    (Vec3(-19.493612, 0.04799992, -7.4807777) ,Vec3(-19.755117, 0.04799992, 6.3438854)),
    (Vec3(-17.988012, 0.04799992, 0.36508211) ,Vec3(-20.823371, 0.04799992, 13.927863)),
    (Vec3(-12.556585, 0.04799992, 10.919402) ,Vec3(-19.928804, 0.04799992, 19.90752) ),
    (Vec3(-13.442509, 0.04799992, 19.666797) ,Vec3(-12.469412, 0.04799992, 26.140049)),
    (Vec3(-10.000979, 0.04799992, 22.828744) ,Vec3(-13.9737625, 0.04799992, 31.358482)),
    (Vec3(-11.468436, 0.04799992, 29.998628) ,Vec3(1.3849747, 0.04799992, 30.671403)),
    (Vec3(1.3441912, 0.04799992, 21.475652) ,Vec3(2.7570662, 0.04799992, 32.253055)),
    (Vec3(2.2737245, 0.04799992, 21.559631) ,Vec3(1.0619777, 0.04799992, 28.689813))
    ])
    foret_elements.extend(trees)
    foret_elements.extend(little_rock)
    foret_elements.extend(middle_rocks)
    foret_elements.extend(high_rocks)
    foret_elements.extend(white_rocks)
    foret_elements.extend(barriers)
    foret_elements.append(maison)


# HITBOX INTERIEUR MAISON
def charger_maison_interior():
    global maison_interior

#  Murs Maison
    mur1=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(30,1,30),position=Vec3(67.67104, 0.0010000467, 80.86156),rotation=(90),collider='box')
    mur2=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(10,1,20),visible=False,position=Vec3(73.337203, -0.5269621, 58.485927) ,rotation=(90),collider='box')
    mur3=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(30,1,30),visible=False,position=Vec3(77.73317, 0.0010000467, 66.70004) ,rotation=(0,0,90),collider='box')
    mur4=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(30,1,30),visible=False,position=Vec3(56.36546, 0.0010000467, 76.18089) ,rotation=(0,0,90),collider='box')
    mur5=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(13.1,1,10),position=Vec3(61.164318, 0.003000021, 67.144935) ,rotation=(0,0,90),collider='box')
    mur6=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(8,1,8),visible=True,position=Vec3(65.28273, 0.0010000467, 61.371696) ,rotation=(90),collider='box')
    mur7=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(8,1,8),visible=False,position=Vec3(71.81998, 0.0010000467, 77.27534) ,rotation=(0,0,90),collider='box')
    mur8=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(8,1,8),visible=False,position=Vec3(63.68886, 0.0010000467, 72.885604),rotation=(90),collider='box')
    mur9=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(5.7,1,8),visible=False,position=Vec3(73.03316, 0.0010000467, 72.940765) ,rotation=(90),collider='box')
    mur10=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(10,1,10),visible=False,position=Vec3(58.278297, 0.0010000467, 72.90055) ,rotation=(90),collider='box')
    mur11=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(10,1,4),visible=False,position=Vec3(64.03227, 0.0010000467, 78.36943),collider='box',rotation=(0,0,90))
    mur12=Entity(model='plane',texture='white_cube',texture_scale=(30,30),scale=(10,1,1.5),visible=False,position=Vec3(64.08575, 0.0010000467, 73.80266),collider='box',rotation=(0,0,90))
    mur13=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(13,1,1),position=Vec3(61.192024, 0.003000021, 72.38777) ,rotation=(0,0,90),collider='box')
    mur14=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(13,1,1),position=Vec3(61.192024, 0.003000021, 72.38777) ,rotation=(0,0,90),collider='box')
    mur15=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(5,1,5),position=Vec3(59.444534, -4.5188903, 61.303504) ,rotation=(90,0,0),collider='box')
    mur16=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(15,1,5),position=Vec3(58.16864, -4.5188903, 59.695194) ,rotation=(0,0,90),collider='box')
    mur17=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(8,1,20),position=Vec3(64.85469, -4.5188903, 58.42412) ,collider='box')
    mur18=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(6,1,5),position=Vec3(59.499847, -6.58245, 49.509075),rotation=(0,90,90),collider='box')
    mur19=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(5,1,15),position=Vec3(58.142211, -6.58245, 55.842605) ,rotation=(0,0,90),collider='box')
    mur20=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(5,1,15),position=Vec3(60.88953, -6.58245, 55.397354), rotation=(0,0,90),collider='box')
    mur21=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(0.5,1,3),position=Vec3(69.102325, 0.0030001401, 60.23239) ,collider='box')

    #  Salle de bain
    armoire=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1.5,3,3),position=Vec3(76.97488, 0.0010000467, 76.94417),collider='box')
    robinet=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1,4,1),position=Vec3(73.99077, 0.0010000467, 80.40795),collider='box')
    baignoire_L=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1.5,1,1.5),rotation=(90),position=Vec3(72.58072, 0.0010000467, 77.16758),collider='box')
    baignoire_l=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1,1,4),rotation=(0,0,90),position=Vec3(73.493904, 0.0010000467, 75.044914),collider='box')
    toilette1=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1,2,1),position=Vec3(74.68441, 0.0010000467, 73.93109),collider='box')
    toilette2=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1,3,0.5),position=Vec3(74.63297, 0.0010000467, 73.42279),collider='box')
    #  Salon
    table1=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1.2,2,2.7),position=Vec3(74.13613, 0.0010000467, 66.859405),collider='box')
    canape1=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1.2,2,4),position=Vec3(71.74751, 0.0010000467, 65.680694) ,collider='box')
    canape2=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(4,3,4),position=Vec3(70.87705, 0.0010000467, 66.062873) ,collider='box',rotation=(0,0,90))
    table_tele=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1,2,2.7),position=Vec3(77.16227, 0.0010000467, 66.80612) ,collider='box')
    fauteuil=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(2,1.5,2),position=Vec3(72.4388, 0.0010000467, 69.57712) ,collider='box',rotation=(0,40,0))
    cheminee=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(4,4,2),position=Vec3(65.22046, 0.0010000467, 61.877033),collider='box')
    table2=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(2,3,2),position=Vec3(64.67419, 0.0010000467, 66.4954) ,collider='box')
    chaise1=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(0.8,2,0.8),position=Vec3(65.97034, 0.0010000467, 66.6068) ,collider='box')
    chaise2=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(0.8,2,0.8),position=Vec3(64.62034, 0.0010000467, 67.93246) ,collider='box')
    chaise3=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(0.8,2,0.8),position=Vec3(64.689514, 0.0010000467, 65.298324) ,collider='box')
    chaise4=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(0.8,2,0.8),position=Vec3(63.379364, 0.0010000467, 66.48863) ,collider='box')
    armoire_haut=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1.2,2,2.7),position=Vec3(77.23342, 2.4382827, 66.952285) ,collider='box')
    #  Chambre
    lit=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(2,1.8,4),position=Vec3(66.43775, 0.0010000467, 79.77684) ,collider='box',rotation=(0,90,0))
    table_chevet=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(0.8,2,0.8),position=Vec3(64.67772, 0.0010000467, 77.646385) ,collider='box')
    armoire_chambre=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(4,10,1),position=Vec3(71.33985, 0.0010000467, 78.81674) ,collider='box',rotation=(0,90,0))
    #  Bureau
    table_bureau1=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(2,2,2),position=Vec3(62.166862, 0.0010000467, 80.27196) ,collider='box')
    table_bureau2=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(2,2,2),position=Vec3(57.715343, 0.0010000467, 80.071754) ,collider='box')
    armoire_bureau=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(1,10,3),position=Vec3(60.402313, 0.0010000467, 73.491584) ,collider='box',rotation=(0,90,0))
    fauteuil_bureau=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(2,2,2),position=Vec3(59.81492, 0.0010000467, 79.84768) ,collider='box')
    armoire_haut_bureau=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(2,1,1),position=Vec3(60.122737, 2.3965232, 80.3881) ,collider='box')
    bureau=Entity(model='cube',texture='white_cube',texture_scale=(30,30),visible=False,scale=(2,2,2),position=Vec3(57.19522, 0.0010000467, 75.355064) ,collider='box')
    # Escalier
    escalier1=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(10,1,2.8),position=Vec3(64.30336, -2.843075855, 59.826772) ,collider='box',rotation=(0,0,-27))
    escalier2=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(5.7,1,2.8),position=Vec3(59.60476, -5.8128657, 56.954914) ,collider='box',rotation=(0,-90,-35))
    cercle_cult=Entity(
        model='quad',
        texture='data/image/cercle_de_cultiste.png',
        scale=3,
        double_sided=True,
        color=color.rgba(255,0,0,200),
        shader=unlit_shader,  # Ne réagit pas à la lumière
        rotation=(90,0,0),
        position=Vec3(59.556522, -6.25, 51.443515) 
        )
    #  Sol
    sol1=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(14,1,30),position=Vec3(75.790245, 0.0020000934, 66.886375) ,collider='box')
    sol2=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(20,1,22),position=Vec3(65.28255, 0.0020000934, 72.34239) ,collider='box')
    sol3=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=False,scale=(20,1,2.8),position=Vec3(61.737537, -4.5198903, 59.766643) ,collider='box')
    sol4=Entity(model='plane',texture='white_cube',texture_scale=(30,30),visible=True,scale=(20,1,20),position=Vec3(59.496284, -6.58345, 54.507595) ,collider='box')
    models_interieur=[maison_interior,cercle_cult,mur1,mur2,mur3,mur4,mur5,mur6,mur7,mur8,mur9,mur10,mur11,mur12,mur13,mur14,mur15,mur16,mur17,mur18,mur19,
    mur20,mur21,armoire,robinet,baignoire_L,baignoire_l,toilette1,toilette2,table1,canape1,canape2,table_tele,fauteuil,cheminee,table2,chaise1,chaise2,chaise3,
    chaise4,armoire_haut,lit,table_chevet,armoire_chambre,table_bureau1,table_bureau2,armoire_bureau,fauteuil_bureau,armoire_haut_bureau,bureau,escalier1,escalier2,
    sol1,sol2,sol3,sol4,]
    for i in models_interieur:
        maison_elements.append(i)
    # --- MAISON ---
    maison_interior = Entity(
    model='data/modele_3D/interieurMaison/interieurMaison.glb',
    position=Vec3(70, 0.1, 70),
    scale=0.3,
    color=color.white * 2,
    collider=None,
    visible=True
    )

crane1=Entity(
    model='data/modele_3D/collectible/crane.glb',
    color=color.rgba(255, 255, 255, 255),
    position=Vec3(59.556522, -6.25, 51.443515) ,
    rotation=(0,180,0),
    scale=0.15,
    collider=None,
    visible=False
)
cercle_bougie1=Entity(
    model='data/modele_3D/cave/cercle_bougie.glb',
    color=color.rgba(255, 255, 255, 255),
    position=Vec3(59.556522, -6.25, 51.443515) ,
    rotation=(0,0,0),
    scale=0.5,
    collider=None,
    visible=False
)
cercle_os=Entity(
    model='data/modele_3D/cave/cercle_os.glb',
    color=color.rgba(255, 255, 255, 255),
    position=Vec3(59.556522,-6.5, 51.443515) ,
    rotation=(0,0,0),
    scale=0.5,
    collider=None,
    visible=False
)


# Nouvelle position pour le graal
graal_cercle = Entity(
    model='data/modele_3D/collectible/graal.glb',
    color=color.rgba(255, 255, 255, 255),
    position=Vec3(50.113101, 1.203226, 31.754013) ,  # Nouvelle position
    rotation=(0, 180, 0),
    scale=0.8,
    collider=None,
    visible=False
)

mur_cave=Entity(
    model='data/modele_3D/interieurMaison/murCave.glb',  # La porte pivote autour du pivot
    parent=maison_interior,
    position=(-4, 0, -34),
    rotation=(0,0,0),
    scale=1,
    color=color.white*2,
    collider='box'
)

charger_foret()
charger_maison_interior()

def changer_zone():
    """Gère le passage entre la forêt et la maison"""
    global etat_jeu,pieges,escalier, sol_cave, Mur_cave,donjon, portes


    if etat_jeu== 'donjon':

        for obj in foret_elements:  # Parcourir la liste
            if isinstance(obj, Entity):  # Vérifier si c'est bien une entité
                destroy(obj)
        for ib in maison_elements:  # Parcourir la liste
            if isinstance(ib, Entity):  # Vérifier si c'est bien une entité
                destroy(ib)
        maison_elements.clear()
        foret_elements.clear()
        pieges, escalier, sol_cave, Mur_cave,donjon = charger_donjon()
        portes[4].collider = 'box' # Activer la collision de la porte
        charger_position_monstre_donjon()
    # Sol
def charger_position_monstre_donjon():
    global positions_monstres
    positions_monstres.clear()
    list_positions_m=[Vec3(60.54677, 2, -7.352968),
        Vec3(91.09325, 2.2, -7.545725),
        Vec3(89.68289, 2.2, 38.02107),
        Vec3(99.35409, 2.2, 53.2639),
        Vec3(60.636104, 2.2, 37.749996),
        Vec3(39.647296, 2.2, 43.387886)]
    # Sol
    for i in list_positions_m:
        positions_monstres.append(i)
floor = Entity(
    model='plane',
    texture='white_cube',
    texture_scale=(20, 20),
    scale=(60, 30, 60),
    visible=False,
    position=(0, 0, 0),
    color=color.red,
    collider='box'
    )




interaction_icon = Entity(
        model='quad',
        texture='data/image/interagir.png',  # Remplacez par le chemin de votre texture
        scale=1,
        rotation=(0,0,0),
        double_sided=True,
        color=color.rgba(255,255,255,255),
        visible=False, # Désactivé par défaut
        shader=unlit_shader  # Ne réagit pas à la lumière
)




# __  __ _____ _   _ _   _   ____   _   _   _ ____  _____   ____  _   _       _ _____ _   ___  __
#|  \/  | ____| \ | | | | | |  _ \ / \ | | | / ___|| ____| |  _ \| | | |     | | ____| | | \ \/ /
#| |\/| |  _| |  \| | | | | | |_) / _ \| | | \___ \|  _|   | | | | | | |  _  | |  _| | | | |\  / 
#| |  | | |___| |\  | |_| | |  __/ ___ \ |_| |___) | |___  | |_| | |_| | | |_| | |___| |_| |/  \ 
#|_|  |_|_____|_| \_|\___/  |_| /_/   \_\___/|____/|_____| |____/ \___/   \___/|_____|\___//_/\_\
                                                                                                





game_paused = False

# Écran de pause
pause_menu = Entity(parent=camera.ui, enabled=False)
pause_background = Entity(
    parent=pause_menu, 
    model='quad', 
    scale=(2, 1), 
    color=color.rgba(0, 0, 0, 150)
)
resume_button = Button(
    model='quad', 
    texture='data/image/reprendre.png',
    parent=pause_menu, 
    scale=(0.7, 0.4), 
    position=(0, 0.15),
    color=color.white
)
quit_button = Button(
    model='quad', 
    texture='data/image/quitter.png',
    parent=pause_menu, 
    scale=(0.7, 0.4), 
    position=(0, -0.1),
    color=color.white
)

# Fonction pour activer/désactiver l'écran de pause
def toggle_pause():
    """hyp : la fonction permet d'activer le menu pause et de le désactiver, en bloquant la possibilité de bouger la caméra du joueur."""
    global game_paused
    game_paused = not game_paused
    pause_menu.enabled = game_paused
    mouse.locked = not game_paused
    player.cursor.visible = not player.cursor.visible
    if game_paused:
        application.pause()  # Arrête les mises à jour du jeu
    else:
        application.resume()  # Reprend les mises à jour du jeu

# Reprendre le jeu
def resume_game():
    toggle_pause()

# Quitter le jeu
def quit_game():
    application.quit()

# Connecter les boutons aux fonctions
resume_button.on_click = resume_game
quit_button.on_click = quit_game

#Mort

temps_restant = random.randint(50, 100)
compte_a_rebours_actif = False  # Pour éviter de démarrer plusieurs fois le timer



def respawn(_=None):
    """Téléporte et réactive le joueur après un délai de 4 secondes."""
    global etat_jeu, menu_de_mort,temps_restant
    temps_restant = random.randint(50, 100)
    menu_de_mort.visible = False  # Cache l'écran de mort après le délai
    if etat_jeu == 'foret':
        player.position = Vec3(1.1259576, 1, -22.242361)

    if etat_jeu == 'maison_interior':
        etat_jeu = 'foret'
        player.position = Vec3(1.1259576, 1, -22.242361)

    elif etat_jeu == 'donjon':
        player.position = Vec3(2.3665275, 0.5203226, -0.20266074)
        charger_position_monstre_donjon()


    player.enable()  # Réactive le joueur


def mourir(_=None):
    """Déclenche la mort du joueur et affiche un écran de game over."""
    global compte_a_rebours_actif, etat_jeu, menu_de_mort

    player.disable()  # Désactive le joueur
    compte_a_rebours_actif = False  # Arrête le timer

    # Si l'écran de mort n'existe pas encore, on le crée une seule fois
    if not hasattr(mourir, "menu_de_mort"):
        mourir.menu_de_mort = Entity(
            parent=camera.ui,
            model='quad',
            texture='data/image/Vous-etes-mort.png',
            color=color.rgba(150, 150, 150, 255),
            visible=False,
            scale=(2, 1)
        )
        

    menu_de_mort = mourir.menu_de_mort  # Récupérer l'entité globale
    menu_de_mort.visible = True  # Afficher l'écran de mort

    # Attendre 4 secondes avant de respawn
    invoke(respawn, delay=4)
#defi
def lancer_timer():
    """Démarre le compte à rebours uniquement si ce n'est pas déjà fait."""
    global compte_a_rebours_actif
    if not compte_a_rebours_actif:  # Empêche plusieurs timers en même temps
        compte_a_rebours_actif = True
        diminuer_temps()  # Démarre le compte à rebours

def diminuer_temps():
    global temps_restant,compte_a_rebours_actif,etat_jeu
    if etat_jeu=='maison_interior':
        if temps_restant > 0:
            temps_restant -= 1
            print(f"Temps restant : {temps_restant}s")
            invoke(diminuer_temps, delay=1)  # Rappel toutes les secondes
        else:
            mourir()  
            if menu_de_mort.visible:
                jump_scare=Audio('data/Son/jump-scare-52517_1SHHSg40.wav',autoplay=True)
                jump_scare.volume=0.4
            compte_a_rebours_actif=False

image_livre = None

def afficher_image_livre():
    """Affiche l'image en plein écran lorsqu'on interagit avec le livre."""
    global image_livre
    image_livre = Entity(
        parent=camera.ui,
        model='quad',
        texture='data/image/image_livre.png',  # Image du livre ouvert
        scale=(1.8, 1),  # Taille ajustée pour couvrir l'écran
        color=color.rgb(170,170,170)
    )
    print("Livre ouvert")

def fermer_image_livre():
    """Ferme l'image du livre si elle est affichée."""
    global image_livre
    if image_livre:
        destroy(image_livre)
        image_livre = None
        print("Livre fermé")    

#importation des murs destructibles de la cave
mur_destructible=Entity(model='data/modele_3D/cave/mur_destructible.glb',scale=0.8)
mur163=Entity(model='data/modele_3D/cave/hitbox/hitboxMurs/mur163.glb',scale=0.8, visible=False)

# _   _ ____  ____    _  _____ _____ 
#| | | |  _ \|  _ \  / \|_   _| ____|
#| | | | |_) | | | |/ _ \ | | |  _|  
#| |_| |  __/| |_| / ___ \| | | |___ 
# \___/|_|   |____/_/   \_\_| |_____|

positions_monstres=[#foret
Vec3(1.6752911, 2.2, -5.9159774) ,
Vec3(-11.372593, 2.2, 2.4471561) ,
Vec3(-7.071984, 2.2, 16.186901) ,
Vec3(10.215871, 2.2, 11.243773) ,
Vec3(10.987204, 2.2, -9.981305)]

monstres = {}
timers_disparition = {}

# Rayon de détection pour SPAWNER un monstre (ex: 15 unités)
rayon_spawn = 8
# Rayon plus petit pour FAIRE DISPARAÎTRE un monstre (ex: 5 unités)
rayon_disparition = 8



player.check_entity = Entity(parent=player, position=(0, 2.5, 0), scale=(player.scale_x, 0.5, player.scale_z), collider='box', visible=False)
cooldown_timer1=0.0
son_marche={
    'foret_marche':Audio('son-pas-herbe_l2v9aGhC.wav',autoplay=False),
    'maison_marche':Audio('pas-interieur-maison_3u96gDv6.wav',autoplay=False),
    'donjon_marche':Audio('marche_donjon.mp3',autoplay=False),
}
dernier_pas = time.time()
mur_cave_detruit=True
no_repeat=True
no_repeat1=False
no_repeat2=True
# Initialisation des variables sons
ambiance = Audio('data/Son/Son ambiance/ambiance_terrifiante.wav', autoplay=False, loop=False)
ambiance1 = Audio('data/Son/Son maison/horloge_son.wav', autoplay=False, loop=False)
ecroulement_graal=Audio('data/Son/Son ambiance/the-end-of-the-world-25685.mp3',autoplay=False,loop=False)
ecroulement_graal.volume=3
ambiance.volume = 0.25
ambiance1.volume = 50

#Minuteur de la croix
minuteur_debut = False
temps = 30
minuteur_fin = False

def minuteur_croix():
    global minuteur_debut, temps, inventory, minuteur_fin, minuteur_texte, nb_slot
    if minuteur_debut:
        if 'croix' in inventory and inventory[nb_slot] == 'croix':
            if temps > 0:
                temps -= 1
                minuteur_texte.text = f"{temps}s"  # Met à jour le texte du minuteur
                minuteur_texte.visible = True  # Rendre le texte visible
                print(f"Temps restant : {temps}s")
                invoke(minuteur_croix, delay=1)  # Rappel à chaque seconde
            else:
                print("Le minuteur est terminé.")
                minuteur_debut = False
                minuteur_fin = True  # Fin du minuteur
                minuteur_texte.visible = False  # Cacher le texte du minuteur
                # Déstruction de la croix à la fin du minuteur
                if 'croix' in inventory:
                    for i in range(len(inventory)):
                        if inventory[i] == 'croix':
                            inventory[i] = None
                            icons[i].texture = None  # Enlève l'affiche de la croix
                            icons[i].visible = False
                            croix_inventaire.visible = False
                            print("La croix est détruite")
                            run_croix_detruite()
                            interface()  # Appelle la fonction interface()
                            application.quit()  # Arrête le programme Ursina
                            break
        else:
            minuteur_debut = False
            minuteur_texte.visible = False  # Cacher le texte du minuteur

# Ajoutez cette ligne pour créer une entité de texte pour le minuteur
minuteur_texte = Text(text='', position=(0.5, -0.45), parent=camera.ui, origin=(0, 0), scale=2, color=color.red, visible=False)

def update():
    global f_pressed, timers_disparition,lampe_active, objects, inventory, nb_slot, porte_ouverte, etat_jeu, cooldown_timer1, cooldown_timer, dernier_pas, no_repeat2, mur_cave_detruit, no_repeat, no_repeat1, ambiance, ambiance1, inventory, compte_a_rebours_actif, minuteur_debut, temps_restant, minuteur_fin, minuteur_texte
    for pos in positions_monstres:
        if abs(player.x - pos.x) < rayon_spawn and abs(player.z - pos.z) < rayon_spawn:
            if pos not in monstres:
                monstre = Entity(
                    model='data/modele_3D/Monstre/79910.glb',  # Modèle du monstre
                    color=color.white,
                    scale=1.5,
                    position=pos,
                    collider='box',
                    visible=True
                )
                monstre.look_at(player.position)  # Tourne vers le joueur une seule fois
                monstre.rotation_z = 0
                monstre.rotation_x = 0
                monstre.rotation_y += 180  # Corrige l'orientation
                monstres[pos] = monstre  # Stocke le monstre
                timers_disparition[pos] = None  # Initialise son timer
                Audio('data/Son/transitional-swipe-2-211689.wav', autoplay=True, loop=False)


    # Vérifie si un monstre doit disparaître
    for pos, monstre in list(monstres.items()):  
        if monstre.visible:
            # Tourne toujours vers le joueur
            monstre.look_at(player.position)
            monstre.rotation_z = 0
            monstre.rotation_x = 0
            monstre.rotation_y += 180  # Corrige l'orientation
            if monstre.intersects(player).hit:
                mourir()
                Audio('jump-scare-52517_1SHHSg40.wav',autoplay=True)

            # Vérifie si le joueur est dans le petit rayon autour du monstre
            if abs(player.x - monstre.x) < rayon_disparition and abs(player.z - monstre.z) < rayon_disparition:
                if timers_disparition[pos] is None:  
                    timers_disparition[pos] = time.time() + 3  # Démarre le timer
                    print(f"Le monstre à {pos} disparaîtra dans 3 secondes.")

            #  Vérifie si le timer est écoulé
            if timers_disparition[pos] is not None and time.time() >= timers_disparition[pos]:
                print(f"Monstre à {pos} supprimé !")

                # Vérifie si le joueur a la croix dans l'inventaire mais pas en main
                if inventory[nb_slot] != 'croix'and etat_jeu=='donjon':
                    print(" Le joueur n'a pas la croix en main... MORT !")
                    mourir()  # Tue le joueur

                destroy(monstre)  # Supprime l'entité du monstre
                del monstres[pos]  # Retire le monstre de la liste
                del timers_disparition[pos]  # Supprime son timer
                del positions_monstres[positions_monstres.index(pos)]  # Retire la position de la liste

    mouvement_detecte = any((held_keys['w'], held_keys['a'], held_keys['s'], held_keys['d']))

    if mouvement_detecte:
        if etat_jeu == 'foret':
            current_time = time.time()
            if current_time - dernier_pas > 0.6:  # Évite le spam
                son_marche['foret_marche'].play()
                dernier_pas = current_time
        elif etat_jeu == 'maison_interior':
            current_time = time.time()
            if current_time - dernier_pas > 0.6:  # Évite le spam
                son_marche['maison_marche'].play()
                dernier_pas = current_time
        elif etat_jeu =='donjon':
            current_time = time.time()
            if current_time - dernier_pas > 0.6:    #Évite le spam
                son_marche['donjon_marche'].volume=6
                son_marche['donjon_marche'].play()
                dernier_pas = current_time
    else:
        if etat_jeu=='donjon' and son_marche['donjon_marche'].playing:
            son_marche['donjon_marche'].stop()

    # Gestion du crouch
    if held_keys['control']:  # vérifie si 'control' est pressé
        player.target_height = 1.2
        player.speed = 2
    else:
        if etat_jeu != 'foret':
            if not player.check_entity.intersects().hit:  # Si aucun obstacle au-dessus
                player.scale_y = 1
                player.target_height = 1.8  # Taille normale
            else:
                pass
        else:
            player.target_height = 1.8

    crouch(player, player.target_height)

    # Gestion de l'accélération
    if held_keys['shift']:
        player.vitesse_visée = 7.5
    else:
        player.vitesse_visée = 4
    accélération(player, player.vitesse_visée)

    if 'Lampe_torche_inventaire' in inventory:
        if inventory[nb_slot] == 'Lampe_torche_inventaire':
            lampe_torche.visible = True
            if held_keys['f'] and not f_pressed:
                f_pressed = True  # Empêche une exécution continue
                lampe_active = not lampe_active  # Change l'état de la lampe
                if lampe_active:
                    lampe_torche_lumière.color = color.white * 2  # Allume la lampe
                    ambiance = Audio('data/Son/Son objet/son_allumage_lampe.wav', autoplay=True, loop=False)
                    ambiance.volume = 0.5
                else:
                    lampe_torche_lumière.color = color.black  # Éteint la lampe
                    ambiance = Audio('data/Son/Son objet/son_eteindre_lampe.wav', autoplay=True, loop=False)
                    ambiance.volume = 0.5
            if not held_keys['f']:
                f_pressed = False
        else:
            lampe_torche.visible = False
            lampe_torche_lumière.color = color.black  # Éteint la lampe

    # aura qui eclaire la lampe torche
    if 'Lampe_torche_inventaire' not in inventory:
        lumiere_de_la_lampe.color = color.yellow * 4
    else:
        lumiere_de_la_lampe.color = color.black

    # Ajoutez cette vérification dans la partie où vous gérez la croix et le minuteur
    if 'croix' in inventory:
        if inventory[nb_slot] == 'croix':
            croix_inventaire.visible = True
            if not minuteur_debut and not minuteur_fin:
                minuteur_debut = True
                minuteur_croix()
        else:
            croix_inventaire.visible = False
    else:
        if minuteur_debut:
            minuteur_debut = False  # Met fin au minuteur quand la croix n'est plus dans l'inventaire
            minuteur_texte.visible = False  # Cacher le texte du minuteur

    # Réduire le temporisateur
    if cooldown_timer > 0:
        cooldown_timer -= time.dt

    if cooldown_timer1 > 0:
        cooldown_timer1 -= time.dt

    # Raycast pour détecter les objets en face du joueur
    raycast_origin = camera.world_position
    raycast_direction = camera.forward
    hit_info = raycast(raycast_origin, raycast_direction, distance=4, ignore=[player])

    if hit_info.hit:
        obj = hit_info.entity
        if obj in objects or obj in portes or obj in objets_cercle:
            if obj in portes:
                bounds = Vec3(0.018861442, 1.4, 0.006459743)
                center_pos = obj.get_position(relative_to=scene) + bounds
                distance_max_hitbox = 1.27
            else:
                bounds = Vec3(0.018861442, 0.25, 0.006459743)
                center_pos = obj.get_position(relative_to=scene) + bounds
                distance_max_hitbox = 1.27

            # Direction du joueur vers l'objet
            direction_to_camera = (camera.world_position - center_pos).normalized()

            # Placer l'icône légèrement en dehors de la hitbox
            interaction_icon.position = center_pos + direction_to_camera * distance_max_hitbox
            interaction_icon.look_at(camera.world_position)  # Oriente l’icône vers la caméra
            interaction_icon.rotation_z = 0  # Empêche la rotation de l'icône
            interaction_icon.visible = True

            # Interaction avec les objets et les portes
            if held_keys['e'] and cooldown_timer <= 0:
                cooldown_timer = 1.0  # Empêche une double interaction rapide
                if obj in objects and obj.name != 'livre':
                    ajoute_a_inventaire(obj, obj.icon)
                    prendre = Audio("data/Son/Son objet/prendre_un_objet.wav", autoplay=True, loop=False)
                    prendre.volume = 8
                if obj.name == 'livre':
                    afficher_image_livre()
                if obj in objets_cercle:
                    objet_a_supprimer = inventory[nb_slot]  # Récupère l'objet correspondant au slot
                    if objet_a_supprimer == 'os' or objet_a_supprimer == 'bougie' or objet_a_supprimer == 'crane' or objet_a_supprimer == 'graal':
                        if objet_a_supprimer == 'os':
                            cercle_os.visible = True
                            destroy(objets_cercle[0])

                        if objet_a_supprimer == 'bougie':
                            cercle_bougie1.visible = True
                            destroy(objets_cercle[1])

                        if objet_a_supprimer == 'crane':
                            crane1.visible = True
                            destroy(objets_cercle[2])

                        if objet_a_supprimer == 'graal':
                            graal_cercle.visible = True
                            destroy(objets_cercle[3])
                            ecroulement_graal.play()
                            destroy(mur_destructible)
                            mur163.collider=None

                        inventory[nb_slot] = None
                        icons[nb_slot].texture = None  # Supprime l'affichage de l'image
                        icons[nb_slot].visible = False

                if obj and obj in scene.entities and hasattr(obj, 'name') and obj.name.startswith('porte_'):
                    index = obj.pivot_index  # Récupère l'index du pivot
                    pivot = pivots[index]  # Associe au bon pivot

                    if index == 4 and inventory[nb_slot] != 'clef':
                        print("Vous avez besoin d'une clef pour ouvrir cette porte.")
                        ambiance = Audio('data/Son/lock-a-door-43194.wav', autoplay=True, loop=False)
                        ambiance.volume = 0.5   # Son de porte verrouillée
                    else:
                        if index == 4 and inventory[nb_slot] == 'clef':
                            inventory[nb_slot] = None
                            icons[nb_slot].texture = None  # Supprime l'affichage de l'image
                            icons[nb_slot].visible = False
                            porte_ouverte_verouille = Audio('data/Son/unlock-the-door-1-46012.wav', autoplay=True, loop=False)
                            porte_ouverte_verouille.volume = 0.5
                        if not porte_ouverte[index]:
                            rotation_targets[index] = -90  # Ouvrir la porte
                            ambiance = Audio('data/Son/Son maison/Porte_ouverture.wav', autoplay=True, loop=False)
                            ambiance.volume = 0.5
                        else:
                            rotation_targets[index] = 0  # Fermer la porte
                            ambiance = Audio('data/Son/Son maison/Porte_fermeture.wav', autoplay=True, loop=False)
                            ambiance.volume = 0.5
                        porte_ouverte[index] = not porte_ouverte[index]  # Change l'état de la porte


        else:
            interaction_icon.visible = False
    else:
        interaction_icon.visible = False

    # Applique la rotation aux pivots des portes
    for i, pivot in enumerate(pivots):
        pivot.rotation_y = lerp(pivot.rotation_y, rotation_targets[i], time.dt * 5)

    zone_position = Vec3(-6.8336386, 0.04799992, 23.8)
    zone_position1 = Vec3(59.556522, -6.25, 51.443515)
    zone_position2 = Vec3(59.450927, -4.3188903, 59.97794)
    
    zone_position3=Vec3(4.4753003, 12.212039, 43.613895)
    rayon_zone = 0.8  # Rayon autour de la position (ajuste selon besoin)
    rayon_zone2 = 1.5


    # Vérification si le joueur est dans la zone
    if distance(player.position, zone_position) < rayon_zone:
        etat_jeu = 'maison_interior'
        player.position = Vec3(72, 0.1, 60)
        no_repeat1 = True

    if distance(player.position, zone_position2) < rayon_zone2 and no_repeat2:
        filleQuiChantent = Audio('data/Son/very-infectious-laughter-117727_1.wav', autoplay=True)
        filleQuiChantent.volume = 0.5
        no_repeat2 = False

    if distance(player.position, zone_position3) < rayon_zone2:
        application.quit()
        run_fin_victoire()
        interface()
        
    if crane1.visible and cercle_bougie1.visible and cercle_os.visible:
        if distance(player.position, zone_position1) < rayon_zone:
            etat_jeu = 'donjon'
            Audio('data/Son/transitional-swipe-2-211689.wav', autoplay=True)
            changer_zone()
            player.position = Vec3(2.115556, 0.5203226, -0.1382158)

    quete_manager.verifier_quetes()

    if mur_cave_detruit and 'crane' in inventory and 'os' in inventory and 'bougie' in inventory:
        destroy(mur_cave)
        Audio('data/Son/Son maison/mechanism-fulltakes-238577_FuhWVbEf.wav', autoplay=True)
        mur_cave_detruit = False

    if etat_jeu == 'maison_interior':
        lancer_timer()

    # Son ambiance du jeu dans la forêt
    if etat_jeu == 'foret' and no_repeat:
        ambiance.play()
        no_repeat = False  # Empêche la répétition

    # Son ambiance du jeu dans la maison
    if etat_jeu == 'maison_interior' and no_repeat1:
        ambiance.stop()
        ambiance1.play()
        no_repeat1 = False  # Empêche la répétition

    if etat_jeu == 'donjon':
        for piege in pieges:
            if player.intersects(piege).hit and cooldown_timer1 <= 0:  # Vérifie la collision avec le piège
                cooldown_timer1 = 4.1
                print("Le joueur est mort !")
                mourir()  # Appelle la fonction de mort
                break






# ____   ___  _   _ 
#/ ___| / _ \| \ | |
#\___ \| | | |  \| |
# ___) | |_| | |\  |
#|____/ \___/|_| \_|












# _    _   _ __  __ ___ _____ ____  _____ 
#| |  | | | |  \/  |_ _| ____|  _ \| ____|
#| |  | | | | |\/| || ||  _| | |_) |  _|  
#| |__| |_| | |  | || || |___|  _ <| |___ 
#|_____\___/|_|  |_|___|_____|_| \_\_____|







# Lumière du soleil    
soleil = DirectionalLight()
soleil.look_at(Vec3(1, -1, -1))
soleil.color = color.rgb(25, 25,25  )

# Lumière ambiante
ambient_light = AmbientLight()
ambient_light.color = color.rgb(0, 0, 0)

# Ciel
sky = Sky()
sky.color=color.white 


# Lancement de l'application
app.run()