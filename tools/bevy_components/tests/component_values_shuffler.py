
import random
import string
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

    'bevy_render::color::Color': lambda : random_vec(4, 'float'),
    'alloc::string::String': lambda : random_word(8),
}

#    
    
def is_def_value_type(definition, registry):
    if definition == None:
        return True
    value_types_defaults = registry.value_types_defaults
    type_name = definition["title"]
    is_value_type = type_name in value_types_defaults
    return is_value_type


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
    type_name = definition["title"]

    #is_value_type = type_def in value_types_defaults or type_name in value_types_defaults
    is_value_type = type_name in value_types_defaults

    if is_value_type:
        #print("value type", type_name)
        fieldValue = type_mappings[type_name]() # see https://docs.python.org/3/library/random.html
        return fieldValue #setattr(propertyGroup , fieldName, fieldValue)

    elif type_info == "Struct":
        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["properties"][field_name]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
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
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
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
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
                value = component_values_shuffler(seed, child_property_group, item_definition, registry, parent=component_name)
            else:
                value = '""'

            is_item_value_type = is_def_value_type(item_definition, registry)
            if is_item_value_type:
                setattr(property_group , field_name, value)
        
    elif type_info == "Enum":
        available_variants = definition["oneOf"] if type_def != "object" else list(map(lambda x: x["title"], definition["oneOf"]))
        print("available variants", available_variants)
        selected = random.choice(available_variants) 

        # set selected variant
        setattr(property_group , component_name, selected)

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
        item_type_name = getattr(property_group, "type_name_short")
        item_type_long = registry.short_names_to_long_names[item_type_name]
        #print("list item type", item_type_name)

        number_of_list_items_to_add =  random.randint(1, 2)

        for i in range(0, number_of_list_items_to_add):
            new_entry = item_list.add()   
            item_type_name = getattr(new_entry, "type_name") # we get the REAL type name
            definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            if definition != None:
                item_value = component_values_shuffler(seed, new_entry, definition, registry, parent=component_name)
            else:
                pass

          


 
          
    else:
        value = "" #conversion_tables[type_name](value) if is_value_type else value
    
   
                        