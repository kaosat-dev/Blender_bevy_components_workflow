import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

from ..preferences import (AutoExportGltfAddonPreferences, AutoExportGltfPreferenceNames)
from ..helpers_scenes import (get_scenes)
from ..helpers_collections import (get_exportable_collections)
######################################################
## ui logic & co

class AutoExportGLTF(Operator, AutoExportGltfAddonPreferences, ExportHelper):
    """test"""
    bl_idname = "export_scenes.auto_gltf"
    bl_label = "Apply settings"
    bl_options = {'PRESET', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ''

    filter_glob: StringProperty(
            default='*.glb;*.gltf', 
            options={'HIDDEN'}
    )

    will_save_settings: BoolProperty(
        name='Remember Export Settings',
        description='Store glTF export settings in the Blender project',
        default=True
    )

    # Custom scene property for saving settings
    scene_key = "auto_gltfExportSettings"

    def save_settings(self, context):
        # find all props to save
        exceptional = [
            # options that don't start with 'export_'  
            'main_scenes',
            'library_scenes',
            'collection_instances_combine_mode',
        ]
        all_props = self.properties
        export_props = {
            x: getattr(self, x) for x in dir(all_props)
            if (x.startswith("export_") or x in exceptional) and all_props.get(x) is not None
        }
        # we add main & library scene names to our preferences
        main_scenes = list(map(lambda scene_data: scene_data, getattr(bpy.context.preferences.addons["gltf_auto_export"].preferences,"main_scenes")))
        library_scenes = list(map(lambda scene_data: scene_data, getattr(bpy.context.preferences.addons["gltf_auto_export"].preferences,"library_scenes")))

        export_props['main_scene_names'] = list(map(lambda scene_data: scene_data.name, getattr(bpy.context.preferences.addons["gltf_auto_export"].preferences,"main_scenes")))
        export_props['library_scene_names'] = list(map(lambda scene_data: scene_data.name, getattr(bpy.context.preferences.addons["gltf_auto_export"].preferences,"library_scenes")))
        self.properties['main_scene_names'] = export_props['main_scene_names']
        self.properties['library_scene_names'] = export_props['library_scene_names']
        context.scene[self.scene_key] = export_props

      
    def apply_settings_to_preferences(self, context):
        # find all props to save
        exceptional = [
            # options that don't start with 'export_'  
            'main_scenes',
            'library_scenes',
            'collection_instances_combine_mode',
        ]
        all_props = self.properties
        export_props = {
            x: getattr(self, x) for x in dir(all_props)
            if (x.startswith("export_") or x in exceptional) and all_props.get(x) is not None
        }
        addon_prefs = bpy.context.preferences.addons["gltf_auto_export"].preferences

        for (k, v) in export_props.items():
            setattr(addon_prefs, k, v)


    def execute(self, context):     
        if self.will_save_settings:
            self.save_settings(context)
        # apply the operator properties to the addon preferences
        self.apply_settings_to_preferences(context)

        return {'FINISHED'}    
    
    def invoke(self, context, event):
        settings = context.scene.get(self.scene_key)
        print("settings", settings)
        self.will_save_settings = False
        if settings:
            print("loading settings in invoke AutoExportGLTF")
            try:
                for (k, v) in settings.items():
                    print("loading setting", k, v)
                    setattr(self, k, v)
                self.will_save_settings = True

                # Update filter if user saved settings
                if hasattr(self, 'export_format'):
                    self.filter_glob = '*.glb' if self.export_format == 'GLB' else '*.gltf'

                # inject scenes data
                if hasattr(self, 'main_scene_names'):
                    main_scenes = bpy.context.preferences.addons["gltf_auto_export"].preferences.main_scenes
                    main_scenes.clear()
                    for item_name in self.main_scene_names:
                        item = main_scenes.add()
                        item.name = item_name

                if hasattr(self, 'library_scene_names'):
                    library_scenes = bpy.context.preferences.addons["gltf_auto_export"].preferences.library_scenes
                    library_scenes.clear()
                    for item_name in self.library_scene_names:
                        item = library_scenes.add()
                        item.name = item_name

                if hasattr(self, 'collection_instances_combine_mode'):
                    bpy.context.preferences.addons["gltf_auto_export"].preferences.collection_instances_combine_mode = self.collection_instances_combine_mode


            except (AttributeError, TypeError):
                self.report({"ERROR"}, "Loading export settings failed. Removed corrupted settings")
                del context.scene[self.scene_key]


        for (k, v) in self.properties.items():
            print("PROPERTIES", k, v)

        addon_prefs = bpy.context.preferences.addons["gltf_auto_export"].preferences

        [main_scene_names, level_scenes, library_scene_names, library_scenes]=get_scenes(addon_prefs)
        (collections, _) = get_exportable_collections(level_scenes, library_scenes, addon_prefs)

        try:
            # we save this list of collections in the context
            bpy.context.window_manager.exportedCollections.clear()
            #TODO: add error handling for this
            for collection_name in collections:
                ui_info = bpy.context.window_manager.exportedCollections.add()
                ui_info.name = collection_name
        except Exception as error:
            self.report({"ERROR"}, "Failed to populate list of exported collections/blueprints")
     


        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
        # return self.execute(context)

    def draw(self, context):
        pass

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
        layout.prop(operator, "export_output_folder")
        layout.prop(operator, "export_scene_settings")

        # scene selectors
        row = layout.row()
        col = row.column(align=True)
        col.separator()

        source = bpy.context.preferences.addons["gltf_auto_export"].preferences

        rows = 2

        # main/level scenes
        layout.label(text="main scenes")
        layout.prop(context.scene, "main_scene", text='')

        row = layout.row()
        row.template_list("SCENE_UL_GLTF_auto_export", "level scenes", source, "main_scenes", source, "main_scenes_index", rows=rows)

        col = row.column(align=True)
        sub_row = col.row()
        add_operator = sub_row.operator("scene_list.list_action", icon='ADD', text="")
        add_operator.action = 'ADD'
        add_operator.scene_type = 'level'
        #add_operator.source = operator
        sub_row.enabled = context.scene.main_scene is not None

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
        layout.prop(context.scene, "library_scene", text='')

        row = layout.row()
        row.template_list("SCENE_UL_GLTF_auto_export", "library scenes", source, "library_scenes", source, "library_scenes_index", rows=rows)

        col = row.column(align=True)
        sub_row = col.row()
        add_operator = sub_row.operator("scene_list.list_action", icon='ADD', text="")
        add_operator.action = 'ADD'
        add_operator.scene_type = 'library'
        sub_row.enabled = context.scene.library_scene is not None


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
        layout.prop(operator, "split_out_dynamic_collections")
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
        addon_prefs = bpy.context.preferences.addons["gltf_auto_export"].preferences

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
        addon_prefs = preferences.addons["gltf_auto_export"].preferences
        layout = self.layout

        sfile = context.space_data
        operator = sfile.active_operator

        #preferences = context.preferences
        #print("ADDON PREFERENCES ", list(preferences.addons.keys()))
        #print("standard blender gltf prefs", list(preferences.addons["io_scene_gltf2"].preferences.keys()))
        # we get the addon preferences from the standard gltf exporter & use those :
        addon_prefs_gltf = preferences.addons["io_scene_gltf2"].preferences

        #addon_prefs = preferences.addons["gltf_auto_export"].preferences

        # print("KEYS", operator.properties.keys())
        #print("BLAS", addon_prefs.__annotations__)
        #print(addon_prefs.__dict__)
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


