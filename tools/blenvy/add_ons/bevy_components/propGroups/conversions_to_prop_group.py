from bpy_types import PropertyGroup
import re

def parse_struct_string(string, start_nesting=0):
    #print("processing struct string", string, "start_nesting", start_nesting)
    fields = {}
    buff = []
    current_fieldName = None
    nesting_level = 0 

    start_offset = 0
    end_offset = 0

    for index, char in enumerate(string):
        buff.append(char)
        if char == "," and nesting_level == start_nesting:
            #print("first case", end_offset)
            end_offset = index
            end_offset = len(string) if end_offset == 0 else end_offset

            val = "".join(string[start_offset:end_offset])
            fields[current_fieldName] = val.strip()
            start_offset = index + 1
            #print("done with field name", current_fieldName, "value", fields[current_fieldName])

        if char == "[" or char == "(":
            nesting_level  += 1
            if nesting_level == start_nesting:
                start_offset = index + 1 
                #print("nesting & setting start offset", start_offset)
            #print("nesting down", nesting_level)

        if char == "]" or char == ")" :
            #print("nesting up", nesting_level)
            if nesting_level == start_nesting:
                end_offset = index
                #print("unesting & setting end offset", end_offset)
            nesting_level  -= 1


        if char == ":" and nesting_level == start_nesting:
            end_offset = index
            fieldName = "".join(string[start_offset:end_offset])
            current_fieldName = fieldName.strip()
            start_offset = index + 1
            end_offset = 0 #hack
            #print("starting field name", fieldName, "index", index)
            buff = []
            
    end_offset = len(string) if end_offset == 0 else end_offset
    #print("final start and end offset", start_offset, end_offset, "total length", len(string))

    val = "".join(string[start_offset:end_offset])

    fields[current_fieldName] = val.strip()
    #print("done with all fields", fields)
    return fields

def parse_tuplestruct_string(string, start_nesting=0):
    #print("processing tuppleStruct", string, "start_nesting", start_nesting)
    fields = []
    buff = []
    nesting_level = 0 
    field_index = 0

    start_offset = 0
    end_offset = 0
    # todo: strip all stuff before start_nesting

    for index, char in enumerate(string):
        buff.append(char)
        if char == "," and nesting_level == start_nesting:
            end_offset = index
            end_offset = len(string) if end_offset == 0 else end_offset

            val = "".join(string[start_offset:end_offset])
            fields.append(val.strip())
            field_index += 1
            #print("start and end offset", start_offset, end_offset, "total length", len(string))
            #print("done with field name", field_index, "value", fields)
            start_offset = index + 1
            end_offset = 0 # hack

        if char == "[" or char == "(":
            nesting_level  += 1
            if nesting_level == start_nesting:
                start_offset = index + 1 
                #print("nesting & setting start offset", start_offset)
            #print("nesting down", nesting_level)

        if char == "]" or char == ")" :
            if nesting_level == start_nesting:
                end_offset = index
                #print("unesting & setting end offset", end_offset)
            #print("nesting up", nesting_level)
            nesting_level  -= 1


    end_offset = len(string) if end_offset == 0 else end_offset
    #print("final start and end offset", start_offset, end_offset, "total length", len(string))

    val = "".join(string[start_offset:end_offset]) #if end_offset != 0 else buff)
    fields.append(val.strip())
    fields = list(filter(lambda entry: entry != '', fields))
    #print("done with all fields", fields)
    return fields


def parse_vec2(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['x']), caster(parsed['y'])]

def parse_vec3(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['x']), caster(parsed['y']), caster(parsed['z'])]

def parse_vec4(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['x']), caster(parsed['y']), caster(parsed['z']), caster(parsed['w'])]

def parse_color_rgba(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['red']), caster(parsed['green']), caster(parsed['blue']), caster(parsed['alpha'])]

