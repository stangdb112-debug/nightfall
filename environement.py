#Projet : Nightfall
#Auteurs : Stanislas Gros de Beler, Paul Berenguer, Nael Arras, Sacha Philipps Herbert, Riadh Jouini

from ursina import *
from math import atan2, pi
from ursina.shaders import basic_lighting_shader,unlit_shader,lit_with_shadows_shader

def create_barrier(point_a, point_b):
    """hyp : la fonction crée une barrière invisible entre deux points avec une orientation correcte."""
    midpoint = (point_a + point_b) / 2  # Position centrale de la barrière
    length = (point_a - point_b).length()  # Longueur de la barrière
    angle = atan2(point_b.z - point_a.z, point_b.x - point_a.x) * 180 / pi  # Correction de l'angle

    # Crée l'entité pour la barrière
    barrier = Entity(
        model='cube',
        scale=(length, 5, 0.5),  # Longueur ajustée, hauteur de 5 unités, épaisseur de 0.5 unités
        position=midpoint,
        rotation=Vec3(0, angle, 0),  # Orientation corrigée
        collider='box',
        visible=False  # Barrière invisible
    )
    return barrier
mur_maison=Entity(model='cube',scale=(20,10,1),position=Vec3(-10.062875, 0.029999949, 24.68852) ,collider='box', visible=False)
def setup_environnement_foret(tree_positions, little_rock_position, middle_rock_position, high_rock_position, white_rock_position, barrier_points):
    """hyp : la fonction initialise l'environnement du jeu (arbres, rochers, barrières, sols, modèles 3D)."""
    
    # Ajouter des troncs d'arbres avec des hitboxes
    trees = [Entity(scale=(0.5, 5, 0.5), position=pos, collider='box') for pos in tree_positions]

    # Ajouter des rochers
    little_rock = [Entity(scale=(1, 1, 1), position=pos, collider='box') for pos in little_rock_position]
    middle_rocks = [Entity(scale=(1.5, 2, 1.5), position=pos, collider='box') for pos in middle_rock_position]
    high_rocks = [Entity(scale=(3, 4, 3), position=pos, collider='box', visible=True) for pos in high_rock_position]
    white_rocks = [Entity(scale=(1.75, 2, 1.75), position=pos, collider='box') for pos in white_rock_position]

    # Crée les barrières
    barriers = [create_barrier(a, b) for a, b in barrier_points]

    

    
    # Maison
    maison = Entity(
        model='data/modele_3D/manoir/manoir.glb',
        position=Vec3(-6.158225, -0.3, 25.497072),
        scale=1,
        skip=1,
        visible=True,
        collider=None,
        color=color.white
    )
    
    return trees, little_rock, middle_rocks, high_rocks, white_rocks, barriers,  maison

def charger_donjon():
    
    floor2 = Entity(model='plane',texture='white_cube',texture_scale=(20, 20),scale=(400, 48, 400),visible=False,position=(0, -1.5, 0),color=color.gray,collider='box')
    sol_cave=[]
    for i in range(1, 46):
        sol = Entity(
            model=f'data/modele_3D/cave/hitbox/hitboxSol/sol{i}glb.glb',
            scale=0.8,
            position=(0, 0, 0),
            collider='box',
            visible=False
        )
        sol_cave.append(sol)
    #Hitbox des murs de la cave et autre
    Mur_cave=[]
    for i in range(1, 163):
        Mur= Entity(
            model=f'data/modele_3D/cave/hitbox/hitboxMurs/mur{i}.glb',
            scale=0.8,
            position=(0, 0, 0),
            collider='box',
            visible=False
        )
        Mur_cave.append(Mur)
    escalier=Entity(model='cube',scale=(4.3,0.1,2),visible=False,rotation=(0,0,-43),position=Vec3(80.01259, 1.3781478, 5.4716076),collider='box')
    donjon=Entity(model='data/modele_3D/cave/cave.glb',scale=0.8,position=(0,0,0))
    cercle_cult=Entity(
        model='quad',
        texture='data/image/cercle_de_cultiste.png',
        scale=10.4,
        double_sided=True,
        color=color.rgba(255,0,0,200),
        shader=unlit_shader,  # Ne réagit pas à la lumière
        rotation=(90,0,45),
        collider=None,
        position=Vec3(49.70985, 0.5203226, 32.182052)
        )
    Mur_cave.append(cercle_cult)
    plateformes=[]
    for i in range(1,26):
        plateforme= Entity(
            model=f'data/modele_3D/cave/hitbox/hitboxJump/plateforme{i}.glb',
            scale=0.8,
            position=(0, 0, 0),
            collider='box',
            visible=True
        )
        plateformes.append(plateforme)
    #Hitbox mort
    pieges = []

    for i in range(1, 28):
        piege = Entity(
            model=f'data/modele_3D/cave/hitbox/hitboxMort/piege{i}.glb',
            scale=0.8,
            position=(0, 0, 0),
            collider='box',
            visible=False
        )
        pieges.append(piege)
    pieges.append(floor2)



    return pieges, escalier, sol_cave, Mur_cave, donjon,

