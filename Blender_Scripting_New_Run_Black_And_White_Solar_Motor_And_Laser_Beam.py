import bpy
import math
from mathutils import Vector

def create_generator():
    # Créer la base du générateur
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=1, location=(0, 0, 0))
    generator = bpy.context.object
    generator.name = "GeneratorBase"
    
    # Positionner le générateur plus haut
    generator.location = (1, 1, 2)  # Déplacement en diagonale et en hauteur

    # Créer les hélices triangulaires
    blade_length = 3.0
    blade_thickness = 0.05
    for i in range(4):
        angle = i * math.pi / 2
        # Création d'une hélice triangulaire
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=blade_length, depth=blade_thickness, location=(0, 0, blade_length / 2))
        blade = bpy.context.object
        blade.rotation_euler = (0, 0, angle)  # Rotation autour de l'axe Z pour les hélices
        blade.parent = generator

        # Positionner les hélices correctement autour du générateur
        blade.location = (blade_length / 2 * math.cos(angle), blade_length / 2 * math.sin(angle), 0.5)
        
        # Ajouter un matériau aux hélices
        blade_material = bpy.data.materials.new(name=f"BladeMaterial_{i}")
        blade_material.diffuse_color = (0.1, 0.1, 0.1, 1) if i % 2 == 0 else (0.9, 0.9, 0.9, 1)  # Alternating black and white
        blade.data.materials.append(blade_material)

    # Créer la base du capteur solaire sous le générateur
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.7, depth=0.1, location=(0, 0, 0))
    solar_base = bpy.context.object
    solar_base.name = "SolarBase"

    # Créer un matériau pour la base du capteur solaire
    solar_material = bpy.data.materials.new(name="SolarBaseMaterial")
    solar_material.diffuse_color = (0.8, 0.8, 0.0, 1)  # Jaune pour simuler le panneau solaire
    solar_base.data.materials.append(solar_material)

    return generator, solar_base

def animate_generator(generator):
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250

    # Animation des hélices (rotation complète autour du moteur)
    for i, blade in enumerate(generator.children):
        blade.rotation_euler = (0, 0, 0)  # Position initiale
        blade.keyframe_insert(data_path="rotation_euler", frame=1)
        blade.rotation_euler = (0, 0, math.radians(360))  # Rotation complète
        blade.keyframe_insert(data_path="rotation_euler", frame=250)

def setup_camera():
    bpy.ops.object.camera_add(location=(10, -10, 5))
    camera = bpy.context.object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    bpy.context.scene.camera = camera

def add_light():
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
    light = bpy.context.object
    light.name = "Sun"
    return light

def create_laser(generator, solar_base):
    # Position du capteur solaire
    solar_pos = solar_base.location
    
    # Créer le rayon laser
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=1, location=generator.location)
    laser = bpy.context.object
    laser.name = "LaserBeam"

    # Calculer la direction du laser
    direction = (solar_pos - generator.location).normalized()
    distance = (solar_base.location - generator.location).length

    # Aligner le laser avec le solar_base
    laser.scale = (1, 1, distance / 2)
    laser.location = generator.location + direction * (distance / 2)
    laser.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

    # Créer un matériau rouge pour le laser
    laser_material = bpy.data.materials.new(name="LaserMaterial")
    laser_material.diffuse_color = (1, 0, 0, 1)
    laser.data.materials.append(laser_material)

def update_laser(generator, solar_base):
    laser = bpy.data.objects.get("LaserBeam")
    if laser:
        # Recalculer la direction du laser pour qu'il soit aligné avec le solar_base
        direction = (solar_base.location - generator.location).normalized()
        distance = (solar_base.location - generator.location).length
        laser.scale = (1, 1, distance / 2)
        laser.location = generator.location + direction * (distance / 2)
        laser.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

def add_track_to_constraint(obj, target):
    constraint = obj.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_Z'
    constraint.up_axis = 'UP_Y'

def create_scene():
    generator, solar_base = create_generator()
    animate_generator(generator)
    setup_camera()
    light = add_light()
    create_laser(generator, solar_base)
    
    # Ajouter la contrainte de suivi pour que le générateur fasse face à la lumière
    add_track_to_constraint(generator, light)

# Créer la scène
create_scene()

# Fonction pour mettre à jour le laser lorsque le générateur se déplace
def update_scene():
    generator = bpy.data.objects.get("GeneratorBase")
    solar_base = bpy.data.objects.get("SolarBase")
    if generator and solar_base:
        update_laser(generator, solar_base)

# Mettre à jour le laser après avoir déplacé le générateur
update_scene()

print("Générateur avec hélices triangulaires, base de capteur solaire, faisceau laser aligné avec le solar_base, et hélices correctement orientées créés avec succès.")
