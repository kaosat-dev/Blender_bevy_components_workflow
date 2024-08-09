bl_info = {
    "name": "blenvy",
    "author": "kaosigh",
    "version": (0, 1, 0, "alpha.1"),
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "description": "tooling for the Bevy engine",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blenvy",
    "tracker_url": "https://github.com/kaosat-dev/Blenvy/issues/new",
    "category": "Import-Export"
}

import bpy
from bpy.app.handlers import persistent
from bpy.props import (StringProperty)


# components management 
from .add_ons.bevy_components.components.operators import BLENVY_OT_component_copy, BLENVY_OT_component_fix, BLENVY_OT_component_rename_component, BLENVY_OT_component_remove_from_all_items, BLENVY_OT_component_remove, BLENVY_OT_component_from_custom_property, BLENVY_OT_component_paste, BLENVY_OT_component_add, RenameHelper, BLENVY_OT_component_toggle_visibility, BLENVY_OT_components_refresh_custom_properties_all, BLENVY_OT_components_refresh_custom_properties_current, BLENVY_OT_components_refresh_propgroups_all, BLENVY_OT_components_refresh_propgroups_current
from .add_ons.bevy_components.registry.registry import ComponentsRegistry,MissingBevyType
from .add_ons.bevy_components.registry.operators import (BLENVY_OT_components_registry_reload, BLENVY_OT_components_registry_browse_schema)
from .add_ons.bevy_components.registry.ui import (BLENVY_PT_components_missing_types_panel, BLENVY_UL_components_missing_types)
from .add_ons.bevy_components.components.metadata import (ComponentMetadata, ComponentsMeta)
from .add_ons.bevy_components.components.lists import BLENVY_OT_component_list_actions
from .add_ons.bevy_components.components.maps import BLENVY_OT_component_map_actions
from .add_ons.bevy_components.components.ui import BLENVY_PT_components_panel, BLENVY_PT_component_tools_panel
from .add_ons.bevy_components.settings import ComponentsSettings
from .add_ons.bevy_components.utils import BLENVY_OT_item_select

# auto export
from .add_ons.auto_export import gltf_post_export_callback
from .add_ons.auto_export.common.tracker import AutoExportTracker
from .add_ons.auto_export.settings import AutoExportSettings

# asset management
from .assets.ui import BLENVY_PT_assets_panel
from .assets.assets_registry import Asset, AssetsRegistry
from .assets.operators import BLENVY_OT_assets_browse, BLENVY_OT_assets_add, BLENVY_OT_assets_remove, BLENVY_OT_assets_generate_files

# levels management
from .levels.ui import BLENVY_PT_levels_panel
from .levels.operators import BLENVY_OT_level_select

# blueprints management
from .blueprints.ui import BLENVY_PT_blueprints_panel
from .blueprints.blueprints_registry import BlueprintsRegistry
from .blueprints.operators import BLENVY_OT_blueprint_select

# blenvy core
from .core.blenvy_manager import BlenvyManager
from .core.operators import BLENVY_OT_configuration_switch, BLENVY_OT_tooling_switch
from .core.ui.ui import (BLENVY_PT_SidePanel)
from .core.ui.scenes_list import BLENVY_OT_scenes_list_actions
from .assets.assets_folder_browser import BLENVY_OT_assets_paths_browse


# this needs to be here, as it is how Blender's gltf exporter callbacks are defined, at the add-on root level
def glTF2_post_export_callback(data):
    gltf_post_export_callback(data)
    

classes = [
    # common/core
    BLENVY_OT_scenes_list_actions,
    BLENVY_OT_assets_paths_browse,

    # blenvy
    BLENVY_PT_SidePanel,

    # bevy components
    ComponentsSettings,
    BLENVY_OT_component_add,  
    BLENVY_OT_component_copy,
    BLENVY_OT_component_paste,
    BLENVY_OT_component_remove,
    BLENVY_OT_component_remove_from_all_items,
    BLENVY_OT_component_fix,
    BLENVY_OT_component_rename_component,
    RenameHelper,
    BLENVY_OT_component_from_custom_property,
    BLENVY_OT_component_toggle_visibility,
    
    ComponentMetadata,
    ComponentsMeta,
    MissingBevyType,
    ComponentsRegistry,

    BLENVY_OT_components_registry_browse_schema,
    BLENVY_OT_components_registry_reload,
    BLENVY_OT_components_refresh_custom_properties_all,
    BLENVY_OT_components_refresh_custom_properties_current,
    BLENVY_OT_components_refresh_propgroups_all,
    BLENVY_OT_components_refresh_propgroups_current,

    BLENVY_OT_item_select,
    
    BLENVY_PT_components_panel,
    BLENVY_PT_component_tools_panel,
    BLENVY_UL_components_missing_types,
    BLENVY_PT_components_missing_types_panel,

    BLENVY_OT_component_list_actions,
    BLENVY_OT_component_map_actions,

    # gltf auto export
    AutoExportTracker,
    AutoExportSettings,

    # blenvy
    BlenvyManager,
    BLENVY_OT_tooling_switch,
    BLENVY_OT_configuration_switch,

    Asset,
    AssetsRegistry,
    BLENVY_OT_assets_add,
    BLENVY_OT_assets_remove,
    BLENVY_OT_assets_generate_files,
    BLENVY_OT_assets_browse,
    BLENVY_PT_assets_panel,

    BLENVY_PT_levels_panel,
    BLENVY_OT_level_select,

    BlueprintsRegistry,
    BLENVY_OT_blueprint_select,
    BLENVY_PT_blueprints_panel,
]


@persistent
def post_update(scene, depsgraph):
    bpy.context.window_manager.auto_export_tracker.deps_post_update_handler( scene, depsgraph)

@persistent
def post_save(scene, depsgraph):
    bpy.context.window_manager.auto_export_tracker.save_handler( scene, depsgraph)

@persistent
def post_load(file_name):
    print("POST LOAD")
    blenvy = bpy.context.window_manager.blenvy
    if blenvy is not None:
        blenvy.load_settings()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.handlers.load_post.append(post_load)
    # for some reason, adding these directly to the tracker class in register() do not work reliably
    bpy.app.handlers.depsgraph_update_post.append(post_update)
    bpy.app.handlers.save_post.append(post_save)


    """ handle = object()

    subscribe_to = bpy.types.Scene, "name" # 

    def notify_test(context):
        #if (context.scene.type == 'MESH'):
        print("Renamed", dir(context), context.scenes)

    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=bpy,
        args=(bpy.context,),
        notify=notify_test,
    )"""


    #bpy.msgbus.publish_rna(key=subscribe_to)




def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(post_load)
    bpy.app.handlers.depsgraph_update_post.remove(post_update)
    bpy.app.handlers.save_post.remove(post_save)
