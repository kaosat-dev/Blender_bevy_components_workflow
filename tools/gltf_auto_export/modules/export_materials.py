import os
import bpy
from pathlib import Path

from ..helpers.generate_and_export import generate_and_export

from ..helpers.helpers_collections import (set_active_collection, traverse_tree)
from ..auto_export.export_gltf import (export_gltf, generate_gltf_export_preferences)
from ..helpers.object_makers import make_cube

# get materials per object, and injects the materialInfo component
def get_materials(object):
    material_slots = object.material_slots
    used_materials_names = []
    #materials_per_object = {}
    current_project_name = Path(bpy.context.blend_data.filepath).stem

    for m in material_slots:
        material = m.material
        # print("    slot", m, "material", material)
        used_materials_names.append(material.name)
        # TODO:, also respect slots & export multiple materials if applicable ! 
        object['MaterialInfo'] = '(name: "'+material.name+'", source: "'+current_project_name + '")' 

    return used_materials_names

def clear_material_info(collection_names, library_scenes):
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                for object in cur_collection.all_objects:
                    if 'MaterialInfo' in dict(object): # FIXME: hasattr does not work ????
                        del object["MaterialInfo"]
                   

def get_all_materials(collection_names, library_scenes): 
    #print("collecton", layerColl, "otot", layerColl.all_objects) #all_objects
    used_material_names = []
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                for object in cur_collection.all_objects:
                    used_material_names = used_material_names + get_materials(object)
    # we only want unique names
    used_material_names = list(set(used_material_names))
    return used_material_names


# creates a new object with the applied material, for the material library
def make_material_object(name, location=[0,0,0], rotation=[0,0,0], scale=[1,1,1], material=None, collection=None): 
    #original_active_object = bpy.context.active_object
    #bpy.ops.mesh.primitive_cube_add(size=0.1, location=location)  
    object = make_cube(name, location=location, rotation=rotation, scale=scale, collection=collection)
    if material:
        if object.data.materials:
            # assign to 1st material slot
            object.data.materials[0] = material
        else:
            # no slots
            object.data.materials.append(material)

    #bpy.context.view_layer.objects.active = original_active_object
    return object


# generates a materials scene: 
def generate_materials_scene_content(root_collection, used_material_names):
    for index, material_name in enumerate(used_material_names):
        material = bpy.data.materials[material_name]
        make_material_object("Material_"+material_name, [index * 0.2,0,0], material=material, collection=root_collection)
    return {}

def clear_materials_scene(temp_scene):
    root_collection = temp_scene.collection 
    scene_objects = [o for o in root_collection.objects]
    for object in scene_objects:
        #print("removing ", object)
        try:
            mesh = bpy.data.meshes[object.name+"_Mesh"]
            bpy.data.meshes.remove(mesh, do_unlink=True)
        except Exception as error:
            pass
            #print("could not remove mesh", error)
            
        try:
            bpy.data.objects.remove(object, do_unlink=True)
        except:pass

    bpy.data.scenes.remove(temp_scene)

# exports the materials used inside the current project:
# the name of the output path is <materials_folder>/<name_of_your_blend_file>_materials_library.gltf/glb
def export_materials(collections, library_scenes, folder_path, addon_prefs):
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_materials_path = getattr(addon_prefs,"export_materials_path")

    used_material_names = get_all_materials(collections, library_scenes)
    current_project_name = Path(bpy.context.blend_data.filepath).stem

    export_settings = { **gltf_export_preferences, 
                    'use_active_scene': True, 
                    'use_active_collection':True, 
                    'use_active_collection_with_nested':True,  
                    'use_visible': False,
                    'use_renderable': False,
                    'export_apply':True
                    }
    gltf_output_path = os.path.join(folder_path, export_materials_path, current_project_name + "_materials_library")

    print("       exporting Materials to", gltf_output_path, ".gltf/glb")

    generate_and_export(
        addon_prefs, 
        temp_scene_name="__materials_scene",
        export_settings=export_settings,
        gltf_output_path=gltf_output_path,
        tempScene_filler= lambda temp_collection: generate_materials_scene_content(temp_collection, used_material_names),
        tempScene_cleaner= lambda temp_scene, params: clear_materials_scene(temp_scene=temp_scene)
    )


def cleanup_materials(collections, library_scenes):
    # remove temporary components
    clear_material_info(collections, library_scenes)