use bevy::{prelude::*, scene::SceneInstance};
use blenvy::{BluePrintBundle, BlueprintName, GameWorldTag, Library};
use std::path::Path;

use crate::{DynamicEntitiesRoot, SaveLoadConfig, StaticEntitiesRoot, StaticEntitiesStorage};

#[derive(Event)]
pub struct LoadingRequest {
    pub path: String,
}

#[derive(Event)]
pub struct LoadingFinished;

#[derive(Resource, Default)]
pub struct LoadRequested {
    pub path: String,
}

#[derive(Resource, Default)]
pub(crate) struct LoadFirstStageDone;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub(crate) struct CleanupScene;

/// helper system that "converts" loadRequest events to `LoadRequested` resources
pub(crate) fn mark_load_requested(
    mut load_requests: EventReader<LoadingRequest>,
    mut commands: Commands,
) {
    let mut save_path: String = "".into();
    for load_request in load_requests.read() {
        if !load_request.path.is_empty() {
            save_path.clone_from(&load_request.path);
        }
    }
    if !save_path.is_empty() {
        commands.insert_resource(LoadRequested { path: save_path });
    }
}

// TODO: replace with generic despawner ?
pub(crate) fn unload_world(mut commands: Commands, gameworlds: Query<Entity, With<GameWorldTag>>) {
    for e in gameworlds.iter() {
        info!("--loading: despawn old world/level");
        commands.entity(e).despawn_recursive();
    }
}

pub(crate) fn load_game(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    load_request: Res<LoadRequested>,
    save_load_config: Res<SaveLoadConfig>,
) {
    info!("--loading: load dynamic data");
    let save_path = load_request.path.clone();
    let save_path = Path::new(&save_load_config.save_path).join(Path::new(save_path.as_str()));

    info!("LOADING FROM {:?}", save_path);

    let world_root = commands
        .spawn((
            bevy::prelude::Name::from("world"),
            GameWorldTag,
            TransformBundle::default(),
            InheritedVisibility::default(),
        ))
        .id();

    // and we fill it with dynamic data
    // let input = std::fs::read(&path)?;
    let dynamic_data = commands
        .spawn((
            DynamicSceneBundle {
                scene: asset_server.load(save_path),
                ..default()
            },
            bevy::prelude::Name::from("dynamic"),
            DynamicEntitiesRoot,
        ))
        .id();

    // commands.entity(world_root).add_child(static_data);
    commands.entity(world_root).add_child(dynamic_data);

    commands.insert_resource(LoadFirstStageDone);

    info!("--loading: loaded dynamic data");
}

pub(crate) fn load_static(
    dynamic_worlds: Query<Entity, With<SceneInstance>>,
    world_root: Query<Entity, With<GameWorldTag>>,
    mut commands: Commands,
    mut loading_finished: EventWriter<LoadingFinished>,

    static_entities: Option<Res<StaticEntitiesStorage>>,
) {
    if let Some(info) = static_entities {
        info!("--loading static data {:?}", info.name);
        let static_data = commands
            .spawn((
                Name::from("static"),
                BluePrintBundle {
                    blueprint: BlueprintName(info.name.clone()),
                    ..Default::default()
                },
                StaticEntitiesRoot,
            ))
            .id();

        if !info.library_path.is_empty() {
            commands
                .entity(static_data)
                .insert(Library(info.library_path.clone().into()));
        }

        let world_root = world_root.get_single().unwrap();
        commands.entity(world_root).add_child(static_data);

        info!("--loading: loaded static data");
        for entity in dynamic_worlds.iter() {
            commands.entity(entity).insert(
                CleanupScene, // we mark this scene as needing a cleanup
            );
        }

        loading_finished.send(LoadingFinished);
    }
}

pub(crate) fn cleanup_loaded_scene(
    loaded_scenes: Query<
        Entity,
        (
            Added<CleanupScene>,
            With<SceneInstance>,
            With<DynamicEntitiesRoot>,
        ),
    >,
    mut commands: Commands,
) {
    for loaded_scene in loaded_scenes.iter() {
        info!("REMOVING DynamicScene");
        commands
            .entity(loaded_scene)
            .remove::<Handle<DynamicScene>>()
            .remove::<SceneInstance>()
            .remove::<CleanupScene>();

        commands.remove_resource::<LoadRequested>();
        commands.remove_resource::<LoadFirstStageDone>();
    }
}
