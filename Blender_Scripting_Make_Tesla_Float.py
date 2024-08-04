import bpy
import math

# Fonction pour créer et ajouter un texte à une position donnée
def add_text(text, location, size=1):
    bpy.ops.object.text_add(location=location)
    text_obj = bpy.context.object
    text_obj.data.body = text
    text_obj.scale = (size, size, size)
    text_obj.rotation_euler[0] = math.radians(90)  # Rotation pour aligner le texte verticalement
    bpy.context.view_layer.update()  # Assurer que les mises à jour sont visibles
    return text_obj

# Fonction pour créer le matériau en verre
def create_glass_material():
    glass_material = bpy.data.materials.new(name="GlassMaterial")
    glass_material.use_nodes = True
    nodes = glass_material.node_tree.nodes
    links = glass_material.node_tree.links
    
    # Supprimer les nœuds existants
    for node in nodes:
        nodes.remove(node)
    
    # Ajouter des nœuds pour créer le matériau en verre
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Transmission'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.1
    bsdf.inputs['IOR'].default_value = 1.45
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Relier les nœuds
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return glass_material

# Fonction pour créer le générateur avec les composants et les étiquettes
def create_generator():
    # Créer le tube (corps du générateur) avec matériau en verre
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=4, location=(0, 0, 2))
    tube = bpy.context.object
    tube.name = "Tube"
    glass_material = create_glass_material()
    if len(tube.data.materials) == 0:
        tube.data.materials.append(glass_material)
    else:
        tube.data.materials[0] = glass_material

    # Créer le ressort collé au disque, juste au-dessus sans le traverser
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.3, depth=0.6, location=(0, 0, 0.1))
    spring = bpy.context.object
    spring.name = "Spring"
    spring.modifiers.new(name='Screw', type='SCREW')
    spring.modifiers['Screw'].angle = math.pi * 4
    spring.modifiers['Screw'].screw_offset = 1.0

    # Créer l'aimant à l'intérieur du tube, centré sur le ressort
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.4, depth=0.8, location=(0, 0, 1.5))
    magnet = bpy.context.object
    magnet.name = "Magnet"

    # Créer la corde d'ancrage traversant le ressort et touchant l'aimant et l'ancre
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.05, depth=7.0, location=(0, 0, -2.0))  # Longueur augmentée
    anchor_rope = bpy.context.object
    anchor_rope.name = "AnchorRope"

    # Créer l'ancre au bout de la corde
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.2, radius2=0, depth=0.5, location=(0, 0, -5.5))  # Position ajustée pour toucher le câble
    anchor = bpy.context.object
    anchor.name = "Anchor"

    # Créer plusieurs fils de cuivre autour du tube, légèrement abaissés pour que l'aimant soit au centre
    for i in range(5):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.05, location=(0, 0, 2.5 - i * 0.5))
        wire_copper = bpy.context.object
        wire_copper.name = f"WireCopper_{i}"

    # Ajouter les étiquettes
    add_text("Tube", location=(0, 0, 4.2), size=0.3)
    add_text("Spring", location=(0, 0, 0.1), size=0.3)
    add_text("Magnet", location=(0, 0, 1.5), size=0.3)
    add_text("Anchor Rope", location=(0.2, 0, -2.0), size=0.3)
    add_text("Anchor", location=(0, 0, -7.0), size=0.3)
    for i in range(5):
        add_text(f"Wire Copper {i+1}", location=(0.8, 0, 2.5 - i * 0.5), size=0.2)

    return tube, magnet, spring

# Fonction pour créer le disque flottant
def create_floating_disc():
    # Créer le disque
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=3, depth=0.1, location=(0, 0, 0))
    disc = bpy.context.object
    disc.name = "TeslaFloat"
    add_text("Bouée Tesla", location=(0, 0, 0.2), size=0.3)

    # Créer une bouée sur le disque
    bpy.ops.mesh.primitive_torus_add(major_radius=2.5, minor_radius=0.3, location=(0, 0, 0.1))
    buoy = bpy.context.object
    buoy.name = "PlasticBuoy"
    add_text("Plastic Buoy", location=(2.8, 0, 0.5), size=0.3)

    return disc

# Fonction pour animer le disque flottant et l'aimant avec les vagues
def animate_floating_disc_and_magnet(disc, magnet):
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250

    # Animation par image clé pour le mouvement de flottement
    for frame in range(1, 251):
        z_offset = 0.2 * math.sin(math.radians(frame * 3.6))
        x_offset = 0.1 * math.cos(math.radians(frame * 3.6))  # Mouvement latéral pour simuler les vagues
        disc.location.z = z_offset
        disc.location.x = x_offset
        disc.keyframe_insert(data_path="location", index=2, frame=frame)
        disc.keyframe_insert(data_path="location", index=0, frame=frame)  # Pour l'axe X aussi

        # Assurer que l'aimant suit le disque
        magnet.location.z = 1.5 + z_offset
        magnet.location.x = x_offset
        magnet.keyframe_insert(data_path="location", index=2, frame=frame)
        magnet.keyframe_insert(data_path="location", index=0, frame=frame)  # Pour l'axe X aussi

# Fonction pour configurer la caméra
def setup_camera():
    bpy.ops.object.camera_add(location=(10, -10, 5))
    camera = bpy.context.object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    bpy.context.scene.camera = camera

# Fonction pour ajouter de la lumière à la scène
def add_light():
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
    light = bpy.context.object
    light.name = "Sun"

# Fonction principale pour créer la scène
def create_scene():
    tube, magnet, spring = create_generator()
    disc = create_floating_disc()
    animate_floating_disc_and_magnet(disc, magnet)
    setup_camera()
    add_light()

# Créer la scène
create_scene()

print("Scène créée avec succès avec le tube en verre transparent, les composants étiquetés, et l'animation du disque flottant.")
