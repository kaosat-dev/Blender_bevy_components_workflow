import json
from bpy_types import Operator
from bpy.props import (StringProperty, EnumProperty, IntProperty)
from ..utils import get_item_by_type

class BLENVY_OT_component_list_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "blenvy.component_list_actions"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
            ('SELECT', "Select", "")
        )
    ) # type: ignore
    
    property_group_path: StringProperty(
        name="property group path",
        description="",
    ) # type: ignore

    component_name: StringProperty(
        name="component name",
        description="",
    ) # type: ignore

    item_name: StringProperty(
        name="item name",
        description="item object/collections we are working on",
        default=""
    ) # type: ignore

    item_type : EnumProperty(
        name="item type",
        description="type of the item we are working on : object or collection",
        items=(
            ('OBJECT', "Object", ""),
            ('COLLECTION', "Collection", ""),
            ('MESH', "Mesh", ""),
            ('MATERIAL', "Material", ""),
            ),
        default="OBJECT"
    ) # type: ignore


    selection_index: IntProperty() # type: ignore

    def invoke(self, context, event):
        item = get_item_by_type(self.item_type, self.item_name)

        # information is stored in component meta
        components_in_item = item.components_meta.components
        component_meta =  next(filter(lambda component: component["long_name"] == self.component_name, components_in_item), None)

        propertyGroup = component_meta
        for path_item in json.loads(self.property_group_path):
            propertyGroup = getattr(propertyGroup, path_item)

        target_list = getattr(propertyGroup, "list")
        index = getattr(propertyGroup, "list_index")


        if self.action == 'DOWN' and index < len(target_list) - 1:
            #item_next = scn.rule_list[index + 1].name
            target_list.move(index, index + 1)
            propertyGroup.list_index += 1
        
        elif self.action == 'UP' and index >= 1:
            #item_prev = scn.rule_list[index - 1].name
            target_list.move(index, index - 1)
            propertyGroup.list_index -= 1

        elif self.action == 'REMOVE':
            target_list.remove(index)
            propertyGroup.list_index = min(max(0, index - 1), len(target_list) - 1) 

        if self.action == 'ADD':
            item = target_list.add()
            propertyGroup.list_index = index + 1 # we use this to force the change detection
            #info = '"%s" added to list' % (item.name)
            #self.report({'INFO'}, info)

        if self.action == 'SELECT':
            propertyGroup.list_index = self.selection_index


        return {"FINISHED"}