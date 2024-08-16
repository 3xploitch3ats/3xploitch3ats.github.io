import bpy

# Réinitialiser la scène
bpy.ops.wm.read_factory_settings(use_empty=True)

# Ajouter un prisme triangulaire à 4 faces (Prisme avec base triangulaire)
bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=1, depth=2, location=(0, 0, 0))
prisme = bpy.context.view_layer.objects.active
prisme.name = "Prisme_Triangulaire_4_Faces"

# Lissage du prisme pour éviter les facettes visibles
bpy.ops.object.shade_smooth()

# Création du matériau "Verre Miroir Interrogatoire"
material = bpy.data.materials.new(name="Verre_Miroir_Interrogatoire")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Effacer les nodes par défaut
for node in nodes:
    nodes.remove(node)

# Ajouter le node "Output Material"
output_node = nodes.new(type='ShaderNodeOutputMaterial')

# Création du shader Glass pour le verre transparent
glass_node = nodes.new(type='ShaderNodeBsdfGlass')
glass_node.inputs['IOR'].default_value = 1.5  # Indice de réfraction pour le verre
glass_node.inputs['Color'].default_value = (1, 1, 1, 0.1)  # Légère transparence pour l'effet interrogatoire

# Création du shader Glossy pour l'effet miroir interne
glossy_node = nodes.new(type='ShaderNodeBsdfGlossy')
glossy_node.inputs['Roughness'].default_value = 0.0  # Miroir parfait

# Ajouter un node Shader Mix pour combiner les deux shaders
mix_shader = nodes.new(type='ShaderNodeMixShader')

# Configurer les liens entre les nodes
links.new(glass_node.outputs['BSDF'], mix_shader.inputs[1])
links.new(glossy_node.outputs['BSDF'], mix_shader.inputs[2])
links.new(mix_shader.outputs['Shader'], output_node.inputs['Surface'])

# Ajouter un node Geometry pour déterminer la face interne
geometry_node = nodes.new(type='ShaderNodeNewGeometry')

# Le node Mix Shader utilise la facette arrière pour appliquer le shader Glossy à l'intérieur
links.new(geometry_node.outputs['Backfacing'], mix_shader.inputs['Fac'])

# Assigner le matériau au prisme triangulaire
prisme.data.materials.append(material)

# Ajouter une lumière à l'intérieur du prisme pour simuler la lumière réfléchie infinie
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
light = bpy.context.view_layer.objects.active
light.name = "Lumiere_Interne"
light.data.energy = 1000  # Intensité de la lumière pour l'effet visuel
light.data.color = (1.0, 0.9, 0.8)  # Couleur légèrement chaude

# Configurer la caméra pour capturer la scène
bpy.ops.object.camera_add(location=(4, -4, 2), rotation=(1.109, 0, 0.785))
camera = bpy.context.view_layer.objects.active
camera.name = "Camera_Interrogatoire"

# Pointer la caméra vers le prisme
bpy.context.scene.camera = camera
camera.data.lens = 50  # Longueur focale de la caméra

# Créer un monde si nécessaire et configurer les nœuds
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new(name="World")
    
bpy.context.scene.world.use_nodes = True
world = bpy.context.scene.world.node_tree.nodes
world_links = bpy.context.scene.world.node_tree.links

# Effacer les nodes par défaut du monde
for node in world:
    world.remove(node)

# Ajouter un fond HDRI pour l'environnement
background_node = world.new(type='ShaderNodeBackground')
background_node.inputs['Color'].default_value = (0.1, 0.1, 0.1, 1)  # Lumière d'environnement faible

world_output = world.new(type='ShaderNodeOutputWorld')
world_links.new(background_node.outputs['Background'], world_output.inputs['Surface'])

# Configurer le moteur de rendu sur Eevee pour des réflexions réalistes
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.eevee.taa_render_samples = 128  # Nombre de samples pour un rendu de meilleure qualité

# Configuration des paramètres de la scène pour le rendu final
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = True  # Rendre le fond transparent

# Configurer la lumière ambiante faible pour renforcer l'effet de miroir interrogatoire
ambient_light = bpy.data.lights.new(name="Ambient_Light", type='AREA')
ambient_light.energy = 50
ambient_light_obj = bpy.data.objects.new(name="Ambient_Light_Obj", object_data=ambient_light)
bpy.context.collection.objects.link(ambient_light_obj)
ambient_light_obj.location = (0, 0, 5)
ambient_light_obj.scale = (5, 5, 1)

# Ajouter une lumière interne visible à l'intérieur du prisme
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
internal_light = bpy.context.view_layer.objects.active
internal_light.name = "Lumiere_Interne_Visible"
internal_light.data.energy = 1000
internal_light.data.color = (1.0, 0.9, 0.8)

# Remarque : La sauvegarde du fichier Blender est omise
print("Configuration terminée.")
