import os
import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (BoolProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty, IntProperty)
from ..settings import upsert_settings, load_settings, generate_complete_settings_dict
from ..add_ons.auto_export.settings import AutoExportSettings
from ..add_ons.bevy_components.settings import ComponentsSettings

# list of settings we do NOT want to save
settings_black_list = ['settings_save_enabled', 'level_scene_selector', 'library_scene_selector']

def save_settings(settings, context):  
    if settings.settings_save_enabled:
        settings_dict =  generate_complete_settings_dict(settings, BlenvyManager, [])
        raw_settings =  {key: settings_dict[key] for key in settings_dict.keys() if key not in settings_black_list}
        # we need to inject the main & library scene names as they are computed properties, not blender ones
        raw_settings['level_scenes_names'] = settings.level_scenes_names
        raw_settings['library_scenes_names'] = settings.library_scenes_names
        upsert_settings(settings.settings_save_path, raw_settings, overwrite=True)

def update_asset_folders(settings, context):
    asset_path_names = ['project_root_path', 'assets_path', 'blueprints_path', 'levels_path', 'materials_path']
    for asset_path_name in asset_path_names:
        upsert_settings(settings.settings_save_path, {asset_path_name: getattr(settings, asset_path_name)})
    settings_dict =  generate_complete_settings_dict(settings, BlenvyManager, [])
    upsert_settings(settings.settings_save_path, {key: settings_dict[key] for key in settings_dict.keys() if key not in settings_black_list}, overwrite=True)


def is_scene_already_in_use(self, scene):
    try:
        current_level_scene_names = list(map(lambda x: x.name, self.level_scenes))
        current_library_scene_names = list(map(lambda x: x.name, self.library_scenes))
        #print("scene ", scene.name, current_level_scene_names, current_library_scene_names)
        return scene.name not in current_level_scene_names and scene.name not in current_library_scene_names
    except:
        return True

class BlenvyManager(PropertyGroup):
    settings_save_path = ".blenvy_common_settings" # where to store data in bpy.texts
    settings_save_enabled: BoolProperty(name="settings save enabled", default=True) # type: ignore
    scenes_to_scene_names = {} # used to map scenes to scene names to detect scene renames for diffing

    mode: EnumProperty(
        items=(
                ('COMPONENTS', "Components", ""),
                ('BLUEPRINTS', "Blueprints", ""),
                ('LEVELS', "Levels", ""),
                ('ASSETS', "Assets", ""),
                ('SETTINGS', "Settings", ""),
                ('TOOLS', "Tools", ""),
        ),
        default="SETTINGS",
        update=save_settings
    ) # type: ignore

    config_mode: EnumProperty(
        items=(
                ('COMMON', "Common", "Switch to common configuration"),
                ('COMPONENTS', "Components", "Switch to components configuration"),
                ('EXPORT', "Export", "Switch to export configuration"),
        ),
        default="COMMON",
        update=save_settings
    ) # type: ignore

    
    project_root_path: StringProperty(
        name = "Project Root Path",
        description="The root folder of your (Bevy) project (not assets!)",
        default='../',
        update= save_settings
    ) # type: ignore

    # computed property for the absolute path of assets
    project_root_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path))
    ) # type: ignore

    assets_path: StringProperty(
        name='Export folder',
        description='The root folder for all exports(relative to the root folder/path) Defaults to "assets" ',
        default='./assets',
        options={'HIDDEN'},
        update= save_settings
    ) # type: ignore
    
    # computed property for the absolute path of assets
    assets_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path, self.assets_path))
    ) # type: ignore

    blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the assets folder)',
        default='blueprints',
        update= save_settings
    ) # type: ignore

    # computed property for the absolute path of blueprints
    blueprints_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path, self.assets_path, self.blueprints_path))
    ) # type: ignore

    levels_path: StringProperty(
        name='Levels path',
        description='path to export the levels (level scenes) to (relative to the assets folder)',
        default='levels',
        update= save_settings
    ) # type: ignore

    # computed property for the absolute path of blueprints
    levels_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path, self.assets_path, self.levels_path))
    ) # type: ignore

    materials_path: StringProperty(
        name='Materials path',
        description='path to export the materials libraries to (relative to the assets folder)',
        default='materials',
        update= save_settings
    ) # type: ignore

    # computed property for the absolute path of blueprints
    materials_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path, self.assets_path, self.materials_path))
    ) # type: ignore

    # sub ones
    auto_export: PointerProperty(type=AutoExportSettings) # type: ignore
    components: PointerProperty(type=ComponentsSettings) # type: ignore

    level_scene_selector: PointerProperty(type=bpy.types.Scene, name="level scene", description="level scene picker", poll=is_scene_already_in_use, update=save_settings)# type: ignore
    library_scene_selector: PointerProperty(type=bpy.types.Scene, name="library scene", description="library scene picker", poll=is_scene_already_in_use, update=save_settings)# type: ignore

    @property
    def level_scenes(self):
        return [scene for scene in bpy.data.scenes if scene.blenvy_scene_type == 'Level']
    
    @property
    def level_scenes_names(self):
        return [scene.name for scene in self.level_scenes]
    
    @property
    def library_scenes(self):
        return [scene for scene in bpy.data.scenes if scene.blenvy_scene_type == 'Library']
    
    @property
    def library_scenes_names(self):
        return [scene.name for scene in self.library_scenes]

    @classmethod
    def register(cls):
        bpy.types.WindowManager.blenvy = PointerProperty(type=BlenvyManager)

        # unsure
        bpy.types.Collection.always_export = BoolProperty(default=False, description="always export this blueprint, regardless of changed status") # FIXME: not sure about this one
        bpy.types.Scene.always_export = BoolProperty(default=False, description="always export this blueprint, regardless of changed status") # FIXME: not sure about this one
        bpy.types.Scene.blenvy_scene_type = EnumProperty(
            items= (
                ('None', 'None', 'No blenvy type specified'),
                ('Level', 'Level','Level scene'),
                ('Library', 'Library', 'Library scene'),
            ),
         default='None'
        )

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.blenvy

        del bpy.types.Collection.always_export
        del bpy.types.Scene.always_export
        del bpy.types.Scene.blenvy_scene_type

    def load_settings(self):
        print("LOAD SETTINGS")
        settings = load_settings(self.settings_save_path)
        if settings is not None:
            self.settings_save_enabled = False # we disable auto_saving of our settings
            try:
                for setting in settings:
                    print("setting", setting, settings[setting])
                    setattr(self, setting, settings[setting])
            except:pass

        self.settings_save_enabled = True
 
        # now load auto_export settings
        self.auto_export.load_settings()

        # now load component settings
        self.components.load_settings()


        for scene in bpy.data.scenes:
            self.scenes_to_scene_names[scene] = scene.name
