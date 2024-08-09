from ....settings import are_settings_identical, load_settings, changed_settings

# which common settings changes should trigger a re-export 
parameter_names_whitelist_common = [
    # blenvy core
    'project_root_path',
    'assets_path',
    'blueprints_path',
    'levels_path',
    'materials_path',
    'level_scene_names',
    'library_scene_names',
]

# which auto export settings changes should trigger a re-export 
parameter_names_whitelist_auto_export = [
    # auto export
    'export_scene_settings',
    'export_blueprints',
    'export_separate_dynamic_and_static_objects',
    'export_materials_library',
    'collection_instances_combine_mode',
]

def get_setting_changes():
     previous_common_settings = load_settings(".blenvy_common_settings_previous")
     current_common_settings = load_settings(".blenvy_common_settings")
     changed_common_settings_fields = changed_settings(previous_common_settings, current_common_settings, white_list=parameter_names_whitelist_common)
     common_settings_changed = len(changed_common_settings_fields) > 0

     previous_export_settings = load_settings(".blenvy_export_settings_previous")
     current_export_settings = load_settings(".blenvy_export_settings")
     changed_export_settings_fields = changed_settings(previous_export_settings, current_export_settings, white_list=parameter_names_whitelist_auto_export)
     export_settings_changed = len(changed_export_settings_fields) > 0

     previous_gltf_settings = load_settings(".blenvy_gltf_settings_previous")
     current_gltf_settings = load_settings(".blenvy_gltf_settings")
     gltf_settings_changed = not are_settings_identical(previous_gltf_settings, current_gltf_settings)

     settings_changed = common_settings_changed or gltf_settings_changed or export_settings_changed

     # if there were no setting before, it is new, we need export # TODO: do we even need this ? I guess in the case where both the previous & the new one are both none ? very unlikely, but still
     if previous_common_settings is None:
          settings_changed = True
     if previous_export_settings is None:
          settings_changed = True
     if previous_gltf_settings is None:
          settings_changed = True


     return settings_changed, current_common_settings, current_export_settings, current_gltf_settings
