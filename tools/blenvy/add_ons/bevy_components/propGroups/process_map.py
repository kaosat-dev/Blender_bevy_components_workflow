from bpy.props import (StringProperty, IntProperty, CollectionProperty, PointerProperty)
from .utils import generate_wrapper_propertyGroup
from . import process_component

def process_map(registry, definition, update, nesting_long_names=[]):
    value_types_defaults = registry.value_types_defaults 
    type_infos = registry.type_infos

    long_name = definition["long_name"]

    nesting_long_names = nesting_long_names + [long_name]

    value_ref_name = definition["valueType"]["type"]["$ref"].replace("#/$defs/", "")
    key_ref_name = definition["keyType"]["type"]["$ref"].replace("#/$defs/", "")

    #print("definition", definition)
    __annotations__ = {}

    if key_ref_name in type_infos:
        key_definition = type_infos[key_ref_name]
        original_long_name = key_definition["long_name"]
        is_key_value_type = original_long_name in value_types_defaults
        definition_link = definition["keyType"]["type"]["$ref"]

        #if the content of the list is a unit type, we need to generate a fake wrapper, otherwise we cannot use layout.prop(group, "propertyName") as there is no propertyName !
        if is_key_value_type:
            keys_property_group_class = generate_wrapper_propertyGroup(f"{long_name}_keys", original_long_name, definition_link, registry, update, nesting_long_names=nesting_long_names)
        else:
            (_, list_content_group_class) = process_component.process_component(registry, key_definition, update, {"nested": True, "long_name": original_long_name}, nesting_long_names=nesting_long_names)
            keys_property_group_class = list_content_group_class

        keys_collection = CollectionProperty(type=keys_property_group_class)
        keys_property_group_pointer = PointerProperty(type=keys_property_group_class)
    else:
        #__annotations__["list"] = StringProperty(default="N/A")
        registry.add_missing_typeInfo(key_ref_name)

    if value_ref_name in type_infos:
        value_definition = type_infos[value_ref_name]
        original_long_name = value_definition["long_name"]
        is_value_value_type = original_long_name in value_types_defaults
        definition_link = definition["valueType"]["type"]["$ref"]

        #if the content of the list is a unit type, we need to generate a fake wrapper, otherwise we cannot use layout.prop(group, "propertyName") as there is no propertyName !
        if is_value_value_type:
            values_property_group_class = generate_wrapper_propertyGroup(f"{long_name}_values", original_long_name, definition_link, registry, update, nesting_long_names)
        else:

            (_, list_content_group_class) = process_component.process_component(registry, value_definition, update, {"nested": True, "long_name": original_long_name}, nesting_long_names)
            values_property_group_class = list_content_group_class

        values_collection = CollectionProperty(type=values_property_group_class)
        values_property_group_pointer = PointerProperty(type=values_property_group_class)

    else:
        #__annotations__["list"] = StringProperty(default="N/A")
        registry.add_missing_typeInfo(value_ref_name)


    if key_ref_name in type_infos and value_ref_name in type_infos:
        #print("hashmap processed normally: key_ref_name",key_ref_name, "value_ref_name", value_ref_name )
        __annotations__ = {
            "list": keys_collection,
            "list_index": IntProperty(name = "Index for keys", default = 0,  update=update),
            "keys_setter":keys_property_group_pointer,
            
            "values_list": values_collection,
            "values_list_index": IntProperty(name = "Index for values", default = 0,  update=update),
            "values_setter":values_property_group_pointer,
        }
    else:    
        # the root component also becomes invalid (in practice it is not always a component, but good enough)
        registry.add_invalid_component(nesting_long_names[0])

    return __annotations__
