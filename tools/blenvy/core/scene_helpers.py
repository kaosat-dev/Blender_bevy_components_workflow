import bpy
from bpy.props import (PointerProperty)
from .object_makers import make_empty

def add_scene_property(scene, scene_component_name, property_data, limit_to=None):
    root_collection = scene.collection
    scene_property = None
    for object in scene.objects:
        if object.name == scene_component_name:
            scene_property = object
            break
    
    if scene_property is None:
        scene_property = make_empty(scene_component_name, [0,0,0], [0,0,0], [0,0,0], root_collection)

    for key in property_data.keys():
        if limit_to is not None:
            if key in limit_to:
                scene_property[key] = property_data[key]
        else:
            scene_property[key] = property_data[key]


# compatibility helper until we land gltf_extras at the scene level for Bevy
# it copies a custom property into an __components object's properties
def copy_scene_or_collection_property_to_object_component(scene, property_name, target_object_name):
    property_value = scene.get(property_name, None)
    if property_value is not None:
        property_data = {}
        property_data[property_name] = property_value
        add_scene_property(scene=scene, scene_component_name=target_object_name, property_data=property_data)