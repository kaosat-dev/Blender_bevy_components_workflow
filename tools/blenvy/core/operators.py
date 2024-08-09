from bpy_types import (Operator)
from bpy.props import (EnumProperty)

class BLENVY_OT_tooling_switch(Operator):
    """Switch blenvy tooling"""
    bl_idname = "bevy.tooling_switch"
    bl_label = "Switch bevy tooling"
    #bl_options = {}

    tool: EnumProperty(
            items=(
                ('COMPONENTS', "Components", "Switch to components"),
                ('BLUEPRINTS', "Blueprints", ""),
                ('LEVELS', "Levels", ""),
                ('ASSETS', "Assets", ""),
                ('SETTINGS', "Settings", ""),
                ('TOOLS', "Tools", ""),
                )
        ) # type: ignore

    @classmethod
    def description(cls, context, properties):
        return properties.tool

    def execute(self, context):
        context.window_manager.blenvy.mode = self.tool
        return {'FINISHED'}
    


class BLENVY_OT_configuration_switch(Operator):
    """Switch tooling configuration"""
    bl_idname = "bevy.config_switch"
    bl_label = "Switch blenvy configuration"
    #bl_options = {}

    tool: EnumProperty(
            items=(
                ('COMMON', "Common", "Switch to common configuration"),
                ('COMPONENTS', "Components", "Switch to components configuration"),
                ('EXPORT', "Export", "Switch to export configuration"),
            )
        ) # type: ignore

    @classmethod
    def description(cls, context, properties):
        return properties.tool

    def execute(self, context):
        context.window_manager.blenvy.config_mode = self.tool
        return {'FINISHED'}
    