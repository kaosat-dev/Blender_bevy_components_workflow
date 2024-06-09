bl_info = {
    "name": "blenvy",
    "author": "kaosigh",
    "version": (0, 1, 0),
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "description": "tooling for the Bevy engine",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "Import-Export"
}

import bpy
from bpy.app.handlers import persistent
from bpy.props import (StringProperty)


# components management 
from .add_ons.bevy_components.components.operators import CopyComponentOperator, Fix_Component_Operator, OT_rename_component, RemoveComponentFromAllItemsOperator, RemoveComponentOperator, GenerateComponent_From_custom_property_Operator, PasteComponentOperator, AddComponentOperator, RenameHelper, Toggle_ComponentVisibility
from .add_ons.bevy_components.registry.registry import ComponentsRegistry,MissingBevyType
from .add_ons.bevy_components.registry.operators import (COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL, COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT, COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL, COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT, OT_select_component_name_to_replace, OT_select_object, ReloadRegistryOperator, OT_OpenSchemaFileBrowser)
from .add_ons.bevy_components.registry.ui import (BEVY_COMPONENTS_PT_Configuration, BEVY_COMPONENTS_PT_AdvancedToolsPanel, BEVY_COMPONENTS_PT_MissingTypesPanel, MISSING_TYPES_UL_List)
from .add_ons.bevy_components.components.metadata import (ComponentMetadata, ComponentsMeta)
from .add_ons.bevy_components.components.lists import GENERIC_LIST_OT_actions, Generic_LIST_OT_AddItem, Generic_LIST_OT_RemoveItem, Generic_LIST_OT_SelectItem
from .add_ons.bevy_components.components.maps import GENERIC_MAP_OT_actions
from .add_ons.bevy_components.components.definitions_list import (ComponentDefinitionsList, ClearComponentDefinitionsList)
from .add_ons.bevy_components.components.ui import (BEVY_COMPONENTS_PT_ComponentsPanel)
from .add_ons.bevy_components.settings import ComponentsSettings

# auto export
from .add_ons.auto_export import gltf_post_export_callback
from .add_ons.auto_export.common.tracker import AutoExportTracker
from .add_ons.auto_export.settings import AutoExportSettings

# asset management
from .assets.ui import Blenvy_assets
from .assets.assets_registry import Asset, AssetsRegistry
from .assets.operators import OT_Add_asset_filebrowser, OT_add_bevy_asset, OT_remove_bevy_asset, OT_test_bevy_assets

# levels management
from .levels.ui import Blenvy_levels
from .levels.operators import OT_select_level

# blueprints management
from .blueprints.ui import GLTF_PT_auto_export_blueprints_list
from .blueprints.blueprints_registry import BlueprintsRegistry
from .blueprints.operators import OT_select_blueprint

# blenvy core
from .core.blenvy_manager import BlenvyManager
from .core.operators import OT_switch_bevy_tooling
from .core.ui.ui import (BLENVY_PT_SidePanel)
from .core.ui.scenes_list import SCENES_LIST_OT_actions
from .core.ui.assets_folder_browser import OT_OpenAssetsFolderBrowser


# this needs to be here, as it is how Blender's gltf exporter callbacks are defined, at the add-on root level
def glTF2_post_export_callback(data):
    gltf_post_export_callback(data)
    

classes = [
    # common/core
    SCENES_LIST_OT_actions,
    OT_OpenAssetsFolderBrowser,

    # blenvy
    BLENVY_PT_SidePanel,

    # bevy components
    ComponentsSettings,
    AddComponentOperator,  
    CopyComponentOperator,
    PasteComponentOperator,
    RemoveComponentOperator,
    RemoveComponentFromAllItemsOperator,
    Fix_Component_Operator,
    OT_rename_component,
    RenameHelper,
    GenerateComponent_From_custom_property_Operator,
    Toggle_ComponentVisibility,

    ComponentDefinitionsList,
    ClearComponentDefinitionsList,
    
    ComponentMetadata,
    ComponentsMeta,
    MissingBevyType,
    ComponentsRegistry,

    OT_OpenSchemaFileBrowser,
    ReloadRegistryOperator,
    COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL,
    COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT,

    COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL,
    COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT,

    OT_select_object,
    OT_select_component_name_to_replace, 
    
    BEVY_COMPONENTS_PT_ComponentsPanel,
    BEVY_COMPONENTS_PT_AdvancedToolsPanel,
    #BEVY_COMPONENTS_PT_Configuration,
    MISSING_TYPES_UL_List,
    BEVY_COMPONENTS_PT_MissingTypesPanel,

    Generic_LIST_OT_SelectItem,
    Generic_LIST_OT_AddItem,
    Generic_LIST_OT_RemoveItem,
    GENERIC_LIST_OT_actions,

    GENERIC_MAP_OT_actions,


    # gltf auto export
    AutoExportTracker,
    AutoExportSettings,

    # blenvy
    BlenvyManager,
    OT_switch_bevy_tooling,

    Asset,
    AssetsRegistry,
    OT_add_bevy_asset,
    OT_remove_bevy_asset,
    OT_test_bevy_assets,
    OT_Add_asset_filebrowser,
    Blenvy_assets,

    Blenvy_levels,
    OT_select_level,

    BlueprintsRegistry,
    OT_select_blueprint,
    GLTF_PT_auto_export_blueprints_list,
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

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(post_load)
    bpy.app.handlers.depsgraph_update_post.remove(post_update)
    bpy.app.handlers.save_post.remove(post_save)