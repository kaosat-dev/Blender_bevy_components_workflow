import json
import bpy
from bpy.props import StringProperty, EnumProperty
from bpy_types import Operator
from ...core.helpers_collections import set_active_collection
from .constants import HIDDEN_COMPONENTS

def select_area(context, area_name):
    for area in context.screen.areas:
        #if area.type == 'PROPERTIES' and context.object is not None and context.object.type not in ('LIGHT_PROBE', 'CAMERA', 'LIGHT', 'SPEAKER'):
        # Set it the active space
        #print("SELECT AREA", area_name)
        try:
            area.spaces.active.context = area_name #'MATERIAL' # 'VIEW_LAYER', 'SCENE' etc.
        except Exception as error: 
            print(f"failed to switch to area {area_name}: {error}")
        break # OPTIONAL

def get_collection_scene(collection):
    for scene in bpy.data.scenes:
        if scene.user_of_id(collection):
            return scene
    return None

def get_object_by_name(name):
    object = bpy.data.objects.get(name, None)
    return object

def get_object_scene(object):
    object = bpy.data.objects.get(object.name, None)
    if object is not None:
        scenes_of_object = list(object.users_scene)
        if len(scenes_of_object) > 0:
            return scenes_of_object[0]
    return None


def get_mesh_object(mesh):
    for object in bpy.data.objects:
        if isinstance(object.data, bpy.types.Mesh) and mesh.name == object.data.name:
            return object

def get_material_object(material):
    for object in bpy.data.objects:
        if isinstance(object.data, bpy.types.Mesh) and material.name in object.data.materials:
            return object
            

class BLENVY_OT_item_select(Operator):
    """Select object by name"""
    bl_idname = "blenvy.select_item"
    bl_label = "Select item (object or collection)"
    bl_options = {"UNDO"}

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

    target_name: StringProperty(
        name="target name",
        description="target to select's name ",
    ) # type: ignore


    @classmethod
    def register(cls):
        bpy.types.WindowManager.blenvy_item_selected_ids = StringProperty(default="{}")
        

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.blenvy_item_selected_ids
        

    def execute(self, context):

        if self.target_name:
            if self.item_type == 'OBJECT':
                object = bpy.data.objects[self.target_name]
                scenes_of_object = list(object.users_scene)
                if len(scenes_of_object) > 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.window.scene = scenes_of_object[0]
                    object.select_set(True)    
                    context.window_manager.blenvy_item_selected_ids = json.dumps({"name": object.name, "type": self.item_type})

                    bpy.context.view_layer.objects.active = object
                    select_area(context=context, area_name="OBJECT")

            elif self.item_type == 'COLLECTION':
                collection = bpy.data.collections[self.target_name]
                scene_of_collection = get_collection_scene(collection)
                if scene_of_collection is not None:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.window.scene = scene_of_collection
                    #bpy.context.view_layer.objects.active = None
                    context.window_manager.blenvy_item_selected_ids = json.dumps({"name": collection.name, "type": self.item_type})
                    set_active_collection(bpy.context.window.scene, collection.name)

                    select_area(context=context, area_name="COLLECTION")

            elif self.item_type == 'MESH':
                mesh = bpy.data.meshes[self.target_name]
                mesh_object = get_mesh_object(mesh)
                scene_of_item = get_object_scene(mesh_object)
                if scene_of_item is not None:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.window.scene = scene_of_item
                    bpy.context.view_layer.objects.active = mesh_object

                    context.window_manager.blenvy_item_selected_ids = json.dumps({"name": mesh.name, "type": self.item_type})
                    select_area(context=context, area_name="DATA")

            elif self.item_type == 'MATERIAL':
                # find object that uses material
                material = bpy.data.materials[self.target_name]
                material_object = get_material_object(material)
                scene_of_item = get_object_scene(material_object)
                select_area(context=context, area_name="MATERIAL")
                if scene_of_item is not None:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.window.scene = scene_of_item
                    bpy.context.view_layer.objects.active = material_object

                    context.window_manager.blenvy_item_selected_ids = json.dumps({"name": material.name, "type": self.item_type})

                    select_area(context=context, area_name="MATERIAL")

        return {'FINISHED'}

