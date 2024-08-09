import bpy

# traverse all collections
def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

#Recursivly transverse layer_collection for a particular name
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found
  
def set_active_collection(scene, collection_name):
    layer_collection = bpy.data.scenes[scene.name].view_layers['ViewLayer'].layer_collection
    layerColl = recurLayerCollection(layer_collection, collection_name)
    # set active collection to the collection
    bpy.context.view_layer.active_layer_collection = layerColl
