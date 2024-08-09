from bpy.props import (StringProperty)
from . import process_component

def process_enum(registry, definition, update, nesting_long_names):
    blender_property_mapping = registry.blender_property_mapping
    long_name = definition["long_name"]

    type_def = definition["type"] if "type" in definition else None
    variants = definition["oneOf"]

    nesting_long_names = nesting_long_names + [long_name]

    __annotations__ = {}
    original_type_name = "enum"

    #print("processing enum", long_name)#, definition)

    if type_def == "object":
        labels = []
        additional_annotations = {}
        for variant in variants:
            variant_name = variant["long_name"]
            variant_prefixed_name = "variant_" + variant_name
            labels.append(variant_name)

            if "prefixItems" in variant:
                #print("tupple variant in enum", variant)
                registry.add_custom_type(variant_name, variant)
                (sub_component_group, _) = process_component.process_component(registry, variant, update, {"nested": True}, nesting_long_names=nesting_long_names) 
                additional_annotations[variant_prefixed_name] = sub_component_group
            elif "properties" in variant:
                #print("struct variant in enum", variant)
                registry.add_custom_type(variant_name, variant)
                (sub_component_group, _) = process_component.process_component(registry, variant, update, {"nested": True}, nesting_long_names=nesting_long_names) 
                additional_annotations[variant_prefixed_name] = sub_component_group
            else: # for the cases where it's neither a tupple nor a structs: FIXME: not 100% sure of this
                #print("other variant in enum")
                annotations = {"variant_"+variant_name: StringProperty(default="----<ignore_field>----")}
                additional_annotations = additional_annotations | annotations

        items = tuple((e, e, e) for e in labels)

        blender_property_def = blender_property_mapping[original_type_name]
        blender_property = blender_property_def["type"](
            **blender_property_def["presets"],# we inject presets first
            items=items, # this is needed by Blender's EnumProperty , which we are using here
            update= update
)
        __annotations__["selection"] = blender_property

        for a in additional_annotations:
            __annotations__[a] = additional_annotations[a]
        # enum_value => what field to display
        # a second field + property for the "content" of the enum
    else:
        items = tuple((e, e, "") for e in variants)        
        blender_property_def = blender_property_mapping[original_type_name]
        blender_property = blender_property_def["type"](
            **blender_property_def["presets"],# we inject presets first
            items=items,
            update= update
        )
        __annotations__["selection"] = blender_property
    
    return __annotations__