def get_selected_item(context):
    selection = None

    def get_outliner_area():
        if bpy.context.area.type!='OUTLINER':
            for area in bpy.context.screen.areas:
                if area.type == 'OUTLINER':
                    return area
        return None
    #print("original context", context)
   


    if selection is None:
        area = get_outliner_area()
        if area is not None:
            region = next(region for region in area.regions if region.type == "WINDOW")
            with bpy.context.temp_override(area=area, region=region):
                #print("overriden context", bpy.context)
                """for obj in bpy.context.selected_ids:
                    print(f"Selected: {obj.name} - {type(obj)}")"""
                number_of_selections = len(bpy.context.selected_ids)
                selection = bpy.context.selected_ids[number_of_selections - 1] if number_of_selections > 0 else None #next(iter(bpy.context.selected_ids), None)

    

    if selection is None:
        number_of_selections = len(context.selected_objects)
        selection = context.selected_objects[number_of_selections - 1] if number_of_selections > 0 else None

    if selection is None:
        try:
            selection_overrides = json.loads(context.window_manager.blenvy_item_selected_ids)
            #print("selection_overrides", selection_overrides)
            if selection_overrides["type"] == "OBJECT":
                selection = bpy.data.objects[selection_overrides["name"]]
            elif selection_overrides["type"] == "COLLECTION":
                selection = bpy.data.collections[selection_overrides["name"]]
            if selection_overrides["type"] == "MESH":
                selection = bpy.data.meshes[selection_overrides["name"]]
            elif selection_overrides["type"] == "MATERIAL":
                selection = bpy.data.materials[selection_overrides["name"]]
            #print("SELECTION", selection)
            #context.window_manager.blenvy_item_selected_ids = "{}"
        except: pass
    return selection


def get_selection_type(selection):
    #print("bla mesh", isinstance(selection, bpy.types.Mesh), "bli bli", selection.type)
    if isinstance(selection, bpy.types.Material):
        return 'MATERIAL'
    if isinstance(selection, bpy.types.Mesh):
        return 'MESH'
    if isinstance(selection, bpy.types.Object):
        return 'OBJECT'
    if isinstance(selection, bpy.types.Collection):
        return 'COLLECTION'

def get_item_by_type(item_type, item_name):
    item = None
    if item_type == 'OBJECT':
        item = bpy.data.objects[item_name]
    elif item_type == 'COLLECTION':
        item = bpy.data.collections[item_name]
    elif item_type == "MESH":
        item = bpy.data.meshes[item_name]
    elif item_type == 'MATERIAL':
        item = bpy.data.materials[item_name]
    return item

def add_component_to_ui_list(self, context, _):
        items = []
        type_infos = context.window_manager.components_registry.type_infos
        for long_name in type_infos.keys():
            definition = type_infos[long_name]
            short_name = definition["short_name"]
            is_component = definition['isComponent']  if "isComponent" in definition else False
            """if self.filter.lower() in short_name.lower() and is_component:"""
            if is_component and not 'Handle' in short_name and not "Cow" in short_name and not "AssetId" in short_name and short_name not in HIDDEN_COMPONENTS: # FIXME: hard coded, seems wrong
                items.append((long_name, short_name))
        items.sort(key=lambda a: a[1])
        return items


def is_component_valid_and_enabled(object, component_name):
    if "components_meta" in object or hasattr(object, "components_meta"):
        target_components_metadata = object.components_meta.components
        component_meta = next(filter(lambda component: component["long_name"] == component_name, target_components_metadata), None)
        if component_meta is not None:
            return component_meta.enabled and not component_meta.invalid
    return True