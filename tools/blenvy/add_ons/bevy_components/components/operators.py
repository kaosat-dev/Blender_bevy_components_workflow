import ast
import json
import bpy
from bpy_types import Operator
from bpy.props import (StringProperty, EnumProperty)

from .metadata import add_component_from_custom_property, add_component_to_item, apply_customProperty_values_to_item_propertyGroups, apply_propertyGroup_values_to_item_customProperties, apply_propertyGroup_values_to_item_customProperties_for_component, copy_propertyGroup_values_to_another_item, get_bevy_component_value_by_long_name, get_bevy_components, is_bevy_component_in_item, remove_component_from_item, rename_component, toggle_component

from ..utils import get_item_by_type, get_selected_item

class BLENVY_OT_component_add(Operator):
    """Add Bevy component to object/collection"""
    bl_idname = "blenvy.component_add"
    bl_label = "Add component to object/collection Operator"
    bl_options = {"UNDO"}

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    ) # type: ignore

    component_value: StringProperty(
        name="component_value",
        description="value of the newly added component"
    ) # type: ignore

    target_item_name: StringProperty(
        name="target item name",
        description="name of the object/collection/mesh/material to add the component to",
    ) # type: ignore

    target_item_type: EnumProperty(
        name="target item type",
        description="type of the object/collection/mesh/material to add the component to",
        items=(
            ('OBJECT', "Object", ""),
            ('COLLECTION', "Collection", ""),
            ('MESH', "Mesh", ""),
            ('MATERIAL', "Material", ""),
            ),
        default="OBJECT"
    ) # type: ignore

    def execute(self, context):
        if self.target_item_name == "" or self.target_item_type == "":
            target_item = get_selected_item(context)
            print("adding component ", self.component_type, "to target  '"+target_item.name+"'")
        else:
            target_item = get_item_by_type(self.target_item_type, self.target_item_name)
            print("adding component ", self.component_type, "to target  '"+target_item.name+"'")

        has_component_type = self.component_type != ""
        if has_component_type and target_item is not None:
            type_infos = context.window_manager.components_registry.type_infos
            component_definition = type_infos[self.component_type]
            component_value = self.component_value if self.component_value != "" else None
            add_component_to_item(target_item, component_definition, value=component_value)

        return {'FINISHED'}

class BLENVY_OT_component_copy(Operator):
    """Copy Bevy component from object"""
    bl_idname = "blenvy.component_copy"
    bl_label = "Copy component Operator"
    bl_options = {"UNDO"}

    source_component_name: StringProperty(
        name="source component_name (long)",
        description="name of the component to copy",
    ) # type: ignore

    source_item_name: StringProperty(
        name="source item name",
        description="name of the object/collection to copy the component from",
    ) # type: ignore

    source_item_type: EnumProperty(
        name="source item type",
        description="type of the object/collection to copy the component from: object or collection",
        items=(
            ('OBJECT', "Object", ""),
            ('COLLECTION', "Collection", ""),
            ('MESH', "Mesh", ""),
            ('MATERIAL', "Material", ""),
            ),
        default="OBJECT"
    ) # type: ignore
    
    @classmethod
    def register(cls):
        bpy.types.WindowManager.copied_source_component_name = StringProperty()
        bpy.types.WindowManager.copied_source_item_name = StringProperty()
        bpy.types.WindowManager.copied_source_item_type = StringProperty()

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.copied_source_component_name
        del bpy.types.WindowManager.copied_source_item_name
        del bpy.types.WindowManager.copied_source_item_type


    def execute(self, context):
        if self.source_component_name != '' and self.source_item_name != "" and self.source_item_type != "":
            context.window_manager.copied_source_component_name = self.source_component_name
            context.window_manager.copied_source_item_name = self.source_item_name
            context.window_manager.copied_source_item_type = self.source_item_type
        else:
            self.report({"ERROR"}, "The source object/collection name or component name to copy a component from have not been specified")

        return {'FINISHED'}
    

