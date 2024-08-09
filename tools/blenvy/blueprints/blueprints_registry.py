from types import SimpleNamespace
import bpy
import json
import os
import uuid
from pathlib import Path
from bpy_types import (PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

from ..settings import load_settings
from .blueprints_scan import blueprints_scan



def refresh_blueprints():
    try:
        blueprints_registry = bpy.context.window_manager.blueprints_registry
        blueprints_registry.refresh_blueprints()
    except:pass

    return 3

# this is where we store the information for all available Blueprints
class BlueprintsRegistry(PropertyGroup):
    blueprints_data = None
    blueprints_list = []

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
                )
    ) # type: ignore

    asset_path_selector: StringProperty(
        name="asset path",
        description="path of asset to add",
        subtype='FILE_PATH'
    ) # type: ignore

    @classmethod
    def register(cls):
        bpy.types.WindowManager.blueprints_registry = PointerProperty(type=BlueprintsRegistry)
        bpy.app.timers.register(refresh_blueprints)

    @classmethod
    def unregister(cls):
        try:
            bpy.app.timers.unregister(refresh_blueprints)
        except: pass
        
        del bpy.types.WindowManager.blueprints_registry


    def add_blueprint(self, blueprint): 
        self.blueprints_list.append(blueprint)

    def refresh_blueprints(self):
        #print("titi", self)
        blenvy = bpy.context.window_manager.blenvy
        settings = blenvy
        blueprints_data = blueprints_scan(settings.level_scenes, settings.library_scenes, settings)
        self.blueprints_data = blueprints_data
        return blueprints_data
