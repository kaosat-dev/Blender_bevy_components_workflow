
import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

from ..core.path_helpers import absolute_path_from_blend_file    

class BLENVY_OT_assets_paths_browse(Operator, ImportHelper):
    """Assets folder's browser"""
    bl_idname = "blenvy.assets_paths_browse" 
    bl_label = "Select folder" 

    # Define this to tell 'fileselect_add' that we want a directoy
    directory: bpy.props.StringProperty(
        name="Outdir Path",
        description="selected folder"
        # subtype='DIR_PATH' is not needed to specify the selection mode.
        # But this will be anyway a directory path.
        ) # type: ignore

    # Filters folders
    filter_folder: bpy.props.BoolProperty(
        default=True,
        options={"HIDDEN"}
        ) # type: ignore
    
    target_property: bpy.props.StringProperty(
        name="target_property",
        options={'HIDDEN'}
    ) # type: ignore
    
    def execute(self, context): 
        """Do something with the selected file(s)."""
        operator = context.window_manager.blenvy
        new_path = self.directory
        target_path_name = self.target_property

        # path to the current blend file
        blend_file_path = bpy.data.filepath
        # Get the folder
        blend_file_folder_path = os.path.dirname(blend_file_path)
        #print("blend_file_folder_path", blend_file_folder_path)
        #print("new_path", self.directory, self.target_property, operator)

        asset_path_names = ['blueprints_path', 'levels_path', 'materials_path']
        project_root_path = absolute_path_from_blend_file(operator.project_root_path)
        assets_path = operator.assets_path
        assets_path_full = absolute_path_from_blend_file(os.path.join(project_root_path, assets_path)) #os.path.join(blend_file_folder_path, project_root_path, assets_path)
        #print("assets_path_full", assets_path_full)

        #new_root_path = os.path.join(blend_file_folder_path, new_path)
        if target_path_name == 'project_root_path':
            new_root_path_relative = os.path.relpath(new_path, blend_file_folder_path)
            new_root_path_absolute = new_path

            #print("new_root_path_relative", new_root_path_relative, new_root_path_absolute)
            # first change the asset's path
            old_assets_paths_relative = getattr(operator, "assets_path", None)
            if old_assets_paths_relative is not None:
                old_assets_paths_absolute = os.path.abspath(os.path.join(project_root_path, old_assets_paths_relative))
                new_assets_path_relative = os.path.relpath(old_assets_paths_absolute, new_root_path_absolute)
                new_assets_path_absolute = os.path.abspath(os.path.join(new_root_path_absolute, new_assets_path_relative))

                """print("old_assets_paths_absolute", old_assets_paths_absolute)
                print("new_assets_path_relative", new_assets_path_relative)
                print("new_assets_path_absolute", new_assets_path_absolute)"""
                setattr(operator, "assets_path", new_assets_path_relative)

                # we need to change all other relative paths (root => assets => blueprints/levels/materials etc)
                for path_name in asset_path_names:
                    # get current relative path
                    relative_path = getattr(operator, path_name, None)
                    if relative_path is not None:
                        # and now get absolute path of asset_path 
                        # compute 'old' absolute path
                        old_absolute_path = os.path.abspath(os.path.join(assets_path_full, relative_path))
                        relative_path = os.path.relpath(old_absolute_path, new_assets_path_absolute)
                        setattr(operator, path_name, relative_path)

            # store the root path as relative to the current blend file
            setattr(operator, target_path_name, new_root_path_relative)
        elif target_path_name == 'assets_path':
            new_assets_path_relative = os.path.relpath(new_path, project_root_path)
            new_assets_path_absolute = new_path
            # we need to change all other relative paths (root => assets => blueprints/levels/materials etc)
            for path_name in asset_path_names:
                # get 'old' relative path
                relative_path = getattr(operator, path_name, None)
                if relative_path is not None:
                    # compute 'old' absolute path
                    old_absolute_path = os.path.abspath(os.path.join(assets_path_full, relative_path))
                    relative_path = os.path.relpath(old_absolute_path, new_assets_path_absolute)
                    setattr(operator, path_name, relative_path)

            setattr(operator, target_path_name, new_assets_path_relative)
        else:
            relative_path = os.path.relpath(new_path, assets_path_full)
            setattr(operator, target_path_name, relative_path)

        return {'FINISHED'}