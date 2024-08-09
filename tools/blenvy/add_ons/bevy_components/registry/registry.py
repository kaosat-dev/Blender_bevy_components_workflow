import bpy
import json
import os
import uuid
from pathlib import Path
from bpy_types import (PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)
from ..components.metadata import ComponentMetadata
from .hashing.tiger import hash as tiger_hash


# helper class to store missing bevy types information
class MissingBevyType(bpy.types.PropertyGroup):
    long_name: bpy.props.StringProperty(
        name="type",
    ) # type: ignore


def property_group_from_infos(property_group_name, property_group_parameters):
    # print("creating property group", property_group_name)
    property_group_class = type(property_group_name, (PropertyGroup,), property_group_parameters)
    
    bpy.utils.register_class(property_group_class)
    property_group_pointer = PointerProperty(type=property_group_class)
    
    return (property_group_pointer, property_group_class)

# this is where we store the information for all available components
class ComponentsRegistry(PropertyGroup):
    registry: bpy.props. StringProperty(
        name="registry",
        description="component registry"
    )# type: ignore

    missing_type_infos: StringProperty(
        name="missing type infos",
        description="unregistered/missing type infos"
    )# type: ignore

    disable_all_object_updates: BoolProperty(name="disable_object_updates", default=False) # type: ignore

    missing_types_list: CollectionProperty(name="missing types list", type=MissingBevyType)# type: ignore
    missing_types_list_index: IntProperty(name = "Index for missing types list", default = 0)# type: ignore

    blender_property_mapping = {
        "bool": dict(type=BoolProperty, presets=dict()),

        "u8": dict(type=IntProperty, presets=dict(min=0, max=255)),
        "u16": dict(type=IntProperty, presets=dict(min=0, max=65535)),
        "u32": dict(type=IntProperty, presets=dict(min=0)),
        "u64": dict(type=IntProperty, presets=dict(min=0)),
        "u128": dict(type=IntProperty, presets=dict(min=0)),
        "u64": dict(type=IntProperty, presets=dict(min=0)),
        "usize": dict(type=IntProperty, presets=dict(min=0)),

        "i8": dict(type=IntProperty, presets=dict()),
        "i16":dict(type=IntProperty, presets=dict()),
        "i32":dict(type=IntProperty, presets=dict()),
        "i64":dict(type=IntProperty, presets=dict()),
        "i128":dict(type=IntProperty, presets=dict()),
        "isize": dict(type=IntProperty, presets=dict()),

        "f32": dict(type=FloatProperty, presets=dict()),
        "f64": dict(type=FloatProperty, presets=dict()),

        "glam::Vec2": {"type": FloatVectorProperty, "presets": dict(size = 2) },
        "glam::DVec2": {"type": FloatVectorProperty, "presets": dict(size = 2) },
        "glam::UVec2": {"type": FloatVectorProperty, "presets": dict(size = 2) },

        "glam::Vec3": {"type": FloatVectorProperty, "presets": {"size":3} },
        "glam::Vec3A":{"type": FloatVectorProperty, "presets": {"size":3} },
        "glam::DVec3":{"type": FloatVectorProperty, "presets": {"size":3} },
        "glam::UVec3":{"type": FloatVectorProperty, "presets": {"size":3} },

        "glam::Vec4": {"type": FloatVectorProperty, "presets": {"size":4} },
        "glam::Vec4A": {"type": FloatVectorProperty, "presets": {"size":4} },
        "glam::DVec4": {"type": FloatVectorProperty, "presets": {"size":4} },
        "glam::UVec4":{"type": FloatVectorProperty, "presets": {"size":4, "min":0.0} },

        "glam::Quat": {"type": FloatVectorProperty, "presets": {"size":4} },

        "bevy_color::srgba::Srgba": dict(type = FloatVectorProperty, presets=dict(subtype='COLOR', size=4)),
        "bevy_color::linear_rgba::LinearRgba": dict(type = FloatVectorProperty, presets=dict(subtype='COLOR', size=4)),
        "bevy_color::hsva::Hsva": dict(type = FloatVectorProperty, presets=dict(subtype='COLOR', size=4)),

        "char": dict(type=StringProperty, presets=dict()),
        "str":  dict(type=StringProperty, presets=dict()),
        "alloc::string::String":  dict(type=StringProperty, presets=dict()),
        "alloc::borrow::Cow<str>": dict(type=StringProperty, presets=dict()),

        "enum":  dict(type=EnumProperty, presets=dict()), 

        'bevy_ecs::entity::Entity': {"type": IntProperty, "presets": {"min":0} },
        'bevy_utils::Uuid':  dict(type=StringProperty, presets=dict()),
    }

    value_types_defaults = {
        "string":" ",
        "boolean": True,
        "float": 0.0,
        "uint": 0,
        "int":0,

        # todo : we are re-doing the work of the bevy /rust side here, but it seems more pratical to alway look for the same field name on the blender side for matches
        "bool": True,

        "u8": 0,
        "u16":0,
        "u32":0,
        "u64":0,
        "u128":0,
        "usize":0,

        "i8": 0,
        "i16":0,
        "i32":0,
        "i64":0,
        "i128":0,
        "isize":0,

        "f32": 0.0,
        "f64":0.0,

        "char": " ",
        "str": " ",
        "alloc::string::String": " ",
        "alloc::borrow::Cow<str>":  " ",

        "glam::Vec2": [0.0, 0.0],
        "glam::DVec2":  [0.0, 0.0],
        "glam::UVec2": [0, 0],

        "glam::Vec3": [0.0, 0.0, 0.0],
        "glam::Vec3A":[0.0, 0.0, 0.0],
        "glam::UVec3": [0, 0, 0],

        "glam::Vec4": [0.0, 0.0, 0.0, 0.0], 
        "glam::DVec4": [0.0, 0.0, 0.0, 0.0], 
        "glam::UVec4": [0, 0, 0, 0], 

        "glam::Quat":  [0.0, 0.0, 0.0, 0.0], 

        "bevy_color::srgba::Srgba": [1.0, 1.0, 0.0, 1.0],
        "bevy_color::linear_rgba::LinearRgba": [1.0, 1.0, 0.0, 1.0],
        "bevy_color::hsva::Hsva": [1.0, 1.0, 0.0, 1.0],

        'bevy_ecs::entity::Entity': 0,#4294967295, # this is the same as Bevy's Entity::Placeholder, too big for Blender..sigh
        'bevy_utils::Uuid': '"'+str(uuid.uuid4())+'"'

    }

    type_infos = {}
    type_infos_missing = []
    component_propertyGroups = {}
    component_property_group_classes = []

    custom_types_to_add = {}
    invalid_components = []

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_registry = PointerProperty(type=ComponentsRegistry)

    @classmethod
    def unregister(cls):
        for propgroup_name in cls.component_propertyGroups.keys():
            try:
                delattr(ComponentMetadata, propgroup_name)
                #print("sucess REMOVAL from Metadata")
            except Exception as error:
                pass
                #print("failed to unregister")

        for propgroup_class in cls.component_property_group_classes:
            try:
                bpy.utils.unregister_class(propgroup_class)
                #print("sucess UNREGISTER")
            except Exception as error:
                pass
                #print("NEW failed to unregister")
        
        del bpy.types.WindowManager.components_registry

    def load_schema(self):
        print("load schema", self)
        blenvy = bpy.context.window_manager.blenvy
        component_settings = blenvy.components

        # cleanup previous data if any
        self.long_names_to_propgroup_names.clear()
        self.missing_types_list.clear()
        self.type_infos.clear()
        self.type_infos_missing.clear()

        self.component_propertyGroups.clear()
        self.component_property_group_classes.clear()

        self.custom_types_to_add.clear()
        self.invalid_components.clear()
        # now prepare paths to load data

        with open(component_settings.schema_path_full) as f: 
            data = json.load(f) 
            defs = data["$defs"]
            self.registry = json.dumps(defs) # FIXME:meh ?

        component_settings.start_schema_watcher()       


    # we load the json once, so we do not need to do it over & over again
    def load_type_infos(self):
        print("load type infos")
        ComponentsRegistry.type_infos = json.loads(self.registry)
    
    def has_type_infos(self):
        return len(self.type_infos.keys()) != 0

    # to be able to give the user more feedback on any missin/unregistered types in their schema file
    def add_missing_typeInfo(self, long_name):
        if not long_name in self.type_infos_missing:
            self.type_infos_missing.append(long_name)
            setattr(self, "missing_type_infos", str(self.type_infos_missing))
            item = self.missing_types_list.add()
            item.long_name = long_name

    def add_custom_type(self, long_name, type_definition):
        self.custom_types_to_add[long_name] = type_definition

    def process_custom_types(self):
        for long_name in self.custom_types_to_add:
            self.type_infos[long_name] = self.custom_types_to_add[long_name]
        self.custom_types_to_add.clear()

    # add an invalid component to the list (long name)
    def add_invalid_component(self, component_name):
        self.invalid_components.append(component_name)


    ###########
        
    long_names_to_propgroup_names = {}

    # we keep a list of component propertyGroup around 
    def register_component_propertyGroup(self, nesting, property_group_params):
        property_group_name = self.generate_propGroup_name(nesting)
        (property_group_pointer, property_group_class) = property_group_from_infos(property_group_name, property_group_params)
        self.component_propertyGroups[property_group_name] = property_group_pointer
        self.component_property_group_classes.append(property_group_class)

        return (property_group_pointer, property_group_class)

    # generate propGroup name from nesting level: each longName + nesting is unique
    def generate_propGroup_name(self, nesting):
        key = str(nesting)

        propGroupHash = tiger_hash(key)
        propGroupName = propGroupHash + "_ui"

        # check for collision
        #padding = "  " * (len(nesting) + 1)
        #print(f"{padding}--computing hash for", nesting)
        if propGroupName in self.long_names_to_propgroup_names.values(): 
            print("  WARNING !! you have a collision between the hash of multiple component names: collision for", nesting)

        self.long_names_to_propgroup_names[key] = propGroupName

        return propGroupName
    
    def get_propertyGroupName_from_longName(self, longName):
        return self.long_names_to_propgroup_names.get(str([longName]), None)

    ###########

"""
    object[component_definition.name] = 0.5
    property_manager = object.id_properties_ui(component_definition.name)
    property_manager.update(min=-10, max=10, soft_min=-5, soft_max=5)

    print("property_manager", property_manager)

    object[component_definition.name] = [0.8,0.2,1.0]
    property_manager = object.id_properties_ui(component_definition.name)
    property_manager.update(subtype='COLOR')

    #IDPropertyUIManager
    #rna_ui = object[component_definition.name].get('_RNA_UI')
"""