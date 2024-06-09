import bpy
from bpy.types import Operator

class SCENES_LIST_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "scene_list.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""))
    ) # type: ignore

    scene_type: bpy.props.EnumProperty(
        items=(
            ('LEVEL', "Level", ""),
            ('LIBRARY', "Library", ""),
        )
    ) # type: ignore

    scene_name : bpy.props.StringProperty(name="scene_name")# type: ignore
    
    def invoke(self, context, event): 
        if self.action == 'REMOVE':
            bpy.data.scenes[self.scene_name].blenvy_scene_type = 'None'
            """info = 'Item "%s" removed from list' % (target[idx].name)
            target.remove(idx)

            setattr(source, target_index, current_index -1 )
            self.report({'INFO'}, info)"""

        if self.action == 'ADD':
            scene_to_add = None
            if self.scene_type == "LEVEL":
                if context.window_manager.blenvy.main_scene_selector:
                    scene_to_add = context.window_manager.blenvy.main_scene_selector
                    scene_to_add.blenvy_scene_type = "Level"
            else:
                if context.window_manager.blenvy.library_scene_selector:
                    scene_to_add = context.window_manager.blenvy.library_scene_selector
                    scene_to_add.blenvy_scene_type = "Library"

            if scene_to_add is not None:
                print("adding scene", scene_to_add)
                
                if self.scene_type == "LEVEL":
                    context.window_manager.blenvy.main_scene_selector = None
                else:
                    context.window_manager.blenvy.library_scene_selector = None

                #setattr(source, target_index, len(target) - 1)

                #info = '"%s" added to list' % (item.name)
                #self.report({'INFO'}, info)
        
        return {"FINISHED"}
