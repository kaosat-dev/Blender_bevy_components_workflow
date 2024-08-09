import bmesh
import bpy
import mathutils

# Makes an empty, at the specified location, rotation, scale stores it in existing collection, from https://blender.stackexchange.com/questions/51290/how-to-add-empty-object-not-using-bpy-ops
def make_empty(name, location, rotation, scale, collection):
    object_data = None 
    empty_obj = bpy.data.objects.new( name, object_data )
    
    empty_obj.empty_display_size = 2
    empty_obj.empty_display_type = 'PLAIN_AXES'   

    empty_obj.name = name
    empty_obj.location = location
    empty_obj.scale = scale
    empty_obj.rotation_euler = rotation

    collection.objects.link( empty_obj )
    #bpy.context.view_layer.update()
    return empty_obj

def make_cube(name, location=[0,0,0], rotation=[0,0,0], scale=[1,1,1], collection=None):
    new_mesh = bpy.data.meshes.new(name+"_Mesh") #None
    """verts = [( 1.0,  1.0,  0.0), 
         ( 1.0, -1.0,  0.0),
         (-1.0, -1.0,  0.0),
         (-1.0,  1.0,  0.0),
         ]  # 4 verts made with XYZ coords
    edges = []
    faces = [[0, 1, 2, 3]]
    new_mesh.from_pydata(verts, edges, faces)"""


    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.1, matrix=mathutils.Matrix.Translation(location)) # FIXME: other ways to set position seems to fail ?
    bm.to_mesh(new_mesh)
    bm.free()

    new_object = bpy.data.objects.new(name, new_mesh)
    new_object.name = name
    new_object.location = location
    new_object.scale = scale
    new_object.rotation_euler = rotation

    if collection is not None:
        collection.objects.link( new_object )
    return new_object



"""import bpy
import json

# Makes an empty, at the specified location, rotation, scale stores it in existing collection, from https://blender.stackexchange.com/questions/51290/how-to-add-empty-object-not-using-bpy-ops
def make_empty(name, location, rotation, scale, collection):
    object_data = None 
    empty_obj = bpy.data.objects.new( name, object_data )
    
    empty_obj.empty_display_size = 2
    empty_obj.empty_display_type = 'PLAIN_AXES'   

    empty_obj.name = name
    empty_obj.location = location
    empty_obj.scale = scale
    empty_obj.rotation_euler = rotation

    collection.objects.link( empty_obj )
    #bpy.context.view_layer.update()
    return empty_obj
"""