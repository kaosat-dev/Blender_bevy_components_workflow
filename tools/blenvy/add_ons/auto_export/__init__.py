import os
import json
import pathlib
import bpy
from ...settings import generate_complete_settings_dict
from io_scene_gltf2 import ExportGLTF2_Base


def cleanup_file():
    gltf_filepath = bpy.context.window_manager.auto_export_tracker.dummy_file_path
    if os.path.exists(gltf_filepath):
        os.remove(gltf_filepath)
        # in case of seperate gltf/bin files, also remove bin file
        if gltf_filepath.endswith('gltf'):
            bin_path = os.path.join(os.path.dirname(gltf_filepath), pathlib.Path(gltf_filepath).stem + ".bin")
            if os.path.exists(bin_path):
                os.remove(bin_path)
        return None
    else:
        return 1.0
    
def gltf_post_export_callback(data):
    #print("post_export", data)
    blenvy = bpy.context.window_manager.blenvy
    tracker = bpy.context.window_manager.auto_export_tracker
    tracker.export_finished()

    gltf_settings_backup = tracker.gltf_settings_backup
    gltf_filepath = data["gltf_filepath"]
    gltf_export_id = data['gltf_export_id']
    if gltf_export_id == "blenvy":
        # some more absurdity: apparently the file is not QUITE done when the export callback is called, so we have to introduce this timer to remove the temporary file correctly
        tracker.dummy_file_path = gltf_filepath
        try:
            bpy.app.timers.unregister(cleanup_file)
        except:pass
        bpy.app.timers.register(cleanup_file, first_interval=2)

        # get the parameters
        scene = bpy.context.scene
        if "glTF2ExportSettings" in scene:
            settings = scene["glTF2ExportSettings"]
            gltf_export_settings = bpy.data.texts[".blenvy_gltf_settings"] if ".blenvy_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".blenvy_gltf_settings")
            # now write new settings
            gltf_export_settings.clear()

            settings = dict(settings)
            current_gltf_settings = generate_complete_settings_dict(settings, presets=ExportGLTF2_Base, ignore_list=["use_active_collection", "use_active_collection_with_nested", "use_active_scene", "use_selection", "will_save_settings", "gltf_export_id"], preset_defaults=False)
            gltf_export_settings.write(json.dumps(current_gltf_settings))
        # now reset the original gltf_settings
        if gltf_settings_backup != "":
            scene["glTF2ExportSettings"] = json.loads(gltf_settings_backup)
        else:
            if "glTF2ExportSettings" in scene:
                del scene["glTF2ExportSettings"]
        tracker.gltf_settings_backup = ""
       
        # the absurd length one has to go through to RESET THE OPERATOR because it has global state !!!!! AAAAAHHH
        last_operator = tracker.last_operator
        last_operator.filepath = ""
        last_operator.gltf_export_id = ""