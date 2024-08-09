import json

def get_user_assets(scene_or_collection):
    user_assets = getattr(scene_or_collection, 'user_assets', [])
    return user_assets

def get_generated_assets(scene_or_collection):
    generated_assets = getattr(scene_or_collection, 'generated_assets', [])
    return generated_assets

def get_user_assets_as_list(scene_or_collection):
    raw = get_user_assets(scene_or_collection)
    result = []
    for asset in raw:
        result.append({"name": asset.name, "path": asset.path, "type": "MODEL", "internal": False, "parent": None})
    return result

def upsert_asset(scene_or_collection, asset):
    new_asset = scene_or_collection.user_assets.add()
    new_asset.name = asset["name"]
    new_asset.path = asset["path"]

def remove_asset(scene_or_collection, ref_asset):
    print("to remove", ref_asset["path"], scene_or_collection.user_assets.find(ref_asset["path"]), scene_or_collection.user_assets)
    removal_index = -1
    for index, asset in enumerate(scene_or_collection.user_assets):
        print("asset in list", asset.name, asset.path)
        if asset.path == ref_asset["path"]:
            print("FOUND", index)
            removal_index = index
            break
    #scene_or_collection.user_assets.find(lambda x,y : print(x))
    if removal_index != -1 :
        print("REMOVE")
        scene_or_collection.user_assets.remove(removal_index)
    #scene_or_collection.user_assets.remove(scene_or_collection.user_assets.find(ref_asset["path"]))

def does_asset_exist(scene_or_collection, ref_asset):
    user_assets = getattr(scene_or_collection, 'user_assets', [])
    in_list = [asset for asset in user_assets if (asset.path == ref_asset["path"])]
    in_list = len(in_list) > 0
    return in_list