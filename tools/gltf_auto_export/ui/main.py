import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

from ..auto_export import auto_export

from ..auto_export.preferences import (AutoExportGltfAddonPreferences, AutoExportGltfPreferenceNames)
from ..helpers.helpers_scenes import (get_scenes)
from ..helpers.helpers_collections import (get_exportable_collections)
######################################################
## ui logic & co

class GLTF_PT_auto_export_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = ""
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data

class GLTF_PT_auto_export_root(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Auto export"
    bl_parent_id = "GLTF_PT_auto_export_main"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        self.layout.prop(operator, "auto_export", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.active = operator.auto_export
        layout.prop(operator, 'will_save_settings')
        layout.prop(operator, "export_change_detection")
        layout.prop(operator, "export_output_folder")
        layout.prop(operator, "export_scene_settings")
        layout.prop(operator, "export_legacy_mode")

        # scene selectors
        row = layout.row()
        col = row.column(align=True)
        col.separator()

        source = operator

        rows = 2

        # main/level scenes
        layout.label(text="main scenes")
        layout.prop(context.window_manager, "main_scene", text='')

        row = layout.row()
        row.template_list("SCENE_UL_GLTF_auto_export", "level scenes", source, "main_scenes", source, "main_scenes_index", rows=rows)

        col = row.column(align=True)
        sub_row = col.row()
        add_operator = sub_row.operator("scene_list.list_action", icon='ADD', text="")
        add_operator.action = 'ADD'
        add_operator.scene_type = 'level'
        #add_operator.source = operator
        sub_row.enabled = context.window_manager.main_scene is not None

        sub_row = col.row()
        remove_operator = sub_row.operator("scene_list.list_action", icon='REMOVE', text="")
        remove_operator.action = 'REMOVE'
        remove_operator.scene_type = 'level'
        col.separator()

        #up_operator = col.operator("scene_list.list_action", icon='TRIA_UP', text="")
        #up_operator.action = 'UP'
        #col.operator("scene_list.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        # library scenes
        layout.label(text="library scenes")
        layout.prop(context.window_manager, "library_scene", text='')

        row = layout.row()
        row.template_list("SCENE_UL_GLTF_auto_export", "library scenes", source, "library_scenes", source, "library_scenes_index", rows=rows)

        col = row.column(align=True)
        sub_row = col.row()
        add_operator = sub_row.operator("scene_list.list_action", icon='ADD', text="")
        add_operator.action = 'ADD'
        add_operator.scene_type = 'library'
        sub_row.enabled = context.window_manager.library_scene is not None


        sub_row = col.row()
        remove_operator = sub_row.operator("scene_list.list_action", icon='REMOVE', text="")
        remove_operator.action = 'REMOVE'
        remove_operator.scene_type = 'library'
        col.separator()
      
class GLTF_PT_auto_export_blueprints(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Blueprints"
    bl_parent_id = "GLTF_PT_auto_export_root"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"


    def draw_header(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, "export_blueprints", text="")

        #self.layout.prop(operator, "auto_export", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.active = operator.export_blueprints
        
         # collections/blueprints 
        layout.prop(operator, "export_blueprints_path")
        layout.prop(operator, "collection_instances_combine_mode")
        layout.prop(operator, "export_marked_assets")
        layout.prop(operator, "export_separate_dynamic_and_static_objects")
        layout.separator()
        # materials
        layout.prop(operator, "export_materials_library")
        layout.prop(operator, "export_materials_path")

       
class GLTF_PT_auto_export_collections_list(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Blueprints: Exported Collections"
    bl_parent_id = "GLTF_PT_auto_export_blueprints"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        for collection in bpy.context.window_manager.exportedCollections:
            row = layout.row()
            row.label(text=collection.name)

class GLTF_PT_auto_export_gltf(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Gltf"
    bl_parent_id = "GLTF_PT_auto_export_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"
    
    def draw(self, context):
        preferences = context.preferences
        layout = self.layout

        sfile = context.space_data
        operator = sfile.active_operator

        addon_prefs = operator

        # we get the addon preferences from the standard gltf exporter & use those :
        addon_prefs_gltf = preferences.addons["io_scene_gltf2"].preferences

        #self.layout.operator("EXPORT_SCENE_OT_gltf", text='glTF 2.0 (.glb/.gltf)')
        #bpy.ops.export_scene.gltf

        for key in addon_prefs.__annotations__.keys():
            if key not in AutoExportGltfPreferenceNames:
                layout.prop(operator, key)
     
class SCENE_UL_GLTF_auto_export(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            #if ma:
            #    layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            #else:
            #    layout.label(text="", translate=False, icon_value=icon)
            layout.label(text=item.name, icon_value=icon)
            #layout.prop(item, "name", text="", emboss=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


