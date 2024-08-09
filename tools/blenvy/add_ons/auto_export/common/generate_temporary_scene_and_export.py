import bpy
from ....core.helpers_collections import set_active_collection
from ....core.object_makers import make_empty
from .duplicate_object import duplicate_object
from .export_gltf import export_gltf
from ..constants import custom_properties_to_filter_out
from ..utils import remove_unwanted_custom_properties
from ....core.utils import exception_traceback, show_message_box

""" 
generates a temporary scene, fills it with data, cleans up after itself
    * named using temp_scene_name 
    * filled using the tempScene_filler
    * written on disk to gltf_output_path, with the gltf export parameters in gltf_export_settings
    * cleaned up using tempScene_cleaner

"""
def generate_temporary_scene_and_export(settings, gltf_export_settings, gltf_output_path, temp_scene_name="__temp_scene", tempScene_filler=None, tempScene_cleaner=None, additional_data=None): 

    temp_scene = bpy.data.scenes.new(name=temp_scene_name)
    temp_root_collection = temp_scene.collection

    properties_black_list = custom_properties_to_filter_out
    if additional_data is not None: # FIXME not a fan of having this here
        for entry in dict(additional_data):
            # we copy everything over except those on the black list
            if entry not in properties_black_list:
                print("entry in additional data", entry, "value", additional_data[entry], "in", additional_data.name)
                temp_scene[entry] = additional_data[entry]

    # we remove everything from the black list
    remove_unwanted_custom_properties(temp_scene)
  
    # save active scene
    active_scene = bpy.context.window.scene
    # and selected collection
    active_collection = bpy.context.view_layer.active_layer_collection
    # and mode
    active_mode = bpy.context.active_object.mode if bpy.context.active_object is not None else None
    # we change the mode to object mode, otherwise the gltf exporter is not happy
    if active_mode is not None and active_mode != 'OBJECT':
        print("setting to object mode", active_mode)
        bpy.ops.object.mode_set(mode='OBJECT')
    # we set our active scene to be this one : this is needed otherwise the stand-in empties get generated in the wrong scene
    bpy.context.window.scene = temp_scene

    area = [area for area in bpy.context.screen.areas if area.type == "VIEW_3D"][0]
    region = [region for region in area.regions if region.type == 'WINDOW'][0]
    with bpy.context.temp_override(scene=temp_scene, area=area, region=region):
        # detect scene mistmatch
        scene_mismatch = bpy.context.scene.name != bpy.context.window.scene.name
        if scene_mismatch:
            show_message_box("Error in Gltf Exporter", icon="ERROR", lines=[f"Context scene mismatch, aborting: {bpy.context.scene.name} vs {bpy.context.window.scene.name}"])
        else:
            set_active_collection(bpy.context.scene, temp_root_collection.name)
            # generate contents of temporary scene
            
            scene_filler_data = tempScene_filler(temp_root_collection)
            # export the temporary scene
            try:
                print("dry_run MODE", settings.auto_export.dry_run)
                if settings.auto_export.dry_run == "DISABLED":           
                    export_gltf(gltf_output_path, gltf_export_settings)
            except Exception as error:
                print("failed to export gltf !", error) 
                show_message_box("Error in Gltf Exporter", icon="ERROR", lines=exception_traceback(error))
            finally:
                print("restoring state of scene")
                # restore everything
                tempScene_cleaner(temp_scene, scene_filler_data)

    # reset active scene
    bpy.context.window.scene = active_scene
    # reset active collection
    bpy.context.view_layer.active_layer_collection = active_collection
    # reset mode
    if active_mode is not None:
        bpy.ops.object.mode_set( mode = active_mode )



# copies the contents of a collection into another one while replacing library instances with empties
def copy_hollowed_collection_into(source_collection, destination_collection, parent_empty=None, filter=None, blueprints_data=None, settings={}):
    collection_instances_combine_mode = getattr(settings.auto_export, "collection_instances_combine_mode")

    for object in source_collection.objects:
        if object.name.endswith("____bak"): # some objects could already have been handled, ignore them
            continue       
        if filter is not None and filter(object) is False:
            continue
        if object.parent is not None: # if there is a parent, this object is not a direct child of the collection, and should be ignored (it will get picked up by the recursive scan inside duplicate_object)
            continue
        #check if a specific collection instance does not have an ovveride for combine_mode
        combine_mode = object['_combine'] if '_combine' in object else collection_instances_combine_mode
        parent = parent_empty
        duplicate_object(object, parent, combine_mode, destination_collection, blueprints_data)
        
    # for every child-collection of the source, copy its content into a new sub-collection of the destination
    for collection in source_collection.children:
        original_name = collection.name
        collection.name = original_name + "____bak"
        collection_placeholder = make_empty(original_name, [0,0,0], [0,0,0], [1,1,1], destination_collection)

        if parent_empty is not None:
            collection_placeholder.parent = parent_empty
        copy_hollowed_collection_into(
            source_collection = collection, 
            destination_collection = destination_collection, 
            parent_empty = collection_placeholder, 
            filter = filter,
            blueprints_data = blueprints_data, 
            settings=settings
        )
    return {}


# clear & remove "hollow scene"
def clear_hollow_scene(temp_scene, original_root_collection):
    def restore_original_names(collection):
        if collection.name.endswith("____bak"):
            collection.name = collection.name.replace("____bak", "")
        for object in collection.all_objects:
            """if object.instance_type == 'COLLECTION':
                if object.name.endswith("____bak"):
                    object.name = object.name.replace("____bak", "")
            else: """
            if object.name.endswith("____bak"):
                object.name = object.name.replace("____bak", "")
        for child_collection in collection.children:
            restore_original_names(child_collection)
    

    # remove any data we created
    temp_root_collection = temp_scene.collection 
    temp_scene_objects = [o for o in temp_root_collection.all_objects]
    for object in temp_scene_objects:
        #print("removing", object.name)
        bpy.data.objects.remove(object, do_unlink=True)

    # remove the temporary scene
    bpy.data.scenes.remove(temp_scene, do_unlink=True)
    
    # reset original names
    restore_original_names(original_root_collection)
