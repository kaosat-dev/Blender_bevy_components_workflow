import bpy
from bpy_types import PropertyGroup
from bpy.props import (PointerProperty)
from . import process_structs
from . import process_tupples
from . import process_enum
from . import process_list
from . import process_map

def process_component(registry, definition, update, extras=None, nesting_long_names = []):
    long_name = definition['long_name']
    short_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    properties = definition["properties"] if "properties" in definition else {}
    prefixItems = definition["prefixItems"] if "prefixItems" in definition else []

    has_properties = len(properties.keys()) > 0
    has_prefixItems = len(prefixItems) > 0
    is_enum = type_info == "Enum"
    is_list = type_info == "List"
    is_map = type_info == "Map"

    __annotations__ = {}
    tupple_or_struct = None

    with_properties = False
    with_items = False
    with_enum = False
    with_list = False
    with_map = False

    #padding = "  " * (len(nesting_long_names) + 1)
    #print(f"{padding}process component", long_name, "nesting_long_names",nesting_long_names, "foo", has_properties, has_prefixItems, is_enum, is_list, is_map)

    if has_properties:
        __annotations__ = __annotations__ | process_structs.process_structs(registry, definition, properties, update, nesting_long_names)
        with_properties = True
        tupple_or_struct = "struct"
        #print(f"{padding}struct")

    if has_prefixItems:
        __annotations__ = __annotations__ | process_tupples.process_tupples(registry, definition, prefixItems, update, nesting_long_names)
        with_items = True
        tupple_or_struct = "tupple"

    if is_enum:
        __annotations__ = __annotations__ | process_enum.process_enum(registry, definition, update, nesting_long_names)
        with_enum = True

    if is_list:
        __annotations__ = __annotations__ | process_list.process_list(registry, definition, update, nesting_long_names)
        with_list= True

    if is_map:
        __annotations__ = __annotations__ | process_map.process_map(registry, definition, update, nesting_long_names)
        with_map = True

    # print("AFTER PROCESS", nesting_long_names, long_name)
    
    field_names = []
    for a in __annotations__:
        field_names.append(a)
 
    extras = extras if extras is not None else {
        "long_name": long_name
    }

    nesting_long_names = nesting_long_names + [long_name]
    root_component = nesting_long_names[0] if len(nesting_long_names) > 0 else long_name

    # print("")
    property_group_params = {
         **extras,
        '__annotations__': __annotations__,
        'tupple_or_struct': tupple_or_struct,
        'field_names': field_names, 
        **dict(with_properties = with_properties, with_items= with_items, with_enum= with_enum, with_list= with_list, with_map = with_map, short_name= short_name, long_name=long_name),
        'root_component': root_component
    }
    
    # we need to pass the full hierarchy to disambiguate between components 
    # Withouth this ; the following does not work
    """ 
    -BasicTest
    - NestingTestLevel2
        -BasicTest => the registration & update callback of this one overwrites the first "basicTest"
    """
    # add our component propertyGroup to the registry
    (property_group_pointer, property_group_class) = registry.register_component_propertyGroup(nesting_long_names, property_group_params)

    return (property_group_pointer, property_group_class)
                
