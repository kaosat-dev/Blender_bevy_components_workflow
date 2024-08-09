import bpy
import os 
import subprocess
import json
import pytest
import shutil


@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")
    root_path =  "../../testing/bevy_example"
    assets_root_path = os.path.join(root_path, "assets")
    blueprints_path =  os.path.join(assets_root_path, "blueprints")
    levels_path =  os.path.join(assets_root_path, "levels")

    models_path =  os.path.join(assets_root_path, "models")
    materials_path = os.path.join(assets_root_path, "materials")

    other_materials_path = os.path.join(assets_root_path, "other_materials")
    other_blueprints_path = os.path.join(assets_root_path, "other_blueprints")

    yield {
        "root_path": root_path, 
        "models_path": models_path,
        "blueprints_path": blueprints_path, 
        "levels_path": levels_path, 
        "materials_path":materials_path,
        "other_materials_path":other_materials_path,
        "other_blueprints_path":other_blueprints_path
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

        if os.path.exists(other_materials_path):
            shutil.rmtree(other_materials_path)

        if os.path.exists(other_blueprints_path):
            shutil.rmtree(other_blueprints_path)
        

    request.addfinalizer(finalizer)

    return None


def get_orphan_data():
    orphan_meshes = [m.name for m in bpy.data.meshes if m.users == 0]
    orphan_objects = [m.name for m in bpy.data.objects if m.users == 0]

    #print("orphan meshes before", orphan_meshes)
    return orphan_meshes + orphan_objects

def test_export_do_not_export_blueprints(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    
    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="assets/models",
        export_scene_settings=True,
        export_blueprints=False,
    )
    assert os.path.exists(os.path.join(setup_data["models_path"], "World.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"],"Blueprint1.glb")) == False
    orphan_data = get_orphan_data()
    assert len(orphan_data) == 0


def test_export_custom_blueprints_path(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }

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
        blueprints_path = "assets/other_blueprints"
    )
    assert os.path.exists(os.path.join(setup_data["levels_path"], "World.glb")) == True
    assert os.path.exists(os.path.join(setup_data["root_path"],"assets", "other_blueprints", "Blueprint1.glb")) == True
    assert len(get_orphan_data()) == 0

def test_export_materials_library(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library = True
    )

    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join(setup_data["materials_path"], "testing_materials_library.glb")) == True
    assert len(get_orphan_data()) == 0

def test_export_materials_library_custom_path(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library = True,
        materials_path="assets/other_materials"
    )

    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join(setup_data["materials_path"], "testing_materials_library.glb")) == False
    assert os.path.exists(os.path.join(setup_data["other_materials_path"], "testing_materials_library.glb")) == True
    assert len(get_orphan_data()) == 0

def test_export_collection_instances_combine_mode(setup_data): # There is more in depth testing of this in the "change_tracking" tests
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))


    bpy.data.objects["Cube"]["dynamic"] = True

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_blueprints=True,
        collection_instances_combine_mode = 'Embed'
    )

    assert os.path.exists(os.path.join(setup_data["levels_path"], "World.glb")) == True
    assert os.path.exists(os.path.join(setup_data["levels_path"], "World_dynamic.glb")) == False
    assert len(get_orphan_data()) == 0


def test_export_do_not_export_marked_assets(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
    )
    assert os.path.exists(os.path.join(setup_data["levels_path"], "World.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"],"Blueprint2.glb")) == False
    assert os.path.exists(os.path.join(setup_data["blueprints_path"],"Blueprint3.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"],"Blueprint4_nested.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"],"Blueprint5.glb")) == False
    assert len(get_orphan_data()) == 0


def test_export_separate_dynamic_and_static_objects(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))


    bpy.data.objects["Cube"]["dynamic"] = True

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_separate_dynamic_and_static_objects = True
    )

    assert os.path.exists(os.path.join(setup_data["levels_path"], "World.glb")) == True
    assert os.path.exists(os.path.join(setup_data["levels_path"], "World_dynamic.glb")) == True
    assert len(get_orphan_data()) == 0


def test_export_should_not_generate_orphan_data(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    
    # first, configure things
    # we use the global settings for that
    export_props = {
        "level_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
    )
    assert os.path.exists(os.path.join(setup_data["levels_path"], "World.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"],"Blueprint1.glb")) == True
    assert len(get_orphan_data()) == 0