def parse_color_hsva(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['hue']), caster(parsed['saturation']), caster(parsed['value']), caster(parsed['alpha'])]

def to_int(input):
    return int(float(input))

type_mappings = {
    "bool": lambda value: True if value == "true" else False,

    "u8": lambda value: int(value),
    "u16": lambda value: int(value),
    "u32": lambda value: int(value),
    "u64": lambda value: int(value),
    "u128": lambda value: int(value),
    "u64": lambda value: int(value),
    "usize": lambda value: int(value),

    "i8": lambda value: int(value),
    "i16": lambda value: int(value),
    "i32": lambda value: int(value),
    "i64": lambda value: int(value),
    "i128": lambda value: int(value),
    "isize": lambda value: int(value),

    'f32': lambda value: float(value),
    'f64': lambda value: float(value),

    "glam::Vec2": lambda value: parse_vec2(value, float, "Vec2"),
    "glam::DVec2": lambda value: parse_vec2(value, float, "DVec2"),
    "glam::UVec2": lambda value: parse_vec2(value, to_int, "UVec2"),

    'glam::Vec3': lambda value: parse_vec3(value, float, "Vec3"),
    "glam::Vec3A": lambda value: parse_vec3(value, float, "Vec3A"),
    "glam::UVec3": lambda value: parse_vec3(value, to_int, "UVec3"),

    "glam::Vec4": lambda value: parse_vec4(value, float, "Vec4"),
    "glam::DVec4": lambda value: parse_vec4(value, float, "DVec4"),
    "glam::UVec4": lambda value: parse_vec4(value, to_int, "UVec4"),

    "glam::Quat": lambda value: parse_vec4(value, float, "Quat"),

    'alloc::string::String': lambda value: str(value.replace('"', "")),
    'alloc::borrow::Cow<str>': lambda value: str(value.replace('"', "")),

    "bevy_color::srgba::Srgba":  lambda value: parse_color_rgba(value, float, "Srgba"),
    "bevy_color::linear_rgba::LinearRgba":  lambda value: parse_color_rgba(value, float, "LinearRgba"),
    "bevy_color::hsva::Hsva":  lambda value: parse_color_hsva(value, float, "Hsva"),

    'bevy_ecs::entity::Entity': lambda value: int(value),
}

def is_def_value_type(definition, registry):
    if definition == None:
        return True
    value_types_defaults = registry.value_types_defaults
    long_name = definition["long_name"]
    is_value_type = long_name in value_types_defaults
    return is_value_type

