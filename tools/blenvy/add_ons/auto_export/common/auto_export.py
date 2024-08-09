
import os
import bpy
import traceback

from ....blueprints.blueprint_helpers import inject_export_path_into_internal_blueprints

from ..blueprints.get_blueprints_to_export import get_blueprints_to_export
from ..levels.get_levels_to_export import get_levels_to_export
from .export_gltf import get_standard_exporter_settings

from ..levels.export_levels import export_level_scene
from ..blueprints.export_blueprints import export_blueprints

from ..materials.get_materials_to_export import get_materials_to_export
from ..materials.export_materials import cleanup_materials, export_materials
from ..levels.bevy_scene_components import remove_scene_components, upsert_scene_components


"""this is the main 'central' function for all auto export """
def auto_export(changes_per_scene, changes_per_collection, changes_per_material, changed_export_parameters, settings):
    # have the export parameters (not auto export, just gltf export) have changed: if yes (for example switch from glb to gltf, compression or not, animations or not etc), we need to re-export everything
    print ("changed_export_parameters", changed_export_parameters)
    try:
        #should we use change detection or not 
        change_detection = getattr(settings.auto_export, "change_detection")
        export_scene_settings = getattr(settings.auto_export, "export_scene_settings")
        export_blueprints_enabled = getattr(settings.auto_export, "export_blueprints")
        export_materials_library = getattr(settings.auto_export, "export_materials_library")

        # standard gltf export settings are stored differently
        standard_gltf_exporter_settings = get_standard_exporter_settings()
        gltf_extension = standard_gltf_exporter_settings.get("export_format", 'GLB')
        gltf_extension = '.glb' if gltf_extension == 'GLB' else '.gltf'
        settings.export_gltf_extension = gltf_extension

        blueprints_data = bpy.context.window_manager.blueprints_registry.refresh_blueprints()
        #blueprints_data = bpy.context.window_manager.blueprints_registry.blueprints_data
        #print("blueprints_data", blueprints_data)
        blueprints_per_scene = blueprints_data.blueprints_per_scenes
        internal_blueprints = [blueprint.name for blueprint in blueprints_data.internal_blueprints]
        external_blueprints = [blueprint.name for blueprint in blueprints_data.external_blueprints]

        # we inject the blueprints export path
        blueprints_path = getattr(settings,"blueprints_path")
        # inject the "export_path" and "material_path" properties into the internal blueprints
        inject_export_path_into_internal_blueprints(internal_blueprints=blueprints_data.internal_blueprints, blueprints_path=blueprints_path, gltf_extension=gltf_extension, settings=settings)


        for blueprint in blueprints_data.blueprints:
            bpy.context.window_manager.blueprints_registry.add_blueprint(blueprint)
        #bpy.context.window_manager.blueprints_registry.refresh_blueprints()

        if export_scene_settings:
            # inject/ update scene components
            upsert_scene_components(settings.level_scenes)
        #inject/ update light shadow information
        for light in bpy.data.lights:
            enabled = 'true' if light.use_shadow else 'false'
            # TODO: directly set relevant components instead ?
            light['BlenderLightShadows'] = f"(enabled: {enabled}, buffer_bias: {light.shadow_buffer_bias})"

        # export
        if export_blueprints_enabled:
            print("EXPORTING")
            # get blueprints/collections infos
            (blueprints_to_export) = get_blueprints_to_export(changes_per_scene, changes_per_collection, changed_export_parameters, blueprints_data, settings)
             
            # get level scenes infos
            (level_scenes_to_export) = get_levels_to_export(changes_per_scene, changes_per_collection, changed_export_parameters, blueprints_data, settings)

            # since materials export adds components we need to call this before blueprints are exported
            # export materials & inject materials components into relevant objects
            materials_to_export = get_materials_to_export(changes_per_material, changed_export_parameters, blueprints_data, settings)    
            
            # update the list of tracked exports
            exports_total = len(blueprints_to_export) + len(level_scenes_to_export) + (1 if export_materials_library else 0)
            bpy.context.window_manager.auto_export_tracker.exports_total = exports_total
            bpy.context.window_manager.auto_export_tracker.exports_count = exports_total

            """bpy.context.window_manager.exportedCollections.clear()
            for  blueprint in blueprints_to_export:
                bla = bpy.context.window_manager.exportedCollections.add()
                bla.name = blueprint.name"""
            print("-------------------------------")
            #print("collections:               all:", collections)
            #print("collections: not found on disk:", collections_not_on_disk)
            print("BLUEPRINTS:    local/internal:", internal_blueprints)
            print("BLUEPRINTS:          external:", external_blueprints)
            print("BLUEPRINTS:         per_scene:", blueprints_per_scene)
            print("-------------------------------")
            print("BLUEPRINTS:        to export:", [blueprint.name for blueprint in blueprints_to_export])
            print("-------------------------------")
            print("LEVELS:            to export:", level_scenes_to_export)
            print("-------------------------------")
            print("MATERIALS:         to export:", materials_to_export)
            print("-------------------------------")
            # backup current active scene
            old_current_scene = bpy.context.scene
            # backup current selections
            old_selections = bpy.context.selected_objects
        
            # deal with materials
            if export_materials_library and (not change_detection or changed_export_parameters or len(materials_to_export) > 0) :
                print("export MATERIALS")
                export_materials(materials_to_export, settings, blueprints_data)

            # export any level/world scenes
            if not change_detection or changed_export_parameters or len(level_scenes_to_export) > 0:
                print("export LEVELS")
                for scene_name in level_scenes_to_export:
                    print("     exporting scene:", scene_name)
                    export_level_scene(bpy.data.scenes[scene_name], settings, blueprints_data)

            # now deal with blueprints/collections
            if not change_detection or changed_export_parameters or len(blueprints_to_export) > 0:
                print("export BLUEPRINTS")
                export_blueprints(blueprints_to_export, settings, blueprints_data)

            # reset current scene from backup
            bpy.context.window.scene = old_current_scene

            # reset selections
            for obj in old_selections:
                obj.select_set(True)
            if export_materials_library:
                cleanup_materials(blueprints_data.blueprint_names, settings.library_scenes)

        else:
            for scene in settings.level_scenes:
                export_level_scene(scene, settings, [])



    except Exception as error:
        print(traceback.format_exc())

        def error_message(self, context):
            self.layout.label(text="Failure during auto_export: Error: "+ str(error))

        bpy.context.window_manager.popup_menu(error_message, title="Error", icon='ERROR')

    finally:
        # FIXME: error handling ? also redundant
        if export_scene_settings:
            # inject/ update scene components
            remove_scene_components(settings.level_scenes)

