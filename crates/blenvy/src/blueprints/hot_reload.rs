use crate::{
    BlueprintAssetsLoadState, BlueprintAssetsLoaded, BlueprintInfo, BlueprintInstanceReady,
    BlueprintSpawning, FromBlueprint, SpawnBlueprint, SubBlueprintsSpawnTracker,
};
use bevy::asset::AssetEvent;
use bevy::prelude::*;
use bevy::scene::SceneInstance;
use bevy::utils::hashbrown::HashMap;

/// Resource mapping asset paths (ideally untyped ids, but more complex) to a list of blueprint instance entity ids
#[derive(Debug, Clone, Resource, Default)]
pub(crate) struct AssetToBlueprintInstancesMapper {
    // pub(crate) untyped_id_to_blueprint_entity_ids: HashMap<UntypedAssetId, Vec<Entity>>
    pub(crate) untyped_id_to_blueprint_entity_ids: HashMap<String, Vec<Entity>>,
}

pub(crate) fn react_to_asset_changes(
    mut gltf_events: EventReader<AssetEvent<Gltf>>, // FIXME: Problem: we need to react to any asset change, not just gltf files !
    // mut untyped_events: EventReader<AssetEvent<LoadedUntypedAsset>>,
    blueprint_assets: Query<(Entity, Option<&Name>, &BlueprintInfo, Option<&Children>)>,
    blueprint_children_entities: Query<&FromBlueprint>, //=> can only be used if the entites are tagged
    assets_to_blueprint_instances: Res<AssetToBlueprintInstancesMapper>,
    all_parents: Query<&Parent>,
    spawning_blueprints: Query<&BlueprintSpawning>,

    asset_server: Res<AssetServer>,
    mut commands: Commands,
) {
    let mut respawn_candidates: Vec<&Entity> = vec![];

    for event in gltf_events.read() {
        // LoadedUntypedAsset
        match event {
            AssetEvent::Modified { id } => {
                // React to the gltf file being modified
                // println!("Modified gltf {:?}", asset_server.get_path(*id));
                if let Some(asset_path) = asset_server.get_path(*id) {
                    // let untyped = asset_server.get_handle_untyped(asset_path.clone());
                    // println!("matching untyped handle {:?}", untyped);
                    // let bla = untyped.unwrap().id();
                    // asset_server.get
                    // in order to avoid respawn both a parent & a child , which would crash Bevy, we do things in two steps
                    if let Some(entities) = assets_to_blueprint_instances
                        .untyped_id_to_blueprint_entity_ids
                        .get(&asset_path.to_string())
                    {
                        for entity in entities.iter() {
                            // println!("matching blueprint instance {}", entity);
                            // disregard entities that are already (re) spawning
                            if !respawn_candidates.contains(&entity)
                                && blueprint_assets.get(*entity).is_ok()
                                && spawning_blueprints.get(*entity).is_err()
                            {
                                respawn_candidates.push(entity);
                            }
                        }
                    }
                }
            }
            _ => {}
        }
    }
    // we process all candidates here to deal with the case where multiple assets have changed in a single frame, which could cause respawn chaos
    // now find hierarchy of changes and only set the uppermost parent up for respawning
    // TODO: improve this, very inneficient
    let mut retained_candidates: Vec<Entity> = vec![];
    'outer: for entity in respawn_candidates.iter() {
        for parent in all_parents.iter_ancestors(**entity) {
            for ent in respawn_candidates.iter() {
                if **ent == parent {
                    if !retained_candidates.contains(&parent) {
                        retained_candidates.push(parent);
                    }
                    continue 'outer;
                }
            }
        }
        if !retained_candidates.contains(entity) {
            retained_candidates.push(**entity);
        }
    }
    // println!("respawn candidates {:?}", respawn_candidates);
    for retained in retained_candidates.iter() {
        // println!("retained {}", retained);

        if let Ok((entity, entity_name, _blueprint_info, children)) =
            blueprint_assets.get(*retained)
        {
            info!("Change detected !!, now respawn {:?}", entity_name);

            // TODO: only remove those that are "in blueprint"
            if children.is_some() {
                for child in children.unwrap().iter() {
                    commands.entity(*child).despawn_recursive();
                }
            }
            commands
                .entity(entity)
                .remove::<BlueprintInstanceReady>()
                .remove::<BlueprintAssetsLoaded>()
                .remove::<SceneInstance>()
                .remove::<BlueprintAssetsLoadState>()
                .remove::<SubBlueprintsSpawnTracker>()
                .insert(SpawnBlueprint);
        }
    }

    // println!("done with asset updates");
}
