import os
import posixpath
from ..core.helpers_collections import (traverse_tree)
from ..add_ons.bevy_components.components.metadata import apply_propertyGroup_values_to_item_customProperties_for_component, upsert_bevy_component, get_bevy_component_value_by_long_name

def find_materials_not_on_disk(materials, materials_path_full, extension):
    not_found_materials = []
    for material in materials:
        gltf_output_path = os.path.join(materials_path_full, material.name + extension)
        # print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_materials.append(material)
    return not_found_materials

def check_if_material_on_disk(scene_name, folder_path, extension):
    gltf_output_path = os.path.join(folder_path, scene_name + extension)
    found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
    return found


# get materials per object, and injects the materialInfo component
def get_materials(object, materials_per_object):
    material_slots = object.material_slots
    used_materials_names = []
   
    if not hasattr(object, "data"):
        return used_materials_names
    if not hasattr(object.data,"materials"):
        return used_materials_names
    if len(object.data.materials) == 0:
        return used_materials_names
    
    # since we are scanning polygons to get the actually used materials, we do not get them in the correct order
    materials_per_object_unordered = []

    """materials_count = len(material_slots)
    print("materials_count", materials_count)
    material_indices = np.empty(materials_count, dtype=np.int64)
    object.data.polygons.foreach_get("material_index", material_indices)
    #for material_index in object.data.polygons.foreach_get("material_index", storage):
    print("polygon material_indices", material_indices)"""
    # TODO: perhaps optimise it using foreach_get
    for polygon in object.data.polygons:
        slot = material_slots[polygon.material_index]
        material = slot.material
        if not material.name in used_materials_names:
            used_materials_names.append(material.name)
            materials_per_object_unordered.append((material, polygon.material_index))

        if len(used_materials_names) == len(material_slots): # we found all materials, bail out
            break

    # now re-order the materials as per the object's material slots 
    sorted_materials = sorted(materials_per_object_unordered, key=lambda tup: tup[1])

    # and add them
    if not object in materials_per_object:
        materials_per_object[object] = []
    materials_per_object[object] = [material[0] for material in sorted_materials]#.append(material)

    """for m in material_slots:
        material = m.material"""

    return used_materials_names


def get_all_materials(collection_names, library_scenes): 
    used_material_names = []
    materials_per_object = {}

    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                for object in cur_collection.all_objects:
                    used_material_names = used_material_names + get_materials(object, materials_per_object)

    # we only want unique names
    used_material_names = list(set(used_material_names))
    return (used_material_names, materials_per_object)

import bpy
def add_material_info_to_objects(materials_per_object, settings):
    materials_path =  getattr(settings, "materials_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    for object in materials_per_object.keys():
        material_infos = []
        for material in materials_per_object[object]:
            materials_exported_path = posixpath.join(materials_path, f"{material.name}{export_gltf_extension}")
            material_info = f'(name: "{material.name}", path: "{materials_exported_path}")' 
            material_infos.append(material_info)
        # problem with using actual components: you NEED the type registry/component infos, so if there is none , or it is not loaded yet, it does not work
        # for a few components we could hardcode this
        component_value = f"({material_infos})".replace("'","")
        try:
            bpy.ops.blenvy.component_add(target_item_name=object.name, target_item_type="OBJECT", component_type="blenvy::blueprints::materials::MaterialInfos", component_value=component_value )
        except:
            object['MaterialInfos'] = f"({material_infos})".replace("'","") 
            #upsert_bevy_component(object, "blenvy::blueprints::materials::MaterialInfos", f"({material_infos})".replace("'","") )
            #apply_propertyGroup_values_to_item_customProperties_for_component(object, "MaterialInfos")
        print("adding materialInfos to object", object, "material infos", material_infos)


# get all the materials of all objects in a given scene
def get_scene_materials(scene):
    used_material_names = []
    materials_per_object = {}

    root_collection = scene.collection
    for cur_collection in traverse_tree(root_collection):
        for object in cur_collection.all_objects:
            used_material_names = used_material_names + get_materials(object, materials_per_object)

    # we only want unique names
    used_material_names = list(set(used_material_names))
    return (used_material_names, materials_per_object)

# get all the materials of all objects used by a given blueprint
def get_blueprint_materials(blueprint):
    materials_per_object = {}
    used_material_names = []

    for object in blueprint.collection.all_objects:
        used_material_names = used_material_names + get_materials(object, materials_per_object)
    
    # we only want unique names
    used_material_names = list(set(used_material_names))
    return (used_material_names, materials_per_object)
