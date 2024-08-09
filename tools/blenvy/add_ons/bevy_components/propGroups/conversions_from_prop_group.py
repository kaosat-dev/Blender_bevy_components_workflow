from bpy_types import PropertyGroup

conversion_tables = {
    "bool": lambda value: value,

    "char": lambda value: '"'+value+'"',
    "str": lambda value: '"'+value+'"',
    "alloc::string::String": lambda value: '"'+str(value)+'"',
    "alloc::borrow::Cow<str>": lambda value: '"'+str(value)+'"',

    "glam::Vec2": lambda value: "Vec2(x:"+str(value[0])+ ", y:"+str(value[1])+")",
    "glam::DVec2": lambda value: "DVec2(x:"+str(value[0])+ ", y:"+str(value[1])+")",
    "glam::UVec2": lambda value: "UVec2(x:"+str(value[0])+ ", y:"+str(value[1])+")",

    "glam::Vec3": lambda value: "Vec3(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+")",
    "glam::Vec3A": lambda value: "Vec3A(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+")",
    "glam::UVec3": lambda value: "UVec3(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+")",

    "glam::Vec4": lambda value: "Vec4(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+ ", w:"+str(value[3])+")",
    "glam::DVec4": lambda value: "DVec4(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+ ", w:"+str(value[3])+")",
    "glam::UVec4": lambda value: "UVec4(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+ ", w:"+str(value[3])+")",

    "glam::Quat":  lambda value: "Quat(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+ ", w:"+str(value[3])+")",

    "bevy_color::srgba::Srgba":  lambda value: "Srgba(red:"+str(value[0])+ ", green:"+str(value[1])+ ", blue:"+str(value[2])+ ", alpha:"+str(value[3])+   ")",
    "bevy_color::linear_rgba::LinearRgba":  lambda value: "LinearRgba(red:"+str(value[0])+ ", green:"+str(value[1])+ ", blue:"+str(value[2])+ ", alpha:"+str(value[3])+   ")",
    "bevy_color::hsva::Hsva":  lambda value: "Hsva(hue:"+str(value[0])+ ", saturation:"+str(value[1])+ ", value:"+str(value[2])+ ", alpha:"+str(value[3])+   ")",
}

#converts the value of a property group(no matter its complexity) into a single custom property value
# this is more or less a glorified "to_ron()" method (not quite but close to)
def property_group_value_to_custom_property_value(property_group, definition, registry, parent=None, value=None):
    long_name = definition["long_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    is_value_type = long_name in conversion_tables
    # print("computing custom property: component name:", long_name, "type_info", type_info, "type_def", type_def, "value", value)

    if is_value_type:
        value = conversion_tables[long_name](value)
    elif type_info == "Struct":
        values = {}
        if len(property_group.field_names) ==0:
            value = '()'
        else:
            for index, field_name in enumerate(property_group.field_names):
                item_long_name = definition["properties"][field_name]["type"]["$ref"].replace("#/$defs/", "")
                item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

                value = getattr(property_group, field_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                if item_definition is not None:
                    value = property_group_value_to_custom_property_value(child_property_group, item_definition, registry, parent=long_name, value=value)
                else:
                    value = '""'
                values[field_name] = value
            value = values        
    elif type_info == "Tuple": 
        values = {}
        for index, field_name in enumerate(property_group.field_names):
            item_long_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition is not None:
                value = property_group_value_to_custom_property_value(child_property_group, item_definition, registry, parent=long_name, value=value)
            else:
                value = '""'
            values[field_name] = value
        value = tuple(e for e in list(values.values()))

    elif type_info == "TupleStruct":
        values = {}
        for index, field_name in enumerate(property_group.field_names):
            #print("toto", index, definition["prefixItems"][index]["type"]["$ref"])
            item_long_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition is not None:
                value = property_group_value_to_custom_property_value(child_property_group, item_definition, registry, parent=long_name, value=value)
            else:
                value = '""'
            values[field_name] = value
        
        value = tuple(e for e in list(values.values()))
    elif type_info == "Enum":
        selected = getattr(property_group, "selection")
        if type_def == "object":
            selection_index = property_group.field_names.index("variant_"+selected)
            variant_name = property_group.field_names[selection_index]
            variant_definition = definition["oneOf"][selection_index-1]
            if "prefixItems" in variant_definition:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = property_group_value_to_custom_property_value(child_property_group, variant_definition, registry, parent=long_name, value=value)
                value = selected + str(value,) #"{}{},".format(selected ,value)
            elif "properties" in variant_definition:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = property_group_value_to_custom_property_value(child_property_group, variant_definition, registry, parent=long_name, value=value)
                value = selected + str(value,)
            else:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                if child_property_group:
                    value = property_group_value_to_custom_property_value(child_property_group, variant_definition, registry, parent=long_name, value=value)
                    value = selected + str(value,)
                else:
                    value = selected # here the value of the enum is just the name of the variant
        else: 
            value = selected

    elif type_info == "List":
        item_list = getattr(property_group, "list")
        value = []
        for item in item_list:
            item_long_name = getattr(item, "long_name")
            definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None
            if definition is not None:
                item_value = property_group_value_to_custom_property_value(item, definition, registry, long_name, None)
                if item_long_name.startswith("wrapper_"): #if we have a "fake" tupple for aka for value types, we need to remove one nested level
                    item_value = item_value[0]
            else:
                item_value = '""'
            value.append(item_value) 

    elif type_info == "Map":
        keys_list = getattr(property_group, "list", {})
        values_list = getattr(property_group, "values_list")
        value = {}
        for index, key in enumerate(keys_list):
            # first get the keys
            key_long_name = getattr(key, "long_name")
            definition = registry.type_infos[key_long_name] if key_long_name in registry.type_infos else None
            if definition is not None:
                key_value = property_group_value_to_custom_property_value(key, definition, registry, long_name, None)
                if key_long_name.startswith("wrapper_"): #if we have a "fake" tupple for aka for value types, we need to remove one nested level
                    key_value = key_value[0]
            else:
                key_value = '""'
            # and then the values
            val = values_list[index]
            value_long_name = getattr(val, "long_name")
            definition = registry.type_infos[value_long_name] if value_long_name in registry.type_infos else None
            if definition is not None:
                val_value = property_group_value_to_custom_property_value(val, definition, registry, long_name, None)
                if value_long_name.startswith("wrapper_"): #if we have a "fake" tupple for aka for value types, we need to remove one nested level
                    val_value = val_value[0]
            else:
                val_value = '""'

            value[key_value] = val_value
        value = str(value).replace('{','@').replace('}','²') # FIXME: eeek !!
    else:
        value = conversion_tables[long_name](value) if is_value_type else value
        value = '""' if isinstance(value, PropertyGroup) else value
        
    #print("generating custom property value", value, type(value))
    if isinstance(value, str):
        value = value.replace("'", "")

    if parent == None:
        value = str(value).replace("'",  "")
        value = value.replace(",)",")")
        value = value.replace("{", "(").replace("}", ")") # FIXME: deal with hashmaps
        value = value.replace("True", "true").replace("False", "false")
        value = value.replace('@', '{').replace('²', '}')
    return value