class BLENVY_OT_component_paste(Operator):
    """Paste Bevy component to object"""
    bl_idname = "blenvy.component_paste"
    bl_label = "Paste component to item Operator"
    bl_options = {"UNDO"}

    def execute(self, context):
        source_item_name = context.window_manager.copied_source_item_name
        source_item_type = context.window_manager.copied_source_item_type
        source_item = get_item_by_type(source_item_type, source_item_name)
        print("HEEEERRE", source_item_name, source_item_type, source_item)
        """if source_item_type == 'Object':
            source_item = bpy.data.objects.get(source_item_name, None)
        elif source_item_type == 'Collection':
            source_item = bpy.data.collections.get(source_item_name, None)"""

        if source_item is None:
            self.report({"ERROR"}, "The source object to copy a component from does not exist")
        else:
            component_name = context.window_manager.copied_source_component_name
            component_value = get_bevy_component_value_by_long_name(source_item, component_name)
            if component_value is None:
                self.report({"ERROR"}, "The source component to copy from does not exist")
            else:
                print("pasting component to item:", source_item, "component name:", str(component_name), "component value:" + str(component_value))
                registry = context.window_manager.components_registry
                target_item = get_selected_item(context)
                copy_propertyGroup_values_to_another_item(source_item, target_item, component_name, registry)

        return {'FINISHED'}
    
class BLENVY_OT_component_remove(Operator):
    """Remove Bevy component from object/collection"""
    bl_idname = "blenvy.component_remove"
    bl_label = "Remove component from object/collection Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to delete",
    ) # type: ignore

    item_name: StringProperty(
        name="object name",
        description="object whose component to delete",
        default=""
    ) # type: ignore

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

    def execute(self, context):
        target = None
        if self.item_name == "":
            self.report({"ERROR"}, "The target to remove ("+ self.component_name +") from does not exist")
        else:
            target = get_item_by_type(self.item_type, self.item_name)

        print("removing component ", self.component_name, "from object  '"+target.name+"'")


        if target is not None:
            if 'bevy_components' in target:
                component_value = get_bevy_component_value_by_long_name(target, self.component_name)
                if component_value is not None:
                    remove_component_from_item(target, self.component_name)
                else :
                    self.report({"ERROR"}, "The component to remove ("+ self.component_name +") does not exist")
            else:
                # for the classic "custom properties"
                if self.component_name in target:
                    del target[self.component_name]
                else:
                    self.report({"ERROR"}, "The component to remove ("+ self.component_name +") does not exist")

        else: 
            self.report({"ERROR"}, "The target to remove ("+ self.component_name +") from does not exist")
        return {'FINISHED'}


