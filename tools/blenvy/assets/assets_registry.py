import bpy
from pathlib import Path
from bpy_types import (PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

# Asset property group
class Asset(PropertyGroup):
    name: StringProperty(name="asset name") # type: ignore
    path: StringProperty(name="asset path") # type: ignore

# this is where we store the information for all available assets
#
class AssetsRegistry(PropertyGroup):
    assets_list = []

    asset_name_selector: StringProperty(
        name="asset name",
        description="name of asset to add",
    ) # type: ignore

    asset_type_selector: EnumProperty(
        name="asset type",
        description="type of asset to add",
         items=(
                ('MODEL', "Model", ""),
                ('AUDIO', "Audio", ""),
                ('IMAGE', "Image", ""),
                ('TEXT', "Text", ""),
                )
    ) # type: ignore

    asset_path_selector: StringProperty(
        name="asset path",
        description="path of asset to add",
        #subtype='FILE_PATH'
    ) # type: ignore


    @classmethod
    def register(cls):
        bpy.types.Scene.user_assets = CollectionProperty(name="user assets", type=Asset)
        bpy.types.Collection.user_assets = CollectionProperty(name="user assets", type=Asset) 

        bpy.types.Scene.generated_assets = CollectionProperty(name="generated assets", type=Asset)
        bpy.types.Collection.generated_assets = CollectionProperty(name="generated assets", type=Asset) 

        bpy.types.WindowManager.assets_registry = PointerProperty(type=AssetsRegistry)


    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.assets_registry
        del bpy.types.Scene.user_assets
        del bpy.types.Collection.user_assets

        del bpy.types.Scene.generated_assets
        del bpy.types.Collection.generated_assets

    def add_asset(self, name, type, path, internal): # internal means it cannot be edited by the user, aka auto generated
        in_list = [asset for asset in self.assets_list if (asset["path"] == path)]
        in_list = len(in_list) > 0
        if not in_list:
            self.assets_list.append({"name": name, "type": type, "path": path, "internal": internal})

    def remove_asset(self, path):
        self.assets_list[:] = [asset for asset in self.assets_list if (asset["path"] != path)]

