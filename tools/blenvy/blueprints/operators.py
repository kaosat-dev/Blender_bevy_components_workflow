import os
import bpy
from bpy_types import (Operator)
from bpy.props import (StringProperty)
from ..core.helpers_collections import set_active_collection

class BLENVY_OT_blueprint_select(Operator):
    """Select blueprint """
    bl_idname = "blenvy.blueprint_select"
    bl_label = "Select blueprint"
    bl_options = {"UNDO"}

    blueprint_collection_name: StringProperty(
        name="blueprint collection name",
        description="blueprints to select's collection name ",
    ) # type: ignore

    blueprint_scene_name: StringProperty(
        name="blueprint scene name",
        description="blueprints to select's collection name ",
    ) # type: ignore

    def execute(self, context):
        if self.blueprint_collection_name:
            scene = bpy.data.scenes[self.blueprint_scene_name]
            if scene:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.window.scene = scene
                bpy.context.view_layer.objects.active = None
                set_active_collection(scene, self.blueprint_collection_name)

        return {'FINISHED'}
    