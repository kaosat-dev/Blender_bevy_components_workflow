import os
import bpy

from .get_standard_exporter_settings import get_standard_exporter_settings
from .preferences import (AutoExportGltfPreferenceNames)

def generate_gltf_export_preferences(addon_prefs): 
    # default values
    gltf_export_preferences = dict(
        export_format= 'GLB', #'GLB', 'GLTF_SEPARATE', 'GLTF_EMBEDDED'
        check_existing=False,

        use_selection=False,
        use_visible=True, # Export visible and hidden objects. See Object/Batch Export to skip.
        use_renderable=False,
        use_active_collection= False,
        use_active_collection_with_nested=False,
        use_active_scene = False,

        export_texcoords=True,
        export_normals=True,
        # here add draco settings
        export_draco_mesh_compression_enable = False,

        export_tangents=False,
        #export_materials
        export_colors=True,
        export_attributes=True,
        #use_mesh_edges
        #use_mesh_vertices
        export_cameras=True,
        export_extras=True, # For custom exported properties.
        export_lights=True,
        export_yup=True,
        export_skins=True,
        export_morph=False,
        export_apply=False,
        export_animations=False,
        export_optimize_animation_size=False
    )
        

   

    for key in addon_prefs.__annotations__.keys():
        if str(key) not in AutoExportGltfPreferenceNames:
            #print("overriding setting", key, "value", getattr(addon_prefs,key))
            gltf_export_preferences[key] = getattr(addon_prefs, key)


    """standard_gltf_exporter_settings = get_standard_exporter_settings()
    print("standard settings", standard_gltf_exporter_settings)
    
    constant_keys = [
        'export_cameras',
        'export_extras', # For custom exported properties.
        'export_lights',
    ]

    # a certain number of essential params should NEVER be overwritten , no matter the settings of the standard exporter
    for key in standard_gltf_exporter_settings.keys():
        if str(key) not in constant_keys:
            gltf_export_preferences[key] =  standard_gltf_exporter_settings.get(key)

    print("final export preferences", gltf_export_preferences)"""


    return gltf_export_preferences


#https://docs.blender.org/api/current/bpy.ops.export_scene.html#bpy.ops.export_scene.gltf
def export_gltf (path, export_settings):
    settings = {**export_settings, "filepath": path}
    # print("export settings",settings)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(**settings)
