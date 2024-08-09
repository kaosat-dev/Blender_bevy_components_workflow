import os
import bpy
from bpy_types import (Operator)
from bpy.props import (StringProperty)

class BLENVY_OT_level_select(Operator):
    """Select level """
    bl_idname = "blenvy.level_select"
    bl_label = "Select level"
    bl_options = {"UNDO"}

    level_name: StringProperty(
        name="level name",
        description="level to select",
    ) # type: ignore

    def execute(self, context):
        if self.level_name:
            scene = bpy.data.scenes[self.level_name]
            if scene:
                # bpy.ops.object.select_all(action='DESELECT')
                bpy.context.window.scene = scene

        return {'FINISHED'}
    