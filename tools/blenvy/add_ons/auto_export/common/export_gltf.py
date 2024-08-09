import json
import os
import bpy

from ....settings import load_settings

def get_standard_exporter_settings():
    standard_gltf_exporter_settings = load_settings(".blenvy_gltf_settings")
    return standard_gltf_exporter_settings if standard_gltf_exporter_settings is not None else {}

def generate_gltf_export_settings(settings): 
    # default values
    gltf_export_settings = dict(
        # export_format= 'GLB', #'GLB', 'GLTF_SEPARATE', 'GLTF_EMBEDDED'
        check_existing=False,

        use_selection=False,
        use_visible=True, # Export visible and hidden objects. See Object/Batch Export to skip.
        use_renderable=False,
        use_active_collection= False,
        use_active_collection_with_nested=False,
        use_active_scene = False,

        export_cameras=True,
        export_extras=True, # For custom exported properties.
        export_lights=True,
        export_hierarchy_full_collections=False

        #export_texcoords=True,
        #export_normals=True,
        # here add draco settings
        #export_draco_mesh_compression_enable = False,

        #export_tangents=False,
        #export_materials
        #export_colors=True,
        #export_attributes=True,
        #use_mesh_edges
        #use_mesh_vertices
       
        
        #export_yup=True,
        #export_skins=True,
        #export_morph=False,
        #export_apply=False,
        #export_animations=False,
        #export_optimize_animation_size=False
    )
        
    """for key in settings.__annotations__.keys():
        if str(key) not in AutoExportGltfPreferenceNames:
            #print("overriding setting", key, "value", getattr(settings,key))
            pass#gltf_export_settings[key] = getattr(settings, key)"""


    standard_gltf_exporter_settings = get_standard_exporter_settings()
    
    # these essential params should NEVER be overwritten , no matter the settings of the standard exporter
    constant_keys = [
        'use_selection',
        'use_visible',
        'use_active_collection',
        'use_active_collection_with_nested',
        'use_active_scene',
        'export_cameras',
        'export_extras', # For custom exported properties.
        'export_lights',
        'export_hierarchy_full_collections'
    ]

    #  
    for key in standard_gltf_exporter_settings.keys():
        if str(key) not in constant_keys:
            gltf_export_settings[key] =  standard_gltf_exporter_settings.get(key)

    #print("GLTF EXPORT SETTINGS", gltf_export_settings)
    return gltf_export_settings


#https://docs.blender.org/api/current/bpy.ops.export_scene.html#bpy.ops.export_scene.gltf
def export_gltf (path, gltf_export_settings):
    settings = {**gltf_export_settings, "filepath": path}
    # print("export settings",settings)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(**settings)

