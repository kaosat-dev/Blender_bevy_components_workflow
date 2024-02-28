bl_info = {
    "name": "gltf_auto_export",
    "author": "kaosigh",
    "version": (0, 10, 0),
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "description": "glTF/glb auto-export",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "Import-Export"
}

import bpy
from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )


# glTF extensions are named following a convention with known prefixes.
# See: https://github.com/KhronosGroup/glTF/tree/main/extensions#about-gltf-extensions
# also: https://github.com/KhronosGroup/glTF/blob/main/extensions/Prefixes.md
glTF_extension_name = "EXT_auto_export"

# Support for an extension is "required" if a typical glTF viewer cannot be expected
# to load a given model without understanding the contents of the extension.
# For example, a compression scheme or new image format (with no fallback included)
# would be "required", but physics metadata or app-specific settings could be optional.
extension_is_required = False

class ExampleExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name=bl_info["name"],
        description='Include this extension in the exported glTF file.',
        default=True
        )
    
    auto_export_main_scene_name: StringProperty(
        name='Main scene',
        description='The name of the main scene/level/world to auto export',
        default='Scene'
    )
    auto_export_output_folder: StringProperty(
        name='Export folder (relative)',
        description='The root folder for all exports(relative to current file) Defaults to current folder',
        default=''
    )
    auto_export_library_scene_name: StringProperty(
        name='Library scene',
        description='The name of the library scene to auto export',
        default='Library'
    )
    # scene components
    auto_export_scene_settings: BoolProperty(
        name='Export scene settings',
        description='Export scene settings ie AmbientLighting, Bloom, AO etc',
        default=False
    )

    # blueprint settings
    auto_export_blueprints: BoolProperty(
        name='Export Blueprints',
        description='Replaces collection instances with an Empty with a BlueprintName custom property',
        default=True
    )
    auto_export_blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the Export folder)',
        default='library'
    )

    auto_export_materials_library: BoolProperty(
        name='Export materials library',
        description='remove materials from blueprints and use the material library instead',
        default=False
    )
    auto_export_materials_path: StringProperty(
        name='Materials path',
        description='path to export the materials libraries to (relative to the root folder)',
        default='materials'
    )

def register():
    bpy.utils.register_class(ExampleExtensionProperties)
    bpy.types.Scene.ExampleExtensionProperties = bpy.props.PointerProperty(type=ExampleExtensionProperties)

def register_panel():
    # Register the panel on demand, we need to be sure to only register it once
    # This is necessary because the panel is a child of the extensions panel,
    # which may not be registered when we try to register this extension
    try:
        bpy.utils.register_class(GLTF_PT_UserExtensionPanel)
    except Exception:
        pass

    # If the glTF exporter is disabled, we need to unregister the extension panel
    # Just return a function to the exporter so it can unregister the panel
    return unregister_panel


def unregister_panel():
    # Since panel is registered on demand, it is possible it is not registered
    try:
        bpy.utils.unregister_class(GLTF_PT_UserExtensionPanel)
    except Exception:
        pass


def unregister():
    unregister_panel()
    bpy.utils.unregister_class(ExampleExtensionProperties)
    del bpy.types.Scene.ExampleExtensionProperties

class GLTF_PT_UserExtensionPanel(bpy.types.Panel):

    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Enabled"
    bl_parent_id = "GLTF_PT_export_user_extensions"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

    def draw_header(self, context):
        props = bpy.context.scene.ExampleExtensionProperties
        self.layout.prop(props, 'enabled')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        props = bpy.context.scene.ExampleExtensionProperties
        layout.active = props.enabled

        props = bpy.context.scene.ExampleExtensionProperties
        for bla in props.__annotations__:
            layout.prop(props, bla)


class glTF2ExportUserExtension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.properties = bpy.context.scene.ExampleExtensionProperties

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if self.properties.enabled:
            if gltf2_object.extensions is None:
                gltf2_object.extensions = {}
            print("bla bla")
            gltf2_object.extensions[glTF_extension_name] = self.Extension(
                name=glTF_extension_name,
                extension={"auto_export_blueprints": self.properties.auto_export_blueprints},
                required=extension_is_required
            )


def did_export_parameters_change(current_params, previous_params):
    set1 = set(previous_params.items())
    set2 = set(current_params.items())
    difference = dict(set1 ^ set2)
    
    changed_param_names = list(set(difference.keys())- set(AutoExportGltfPreferenceNames))
    changed_parameters = len(changed_param_names) > 0
    return changed_parameters

# original in export_blueprints => export_collections
 # The part below is not necessary NORMALLY , but blender crashes in the "normal" case when using bpy.context.temp_override, 
        #if relevant we replace sub collections instances with placeholders too
        # this is not needed if a collection/blueprint does not have sub blueprints or sub collections
        collection_in_blueprint_hierarchy = collection_name in blueprint_hierarchy and len(blueprint_hierarchy[collection_name]) > 0
        collection_has_child_collections = len(bpy.data.collections[collection_name].children) > 0
        #if collection_in_blueprint_hierarchy or collection_has_child_collections:
    


        """else:
            print("standard export")
             # set active scene to be the library scene
            original_scene = bpy.context.window.scene
            bpy.context.window.scene = library_scene
            with bpy.context.temp_override(scene=library_scene):
                print("active scene", bpy.context.scene)
            export_gltf(gltf_output_path, export_settings)
            bpy.context.window.scene = original_scene"""

"""
                blueprint_template = object['Template'] if 'Template' in object else False
                if blueprint_template and parent_empty is None: # ONLY WORKS AT ROOT LEVEL
                    print("BLUEPRINT TEMPLATE", blueprint_template, destination_collection, parent_empty)
                    for object in source_collection.objects:
                        if object.type == 'EMPTY' and object.name.endswith("components"):
                            original_collection = bpy.data.collections[collection_name]
                            components_holder = object
                            print("WE CAN INJECT into", object, "data from", original_collection)

                            # now we look for components inside the collection
                            components = {}
                            for object in original_collection.objects:
                                if object.type == 'EMPTY' and object.name.endswith("components"):
                                    for component_name in object.keys():
                                        if component_name not in '_RNA_UI':
                                            print( component_name , "-" , object[component_name] )
                                            components[component_name] = object[component_name]

                            # copy template components into target object
                            for key in components:
                                print("copying ", key,"to", components_holder)
                                if not key in components_holder:
                                    components_holder[key] = components[key]                            
                """

# potentially useful alternative
def duplicate_object2(object, original_name):
    print("copy object", object)

    with bpy.context.temp_override(object=object, active_object = object):
        bpy.ops.object.duplicate(linked=False)
        new_obj = bpy.context.active_object

        print("new obj", new_obj, "bpy.context.view_layer", bpy.context.view_layer.objects)
        for obj in bpy.context.view_layer.objects:
            print("obj", obj)
        bpy.context.view_layer.update()
        new_obj.name = original_name

        if object.animation_data:
            print("OJECT ANIMATION")
            new_obj.animation_data.action = object.animation_data.action.copy()
      
    return new_obj