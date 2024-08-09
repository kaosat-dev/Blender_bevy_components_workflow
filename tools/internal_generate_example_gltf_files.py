import os
import bpy
import subprocess

def test_generate_example_gltf_files():
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] 
    print("export settings", stored_settings.as_string())
    auto_export_operator(
        direct_mode = True,
        export_change_detection=False
    )

if __name__ == "__main__":
    examples = [
        '../examples/blenvy/basic',
        """'../examples/blenvy/animation',
        '../examples/blenvy/basic_xpbd_physics',
        '../examples/blenvy/materials',
        '../examples/blenvy/multiple_levels_multiple_blendfiles',"""
    ]

    for example_path in examples:
        print("generating gltf files for ", example_path)
        assets_path = os.path.join(example_path, "assets")
        art_path = os.path.join(example_path, "art")
        blend_files = []

        if os.path.exists(assets_path):
            for file in os.listdir(assets_path):
                if file.endswith(".blend"):
                    print("file found !", file)
                    blend_files.append(os.path.join("assets", file))
        if os.path.exists(art_path):
            for file in os.listdir(art_path):
                if file.endswith(".blend"):
                    print("file found !", file)
                    blend_files.append(os.path.join("art", file))

        
        print("blend files", blend_files)
        for blend_file in blend_files:
            fake_test_path = os.path.abspath("./internal_generate_example_gltf_files.py")
            command = "pytest -svv --blender-executable /home/ckaos/tools/blender/blender-4.0.2-linux-x64/blender --blender-template "+blend_file + " "+fake_test_path
            return_code = subprocess.call(command.split(" "), cwd=example_path)
