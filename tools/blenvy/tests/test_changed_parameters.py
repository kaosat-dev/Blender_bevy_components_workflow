import bpy
import os 
import json
import pytest
import shutil

from .test_helpers import prepare_auto_export

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")
    root_path =  "../../testing/bevy_example"
    assets_root_path = os.path.join(root_path, "assets")
    blueprints_path =  os.path.join(assets_root_path, "blueprints")
    levels_path =  os.path.join(assets_root_path, "levels")

    models_path =  os.path.join(assets_root_path, "models")
    materials_path = os.path.join(assets_root_path, "materials")

    #other_materials_path = os.path.join("../../testing", "other_materials")
    yield {
        "root_path": root_path, 
        "models_path": models_path,
        "blueprints_path": blueprints_path, 
        "levels_path": levels_path, 
        "materials_path":materials_path 
    }

    def finalizer():
       

        print("\nPerforming teardown...")
        if os.path.exists(blueprints_path):
            shutil.rmtree(blueprints_path)

        if os.path.exists(levels_path):
            shutil.rmtree(levels_path)

        if os.path.exists(models_path):
            shutil.rmtree(models_path)

        if os.path.exists(materials_path):
            shutil.rmtree(materials_path)

        diagnostics_file_path = os.path.join(root_path, "bevy_diagnostics.json")
        if os.path.exists(diagnostics_file_path):
            os.remove(diagnostics_file_path)
        
        hierarchy_file_path = os.path.join(root_path, "bevy_hierarchy.json")
        if os.path.exists(hierarchy_file_path):
            os.remove(hierarchy_file_path)

        screenshot_observed_path = os.path.join(root_path, "screenshot.png")
        if os.path.exists(screenshot_observed_path):
            os.remove(screenshot_observed_path)

    request.addfinalizer(finalizer)

    return None


"""
- setup gltf parameters & auto_export parameters
- calls exporter on the testing scene
- saves timestamps of generated files
- changes exporter parameters
- checks if timestamps have changed
- if all worked => test is a-ok
- removes generated files
"""

def test_export_no_parameters(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # make sure to clear any parameters first
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps({}))

    # first test exporting without any parameters set, this should not export anything
    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        export_materials_library=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
    )

    world_file_path = os.path.join(setup_data["levels_path"], "World.glb")
    assert os.path.exists(world_file_path) != True

def test_export_auto_export_parameters_only(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library'],
    }
  
    # store settings for the auto_export part
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))
    
    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_materials_library=True
    )

    world_file_path = os.path.join(setup_data["levels_path"], "World.glb")
    assert os.path.exists(world_file_path) == True

def test_export_changed_parameters(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library'],
    }
  
    # store settings for the auto_export part
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))

    gltf_settings = {
        "export_animations": True,
        "export_optimize_animation_size": False
    }
    # and store settings for the gltf part
    stored_gltf_settings = bpy.data.texts[".blenvy_gltf_settings"] if ".blenvy_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".blenvy_gltf_settings")
    stored_gltf_settings.clear()
    stored_gltf_settings.write(json.dumps(gltf_settings))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library=True
    )

    world_file_path = os.path.join(setup_data["levels_path"], "World.glb")
    assert os.path.exists(world_file_path) == True

    blueprints_path = setup_data["blueprints_path"]
    model_library_file_paths = list(map(lambda file_name: os.path.join(blueprints_path, file_name), sorted(os.listdir(blueprints_path))))
    modification_times_first = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths))

    # export again, with no param changes: this should NOT export anything again, ie, modification times should be the same
    print("second export")
    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library=True
    )

    modification_times_no_change = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths))
    assert modification_times_no_change == modification_times_first

    # export again, this time changing the gltf settings
    print("third export, changed gltf parameters")

    gltf_settings = {
        "export_animations": True,
        "export_optimize_animation_size": True
    }

    stored_gltf_settings = bpy.data.texts[".blenvy_gltf_settings"] if ".blenvy_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".blenvy_gltf_settings")
    stored_gltf_settings.clear()
    stored_gltf_settings.write(json.dumps(gltf_settings))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library=True
    )

    modification_times_changed_gltf = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths))
    assert modification_times_changed_gltf != modification_times_first
    modification_times_first = modification_times_changed_gltf

    # now run it again, without changes, timestamps should be identical

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library=True
    )

    modification_times_changed_gltf = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths))
    assert modification_times_changed_gltf == modification_times_first
    modification_times_first = modification_times_changed_gltf


    # export again, this time changing the auto_export settings
    print("fourth export, changed auto parameters")

    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library'],
        "export_materials_library": False # we need to add it here, as the direct settings set on the operator will only be used for the NEXT run
    }
  
    # store settings for the auto_export part
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library=False
    )

    modification_times_changed_auto = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths))
    assert modification_times_changed_auto != modification_times_first
    modification_times_first = modification_times_changed_auto

    # now run it again, withouth changes, timestamps should be identical

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library=False
    )

    modification_times_changed_gltf = list(map(lambda file_path: os.path.getmtime(file_path), model_library_file_paths))
    assert modification_times_changed_gltf == modification_times_first
    modification_times_first = modification_times_changed_gltf
