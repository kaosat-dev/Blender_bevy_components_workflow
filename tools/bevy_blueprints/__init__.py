bl_info = {
    "name": "bevy_blueprints",
    "author": "kaosigh",
    "version": (0, 0, 1),
    "blender": (3, 4, 0),
    "location": "VIEW_3D",
    "description": "UI to help create Bevy blueprints and components",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "User Interface"
}
import bpy
from bpy_types import Operator
from bpy.props import (StringProperty, EnumProperty, PointerProperty)
from .helpers import make_empty3


stored_component = None
bla = PointerProperty()

class CreateBlueprintOperator(Operator):
    """Print object name in Console"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    def execute(self, context):
        print("calling operator")
        print (context.object)

        blueprint_name = "NewBlueprint"
        collection = bpy.data.collections.new(blueprint_name)
        bpy.context.scene.collection.children.link(collection)

        collection['AutoExport'] = True

        blueprint_name = collection.name

        components_empty = make_empty3(blueprint_name + "_components", [0,0,0], [0,0,0], [0,0,0])
        bpy.ops.collection.objects_remove_all()

        collection.objects.link(components_empty)


        return {'FINISHED'}
    
class AddComponentToBlueprintOperator(Operator):
    """Add component to blueprint"""
    bl_idname = "object.addblueprint_to_component"
    bl_label = "Add component to blueprint Operator"

    def execute(self, context):
        print("adding component to blueprint")
        original_active_object = bpy.context.active_object

        # fixme: refactor, do this better
        collection = context.collection
        current_components_container = None
        for child in collection.objects:
            if child.name == collection.name + "_components":
                current_components_container= child

        if current_components_container is not None:
            current_components_container["foo"] = 42


        return {'FINISHED'}

import ast

class CopyComponentOperator(Operator):
    """Copy component from blueprint"""
    bl_idname = "object.copy_component"
    bl_label = "Copy component from blueprint Operator"


    target_property: StringProperty(
        name="component_name",
        description="component to copy",
    )

    target_property_value: StringProperty(
        name="component_value",
        description="component value to copy",
    )

    def execute(self, context):
        print("copying component to blueprint")
        print ("infos", self.target_property, self.target_property_value)
        print("recast", ast.literal_eval(self.target_property_value))

        #stored_component

        return {'FINISHED'}
    
class DeleteComponentOperator(Operator):
    """Delete component from blueprint"""
    bl_idname = "object.delete_component"
    bl_label = "Delete component from blueprint Operator"
    bl_options = {"REGISTER", "UNDO"}

    target_property: StringProperty(
        name="component_name",
        description="component to delete",
    )

    def execute(self, context):
        print("delete component to blueprint")
        print (context.object)

        # fixme: refactor, do this better
        collection = context.collection
        current_components_container = None
        for child in collection.objects:
            if child.name == collection.name + "_components":
                current_components_container= child
        if current_components_container is not None: 
            del current_components_container[self.target_property]

        return {'FINISHED'}

class PasteComponentOperator(Operator):
    """Paste component to blueprint"""
    bl_idname = "object.paste_component"
    bl_label = "Paste component to blueprint Operator"

    def execute(self, context):
        print("pasting component to blueprint")
        print (context.object)
        

        return {'FINISHED'}

class BEVY_BLUEPRINTS_PT_TestPanel(bpy.types.Panel):
    bl_idname = "BEVY_BLUEPRINTS_PT_TestPanel"
    bl_label = "Bevy Components"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"

    def draw(self, context):



        component_types =  EnumProperty(
            name='ComponentType',
            items=(('GLB', 'glTF Binary (.glb)',
                    'Exports a single file, with all data packed in binary form. '
                    'Most efficient and portable, but more difficult to edit later'),
                ('GLTF_EMBEDDED', 'glTF Embedded (.gltf)',
                    'Exports a single file, with all data packed in JSON. '
                    'Less efficient than binary, but easier to edit later'),
                ('GLTF_SEPARATE', 'glTF Separate (.gltf + .bin + textures)',
                    'Exports multiple files, with separate JSON, binary and texture data. '
                    'Easiest to edit later')),
            description=(
                'Component types'
            ),
            default='GLB'
        )



        layout = self.layout
        obj = context.object
        collection = context.collection

        layout.label(text="Create blueprint:")

        col = layout.column(align=True)
        row = col.row(align=True)

        #row.prop(obj, "show_name", toggle=True, icon="FILE_FONT", text="Create blueprint")

        col.operator(CreateBlueprintOperator.bl_idname, text="Create blueprint", icon="CONSOLE")
        layout.separator()

     
        #layout.label(text =obj.name)
        # layout.label(text =context.collection.name)
        # and hasattr(collection, 'AutoExport')
        current_components_container = None
        has_components = False
        for child in collection.objects:
            if child.name == collection.name + "_components":
                has_components = True
                current_components_container= child

        # layout.label(text= "has_components" + str(has_components))
        if collection is not None and has_components:
            layout.label(text="Edit blueprint: "+ collection.name)
            layout.operator(AddComponentToBlueprintOperator.bl_idname, text="Add component", icon="CONSOLE")
            layout.operator(PasteComponentOperator.bl_idname, text="Paste component", icon="PASTEDOWN")

            #layout.prop(component_types, "")
            # components_empty_name = collection.name + "_components"
            # fixme: hack for toggling components
            # current_components_container["enableds"] = {}
            #current_components_container["toto"] = False
            
         
            for component_name in dict(current_components_container):
                #current_components_container["enableds"][component_name] = False
                #bla = Bool
                #bla["enabled"] = False
                #layout.label(text= component)
                #layout.prop_enum
                col = layout.column(align=True)
                row = col.row(align=True)

                component_value = current_components_container[component_name]
               
                
                # row.prop(current_components_container, '["'+ component_name +'"].name', text="")
                row.label(text=component_name)

                # add a "disabled" pseudo property for all of the components
                #row.prop(current_components_container.enableds, "enabled", text="")

                row.prop(current_components_container, '["'+ component_name +'"]', text="")
                op = row.operator(CopyComponentOperator.bl_idname, text="", icon="SETTINGS")
               

                op = row.operator(DeleteComponentOperator.bl_idname, text="", icon="X")
                op.target_property = component_name
                
                op =row.operator(CopyComponentOperator.bl_idname, text="", icon="COPYDOWN")
                op.target_property = component_name
                op.target_property_value = str(component_value)
                #layout.prop(obj,'["boolean"]',text='test')

                # bpy.ops.wm.properties_remove
                #bpy.ops.wm.properties_add()

        else: 
            layout.label(text ="Select a collection/blueprint to edit it")


classes = [
    CreateBlueprintOperator,
    AddComponentToBlueprintOperator,  
    CopyComponentOperator,
    PasteComponentOperator,
    DeleteComponentOperator,
    BEVY_BLUEPRINTS_PT_TestPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
