import posixpath
import bpy
from pathlib import Path
from ...assets.assets_scan import get_blueprint_asset_tree, get_level_scene_assets_tree2
from ..bevy_components.utils import is_component_valid_and_enabled
from .constants import custom_properties_to_filter_out
from ...assets.assets_scan import get_level_scene_assets_tree2

def remove_unwanted_custom_properties(object):
    to_remove = []
    component_names = list(object.keys()) # to avoid 'IDPropertyGroup changed size during iteration' issues
    for component_name in component_names:
        if not is_component_valid_and_enabled(object, component_name):
            to_remove.append(component_name)
    for cp in custom_properties_to_filter_out + to_remove:
        if cp in object:
            del object[cp]

def assets_to_fake_ron(list_like):
    result = []
    for item in list_like:
        result.append(f"(name: \"{item['name']}\", path: \"{item['path']}\")")

    return f"(assets: {result})".replace("'", '')

# TODO : move to assets
def upsert_scene_assets(scene, blueprints_data, settings):
    all_assets = []
    all_assets_raw = get_level_scene_assets_tree2(level_scene=scene, blueprints_data=blueprints_data, settings=settings)
    local_assets =  [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset['parent'] is None and asset["path"] != "" ] 
    all_assets = [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset["path"] != "" ] 
    print("all_assets_raw", all_assets_raw)
    print("all_assets", all_assets)
    print("local assets", local_assets)
    scene["BlueprintAssets"] = assets_to_fake_ron(all_assets) #local_assets

def upsert_blueprint_assets(blueprint, blueprints_data, settings):   
    all_assets_raw = get_blueprint_asset_tree(blueprint=blueprint, blueprints_data=blueprints_data, settings=settings)
   
    all_assets = []
    auto_assets = []
    local_assets =  [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset['parent'] is None and asset["path"] != "" ]
    print("all_assets_raw", all_assets_raw)
    print("local assets", local_assets)
    blueprint.collection["BlueprintAssets"] = assets_to_fake_ron(local_assets)

import os 
def write_level_metadata_file(scene, blueprints_data, settings):
    levels_path_full = getattr(settings,"levels_path_full")
    all_assets_raw = get_level_scene_assets_tree2(level_scene=scene, blueprints_data=blueprints_data, settings=settings)

    formated_assets = []
    for asset in all_assets_raw:
        #if asset["internal"] :
        formated_asset = f'\n    ("{asset["name"]}", File ( path: "{asset["path"]}" )),'
        formated_assets.append(formated_asset)
    
    metadata_file_path_full = os.path.join(levels_path_full, scene.name+".meta.ron")
    os.makedirs(os.path.dirname(metadata_file_path_full), exist_ok=True)

    with open(metadata_file_path_full, "w") as assets_file:
        assets_file.write("(\n ")
        assets_file.write(" assets:\n   [ ")
        assets_file.writelines(formated_assets)
        assets_file.write("\n   ]\n")
        assets_file.write(")")

def write_blueprint_metadata_file(blueprint, blueprints_data, settings):
    blueprints_path_full = getattr(settings,"blueprints_path_full")
    all_assets_raw = get_blueprint_asset_tree(blueprint=blueprint, blueprints_data=blueprints_data, settings=settings)

    formated_assets = []
    for asset in all_assets_raw:
        #if asset["internal"] :
        formated_asset = f'\n    ("{asset["name"]}", File ( path: "{asset["path"]}" )),'
        formated_assets.append(formated_asset)


    metadata_file_path_full = os.path.join(blueprints_path_full, blueprint.name+".meta.ron")
    os.makedirs(os.path.dirname(metadata_file_path_full), exist_ok=True)

    with open(metadata_file_path_full, "w") as assets_file:
        assets_file.write("(\n ")
        assets_file.write(" assets:\n   [ ")
        assets_file.writelines(formated_assets)
        assets_file.write("\n   ]\n")
        assets_file.write(")")