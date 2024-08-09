import os
import zipfile

ignore_list = ['.pytest_cache', '__pycache__']

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        # filter out invalid paths
        root_path = os.path.normpath(root)
        root_path = root_path.split(os.sep)
        add_file = True
        for sub_path in root_path:
            if sub_path in ignore_list:
                add_file = False
                break

        if add_file:
            for file in files:
                ziph.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        os.path.join(path, '..')))

with zipfile.ZipFile("blenvy.zip", mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
    zipdir('./blenvy', archive)

