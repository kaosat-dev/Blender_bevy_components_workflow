import bpy
# from ...bevy_components.components import ui# as components_ui
from ...add_ons.bevy_components import ui as components_ui
from ...add_ons.auto_export import ui as auto_export_ui

######################################################

## ui logic & co
def draw_folder_browser(layout, label, prop_origin, target_property):
    row = layout.row()
    row.label(text=label)

    '''box = row.box()
    box.scale_y = 0.5
    box.label(text=value)'''

    col = row.column()
    col.enabled = False
    col.prop(prop_origin, target_property, text="")

    folder_selector = row.operator("blenvy.assets_paths_browse", icon="FILE_FOLDER", text="")
    folder_selector.target_property = target_property #"project_root_path"

# side panel
class BLENVY_PT_SidePanel(bpy.types.Panel):
    bl_idname = "BLENVY_PT_SidePanel"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blenvy"
    #bl_context = "objectmode"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Blenvy")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        blenvy = context.window_manager.blenvy
        active_mode = blenvy.mode
        world_scene_active = False
        library_scene_active = False
        active_collection = context.collection

        """print("BLA", blenvy.assets_path_full)
        print("BLA", blenvy.blueprints_path_full)
        print("BLA", blenvy.levels_path_full)
        print("BLA", blenvy.materials_path_full)"""

        # Now to actual drawing of the UI
        target = row.box() if active_mode == 'COMPONENTS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="PROPERTIES")
        tool_switch_components.tool = "COMPONENTS"

        target = row.box() if active_mode == 'BLUEPRINTS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="PACKAGE")
        tool_switch_components.tool = "BLUEPRINTS"

        target = row.box() if active_mode == 'LEVELS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="ASSET_MANAGER")
        tool_switch_components.tool = "LEVELS"

        '''target = row.box() if active_mode == 'ASSETS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="ASSET_MANAGER")
        tool_switch_components.tool = "ASSETS"'''

        target = row.box() if active_mode == 'SETTINGS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="SETTINGS")
        tool_switch_components.tool = "SETTINGS"

        target = row.box() if active_mode == 'TOOLS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="TOOL_SETTINGS")
        tool_switch_components.tool = "TOOLS"

        if blenvy.mode == "SETTINGS":
            config_mode = blenvy.config_mode
            row = layout.row()
            config_target = row.box() if config_mode == 'COMMON' else row
            config_switch = config_target.operator(operator="bevy.config_switch", text="", icon="OPTIONS")
            config_switch.tool = "COMMON"

            config_target = row.box() if config_mode == 'COMPONENTS' else row
            config_switch = config_target.operator(operator="bevy.config_switch", text="", icon="PROPERTIES")
            config_switch.tool = "COMPONENTS"

            config_target = row.box() if config_mode == 'EXPORT' else row
            config_switch = config_target.operator(operator="bevy.config_switch", text="", icon="EXPORT")
            config_switch.tool = "EXPORT"

            if config_mode == 'COMMON':
                header, panel = layout.panel("common", default_closed=False)
                header.label(text="Common")
                if panel:
                    draw_common_settings_ui(panel, blenvy)

            if config_mode == 'COMPONENTS':
                header, panel = layout.panel("components", default_closed=False)
                header.label(text="Components")
                if panel:
                    components_ui.draw_settings_ui(panel, blenvy.components)

            if config_mode == 'EXPORT':
                header, panel = layout.panel("auto_export", default_closed=False)
                header.label(text="Export")
                if panel:
                    auto_export_ui.draw_settings_ui(panel, blenvy.auto_export)




def draw_common_settings_ui(layout, settings):
    blenvy = settings
    row = layout.row()
    draw_folder_browser(layout=row, label="Root Folder", prop_origin=blenvy, target_property="project_root_path")
    row = layout.row()
    draw_folder_browser(layout=row, label="Assets Folder", prop_origin=blenvy, target_property="assets_path")
    row = layout.row()
    draw_folder_browser(layout=row, label="Blueprints Folder", prop_origin=blenvy, target_property="blueprints_path")
    row = layout.row()
    draw_folder_browser(layout=row, label="Levels Folder", prop_origin=blenvy, target_property="levels_path")
    row = layout.row()
    draw_folder_browser(layout=row, label="Materials Folder", prop_origin=blenvy, target_property="materials_path")

    layout.separator()
    # scenes selection
    if len(blenvy.level_scenes) == 0 and len(blenvy.library_scenes) == 0:
        row = layout.row()
        row.alert = True
        layout.alert = True
        row.label(text="NO library or level scenes specified! at least one level scene or library scene is required!")
        row = layout.row()
        row.label(text="Please select and add at least one:")

    section = layout
    rows = 2
    row = section.row()
    col = row.column()
    col.label(text="level scenes")
    col = row.column()
    col.prop(blenvy, "level_scene_selector", text='')
    col = row.column()
    add_operator = col.operator("blenvy.scenes_list_actions", icon='ADD', text="")
    add_operator.action = 'ADD'
    add_operator.scene_type = 'LEVEL'
    col.enabled = blenvy.level_scene_selector is not None


    row = section.row()
    col = row.column()
    for scene in blenvy.level_scenes:
        sub_row = col.box().row()
        sub_row.label(text=scene.name)
        remove_operator = sub_row.operator("blenvy.scenes_list_actions", icon='TRASH', text="")
        remove_operator.action = 'REMOVE'
        remove_operator.scene_type = 'LEVEL'
        remove_operator.scene_name = scene.name

    col.separator()

    # library scenes
    row = section.row()

    col = row.column()
    col.label(text="library scenes")
    col = row.column()
    col.prop(blenvy, "library_scene_selector", text='')
    col = row.column()
    add_operator = col.operator("blenvy.scenes_list_actions", icon='ADD', text="")
    add_operator.action = 'ADD'
    add_operator.scene_type = 'LIBRARY'
    col.enabled = blenvy.library_scene_selector is not None

    row = section.row()
    col = row.column()
    for scene in blenvy.library_scenes:
        sub_row = col.box().row()
        sub_row.label(text=scene.name)
        remove_operator = sub_row.operator("blenvy.scenes_list_actions", icon='TRASH', text="")
        remove_operator.action = 'REMOVE'
        remove_operator.scene_type = 'LEVEL'
        remove_operator.scene_name = scene.name
    col.separator()