class BLENVY_OT_component_remove_from_all_items(Operator):
    """Remove Bevy component from all items"""
    bl_idname = "blenvy.component_remove_from_all_items"
    bl_label = "Remove component from all items Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name (long name)",
        description="component to delete",
    ) # type: ignore

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_remove_progress = bpy.props.FloatProperty(default=-1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_remove_progress

    def execute(self, context):
        print("removing component ", self.component_name, "from all objects/collections")
        total = len(bpy.data.objects) + len(bpy.data.collections)
        for index, object in enumerate(bpy.data.objects):
            if len(object.keys()) > 0:
                if object is not None and is_bevy_component_in_item(object, self.component_name): 
                    remove_component_from_item(object, self.component_name)
            
            progress = index / total
            context.window_manager.components_remove_progress = progress
            # now force refresh the ui
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        for index, collection in enumerate(bpy.data.collections):
            if len(collection.keys()) > 0:
                if collection is not None and is_bevy_component_in_item(collection, self.component_name): 
                    remove_component_from_item(collection, self.component_name)
            
            progress = index / total
            context.window_manager.components_remove_progress = progress
            # now force refresh the ui
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        context.window_manager.components_remove_progress = -1.0

        return {'FINISHED'}


class RenameHelper(bpy.types.PropertyGroup):
    original_name: bpy.props.StringProperty(name="") # type: ignore
    target_name: bpy.props.StringProperty(name="") # type: ignore

    #object: bpy.props.PointerProperty(type=bpy.types.Object)
    @classmethod
    def register(cls):
        bpy.types.WindowManager.bevy_component_rename_helper = bpy.props.PointerProperty(type=RenameHelper)

    @classmethod
    def unregister(cls):
        # remove handlers & co
        del bpy.types.WindowManager.bevy_component_rename_helper

class BLENVY_OT_component_rename_component(Operator):
    """Rename Bevy component"""
    bl_idname = "blenvy.component_rename"
    bl_label = "rename component"
    bl_options = {"UNDO"}

    original_name: bpy.props.StringProperty(default="") # type: ignore
    target_name: StringProperty(
        name="target_name",
        description="new name of component",
    ) # type: ignore

    target_items: bpy.props.StringProperty() # type: ignore

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_rename_progress = bpy.props.FloatProperty(default=-1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_rename_progress

    def execute(self, context):
        registry = context.window_manager.components_registry
        settings = context.window_manager.bevy_component_rename_helper
        original_name = settings.original_name if self.original_name == "" else self.original_name
        target_name = self.target_name


        print("renaming components: original name", original_name, "target_name", self.target_name, "targets", self.target_items)
        target_items = json.loads(self.target_items)
        errors = []
        warnings = []
        total = len(target_items)


        if original_name != '' and target_name != '' and original_name != target_name and len(target_items) > 0:
            for index, item_data in enumerate(target_items):
                [item_name, item_type] = item_data
                item = get_item_by_type(item_type, item_name)

                if item and original_name in get_bevy_components(item) or original_name in item:
                    try:
                        # attempt conversion
                        warnings += rename_component(registry=registry, item=item, original_long_name=original_name, new_long_name=target_name)
                    except Exception as error:
                        if '__disable__update' in item:
                            del item["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
                        components_metadata = getattr(item, "components_meta", None)
                        if components_metadata:
                            components_metadata = components_metadata.components
                            component_meta =  next(filter(lambda component: component["long_name"] == target_name, components_metadata), None)
                            if component_meta:
                                component_meta.invalid = True
                                component_meta.invalid_details = "wrong custom property value, overwrite them by changing the values in the ui or change them & regenerate"

                        errors.append( "wrong custom property values to generate target component: object: '" + item.name + "', error: " + str(error))
   
                progress = index / total
                context.window_manager.components_rename_progress = progress

                try:
                    # now force refresh the ui
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                except: pass # this is to allow this to run in cli/headless mode

        if len(errors) > 0:
            self.report({'ERROR'}, "Failed to rename component: Errors:" + str(errors))
        else: 
            self.report({'INFO'}, f"Sucessfully renamed component for {total} items: Warnings: {str(warnings)}")

        #clear data after we are done
        self.original_name = ""
        context.window_manager.bevy_component_rename_helper.original_name = ""
        context.window_manager.components_rename_progress = -1.0

        return {'FINISHED'}


class BLENVY_OT_component_from_custom_property(Operator):
    """Generate Bevy components from custom property"""
    bl_idname = "blenvy.component_from_custom_property"
    bl_label = "Generate component from custom_property Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to generate custom properties for",
    ) # type: ignore

    def execute(self, context):
        object = context.object

        error = False
        try:
            add_component_from_custom_property(object)
        except Exception as error:
            del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
            error = True
            self.report({'ERROR'}, "Failed to update propertyGroup values from custom property: Error:" + str(error))
        if not error:
            self.report({'INFO'}, "Sucessfully generated UI values for custom properties for selected object")
        return {'FINISHED'}


class BLENVY_OT_component_fix(Operator):
    """Attempt to fix Bevy component"""
    bl_idname = "blenvy.component_fix"
    bl_label = "Fix component (attempts to)"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to fix",
    ) # type: ignore

    def execute(self, context):
        object = context.object
        error = False
        try:
            apply_propertyGroup_values_to_item_customProperties_for_component(object, self.component_name)
        except Exception as error:
            if "__disable__update" in object:
                del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
            error = True
            self.report({'ERROR'}, "Failed to fix component: Error:" + str(error))
        if not error:
            self.report({'INFO'}, "Sucessfully fixed component (please double check component & its custom property value)")
        return {'FINISHED'}

class BLENVY_OT_component_toggle_visibility(Operator):
    """Toggle Bevy component's visibility"""
    bl_idname = "blenvy.component_toggle_visibility"
    bl_label = "Toggle component visibility"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to toggle",
    ) # type: ignore

    def execute(self, context):
        target = get_selected_item(context)
        toggle_component(target, self.component_name)
        return {'FINISHED'}




    
