
from ....blueprints.blueprint_helpers  import find_blueprints_not_on_disk

def is_blueprint_always_export(blueprint):
    return blueprint.collection['always_export'] if 'always_export' in blueprint.collection else False

# this also takes the split/embed mode into account: if a nested collection changes AND embed is active, its container collection should also be exported
def get_blueprints_to_export(changes_per_scene, changes_per_collection, changed_export_parameters, blueprints_data, settings):
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    blueprints_path_full = getattr(settings,"blueprints_path_full", "")
    change_detection = getattr(settings.auto_export, "change_detection")
    collection_instances_combine_mode = getattr(settings.auto_export, "collection_instances_combine_mode")

    internal_blueprints = blueprints_data.internal_blueprints
    blueprints_to_export = internal_blueprints # just for clarity

    # print("change_detection", change_detection, "changed_export_parameters", changed_export_parameters, "changes_per_scene", changes_per_scene)
    
    # if the export parameters have changed, bail out early
    # we need to re_export everything if the export parameters have been changed
    if change_detection and not changed_export_parameters:
        changed_blueprints = []

        # first check if all collections have already been exported before (if this is the first time the exporter is run
        # in your current Blender session for example)
        blueprints_not_on_disk = find_blueprints_not_on_disk(internal_blueprints, blueprints_path_full, export_gltf_extension)

        for scene in settings.library_scenes:
            if scene.name in changes_per_scene:
                changed_objects = list(changes_per_scene[scene.name].keys())
                changed_blueprints = [blueprints_data.blueprints_from_objects[changed] for changed in changed_objects if changed in blueprints_data.blueprints_from_objects]
                # we only care about local blueprints/collections
                changed_local_blueprints = [blueprint for blueprint in changed_blueprints if blueprint.name in blueprints_data.blueprints_per_name.keys() and blueprint.local]
                # FIXME: double check this: why are we combining these two ?
                changed_blueprints += changed_local_blueprints

        # also deal with blueprints that are always marked as "always_export"
        blueprints_always_export = [blueprint for blueprint in internal_blueprints if is_blueprint_always_export(blueprint)]
        changed_blueprints_based_on_changed_collections = [blueprint for blueprint in internal_blueprints if blueprint.collection in changes_per_collection.values()]

        blueprints_to_export =  list(set(changed_blueprints + blueprints_not_on_disk + blueprints_always_export + changed_blueprints_based_on_changed_collections))


    # filter out blueprints that are not marked & deal with the different combine modes
    # we check for blueprint & object specific overrides ...
    filtered_blueprints = []
    for blueprint in blueprints_to_export:
        if blueprint.marked:
            filtered_blueprints.append(blueprint)
        else:
            blueprint_instances = blueprints_data.internal_collection_instances.get(blueprint.name, [])
            # print("INSTANCES", blueprint_instances, blueprints_data.internal_collection_instances)
            # marked blueprints that have changed are always exported, regardless of whether they are in use (have instances) or not 
            for blueprint_instance in blueprint_instances:
                combine_mode = blueprint_instance['_combine'] if '_combine' in blueprint_instance else collection_instances_combine_mode
                if combine_mode == "Split": # we only keep changed blueprints if mode is set to split for at least one instance (aka if ALL instances of a blueprint are merged, do not export ? )  
                    filtered_blueprints.append(blueprint)

        blueprints_to_export =  list(set(filtered_blueprints))

    
    # changed/all blueprints to export     
    return (blueprints_to_export)