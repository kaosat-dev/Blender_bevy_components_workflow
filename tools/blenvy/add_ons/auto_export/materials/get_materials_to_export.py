
import bpy
from ....materials.materials_helpers import find_materials_not_on_disk

def get_materials_to_export(changes_per_material, changed_export_parameters, blueprints_data, settings):
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    blueprints_path_full = getattr(settings,"blueprints_path_full", "")
    materials_path_full = getattr(settings,"materials_path_full", "")

    change_detection = getattr(settings.auto_export, "change_detection")
    export_materials_library = getattr(settings.auto_export, "export_materials_library")
    collection_instances_combine_mode = getattr(settings.auto_export, "collection_instances_combine_mode")

    all_materials = bpy.data.materials
    local_materials = [material for material in all_materials if material.library is None]
    materials_to_export = []

    # print("export_materials_library", export_materials_library, "change detection", change_detection, "changed_export_parameters", changed_export_parameters)
    if export_materials_library and change_detection:
        if changed_export_parameters:
            materials_to_export = local_materials
        else :
            changed_materials = [bpy.data.materials[material_name] for material_name in list(changes_per_material.keys())]

            # first check if all materials have already been exported before (if this is the first time the exporter is run
            # in your current Blender session for example)
            materials_not_on_disk = find_materials_not_on_disk(local_materials, materials_path_full, export_gltf_extension)

            # also deal with blueprints that are always marked as "always_export"   
            #materials_always_export = [material for material in internal_materials if is_material_always_export(material)]
            materials_always_export = []
            materials_to_export =  list(set(changed_materials + materials_not_on_disk + materials_always_export))
    print("materials_to_export", materials_to_export, local_materials)
    return materials_to_export
