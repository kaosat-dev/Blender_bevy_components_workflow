import os
import bpy


from .preferences import (AutoExportGltfPreferenceNames)
from .helpers_scenes import (generate_hollow_scene, clear_hollow_scene)
from .helpers_collections import (recurLayerCollection)
from .blueprints import clear_blueprint_hollow_scene, generate_blueprint_hollow_scene
from .helpers import (traverse_tree)
from .dynamic import (is_object_dynamic, is_object_static)

######################################################
#### Export logic #####


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
        export_animations=False
    )
        
    for key in addon_prefs.__annotations__.keys():
        if str(key) not in AutoExportGltfPreferenceNames:
            #print("overriding setting", key, "value", getattr(addon_prefs,key))
            gltf_export_preferences[key] = getattr(addon_prefs,key)

    return gltf_export_preferences

# find which of the library scenes the given collection stems from
# TODO: does not seem efficient at all ?
def get_source_scene(collection_name, library_scenes): 
    match = None
    for scene in library_scenes:
        root_collection = scene.collection
        found = False
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name == collection_name:
                found = True
                break
        if found:
            match = scene
            break
    return match

# export collections: all the collections that have an instance in the main scene AND any marked collections, even if they do not have instances
def export_collections(collections, folder_path, library_scene, addon_prefs, gltf_export_preferences, blueprint_hierarchy, library_collections): 
    # set active scene to be the library scene (hack for now)
    bpy.context.window.scene = library_scene
    # save current active collection
    active_collection =  bpy.context.view_layer.active_layer_collection
    export_materials_library = getattr(addon_prefs,"export_materials_library")

    for collection_name in collections:
        print("exporting collection", collection_name)
        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, collection_name)
        # set active collection to the collection
        bpy.context.view_layer.active_layer_collection = layerColl
        gltf_output_path = os.path.join(folder_path, collection_name)

        export_settings = { **gltf_export_preferences, 'use_active_scene': True, 'use_active_collection': True, 'use_active_collection_with_nested':True}
        
        # if we are using the material library option, do not export materials, use placeholder instead
        if export_materials_library:
            export_settings['export_materials'] = 'PLACEHOLDER'


        #if relevant we replace sub collections instances with placeholders too
        # this is not needed if a collection/blueprint does not have sub blueprints or sub collections
        collection_in_blueprint_hierarchy = collection_name in blueprint_hierarchy and len(blueprint_hierarchy[collection_name]) > 0
        collection_has_child_collections = len(bpy.data.collections[collection_name].children) > 0
        if collection_in_blueprint_hierarchy or collection_has_child_collections:
            #print("generate hollow scene for nested blueprints", library_collections)
            backup = bpy.context.window.scene
            collection = bpy.data.collections[collection_name]
            (hollow_scene, temporary_collections, root_objects, special_properties) = generate_blueprint_hollow_scene(collection, library_collections, addon_prefs)

            export_gltf(gltf_output_path, export_settings)

            clear_blueprint_hollow_scene(hollow_scene, collection, temporary_collections, root_objects, special_properties)
            bpy.context.window.scene = backup
        else:
            #print("standard export")
            export_gltf(gltf_output_path, export_settings)

    
    # reset active collection to the one we save before
    bpy.context.view_layer.active_layer_collection = active_collection


def export_blueprints_from_collections(collections, library_scene, folder_path, addon_prefs, blueprint_hierarchy, library_collections):
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_blueprints_path = os.path.join(folder_path, export_output_folder, getattr(addon_prefs,"export_blueprints_path")) if getattr(addon_prefs,"export_blueprints_path") != '' else folder_path

    #print("-----EXPORTING BLUEPRINTS----")
    #print("LIBRARY EXPORT", export_blueprints_path )

    try:
        export_collections(collections, export_blueprints_path, library_scene, addon_prefs, gltf_export_preferences, blueprint_hierarchy, library_collections)
    except Exception as error:
        print("failed to export collections to gltf: ", error)
        # TODO : rethrow


# export all main scenes
def export_main_scenes(scenes, folder_path, addon_prefs): 
    for scene in scenes:
        export_main_scene(scene, folder_path, addon_prefs)

def export_main_scene(scene, folder_path, addon_prefs, library_collections): 
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    export_blueprints = getattr(addon_prefs,"export_blueprints")
    split_out_dynamic_collections = getattr(addon_prefs, "split_out_dynamic_collections")
    
    gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name)
    export_settings = { **gltf_export_preferences, 
                       'use_active_scene': True, 
                       'use_active_collection':True, 
                       'use_active_collection_with_nested':True,  
                       'use_visible': False,
                       'use_renderable': False,
                       'export_apply':True
                       }

    if export_blueprints : 
        if split_out_dynamic_collections:
            # first export all dynamic objects
            (hollow_scene, temporary_collections, root_objects, special_properties) = generate_hollow_scene(scene, library_collections, addon_prefs, is_object_dynamic) 
            gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name+ "_dynamic")
            # set active scene to be the given scene
            bpy.context.window.scene = hollow_scene
            print("       exporting gltf to", gltf_output_path, ".gltf/glb")
            export_gltf(gltf_output_path, export_settings)
            clear_hollow_scene(hollow_scene, scene, temporary_collections, root_objects, special_properties)

            # now export static objects
            (hollow_scene, temporary_collections, root_objects, special_properties) = generate_hollow_scene(scene, library_collections, addon_prefs, is_object_static) 
            gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name)
            # set active scene to be the given scene
            bpy.context.window.scene = hollow_scene
            print("       exporting gltf to", gltf_output_path, ".gltf/glb")
            export_gltf(gltf_output_path, export_settings)
            clear_hollow_scene(hollow_scene, scene, temporary_collections, root_objects, special_properties)

        else:
            # todo: add exception handling
            (hollow_scene, temporary_collections, root_objects, special_properties) = generate_hollow_scene(scene, library_collections, addon_prefs) 
            # set active scene to be the given scene
            bpy.context.window.scene = hollow_scene
            print("       exporting gltf to", gltf_output_path, ".gltf/glb")
            export_gltf(gltf_output_path, export_settings)

            clear_hollow_scene(hollow_scene, scene, temporary_collections, root_objects, special_properties)
    else:
        print("       exporting gltf to", gltf_output_path, ".gltf/glb")
        export_gltf(gltf_output_path, export_settings)


#https://docs.blender.org/api/current/bpy.ops.export_scene.html#bpy.ops.export_scene.gltf
def export_gltf (path, export_settings):
    settings = {**export_settings, "filepath": path}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(**settings)


