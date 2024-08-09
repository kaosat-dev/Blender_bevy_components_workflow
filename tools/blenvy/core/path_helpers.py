import bpy
import os

def absolute_path_from_blend_file(path):
    # path to the current blend file
    blend_file_path = bpy.data.filepath
    # Get the folder
    blend_file_folder_path = os.path.dirname(blend_file_path) 

    # absolute path
    return os.path.abspath(os.path.join(blend_file_folder_path, path))
