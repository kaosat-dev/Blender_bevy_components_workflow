import bpy
import os 
import subprocess
import json
import pytest
import shutil

import filecmp
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")

    def finalizer():
        root_path =  "../../testing/bevy_example"
        assets_root_path = os.path.join(root_path, "assets")
        models_path =  os.path.join(assets_root_path, "models")
        materials_path = os.path.join(assets_root_path, "materials")
        #other_materials_path = os.path.join("../../testing", "other_materials")

        print("\nPerforming teardown...")
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
- removes existing gltf files if needed
- calls exporter on the testing scene
- launches bevy app & checks for output
- if all worked => test is a-ok
"""
def test_export_complex(setup_data):
    root_path = "../../testing/bevy_example"
    assets_root_path = os.path.join(root_path, "assets")
    models_path = os.path.join(assets_root_path, "models")
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['World'],
        "library_scene_names": ['Library'],
        # "export_format":'GLTF_SEPARATE'
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    # move the main cube
    bpy.data.objects["Cube"].location = [1, 0, 0]
    # move the cube in the library
    bpy.data.objects["Blueprint1_mesh"].location = [1, 2, 1]

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_legacy_mode=False,
        export_animations=True,
        export_materials_library=True
    )
    # blueprint1 => has an instance, got changed, should export
    # blueprint2 => has NO instance, but marked as asset, should export
    # blueprint3 => has NO instance, not marked as asset, used inside blueprint 4: should export
    # blueprint4 => has an instance, with nested blueprint3, should export
    # blueprint5 => has NO instance, not marked as asset, should NOT export

    assert os.path.exists(os.path.join(models_path, "World.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint2.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint3.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint4_nested.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint5.glb")) == False
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint6_animated.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint7_hierarchy.glb")) == True

    # 'assets_list_'+scene.name+"_components" should have been removed after the export
    assets_list_object_name = "assets_list_"+"World"+"_components"
    assets_list_object_present = assets_list_object_name in bpy.data.objects
    assert assets_list_object_present == False

    # now run bevy
    command = "cargo run --features bevy/dynamic_linking"
    FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess
    return_code = subprocess.call(["cargo", "run", "--features", "bevy/dynamic_linking"], cwd=root_path)
    print("RETURN CODE OF BEVY APP", return_code)
    assert return_code == 0

    with open(os.path.join(root_path, "bevy_diagnostics.json")) as diagnostics_file:
        diagnostics = json.load(diagnostics_file)
        print("diagnostics", diagnostics)
        assert diagnostics["animations"] == True
        assert diagnostics["empty_found"] == True
        assert diagnostics["blueprints_list_found"] == True
        assert diagnostics["exported_names_correct"] == True

    with open(os.path.join(root_path, "bevy_hierarchy.json")) as hierarchy_file:
        with open(os.path.join(os.path.dirname(__file__), "expected_bevy_hierarchy.json")) as expexted_hierarchy_file:
            hierarchy = json.load(hierarchy_file)
            expected = json.load(expexted_hierarchy_file)
            assert sorted(hierarchy.items()) == sorted(expected.items())

    # last but not least, do a visual compare
    screenshot_expected_path = os.path.join(root_path, "expected_screenshot.png")
    screenshot_observed_path = os.path.join(root_path, "screenshot.png")
    img_a = Image.open(screenshot_expected_path)
    img_b = Image.open(screenshot_observed_path)
    img_diff = Image.new("RGBA", img_a.size)
    mismatch = pixelmatch(img_a, img_b, img_diff, includeAA=True)
    print("image mismatch", mismatch)
    assert mismatch < 50


        
