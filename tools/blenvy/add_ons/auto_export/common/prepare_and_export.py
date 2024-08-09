import bpy

from .project_diff import get_changes_per_scene
from .auto_export import auto_export
from .settings_diff import get_setting_changes
from ....settings import upsert_settings

# prepare export by gather the changes to the scenes & settings
def prepare_and_export():
    print("prepare and export")
    #bpy.context.window_manager.auto_export_tracker.disable_change_detection()
    blenvy = bpy.context.window_manager.blenvy
    auto_export_settings = blenvy.auto_export

    # if there are no level or blueprint scenes, bail out early
    if len(blenvy.level_scenes) == 0 and len(blenvy.library_scenes) == 0:
        print("no level or library scenes, skipping auto export")
        return 

    if auto_export_settings.auto_export: # only do the actual exporting if auto export is actually enabled
        # determine changed objects
        per_scene_changes, per_collection_changes, per_material_changes, project_hash = get_changes_per_scene(settings=blenvy)
        # determine changed parameters 
        setting_changes, current_common_settings, current_export_settings, current_gltf_settings = get_setting_changes()
        print("changes: settings:", setting_changes)
        print("changes: scenes:", per_scene_changes)
        print("changes: collections:", per_collection_changes)
        print("changes: materials:", per_material_changes)

        # do the actual export
        # blenvy.auto_export.dry_run = 'NO_EXPORT'#'DISABLED'#
        auto_export(per_scene_changes, per_collection_changes, per_material_changes, setting_changes, blenvy)

        # -------------------------------------
        # now that this point is reached, the export should have run correctly, so we can save all the current state to the "previous one"
        for scene in bpy.data.scenes:
            blenvy.scenes_to_scene_names[scene] = scene.name
        print("bla", blenvy.scenes_to_scene_names, "hash", project_hash)
        # save the current project hash as previous
        upsert_settings(".blenvy.project_serialized_previous", project_hash, overwrite=True)
        # write the new settings to the old settings
        upsert_settings(".blenvy_common_settings_previous", current_common_settings, overwrite=True)
        upsert_settings(".blenvy_export_settings_previous", current_export_settings, overwrite=True)
        upsert_settings(".blenvy_gltf_settings_previous", current_gltf_settings, overwrite=True)

        # cleanup 
        # TODO: these are likely obsolete
        # reset the list of changes in the tracker
        #bpy.context.window_manager.auto_export_tracker.clear_changes()
        print("AUTO EXPORT DONE")            
