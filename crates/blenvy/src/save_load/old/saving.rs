use bevy::prelude::*;
use bevy::tasks::IoTaskPool;
use blenvy::{BlueprintName, InBlueprint, Library, SpawnHere};

use std::fs::File;
use std::io::Write;
use std::path::Path;

use crate::{DynamicEntitiesRoot, SaveLoadConfig, StaticEntitiesRoot};

#[derive(Event, Debug)]
pub struct SavingRequest {
    pub path: String,
}

#[derive(Event)]
pub struct SavingFinished;

pub fn should_save(save_requests: EventReader<SavingRequest>) -> bool {
    !save_requests.is_empty()
}

#[derive(Resource, Clone, Debug, Default, Reflect)]
#[reflect(Resource)]
pub struct StaticEntitiesStorage {
    pub name: String,
    pub library_path: String,
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// marker component for entities that do not have parents, or whose parents should be ignored when serializing
pub(crate) struct RootEntity;

#[derive(Component, Debug)]
/// internal helper component to store parents before resetting them
pub(crate) struct OriginalParent(pub(crate) Entity);

// any child of dynamic/ saveable entities that is not saveable itself should be removed from the list of children
pub(crate) fn prepare_save_game(
    saveables: Query<Entity, (With<Dynamic>, With<BlueprintName>)>,
    root_entities: Query<Entity, Or<(With<DynamicEntitiesRoot>, Without<Parent>)>>, //  With<DynamicEntitiesRoot>
    dynamic_entities: Query<(Entity, &Parent, Option<&Children>), With<Dynamic>>,
    static_entities: Query<(Entity, &BlueprintName, Option<&Library>), With<StaticEntitiesRoot>>,

    mut commands: Commands,
) {
    for entity in saveables.iter() {
        commands.entity(entity).insert(SpawnHere);
    }

    for (entity, parent, children) in dynamic_entities.iter() {
        let parent = parent.get();
        if root_entities.contains(parent) {
            commands.entity(entity).insert(RootEntity);
        }

        if let Some(children) = children {
            for sub_child in children.iter() {
                if !dynamic_entities.contains(*sub_child) {
                    commands.entity(*sub_child).insert(OriginalParent(entity));
                    commands.entity(entity).remove_children(&[*sub_child]);
                }
            }
        }
    }
    for (_, blueprint_name, library) in static_entities.iter() {
        let library_path: String = library.map_or_else(|| "", |l| l.0.to_str().unwrap()).into();
        commands.insert_resource(StaticEntitiesStorage {
            name: blueprint_name.0.clone(),
            library_path,
        });
    }
}

pub(crate) fn save_game(world: &mut World) {
    info!("saving");

    let mut save_path: String = "".into();
    let mut events = world.resource_mut::<Events<SavingRequest>>();

    for event in events.get_reader().read(&events) {
        info!("SAVE EVENT !! {:?}", event);
        save_path.clone_from(&event.path);
    }
    events.clear();

    let saveable_entities: Vec<Entity> = world
        .query_filtered::<Entity, (With<Dynamic>, Without<InBlueprint>, Without<RootEntity>)>()
        .iter(world)
        .collect();

    let saveable_root_entities: Vec<Entity> = world
        .query_filtered::<Entity, (With<Dynamic>, Without<InBlueprint>, With<RootEntity>)>()
        .iter(world)
        .collect();

    info!("saveable entities {}", saveable_entities.len());
    info!("saveable root entities {}", saveable_root_entities.len());

    let save_load_config = world
        .get_resource::<SaveLoadConfig>()
        .expect("SaveLoadConfig should exist at this stage");

    // we hardcode some of the always allowed types
    let filter = save_load_config
        .component_filter
        .clone()
        .allow::<Parent>()
        .allow::<Children>()
        .allow::<BlueprintName>()
        .allow::<SpawnHere>()
        .allow::<Dynamic>()
        

        ;

    // for root entities, it is the same EXCEPT we make sure parents are not included
    let filter_root = filter.clone().deny::<Parent>();

    let filter_resources = save_load_config
        .resource_filter
        .clone()
        .allow::<StaticEntitiesStorage>()
        ;

    // for default stuff
    let scene_builder = DynamicSceneBuilder::from_world(world)
        .with_filter(filter.clone())
        .with_resource_filter(filter_resources.clone());

    let mut dyn_scene = scene_builder
        .extract_resources()
        .extract_entities(saveable_entities.clone().into_iter())
        .remove_empty_entities()
        .build();

    // for root entities
    let scene_builder_root = DynamicSceneBuilder::from_world(world)
        .with_filter(filter_root.clone())
        .with_resource_filter(filter_resources.clone());

    // FIXME : add back
    let mut dyn_scene_root = scene_builder_root
        .extract_resources()
        .extract_entities(
            saveable_root_entities.clone().into_iter(), // .chain(static_world_markers.into_iter()),
        )
        .remove_empty_entities()
        .build();

    dyn_scene.entities.append(&mut dyn_scene_root.entities);
    // dyn_scene.resources.append(&mut dyn_scene_root.resources);

    let serialized_scene = dyn_scene
        .serialize(&world.resource::<AppTypeRegistry>().read())
        .unwrap();

    let save_path = Path::new("assets")
        .join(&save_load_config.save_path)
        .join(Path::new(save_path.as_str())); // Path::new(&save_load_config.save_path).join(Path::new(save_path.as_str()));
    info!("saving game to {:?}", save_path);

    // world.send_event(SavingFinished);

    #[cfg(not(target_arch = "wasm32"))]
    IoTaskPool::get()
        .spawn(async move {
            // Write the scene RON data to file
            File::create(save_path)
                .and_then(|mut file| file.write(serialized_scene.as_bytes()))
                .expect("Error while writing save to file");
        })
        .detach();
}

pub(crate) fn cleanup_save(
    needs_parent_reset: Query<(Entity, &OriginalParent)>,
    mut saving_finished: EventWriter<SavingFinished>,
    mut commands: Commands,
) {
    for (entity, original_parent) in needs_parent_reset.iter() {
        commands.entity(original_parent.0).add_child(entity);
    }
    commands.remove_resource::<StaticEntitiesStorage>();
    saving_finished.send(SavingFinished);
}
/*
pub(crate) fn cleanup_save(mut world: &mut World) {

    let mut query = world.query::<(Entity, &OriginalParent)>();
    for (mut entity, original_parent) in query.iter_mut(&mut world) {
        let e = world.entity_mut(original_parent.0);
        // .add_child(entity);
    }
}*/
