from bpy.props import (StringProperty)
from . import process_component

def process_tupples(registry, definition, prefixItems, update, nesting=[]):
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos
    short_name = definition["short_name"]

    nesting = nesting+[short_name]
    __annotations__ = {}

    default_values = []
    prefix_infos = []
    for index, item in enumerate(prefixItems):
        ref_name = item["type"]["$ref"].replace("#/$defs/", "")

        property_name = str(index)# we cheat a bit, property names are numbers here, as we do not have a real property name
       
        if ref_name in type_infos:
            original = type_infos[ref_name]
            original_type_name = original["title"]
            is_value_type = original_type_name in value_types_defaults

            value = value_types_defaults[original_type_name] if is_value_type else None
            default_values.append(value)
            prefix_infos.append(original)

            if is_value_type:
                if original_type_name in blender_property_mapping:
                    blender_property_def = blender_property_mapping[original_type_name]
                    blender_property = blender_property_def["type"](
                        **blender_property_def["presets"],# we inject presets first
                        name = property_name, 
                        default=value,
                        update= update
                    )
                  
                    __annotations__[property_name] = blender_property
            else:
                original_long_name = original["title"]
                (sub_component_group, _) = process_component.process_component(registry, original, update, {"nested": True, "type_name": original_long_name}, nesting)
                __annotations__[property_name] = sub_component_group
        else: 
            # component not found in type_infos, generating placeholder
            __annotations__[property_name] = StringProperty(default="N/A")
            registry.add_missing_typeInfo(ref_name)
            # the root component also becomes invalid (in practice it is not always a component, but good enough)
            registry.add_invalid_component(nesting[0])


    return __annotations__