class BLENVY_OT_components_refresh_custom_properties_all(Operator):
    """Apply registry to ALL objects: update the custom property values of all objects based on their definition, if any"""
    bl_idname = "object.refresh_custom_properties_all"
    bl_label = "Apply Registry to all objects"
    bl_options = {"UNDO"}

    @classmethod
    def register(cls):
        bpy.types.WindowManager.custom_properties_from_components_progress_all = bpy.props.FloatProperty(default=-1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.custom_properties_from_components_progress_all

    def execute(self, context):
        print("apply registry to all")
        #context.window_manager.components_registry.load_schema()
        total = len(bpy.data.objects)

        for index, object in enumerate(bpy.data.objects):
            apply_propertyGroup_values_to_item_customProperties(object)
            progress = index / total
            context.window_manager.custom_properties_from_components_progress_all = progress
            # now force refresh the ui
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        context.window_manager.custom_properties_from_components_progress_all = -1.0

        return {'FINISHED'}
    
class BLENVY_OT_components_refresh_custom_properties_current(Operator):
    """Apply registry to CURRENT object: update the custom property values of current object based on their definition, if any"""
    bl_idname = "object.refresh_custom_properties_current"
    bl_label = "Apply Registry to current object"
    bl_options = {"UNDO"}

    @classmethod
    def register(cls):
        bpy.types.WindowManager.custom_properties_from_components_progress = bpy.props.FloatProperty(default=-1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.custom_properties_from_components_progress

    def execute(self, context):
        print("apply registry to current object")
        object = context.object
        context.window_manager.custom_properties_from_components_progress = 0.5
        # now force refresh the ui
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        apply_propertyGroup_values_to_item_customProperties(object)

        context.window_manager.custom_properties_from_components_progress = -1.0
        return {'FINISHED'}
    

class BLENVY_OT_components_refresh_propgroups_current(Operator):
    """Update UI values from custom properties to CURRENT object"""
    bl_idname = "object.refresh_ui_from_custom_properties_current"
    bl_label = "Apply custom_properties to current object"
    bl_options = {"UNDO"}

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_from_custom_properties_progress = bpy.props.FloatProperty(default=-1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_from_custom_properties_progress

    def execute(self, context):
        print("apply custom properties to current object")
        object = context.object
        error = False
        try:
            apply_customProperty_values_to_item_propertyGroups(object)
            progress = 0.5
            context.window_manager.components_from_custom_properties_progress = progress
            try:
                # now force refresh the ui
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            except:pass # ony run in ui

        except Exception as error_message:
            del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
            error = True
            self.report({'ERROR'}, "Failed to update propertyGroup values from custom property: Error:" + str(error_message))
        if not error:
            self.report({'INFO'}, "Sucessfully generated UI values for custom properties for selected object")
        context.window_manager.components_from_custom_properties_progress = -1.0

        return {'FINISHED'}
    

class BLENVY_OT_components_refresh_propgroups_all(Operator):
    """Update UI values from custom properties to ALL object"""
    bl_idname = "object.refresh_ui_from_custom_properties_all"
    bl_label = "Apply custom_properties to all objects"
    bl_options = {"UNDO"}

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_from_custom_properties_progress_all = bpy.props.FloatProperty(default=-1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_from_custom_properties_progress_all

    def execute(self, context):
        print("apply custom properties to all object")
        bpy.context.window_manager.components_registry.disable_all_object_updates = True
        errors = []
        total = len(bpy.data.objects)

        for index, object in enumerate(bpy.data.objects):
          
            try:
                apply_customProperty_values_to_item_propertyGroups(object)
            except Exception as error:
                del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
                errors.append( "object: '" + object.name + "', error: " + str(error))

            progress = index / total
            context.window_manager.components_from_custom_properties_progress_all = progress
            # now force refresh the ui
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)



        if len(errors) > 0:
            self.report({'ERROR'}, "Failed to update propertyGroup values from custom property: Errors:" + str(errors))
        else: 
            self.report({'INFO'}, "Sucessfully generated UI values for custom properties for all objects")
        bpy.context.window_manager.components_registry.disable_all_object_updates = False
        context.window_manager.components_from_custom_properties_progress_all = -1.0
        return {'FINISHED'}
