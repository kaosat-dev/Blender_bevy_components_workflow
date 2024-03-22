import bpy 

def get_standard_exporter_settings():
    settings_key = 'glTF2ExportSettings'
    for scene in bpy.data.scenes:
        if settings_key in scene:
            settings = scene[settings_key]
            #print("standard exporter settings", settings, dict(settings))
            return dict(settings)