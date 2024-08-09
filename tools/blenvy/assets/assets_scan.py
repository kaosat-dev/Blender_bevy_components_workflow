import os
import json
import posixpath
import bpy

from ..materials.materials_helpers import get_blueprint_materials
from .asset_helpers import does_asset_exist, get_user_assets, get_user_assets_as_list

def scan_assets(scene, blueprints_data, settings):
    project_root_path = getattr(settings, "project_root_path")
    export_output_folder = getattr(settings,"export_output_folder")
    levels_path = getattr(settings,"levels_path")
    blueprints_path = getattr(settings, "blueprints_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension")

    relative_blueprints_path = os.path.relpath(blueprints_path, project_root_path)
    blueprint_instance_names_for_scene = blueprints_data.blueprint_instances_per_level_scene.get(scene.name, None)

    blueprint_assets_list = []
    if blueprint_instance_names_for_scene:
        for blueprint_name in blueprint_instance_names_for_scene:
            blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
            if blueprint is not None: 
                #print("BLUEPRINT", blueprint)
                blueprint_exported_path = None
                if blueprint.local:
                    blueprint_exported_path = posixpath.join(relative_blueprints_path, f"{blueprint.name}{export_gltf_extension}")
                else:
                    # get the injected path of the external blueprints
                    blueprint_exported_path = blueprint.collection['Export_path'] if 'Export_path' in blueprint.collection else None
                if blueprint_exported_path is not None:
                    blueprint_assets_list.append({"name": blueprint.name, "path": blueprint_exported_path})
                

    # fetch images/textures
    # see https://blender.stackexchange.com/questions/139859/how-to-get-absolute-file-path-for-linked-texture-image
    textures = []
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            for mat_slot in ob.material_slots:
                if mat_slot.material:
                    if mat_slot.material.node_tree:
                        textures.extend([x.image.filepath for x in mat_slot.material.node_tree.nodes if x.type=='TEX_IMAGE'])
    print("textures", textures)

    assets_list_name = f"assets_{scene.name}"
    assets_list_data = {"blueprints": json.dumps(blueprint_assets_list), "sounds":[], "images":[]}

    #print("blueprint assets", blueprint_assets_list)


def get_userTextures():
    # TODO: limit this to the ones actually in use
    # fetch images/textures
    # see https://blender.stackexchange.com/questions/139859/how-to-get-absolute-file-path-for-linked-texture-image
    textures = []
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            for mat_slot in ob.material_slots:
                if mat_slot.material:
                    if mat_slot.material.node_tree:
                        textures.extend([x.image.filepath for x in mat_slot.material.node_tree.nodes if x.type=='TEX_IMAGE'])
    print("textures", textures)

