import bpy

def make_empty3(name, location, rotation, scale): 
    original_active_object = bpy.context.active_object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location, rotation=rotation, scale=scale)
    empty_obj = bpy.context.active_object
    empty_obj.name = name
    empty_obj.scale = scale # scale is not set correctly ?????
    bpy.context.view_layer.objects.active = original_active_object
    return empty_obj
