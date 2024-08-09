import os
import bpy
from bpy_types import (Operator)
from bpy.props import (StringProperty)
from bpy_extras.io_utils import ImportHelper
from ....settings import upsert_settings
from ..components.metadata import ensure_metadata_for_all_items
from ..propGroups.prop_groups import generate_propertyGroups_for_components

class BLENVY_OT_components_registry_reload(Operator):
    """Reloads registry (schema file) from disk, generates propertyGroups for components & ensures all objects have metadata """
    bl_idname = "blenvy.components_registry_reload"
    bl_label = "Reload Registry"
    bl_options = {"UNDO"}

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    ) # type: ignore

    def execute(self, context):
        print("reload registry")
        context.window_manager.components_registry.load_schema()
        generate_propertyGroups_for_components()
        print("")
        print("")
        print("")
        ensure_metadata_for_all_items()

        # now force refresh the ui
        for area in context.screen.areas: 
            for region in area.regions:
                if region.type == "UI":
                    region.tag_redraw()

        return {'FINISHED'}

class BLENVY_OT_components_registry_browse_schema(Operator, ImportHelper):
    """Browse for registry json file"""
    bl_idname = "blenvy.components_registry_browse_schema" 
    bl_label = "Open the file browser" 

    filter_glob: StringProperty( 
        default='*.json', 
        options={'HIDDEN'} 
    ) # type: ignore
    
    def execute(self, context): 
        """Do something with the selected file(s)."""
        #filename, extension = os.path.splitext(self.filepath) 
        file_path = bpy.data.filepath
        # Get the folder
        folder_path = os.path.dirname(file_path)
        relative_path = os.path.relpath(self.filepath, folder_path)

        blenvy = context.window_manager.blenvy
        blenvy.components.schema_path = relative_path
        upsert_settings(blenvy.components.settings_save_path, {"schema_path": relative_path})
        
        return {'FINISHED'}
    
