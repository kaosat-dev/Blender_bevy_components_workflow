import bpy


# checks if an object is dynamic
# TODO: for efficiency, it might make sense to write this flag semi automatically at the root level of the object so we can skip the inner loop
# TODO: we need to recompute these on blueprint changes too
# even better, keep a list of dynamic objects per scene , updated only when needed ?
def is_object_dynamic(object):
    is_dynamic =  object['Dynamic'] if 'Dynamic' in object else False
    # only look for data in the original collection if it is not alread marked as dynamic at instance level
    if not is_dynamic and object.type == 'EMPTY' and hasattr(object, 'instance_collection'):
         # get the name of the collection this is an instance of
        collection_name = object.instance_collection.name
        original_collection = bpy.data.collections[collection_name]

        #print("inspecting insides", original_collection)

        # scan original collection, look for a 'Dynamic' flag
        for object in original_collection.objects:
            #print(" inner", object)
            if object.type == 'EMPTY' and object.name.endswith("components"):
                for component_name in object.keys():
                    #print("   compo", component_name)
                    if component_name == 'Dynamic':
                        is_dynamic = True
                        break
    print("is object dynamic", is_dynamic, object)

    return is_dynamic

def is_object_static(object):
    return not is_object_dynamic(object)