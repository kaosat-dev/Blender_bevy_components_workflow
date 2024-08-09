import os
import json
import pytest
import bpy
from blenvy.add_ons.auto_export.common.prepare_and_export import prepare_and_export

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")

    root_path =  "../../testing/bevy_example"
    assets_root_path = os.path.join(root_path, "assets")
    blueprints_path =  os.path.join(assets_root_path, "blueprints")
    levels_path =  os.path.join(assets_root_path, "levels")

    models_path =  os.path.join(assets_root_path, "models")
    materials_path = os.path.join(assets_root_path, "materials")
    yield {
        "root_path": root_path, 
        "models_path": models_path,
        "blueprints_path": blueprints_path, 
        "levels_path": levels_path, 
        "materials_path":materials_path 
        }
    
# this runs the external blueprints file 
def test_export_external_blueprints(setup_data):
    root_path = setup_data["root_path"]

    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
    }
    gltf_settings = {
        "export_animations": True,
        "export_optimize_animation_size": False
    }

    # store settings for the auto_export part
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))

    # and store settings for the gltf part
    stored_gltf_settings = bpy.data.texts[".blenvy_gltf_settings"] if ".blenvy_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".blenvy_gltf_settings")
    stored_gltf_settings.clear()
    stored_gltf_settings.write(json.dumps(gltf_settings))

    blenvy = bpy.context.window_manager.blenvy
    #blenvy.project_root_path = 
    #blenvy.blueprints_path
    blenvy.auto_export.auto_export = True
    blenvy.auto_export.export_scene_settings = True
    blenvy.auto_export.export_blueprints = True
    #blenvy.auto_export.export_materials_library = True

    print("SCENES", bpy.data.scenes)
    for scene in bpy.data.scenes:
        print("SCNE", scene)
    bpy.data.scenes['Library'].blenvy_scene_type = 'Library' # set scene as Library scene
    # do the actual export
    prepare_and_export()

    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "External_blueprint.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "External_blueprint2.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "External_blueprint3.glb")) == True