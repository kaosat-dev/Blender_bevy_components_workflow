import bpy
import os 
import json
import pathlib

def prepare_auto_export(auto_export_overrides={}, gltf_export_settings = {"export_animations": False, "export_optimize_animation_size": False}):
    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library'],
        **auto_export_overrides
    }
  
    # store settings for the auto_export part
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))

    gltf_settings = gltf_export_settings
    # and store settings for the gltf part
    stored_gltf_settings = bpy.data.texts[".blenvy_gltf_settings"] if ".blenvy_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".blenvy_gltf_settings")
    stored_gltf_settings.clear()
    stored_gltf_settings.write(json.dumps(gltf_settings))

def run_auto_export(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library=False
    )

    levels_path = setup_data["levels_path"]
    level_file_paths = list(map(lambda file_name: os.path.join(levels_path, file_name), sorted(os.listdir(levels_path)))) if os.path.exists(levels_path) else []

    blueprints_path = setup_data["blueprints_path"]
    blueprints_file_paths = list(map(lambda file_name: os.path.join(blueprints_path, file_name), sorted(os.listdir(blueprints_path)))) if os.path.exists(blueprints_path) else []

    modification_times = list(map(lambda file_path: os.path.getmtime(file_path), blueprints_file_paths + level_file_paths))
    # assert os.path.exists(world_file_path) == True

    mapped_files_to_timestamps_and_index = {}
    for (index, file_path) in enumerate(blueprints_file_paths + level_file_paths):
        file_path = pathlib.Path(file_path).stem
        mapped_files_to_timestamps_and_index[file_path] = (modification_times[index], index)

    return (modification_times, mapped_files_to_timestamps_and_index)

def run_auto_export_and_compare(setup_data, changes, expected_changed_files = []):
    (modification_times_first, mapped ) = run_auto_export(setup_data)   
    for index, change in enumerate(changes):
        change()
        (modification_times, mapped ) = run_auto_export(setup_data)   

        changed_files = expected_changed_files[index]
        changed_file_indices =  [mapped[changed_file][1] for changed_file in changed_files]
        print("changed files", changed_files, changed_file_indices, "mapped", mapped)
        other_files_modification_times = [value for index, value in enumerate(modification_times) if index not in changed_file_indices]
        other_files_modification_times_first = [value for index, value in enumerate(modification_times_first) if index not in changed_file_indices]

        print("other_files_modification_times_new  ", other_files_modification_times)
        print("other_files_modification_times_first", other_files_modification_times_first)
        for changed_file_index in changed_file_indices:
            #print("modification_times_new  [changed_file_index]", modification_times[changed_file_index])
            #print("modification_times_first[changed_file_index]", modification_times_first[changed_file_index])
            if changed_file_index in modification_times_first and changed_file_index in modification_times:
                assert modification_times[changed_file_index] != modification_times_first[changed_file_index], f"failure in change: {index}, at file {changed_file_index}"
            # TODO: we should throw an error in the "else" case ?
        assert other_files_modification_times == other_files_modification_times_first ,  f"failure in change: {index}"
        
        # reset the comparing 
        modification_times_first = modification_times