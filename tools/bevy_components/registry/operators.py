import os
import bpy
from bpy_types import (Operator, PropertyGroup, UIList)
from bpy.props import (StringProperty)
from bpy_extras.io_utils import ImportHelper

from ..components.metadata import apply_propertyGroup_values_to_object_customProperties, ensure_metadata_for_all_objects
from ..components.operators import GenerateComponent_From_custom_property_Operator
from ..propGroups.prop_groups import generate_propertyGroups_for_components

class ReloadRegistryOperator(Operator):
    """Reload registry operator"""
    bl_idname = "object.reload_registry"
    bl_label = "Reload Registry"
    bl_options = {"UNDO"}

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    )

    def execute(self, context):
        print("reload registry")
        context.window_manager.components_registry.load_schema()
        generate_propertyGroups_for_components()
        print("")
        print("")
        print("")
        ensure_metadata_for_all_objects()
        #add_metadata_to_components_without_metadata(context.object)

        return {'FINISHED'}
    
class COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL(Operator):
    """Apply registry to ALL objects operator: update the custom property values of all objects based on their definition, if any"""
    bl_idname = "object.refresh_custom_properties_all"
    bl_label = "Apply Registry to all objects"
    bl_options = {"UNDO"}

    def execute(self, context):
        print("apply registry to all")
        #context.window_manager.components_registry.load_schema()
        for object in bpy.data.objects:
            apply_propertyGroup_values_to_object_customProperties(object)

        return {'FINISHED'}
    
class COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT(Operator):
    """Apply registry to ALL objects operator: updated the custom property values of all objects based on their definition, if any"""
    bl_idname = "object.refresh_custom_properties_current"
    bl_label = "Apply Registry to current object"
    bl_options = {"UNDO"}

    def execute(self, context):
        print("apply registry to current object")
        object = context.object
        apply_propertyGroup_values_to_object_customProperties(object)
        return {'FINISHED'}

class OT_OpenFilebrowser(Operator, ImportHelper): 
    bl_idname = "generic.open_filebrowser" 
    bl_label = "Open the file browser" 

    filter_glob: StringProperty( 
        default='*.json', 
        options={'HIDDEN'} 
    )
    def execute(self, context): 
        """Do something with the selected file(s)."""

        filename, extension = os.path.splitext(self.filepath) 
        print('Selected file:', self.filepath)
        print('File name:', filename)
        print('File extension:', extension)

        file_path = bpy.data.filepath
        # Get the folder
        folder_path = os.path.dirname(file_path)
        print("file_path", file_path)
        print("folder_path", folder_path)

        relative_path = os.path.relpath(self.filepath, folder_path)
        print("rel path", relative_path )
        context.window_manager.components_registry.schemaPath = relative_path
        
        return {'FINISHED'}
    