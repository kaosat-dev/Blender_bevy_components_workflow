import bpy

from ...bevy_components.components.metadata import get_bevy_component_value_by_long_name

# checks if an object is dynamic
# TODO: we need to recompute these on blueprint changes too
# even better, keep a list of dynamic objects per scene , updated only when needed ?
def is_object_dynamic(object):
    is_dynamic = get_bevy_component_value_by_long_name(object, 'blenvy::save_load::Dynamic') is not None
    #is_dynamic =  object['Dynamic'] if 'Dynamic' in object else False
    # only look for data in the original collection if it is not alread marked as dynamic at instance level
    if not is_dynamic and object.type == 'EMPTY' and hasattr(object, 'instance_collection') and object.instance_collection is not None :
        #print("collection", object.instance_collection, "object", object.name)
        # get the name of the collection this is an instance of
        collection_name = object.instance_collection.name
        original_collection = bpy.data.collections[collection_name]
        # scan original collection, look for a 'Dynamic' flag
        is_dynamic = get_bevy_component_value_by_long_name(original_collection, 'blenvy::save_load::Dynamic') is not None
        
    #print("IS OBJECT DYNAMIC", object, is_dynamic)

    return is_dynamic

def is_object_static(object):
    return not is_object_dynamic(object)