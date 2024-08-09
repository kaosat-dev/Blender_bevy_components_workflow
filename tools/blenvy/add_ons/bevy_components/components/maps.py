import json
from bpy_types import Operator, UIList
from bpy.props import (StringProperty, EnumProperty, PointerProperty, FloatVectorProperty, IntProperty)

from ..propGroups.conversions_from_prop_group import property_group_value_to_custom_property_value
from ..utils import get_item_by_type

class BLENVY_OT_component_map_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "blenvy.component_map_actions"
    bl_label = "Map Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""))) # type: ignore
    
    property_group_path: StringProperty(
        name="property group path",
        description="",
    ) # type: ignore

    component_name: StringProperty(
        name="component name",
        description="",
    ) # type: ignore

    target_index: IntProperty(name="target index", description="index of item to manipulate")# type: ignore

    item_type : EnumProperty(
        name="item type",
        description="type of the item to select: object or collection",
        items=(
            ('OBJECT', "Object", ""),
            ('COLLECTION', "Collection", ""),
            ('MESH', "Mesh", ""),
            ('MATERIAL', "Material", ""),
            ),
        default="OBJECT"
    ) # type: ignore

    item_name: StringProperty(
        name="object name",
        description="object whose component to delete",
        default=""
    ) # type: ignore

    def invoke(self, context, event):

        item = get_item_by_type(self.item_type, self.item_name)

        # information is stored in component meta
        components_in_item = item.components_meta.components
        component_meta =  next(filter(lambda component: component["long_name"] == self.component_name, components_in_item), None)

        propertyGroup = component_meta
        for path_item in json.loads(self.property_group_path):
            propertyGroup = getattr(propertyGroup, path_item)

        keys_list = getattr(propertyGroup, "list")
        index = getattr(propertyGroup, "list_index")

        values_list = getattr(propertyGroup, "values_list")
        values_index = getattr(propertyGroup, "values_list_index")

        key_setter = getattr(propertyGroup, "keys_setter")
        value_setter = getattr(propertyGroup, "values_setter")

        if self.action == 'DOWN' and index < len(keys_list) - 1:
            #item_next = scn.rule_list[index + 1].name
            keys_list.move(index, index + 1)
            propertyGroup.list_index += 1
        
        elif self.action == 'UP' and index >= 1:
            #item_prev = scn.rule_list[index - 1].name
            keys_list.move(index, index - 1)
            propertyGroup.list_index -= 1

        elif self.action == 'REMOVE':
            index = self.target_index
            keys_list.remove(index)
            values_list.remove(index)
            propertyGroup.list_index = min(max(0, index - 1), len(keys_list) - 1) 
            propertyGroup.values_index = min(max(0, index - 1), len(keys_list) - 1) 

        if self.action == 'ADD':            
            # first we gather all key/value pairs
            hashmap = {}
            for index, key in enumerate(keys_list):
                print("key", key)
                key_entry = {}
                for field_name in key.field_names:
                    key_entry[field_name] = getattr(key, field_name, None)
                """value_entry = {}
                for field_name in values_list[index].field_names:
                    value_entry[field_name] = values_list[index][field_name]"""
                hashmap[json.dumps(key_entry)] = index

            # then we need to find the index of a specific value if it exists
            key_entry = {}
            for field_name in key_setter.field_names:
                key_entry[field_name] = getattr(key_setter, field_name, None)
            key_to_add = json.dumps(key_entry)
            existing_index = hashmap.get(key_to_add, None)

            if existing_index is None:
                #print("adding new value", "key field names", key_setter.field_names, "value_setter", value_setter, "field names", value_setter.field_names)
                key = keys_list.add()
                # copy the values over 
                for field_name in key_setter.field_names:
                    val = getattr(key_setter, field_name, None)
                    if val is not None:
                        key[field_name] = val
                    # TODO: add error handling

                value = values_list.add()
                # copy the values over 
                is_enum = getattr(value_setter, "with_enum", False)
                if not is_enum:
                    for field_name in list(value_setter.field_names):
                        val = getattr(value_setter, field_name, None)
                        if val is not None:
                            value[field_name] = val
                else:
                    selection = getattr(value_setter, "selection", None)
                    setattr(value, 'selection', selection)
                    selector = "variant_" + selection
                    try:
                        val = getattr(value_setter, selector, None)
                        for field_name in val.field_names:
                            source = getattr(val, field_name)
                            setattr(getattr(value, selector), field_name, source)
                    except Exception as inst:
                        print("EROOR", inst)
                       
                    # TODO: add error handling
                propertyGroup.list_index = index + 1 # we use this to force the change detection
                propertyGroup.values_index = index + 1 # we use this to force the change detection
            else:
                for field_name in value_setter.field_names:
                    values_list[existing_index][field_name] = value_setter[field_name]


            #info = '"%s" added to list' % (item.name)
            #self.report({'INFO'}, info)

        return {"FINISHED"}