#converts the value of a single custom property into a value (values) of a property group 
def property_group_value_from_custom_property_value(property_group, definition, registry, value, nesting = []):
    value_types_defaults = registry.value_types_defaults
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    properties = definition["properties"] if "properties" in definition else {}
    prefixItems = definition["prefixItems"] if "prefixItems" in definition else []
    long_name = definition["long_name"]

    #is_value_type = type_def in value_types_defaults or long_name in value_types_defaults
    is_value_type = long_name in value_types_defaults
    nesting = nesting + [definition["short_name"]]


    if is_value_type:
        value = value.replace("(", "").replace(")", "")# FIXME: temporary, incoherent use of nesting levels between parse_tuplestruct_string & parse_struct_string
        value = type_mappings[long_name](value) if long_name in type_mappings else value
        return value
    elif type_info == "Struct":
        if len(property_group.field_names) != 0 :
            custom_property_values = parse_struct_string(value, start_nesting=1 if value.startswith("(") else 0)
            for index, field_name in enumerate(property_group.field_names):
                item_long_name = definition["properties"][field_name]["type"]["$ref"].replace("#/$defs/", "")
                item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

                custom_prop_value = custom_property_values[field_name]
                #print("field name", field_name, "value", custom_prop_value)
                propGroup_value = getattr(property_group, field_name)
                is_property_group = isinstance(propGroup_value, PropertyGroup)
                child_property_group = propGroup_value if is_property_group else None
                if item_definition is not None:
                    custom_prop_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_prop_value, nesting=nesting)
                else:
                    custom_prop_value = custom_prop_value

                if is_def_value_type(item_definition, registry):
                    setattr(property_group , field_name, custom_prop_value)
               

        else:
            if len(value) > 2: #a unit struct should be two chars long :()
                #print("struct with zero fields")
                raise Exception("input string too big for a unit struct")

    elif type_info == "Tuple": 
        custom_property_values = parse_tuplestruct_string(value, start_nesting=1 if len(nesting) == 1 else 1)

        for index, field_name in enumerate(property_group.field_names):
            item_long_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None
            
            custom_property_value = custom_property_values[index]

            propGroup_value = getattr(property_group, field_name)
            is_property_group = isinstance(propGroup_value, PropertyGroup)
            child_property_group = propGroup_value if is_property_group else None
            if item_definition is not None:
                custom_property_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_property_value, nesting=nesting)
            if is_def_value_type(item_definition, registry):
                setattr(property_group , field_name, custom_property_value)

    elif type_info == "TupleStruct":
        custom_property_values = parse_tuplestruct_string(value, start_nesting=1 if len(nesting) == 1 else 0)
        for index, field_name in enumerate(property_group.field_names):
            item_long_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

            custom_prop_value = custom_property_values[index]

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition is not None:
                custom_prop_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_prop_value, nesting=nesting)

            if is_def_value_type(item_definition, registry):
                    setattr(property_group , field_name, custom_prop_value)

    elif type_info == "Enum":
        field_names = property_group.field_names
        if type_def == "object":
            regexp = re.search('(^[^\(]+)(\((.*)\))', value)
            try:
                chosen_variant_raw = regexp.group(1)
                chosen_variant_value = regexp.group(3)
                chosen_variant_name = "variant_" + chosen_variant_raw 
            except:
                chosen_variant_raw = value
                chosen_variant_value = ""
                chosen_variant_name = "variant_" + chosen_variant_raw 
            selection_index = property_group.field_names.index(chosen_variant_name)
            variant_definition = definition["oneOf"][selection_index-1]
            # first we set WHAT variant is selected
            setattr(property_group, "selection", chosen_variant_raw)

            # and then we set the value of the variant
            if "prefixItems" in variant_definition:
                value = getattr(property_group, chosen_variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                
                chosen_variant_value = "(" +chosen_variant_value +")" # needed to handle nesting correctly
                value = property_group_value_from_custom_property_value(child_property_group, variant_definition, registry, value=chosen_variant_value, nesting=nesting)
                
            elif "properties" in variant_definition:
                value = getattr(property_group, chosen_variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = property_group_value_from_custom_property_value(child_property_group, variant_definition, registry, value=chosen_variant_value, nesting=nesting)
                
        else:
            chosen_variant_raw = value
            setattr(property_group, field_names[0], chosen_variant_raw)

    elif type_info == "List":
        item_list = getattr(property_group, "list")
        item_long_name = getattr(property_group, "long_name")
        custom_property_values = parse_tuplestruct_string(value, start_nesting=2 if item_long_name.startswith("wrapper_") and value.startswith('(') else 1) # TODO : the additional check here is wrong, there is an issue somewhere in higher level stuff
        # clear list first
        item_list.clear()
        for raw_value in custom_property_values:
            new_entry = item_list.add()   
            item_long_name = getattr(new_entry, "long_name") # we get the REAL type name
            definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

            if definition is not None:
                property_group_value_from_custom_property_value(new_entry, definition, registry, value=raw_value, nesting=nesting)            
    else:
        try:
            value = value.replace("(", "").replace(")", "")# FIXME: temporary, incoherent use of nesting levels between parse_tuplestruct_string & parse_struct_string
            value = type_mappings[long_name](value) if long_name in type_mappings else value
            return value
        except:
            pass