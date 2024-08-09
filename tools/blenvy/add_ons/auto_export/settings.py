import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty)
from ...settings import load_settings, upsert_settings, generate_complete_settings_dict

# list of settings we do NOT want to save
settings_black_list = ['settings_save_enabled', 'dry_run']

def save_settings(settings, context): 
    if settings.settings_save_enabled:
        settings_dict =  generate_complete_settings_dict(settings, AutoExportSettings, [])
        upsert_settings(settings.settings_save_path, {key: settings_dict[key] for key in settings_dict.keys() if key not in settings_black_list}, overwrite=True)

class AutoExportSettings(PropertyGroup):

    settings_save_path = ".blenvy_export_settings" # where to store data in bpy.texts
    settings_save_enabled: BoolProperty(name="settings save enabled", default=True) # type: ignore

    auto_export: BoolProperty(
        name='Auto export',
        description='Automatically export to gltf on save',
        default=True,
        update=save_settings
    ) # type: ignore

    #### change detection
    change_detection: BoolProperty(
        name='Change detection',
        description='Use change detection to determine what/if should be exported',
        default=True,
        update=save_settings
    ) # type: ignore

    materials_in_depth_scan : BoolProperty(
        name='In depth scan of materials (could be slow)',
        description='serializes more details of materials in order to detect changes (could be slower, but much more accurate in detecting changes)',
        default=True,
        update=save_settings
    ) # type: ignore

    modifiers_in_depth_scan : BoolProperty(
        name='In depth scan of modifiers (could be slow)',
        description='serializes more details of modifiers (particularly geometry nodes) in order to detect changes (could be slower, but much more accurate in detecting changes)',
        default=True,
        update=save_settings
    ) # type: ignore

    # scenes 

    # scene components
    export_scene_settings: BoolProperty(
        name='Export scene settings',
        description='Export scene settings ie AmbientLighting, Bloom, AO etc',
        default=False,
        update=save_settings
    ) # type: ignore

    # blueprint settings
    export_blueprints: BoolProperty(
        name='Export Blueprints',
        description='Replaces collection instances with an Empty with a BlueprintInfo custom property, and enabled a lot more features !',
        default=True,
        update=save_settings
    ) # type: ignore

    export_separate_dynamic_and_static_objects: BoolProperty(
        name="Export levels' dynamic and static objects seperatly",
        description="""For MAIN scenes only (aka levels), toggle this to generate 2 files per level: 
            - one with all dynamic data: collection or instances marked as dynamic/ saveable
            - one with all static data: anything else that is NOT marked as dynamic""",
        default=False,
        update=save_settings
    ) # type: ignore

    export_materials_library: BoolProperty(
        name='Export materials library',
        description='remove materials from blueprints and use the material library instead',
        default=True,
        update=save_settings
    ) # type: ignore


    """ combine mode can be 
              - 'Split' (default): replace with an empty, creating links to sub blueprints 
              - 'Embed' : treat it as an embeded object and do not replace it with an empty
              - 'EmbedExternal': embed any instance of a non local collection (ie external assets)

              - 'Inject': inject components from sub collection instances into the curent object => this is now a seperate custom property that you can apply to a collecion instance
            """

    collection_instances_combine_mode : EnumProperty(
        name='Collection instances',
        items=(
           ('Split', 'Split', 'replace collection instances with an empty + blueprint, creating links to sub blueprints (Default, Recomended)'),
           ('Embed', 'Embed', 'treat collection instances as embeded objects and do not replace them with an empty'),
           ('EmbedExternal', 'EmbedExternal', 'treat instances of external (not specifified in the current blend file) collections (aka assets etc) as embeded objects and do not replace them with empties'),
           #('Inject', 'Inject', 'inject components from sub collection instances into the curent object')
        ),
        default='Split',
        update=save_settings
    ) # type: ignore

    dry_run: EnumProperty(
        name="dry run",
        description="debug/ develop helper to enable everything but the actual exporting of files",
        items=(
            ("DISABLED", "Disabled","Run exports normally (no Dry run)"),
            ("NO_EXPORT", "No export", "do not actually export gltf files"),
            ("NO_PREPARE", "No prepare", "do not actually export gltf files AND do not prepare the exports either (ie no creating fake scenes etc)"),
        ),
        default="DISABLED",
    ) # type: ignore


    def load_settings(self):
        settings = load_settings(self.settings_save_path)
        if settings is not None:
            self.settings_save_enabled = False # we disable auto_saving of our settings
            try:
                for setting in settings:
                    setattr(self, setting, settings[setting])
            except: pass
            # TODO: remove setting if there was a failure
        
        self.settings_save_enabled = True

