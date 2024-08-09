

def write_ron_assets_file(name, assets_hierarchy, internal_only=False, output_path_full="."):
    # just for testing, this uses the format of bevy_asset_loader's asset files
    '''
            ({
        "world":File (path: "models/StartLevel.glb"),
        "level1":File (path: "models/Level1.glb"),
        "level2":File (path: "models/Level2.glb"),

        "models": Folder (
            path: "models/library",
        ),
        "materials": Folder (
            path: "materials",
        ),
    })
    '''
    formated_assets = []
    for asset in assets_hierarchy:
        if asset["internal"] or not internal_only:
            formated_asset = f'\n    "{asset["name"]}": File ( path: "{asset["path"]}" ),'
            formated_assets.append(formated_asset)

    with open(f"{output_path_full}/{name}.assets.ron", "w") as assets_file:
        assets_file.write("({")
        assets_file.writelines(formated_assets)
        assets_file.write("\n})")