import bpy
import os
import json

bl_info = {
    "name": "FBX Mesh Exporter with Accurate Details",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "File > Export > Export FBX Mesh with Details",
    "description": "Exports meshes to FBX files and records their texture space details.",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

class ExportMeshesToFBXWithDetails(bpy.types.Operator):
    bl_idname = "export_meshes.to_fbx_with_details"
    bl_label = "Export Meshes to FBX with Details"
    bl_options = {'REGISTER', 'UNDO'}

    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if not self.directory:
            self.report({'ERROR'}, "Directory path not provided.")
            return {'CANCELLED'}

        destination_folder = os.path.abspath(self.directory)
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Exporter les objets en FBX
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                base_name = obj.name.split('.')[0]  # Nettoyer le nom de l'objet

                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)

                export_path = os.path.join(destination_folder, f"{base_name}.fbx")

                # Assurez-vous que le fichier n'existe pas déjà
                if os.path.exists(export_path):
                    self.report({'WARNING'}, f"File {base_name}.fbx already exists and will be overwritten.")

                bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True)
                obj.select_set(False)

        # Appeler la fonction d'extraction des détails après avoir exporté les FBX
        self.export_texture_details(destination_folder)

        return {'FINISHED'}

    def export_texture_details(self, destination_folder):
        mesh_details = {}

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                # Assurez-vous que nous sommes en mode Objet
                if bpy.context.object.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')

                obj_name = obj.name

                # Initialisation des valeurs de texture space location
                texture_space_location = {"x": 0.0, "y": 0.0, "z": 0.0}
                texture_space_size = {"x": 0.0, "y": 0.0, "z": 0.0}

                # Assurez-vous que l'objet est visible pour éviter les problèmes de données cachées
                if obj.hide_get() or obj.hide_viewport:
                    self.report({'WARNING'}, f"Object {obj_name} is hidden. Skipping.")
                    continue

                # Vérifiez si des UV maps existent et extrayez les coordonnées UV si disponibles
                if obj.data.uv_layers:
                    uv_layer = obj.data.uv_layers.active
                    if uv_layer.data:
                        # Calcul des coordonnées UV
                        min_x = float('inf')
                        min_y = float('inf')
                        max_x = float('-inf')
                        max_y = float('-inf')
                        min_z = float('inf')
                        max_z = float('-inf')

                        for poly in obj.data.polygons:
                            for loop_index in poly.loop_indices:
                                uv = uv_layer.data[loop_index].uv
                                min_x = min(min_x, uv[0])
                                min_y = min(min_y, uv[1])
                                max_x = max(max_x, uv[0])
                                max_y = max(max_y, uv[1])
                                # Nous n'avons pas de coordonnées Z dans UV, donc nous utilisons les coordonnées du sommet
                                min_z = float('inf')
                                max_z = float('-inf')
                                for vert in obj.data.vertices:
                                    world_coord = obj.matrix_world @ vert.co
                                    min_z = min(min_z, world_coord.z)
                                    max_z = max(max_z, world_coord.z)

                        texture_space_location = {
                            "x": min_x,
                            "y": min_y,
                            "z": (min_z + max_z) / 2.0
                        }
                        texture_space_size = {
                            "x": max_x - min_x,
                            "y": max_y - min_y,
                            "z": max_z - min_z
                        }
                else:
                    # Utilisez les coordonnées de l'objet si UV maps ne sont pas disponibles
                    if obj.data.vertices:
                        min_x = min_y = min_z = float('inf')
                        max_x = max_y = max_z = float('-inf')

                        for vert in obj.data.vertices:
                            world_coord = obj.matrix_world @ vert.co
                            min_x = min(min_x, world_coord.x)
                            min_y = min(min_y, world_coord.y)
                            min_z = min(min_z, world_coord.z)
                            max_x = max(max_x, world_coord.x)
                            max_y = max(max_y, world_coord.y)
                            max_z = max(max_z, world_coord.z)

                        texture_space_location = {
                            "x": (min_x + max_x) / 2.0,
                            "y": (min_y + max_y) / 2.0,
                            "z": (min_z + max_z) / 2.0
                        }
                        texture_space_size = {
                            "x": max_x - min_x,
                            "y": max_y - min_y,
                            "z": max_z - min_z
                        }
                    else:
                        # Si aucun sommet n'est trouvé, utiliser la position de l'objet comme dernier recours
                        texture_space_location = {
                            "x": obj.location.x,
                            "y": obj.location.y,
                            "z": obj.location.z
                        }

                mesh_details[obj_name] = {
                    "texture_space": {
                        "location": texture_space_location,
                        "size": texture_space_size
                    }
                }

        # Sauvegarder les détails dans un fichier JSON
        details_path = os.path.join(destination_folder, "mesh_details.json")
        try:
            with open(details_path, "w") as f:
                json.dump(mesh_details, f, indent=4)
            self.report({'INFO'}, f"Details saved to {details_path}")
        except IOError as e:
            self.report({'ERROR'}, f"Failed to write JSON file: {e}")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_export(self, context):
    self.layout.operator(ExportMeshesToFBXWithDetails.bl_idname, text="Export Meshes to FBX with Details")

def register():
    bpy.utils.register_class(ExportMeshesToFBXWithDetails)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportMeshesToFBXWithDetails)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
