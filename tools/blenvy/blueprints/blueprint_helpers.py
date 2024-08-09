
import os
import json
import bpy
from pathlib import Path
import posixpath

def find_blueprints_not_on_disk(blueprints, folder_path, extension):
    not_found_blueprints = []
    for blueprint in blueprints:
        gltf_output_path = os.path.join(folder_path, blueprint.name + extension)
        # print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_blueprints.append(blueprint)
    return not_found_blueprints

def check_if_blueprint_on_disk(scene_name, folder_path, extension):
    gltf_output_path = os.path.join(folder_path, scene_name + extension)
    found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
    return found

def inject_export_path_into_internal_blueprints(internal_blueprints, blueprints_path, gltf_extension, settings):
    for blueprint in internal_blueprints:
        blueprint_exported_path = posixpath.join(blueprints_path, f"{blueprint.name}{gltf_extension}")
        # print("injecting blueprint path", blueprint_exported_path, "for", blueprint.name)
        blueprint.collection["export_path"] = blueprint_exported_path
        """if export_materials_library:
            blueprint.collection["materials_path"] = materials_exported_path"""