def get_blueprint_assets_tree(blueprint, blueprints_data, parent, settings):
    print("blueprint", blueprint.name)
    blueprints_path = getattr(settings, "blueprints_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    assets_list = []
    

    for blueprint_name in blueprint.nested_blueprints:
        child_blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
        if child_blueprint:
            blueprint_exported_path = None
            if blueprint.local:
                blueprint_exported_path = posixpath.join(blueprints_path, f"{child_blueprint.name}{export_gltf_extension}")
            else:
                # get the injected path of the external blueprints
                blueprint_exported_path = child_blueprint.collection['export_path'] if 'export_path' in child_blueprint.collection else None
            if blueprint_exported_path is not None:
                assets_list.append({"name": child_blueprint.name, "path": blueprint_exported_path, "type": "MODEL", "generated": True,"internal":blueprint.local, "parent": blueprint.name})

            # and add sub stuff
            sub_assets_lists = get_blueprint_assets_tree(child_blueprint, blueprints_data, parent=child_blueprint.name, settings=settings)
            assets_list += sub_assets_lists

    direct_assets = get_user_assets_as_list(blueprint.collection)
    for asset in direct_assets:
        asset["parent"] = parent
        asset["internal"] = blueprint.local
    assets_list += direct_assets

    # now get materials used by this blueprint
    (blueprint_materials_names, materials_per_object) = get_blueprint_materials(blueprint=blueprint)
    print("blueprint_materials", blueprint_materials_names)
    for material_name in blueprint_materials_names:
        materials_path =  getattr(settings, "materials_path")
        materials_exported_path = posixpath.join(materials_path, f"{material_name}{export_gltf_extension}")
        assets_list.append({"name": material_name, "path": materials_exported_path, "type": "MATERIAL", "generated": True,"internal":blueprint.local, "parent": blueprint.name})

    return assets_list

def get_level_scene_assets_tree(level_scene, blueprints_data, settings):
    blueprints_path =  getattr(settings, "blueprints_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    blueprint_instance_names_for_scene = blueprints_data.blueprint_instances_per_level_scene.get(level_scene.name, None)

    assets_list = get_user_assets_as_list(level_scene)
    if blueprint_instance_names_for_scene:
        for blueprint_name in blueprint_instance_names_for_scene:
            blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
            if blueprint is not None: 
                blueprint_exported_path = None
                if blueprint.local:
                    blueprint_exported_path = posixpath.join(blueprints_path, f"{blueprint.name}{export_gltf_extension}")
                else:
                    # get the injected path of the external blueprints
                    blueprint_exported_path = blueprint.collection['export_path'] if 'export_path' in blueprint.collection else None
                if blueprint_exported_path is not None and not does_asset_exist(assets_list, blueprint_exported_path):
                    assets_list.append({"name": blueprint.name, "path": blueprint_exported_path, "type": "MODEL", "generated": True, "internal":blueprint.local, "parent": None})
                
                assets_list += get_blueprint_assets_tree(blueprint, blueprints_data, parent=blueprint.name, settings=settings)

    print("TOTAL ASSETS", assets_list)
    # FIXME: do not do it here !!
    scene = bpy.data.scenes[level_scene.name]
    scene.generated_assets.clear()
    for asset in assets_list:
        if asset.get("generated", False):
            added_asset = scene.generated_assets.add()
            added_asset.name = asset["name"]
            added_asset.path = asset["path"]
    return assets_list

# same as the above, withouth the clutter below : TODO: unify
def get_level_scene_assets_tree2(level_scene, blueprints_data, settings):
    blueprints_path =  getattr(settings, "blueprints_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    blueprint_instance_names_for_scene = blueprints_data.blueprint_instances_per_level_scene.get(level_scene.name, None)

    assets_list = get_user_assets_as_list(level_scene)
    if blueprint_instance_names_for_scene:
        for blueprint_name in blueprint_instance_names_for_scene:
            blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
            if blueprint is not None: 
                blueprint_exported_path = None
                if blueprint.local:
                    blueprint_exported_path = posixpath.join(blueprints_path, f"{blueprint.name}{export_gltf_extension}")
                else:
                    # get the injected path of the external blueprints
                    blueprint_exported_path = blueprint.collection['export_path'] if 'export_path' in blueprint.collection else None
                if blueprint_exported_path is not None and not does_asset_exist(assets_list, blueprint_exported_path):
                    assets_list.append({"name": blueprint.name, "path": blueprint_exported_path, "type": "MODEL", "generated": True, "internal":blueprint.local, "parent": None})
                
                assets_list += get_blueprint_assets_tree(blueprint, blueprints_data, parent=blueprint.name, settings=settings)
   
    return assets_list

def get_blueprint_asset_tree(blueprint, blueprints_data, settings):
    blueprints_path =  getattr(settings, "blueprints_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")

    assets_list = get_user_assets_as_list(blueprint.collection)

    for blueprint_name in blueprint.nested_blueprints:
        sub_blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
        if sub_blueprint is not None: 
            sub_blueprint_exported_path = None
            if sub_blueprint.local:
                sub_blueprint_exported_path = posixpath.join(blueprints_path, f"{sub_blueprint.name}{export_gltf_extension}")
            else:
                # get the injected path of the external blueprints
                sub_blueprint_exported_path = sub_blueprint.collection['export_path'] if 'export_path' in sub_blueprint.collection else None

            if sub_blueprint_exported_path is not None and not does_asset_exist(assets_list, sub_blueprint_exported_path):
                assets_list.append({"name": sub_blueprint.name, "path": sub_blueprint_exported_path, "type": "MODEL", "generated": True, "internal": sub_blueprint.local, "parent": None})
            
            assets_list += get_blueprint_assets_tree(sub_blueprint, blueprints_data, parent=sub_blueprint.name, settings=settings)
    
    return assets_list
