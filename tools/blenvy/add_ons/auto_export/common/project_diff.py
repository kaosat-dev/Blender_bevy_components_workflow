import json
import traceback
import bpy
from .serialize_project import serialize_project
from ....settings import load_settings

def bubble_up_changes(object, changes_per_scene):
    if object is not None and object.parent:
        changes_per_scene[object.parent.name] = bpy.data.objects[object.parent.name]
        bubble_up_changes(object.parent, changes_per_scene)

import uuid
def serialize_current(settings):
    # sigh... you need to save & reset the frame otherwise it saves the values AT THE CURRENT FRAME WHICH CAN DIFFER ACROSS SCENES
    current_frames = [scene.frame_current for scene in bpy.data.scenes]
    """for scene in bpy.data.scenes:
        scene.frame_set(0)
        if scene.id_test == '':
            print("GENERATE ID")
            scene.id_test = str(uuid.uuid4())
        print("SCENE ID", scene.id_test)"""
    #https://blender.stackexchange.com/questions/216411/whats-the-replacement-for-id-or-hash-on-bpy-objects

    current_scene = bpy.context.window.scene
    bpy.context.window.scene = bpy.data.scenes[0]
    #serialize scene at frame 0
    # TODO: add back
    """with bpy.context.temp_override(scene=bpy.data.scenes[1]):
        bpy.context.scene.frame_set(0)"""
    
    current = serialize_project(settings)
    bpy.context.window.scene = current_scene

    # reset previous frames
    for (index, scene) in enumerate(bpy.data.scenes):
        scene.frame_set(int(current_frames[index]))
    
    return current

def get_changes_per_scene(settings):
    previous = load_settings(".blenvy.project_serialized_previous")
    current = serialize_current(settings)

    # so in Blender, there is no uuid per object, hash changes on undo redo, adress/pointer to object may change at any undo / redo without possible way of knowing when
    # so... ugh
    scenes_to_scene_names = {}
    for scene in bpy.data.scenes:
        scenes_to_scene_names[scene] = scene.name
    print("cur scenes_to_scene_names", scenes_to_scene_names)
    print("pre fpp", settings.scenes_to_scene_names)

    scene_renames = {}
    for scene in settings.scenes_to_scene_names:
        if scene in scenes_to_scene_names:
            previous_name_of_scene = settings.scenes_to_scene_names[scene]
            current_name_of_scene = scenes_to_scene_names[scene]
            if previous_name_of_scene != current_name_of_scene:
                scene_renames[current_name_of_scene] = previous_name_of_scene
                print("SCENE RENAMED !previous", previous_name_of_scene, "current", current_name_of_scene)
    print("scene new name to old name", scene_renames)

    # determine changes
    changes_per_scene = {}
    changes_per_collection = {}
    changes_per_material = {}
    try:
        (changes_per_scene, changes_per_collection, changes_per_material) = project_diff(previous, current, scene_renames, settings)
    except Exception as error:
        print(traceback.format_exc())
        print("failed to compare current serialized scenes to previous ones: Error:", error)

    return changes_per_scene, changes_per_collection, changes_per_material, current


def project_diff(previous, current, scene_renames, settings):
    """print("previous", previous)
    print("current", current)"""
    if previous is None or current is None:
        return {}
    
    changes_per_scene = {}
    changes_per_collection = {}
    changes_per_material = {}

    # possible ? on each save, inject an id into each scene, that cannot be copied over
    current_scenes = current["scenes"]
    previous_scenes = previous["scenes"]

    print("previous scenes", previous_scenes.keys())
    print("current scenes", current_scenes.keys())
    print("new names to old names", scene_renames)
    print("")
    for scene_name in current_scenes:
        print("scene name", scene_name, scene_name in scene_renames)
        current_scene = current_scenes[scene_name]
        previous_scene = previous_scenes[scene_name] if not scene_name in scene_renames else previous_scenes[scene_renames[scene_name]]
        current_object_names =list(current_scene.keys())

        updated_scene_name = scene_name if not scene_name in scene_renames else scene_renames[scene_name]
        if updated_scene_name in previous_scenes: # we can only compare scenes that are in both previous and current data, with the above we also account for renames

            previous_object_names = list(previous_scene.keys())
            added =  list(set(current_object_names) - set(previous_object_names))
            removed = list(set(previous_object_names) - set(current_object_names))
            
            for obj in added:
                if not scene_name in changes_per_scene:
                    changes_per_scene[scene_name] = {}
                changes_per_scene[scene_name][obj] = bpy.data.objects[obj] if obj in bpy.data.objects else None
            
            # TODO: how do we deal with this, as we obviously do not have data for removed objects ?
            for obj in removed:
                if not scene_name in changes_per_scene:
                    changes_per_scene[scene_name] = {}
                changes_per_scene[scene_name][obj] = None

            for object_name in list(current_scene.keys()): # TODO : exclude directly added/removed objects  
                if object_name in previous_scene:
                    current_obj = current_scene[object_name]
                    prev_obj = previous_scene[object_name]
                    same = str(current_obj) == str(prev_obj)

                    if not same:
                        if not scene_name in changes_per_scene:
                            changes_per_scene[scene_name] = {}

                        target_object = bpy.data.objects[object_name] if object_name in bpy.data.objects else None
                        changes_per_scene[scene_name][object_name] = target_object
                        bubble_up_changes(target_object, changes_per_scene[scene_name])
                        # now bubble up for instances & parents
        else:
            print(f"scene {scene_name} not present in previous data")



    current_collections = current["collections"]
    previous_collections = previous["collections"]

    for collection_name in current_collections:
        if collection_name in previous_collections:
            current_collection = current_collections[collection_name]
            prev_collection = previous_collections[collection_name]
            same = str(current_collection) == str(prev_collection)

            if not same:
                #if not collection_name in changes_per_collection:
                target_collection = bpy.data.collections[collection_name] if collection_name in bpy.data.collections else None
                changes_per_collection[collection_name] = target_collection

    # process changes to materials
    current_materials = current["materials"]
    previous_materials = previous["materials"]

    for material_name in current_materials:
        if material_name in previous_materials:
            current_material = current_materials[material_name]
            prev_material = previous_materials[material_name]
            same = str(current_material) == str(prev_material)

            if not same:
                #if not material_name in changes_per_material:
                target_material = bpy.data.materials[material_name] if material_name in bpy.data.materials else None
                changes_per_material[material_name] = target_material
        
    return (changes_per_scene, changes_per_collection, changes_per_material)