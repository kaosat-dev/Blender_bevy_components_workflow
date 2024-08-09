import os
import json
import bpy
from bpy_types import (Operator)
from bpy.props import (BoolProperty, StringProperty, EnumProperty)

from .asset_helpers import does_asset_exist, get_user_assets, remove_asset, upsert_asset
from .assets_scan import get_level_scene_assets_tree
from ..core.path_helpers import absolute_path_from_blend_file
from .generate_asset_file import write_ron_assets_file

class BLENVY_OT_assets_add(Operator):
    """Add asset"""
    bl_idname = "blenvy.assets_add"
    bl_label = "Add bevy asset"
    bl_options = {"UNDO"}

    asset_name: StringProperty(
        name="asset name",
        description="name of asset to add",
    ) # type: ignore

    asset_type: EnumProperty(
            items=(
                ('MODEL', "Model", ""),
                ('AUDIO', "Audio", ""),
                ('IMAGE', "Image", ""),
                ('TEXT', "Text", ""),
                )
        ) # type: ignore

    asset_path: StringProperty(
        name="asset path",
        description="path of asset to add",
        subtype='FILE_PATH'
    ) # type: ignore

    # what are we targetting
    target_type: EnumProperty(
        name="target type",
        description="type of the target: scene or blueprint to add an asset to",
        items=(
            ('SCENE', "Scene", ""),
            ('BLUEPRINT', "Blueprint", ""),
            ),
    ) # type: ignore

    target_name: StringProperty(
        name="target name",
        description="name of the target blueprint or scene to add asset to"
    ) # type: ignore

    def execute(self, context):
        blueprint_assets = self.target_type == 'BLUEPRINT'
        target = None
        if blueprint_assets:
            target = bpy.data.collections[self.target_name]
        else:
            target = bpy.data.scenes[self.target_name]
        assets = get_user_assets(target)
        asset = {"name": self.asset_name, "type": self.asset_type, "path": self.asset_path}
        print('assets', assets, target)
        if not does_asset_exist(target, asset):
            print("add asset", target, asset)
            upsert_asset(target, asset)

            #assets.append({"name": self.asset_name, "type": self.asset_type, "path": self.asset_path, "internal": False})
            # reset controls
            context.window_manager.assets_registry.asset_name_selector = ""
            context.window_manager.assets_registry.asset_type_selector = "MODEL"
            context.window_manager.assets_registry.asset_path_selector = ""

        return {'FINISHED'}
    

class BLENVY_OT_assets_remove(Operator):
    """Remove asset"""
    bl_idname = "blenvy.assets_remove"
    bl_label = "remove bevy asset"
    bl_options = {"UNDO"}

    asset_path: StringProperty(
        name="asset path",
        description="path of asset to add",
        subtype='FILE_PATH'
    ) # type: ignore


    clear_all: BoolProperty (
        name="clear all assets",
        description="clear all assets",
        default=False
    ) # type: ignore

    # what are we targetting
    target_type: EnumProperty(
        name="target type",
        description="type of the target: scene or blueprint to add an asset to",
        items=(
            ('SCENE', "Scene", ""),
            ('BLUEPRINT', "Blueprint", ""),
            ),
    ) # type: ignore

    target_name: StringProperty(
        name="target name",
        description="name of the target blueprint or scene to add asset to"
    ) # type: ignore


    def execute(self, context):
        print("REMOVE ASSET", self.target_name, self.target_type, self.asset_path)
        assets = []
        blueprint_assets = self.target_type == 'BLUEPRINT'
        if blueprint_assets:
            target = bpy.data.collections[self.target_name]
        else:
            target = bpy.data.scenes[self.target_name]
            print("removing this", target)
        remove_asset(target, {"path": self.asset_path})
       
        return {'FINISHED'}
    

import os
from bpy_extras.io_utils import ImportHelper
from pathlib import Path

class BLENVY_OT_assets_browse(Operator, ImportHelper):
    """Browse for asset files"""
    bl_idname = "blenvy.assets_open_filebrowser" 
    bl_label = "Select asset file" 

    # Define this to tell 'fileselect_add' that we want a directoy
    filepath: bpy.props.StringProperty(
        name="asset Path",
        description="selected file",
        subtype='FILE_PATH',
        ) # type: ignore
    
    # Filters files
    filter_glob: StringProperty(options={'HIDDEN'}, default='*.*') # type: ignore

    def execute(self, context):      
        blenvy = context.window_manager.blenvy   
        project_root_path = blenvy.project_root_path
        assets_path =  blenvy.assets_path
        # FIXME: not sure
        print("project_root_path", project_root_path, "assets_path", assets_path)
        export_assets_path_absolute = absolute_path_from_blend_file(os.path.join(project_root_path, assets_path))

        asset_path = os.path.relpath(self.filepath, export_assets_path_absolute)
        print("asset path", asset_path)

        assets_registry = context.window_manager.assets_registry
        assets_registry.asset_path_selector = asset_path
        if assets_registry.asset_name_selector == "":
            assets_registry.asset_name_selector = Path(os.path.basename(asset_path)).stem

        print("SELECTED ASSET PATH", asset_path)


        
        return {'FINISHED'}
    


from types import SimpleNamespace


class BLENVY_OT_assets_generate_files(Operator):
    """Test assets"""
    bl_idname = "blenvy.assets_generate_files"
    bl_label = "test bevy assets"
    bl_options = {"UNDO"}

    def execute(self, context):
        blenvy = context.window_manager.blenvy
        settings = blenvy
        blueprints_registry = context.window_manager.blueprints_registry
        blueprints_registry.refresh_blueprints()
        blueprints_data = blueprints_registry.blueprints_data

        for scene in blenvy.level_scenes:
            assets_hierarchy = get_level_scene_assets_tree(scene, blueprints_data, settings)
            # scene["assets"] = json.dumps(assets_hierarchy)
            write_ron_assets_file(scene.name, assets_hierarchy, internal_only = False, output_path_full = blenvy.levels_path_full)

        return {'FINISHED'}
