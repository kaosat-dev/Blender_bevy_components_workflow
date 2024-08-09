
import random
import string
import uuid
from bpy_types import PropertyGroup

def random_bool():
    return bool(random.getrandbits(1))

def rand_int():
    return random.randint(0, 100)

def rand_float():
    return random.random()

def random_word(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def random_vec(length, type,):
    value = []
    for i in range(0, length):
        if type == 'float':
            value.append(rand_float())
        if type == 'int':
            value.append(rand_int())
    return value

type_mappings = {
    "bool": random_bool,

    "u8": rand_int,
    "u16": rand_int,
    "u32": rand_int,
    "u64": rand_int,
    "u128": rand_int,
    "u64": rand_int,
    "usize": rand_int,

    "i8": rand_int,
    "i16": rand_int,
    "i32": rand_int,
    "i64": rand_int,
    "i128": rand_int,
    "isize": rand_int,

    'f32': rand_float,
    'f64': rand_float,

    "glam::Vec2": lambda : random_vec(2, 'float'),
    "glam::DVec2": lambda : random_vec(2, 'float'),
    "glam::UVec2": lambda : random_vec(2, 'int'),

    'glam::Vec3': lambda : random_vec(3, 'float'),
    "glam::Vec3A": lambda : random_vec(3, 'float'),
    "glam::UVec3": lambda : random_vec(3, 'int'),

    "glam::Vec4": lambda : random_vec(4, 'float'),
    "glam::DVec4": lambda : random_vec(4, 'float'),
    "glam::UVec4": lambda : random_vec(4, 'int'),

    "glam::Quat": lambda : random_vec(4, 'float'),

    'bevy_color::srgba::Srgba': lambda : random_vec(4, 'float'),
    'bevy_color::linear_rgba::LinearRgba': lambda : random_vec(4, 'float'),
    'bevy_color::hsva::Hsva': lambda : random_vec(4, 'float'),
    
    'alloc::string::String': lambda : random_word(8),
    'alloc::borrow::Cow<str>': lambda : random_word(8),

    'bevy_ecs::entity::Entity': lambda: 0, #4294967295, #
    'bevy_utils::Uuid': lambda: '"'+str( uuid.UUID("73b3b118-7d01-4778-8bcc-4e79055f5d22") )+'"'
}
#    
    
def is_def_value_type(definition, registry):
    if definition == None:
        return True
    value_types_defaults = registry.value_types_defaults
    long_name = definition["long_name"]
    is_value_type = long_name in value_types_defaults
    return is_value_type

# see https://docs.python.org/3/library/random.html
def component_values_shuffler(seed=1, property_group=None, definition=None, registry=None, parent=None):
    if parent == None:
        random.seed(seed)

    value_types_defaults = registry.value_types_defaults
    component_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    properties = definition["properties"] if "properties" in definition else {}
    prefixItems = definition["prefixItems"] if "prefixItems" in definition else []
    has_properties = len(properties.keys()) > 0
    has_prefixItems = len(prefixItems) > 0
    is_enum = type_info == "Enum"
    is_list = type_info == "List"
    long_name = definition["long_name"]

    #is_value_type = type_def in value_types_defaults or long_name in value_types_defaults
    is_value_type = long_name in value_types_defaults

    if is_value_type:
        fieldValue = type_mappings[long_name]() 
        return fieldValue 

    elif type_info == "Struct":
        for index, field_name in enumerate(property_group.field_names):
            item_long_name = definition["properties"][field_name]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition is not None:
                value = component_values_shuffler(seed, child_property_group, item_definition, registry, parent=component_name)
            else:
                value = '""'
            is_item_value_type = is_def_value_type(item_definition, registry)
            if is_item_value_type:
                #print("setting attr", field_name , "for", component_name, "to", value, "value type", is_item_value_type)
                setattr(property_group , field_name, value)

    elif type_info == "Tuple": 
        #print("tup")

        for index, field_name in enumerate(property_group.field_names):
            item_long_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition is not None:
                value = component_values_shuffler(seed, child_property_group, item_definition, registry, parent=component_name)
            else:
                value = '""'

            is_item_value_type = is_def_value_type(item_definition, registry)
            if is_item_value_type:
                #print("setting attr", field_name , "for", component_name, "to", value, "value type", is_item_value_type)
                setattr(property_group , field_name, value)

    elif type_info == "TupleStruct":
        #print("tupstruct")
        for index, field_name in enumerate(property_group.field_names):
            item_long_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition is not None:
                value = component_values_shuffler(seed, child_property_group, item_definition, registry, parent=component_name)
            else:
                value = '""'

            is_item_value_type = is_def_value_type(item_definition, registry)
            if is_item_value_type:
                setattr(property_group , field_name, value)
        
    elif type_info == "Enum":
        available_variants = definition["oneOf"] if type_def != "object" else list(map(lambda x: x["long_name"], definition["oneOf"]))
        selected = random.choice(available_variants) 

        # set selected variant
        setattr(property_group , "selection", selected)

        if type_def == "object":
            selection_index = property_group.field_names.index("variant_"+selected)
            variant_name = property_group.field_names[selection_index]
            variant_definition = definition["oneOf"][selection_index-1]
            if "prefixItems" in variant_definition:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                
                value = component_values_shuffler(seed, child_property_group, variant_definition, registry, parent=component_name)
                value = selected + str(value,) 
            elif "properties" in variant_definition:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = component_values_shuffler(seed, child_property_group, variant_definition, registry, parent=component_name)
                value = selected + str(value,)
            else:
                value = selected # here the value of the enum is just the name of the variant
        else: 
            value = selected

        

    elif type_info == "List":
        item_list = getattr(property_group, "list")
        item_list.clear()

        item_long_name = getattr(property_group, "long_name")
        number_of_list_items_to_add =  random.randint(1, 2)

        for i in range(0, number_of_list_items_to_add):
            new_entry = item_list.add()   
            item_long_name = getattr(new_entry, "long_name") # we get the REAL type name

            definition = registry.type_infos[item_long_name] if item_long_name in registry.type_infos else None

            if definition is not None:
                component_values_shuffler(seed, new_entry, definition, registry, parent=component_name)
            else:
                pass
    else:
        print("something else")
        fieldValue = type_mappings[long_name]() if long_name in type_mappings else 'None'
        return fieldValue 

    #return value
    
   
                        