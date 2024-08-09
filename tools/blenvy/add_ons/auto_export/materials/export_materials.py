import os
import bpy
from ....core.helpers_collections import traverse_tree
from ....core.object_makers import make_cube
from ..common.generate_temporary_scene_and_export import generate_temporary_scene_and_export
from ..common.export_gltf import (generate_gltf_export_settings)

# material library logic
# To avoid redundant materials (can be very costly, mostly when using high res textures)
# - we explore a gltf file containing all materials from a blend file
# - we add materialInfo component to each object that uses one of the materials, so that "what material is used by which object" is preserved
#

def clear_material_info(collection_names, library_scenes):
    pass
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                for object in cur_collection.all_objects:
                    if 'MaterialInfo' in dict(object): # FIXME: hasattr does not work ????
                        del object["MaterialInfo"]
                   
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
    return object


# generates a materials scene: 
def generate_materials_scene_content(root_collection, used_material_names):
    for index, material_name in enumerate(used_material_names):
        material = bpy.data.materials[material_name]
        make_material_object("Material_"+material_name, [index * 0.2,0,0], material=material, collection=root_collection)
    return {}

# generates a scene for a given material
def generate_material_scene_content(root_collection, material_name):
    material = bpy.data.materials[material_name]
    make_material_object(f"Material_{material_name}", [0,0,0], material=material, collection=root_collection)
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
def export_materials(materials_to_export, settings, blueprints_data):
    gltf_export_settings = generate_gltf_export_settings(settings)
    materials_path_full = getattr(settings,"materials_path_full")

    gltf_export_settings = { **gltf_export_settings, 
                    'use_active_scene': True, 
                    'use_active_collection':True, 
                    'use_active_collection_with_nested':True,  
                    'use_visible': False,
                    'use_renderable': False,
                    'export_apply':True
                    }

    for material in materials_to_export:
        print("exporting material", material.name)
        gltf_output_path = os.path.join(materials_path_full, material.name)

        generate_temporary_scene_and_export(
            settings=settings, 
            gltf_export_settings=gltf_export_settings,
            temp_scene_name="__materials_scene",
            gltf_output_path=gltf_output_path,
            tempScene_filler= lambda temp_collection: generate_material_scene_content(temp_collection, material.name),
            tempScene_cleaner= lambda temp_scene, params: clear_materials_scene(temp_scene=temp_scene)
        )

    
def cleanup_materials(collections, library_scenes):
    # remove temporary components
    clear_material_info(collections, library_scenes)