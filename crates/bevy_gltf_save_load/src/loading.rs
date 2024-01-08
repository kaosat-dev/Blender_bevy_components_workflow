use std::path::Path;

use bevy::{prelude::*, scene::SceneInstance};
use bevy_gltf_blueprints::{BluePrintBundle, BlueprintName, GameWorldTag};

use crate::{DynamicEntitiesRoot, StaticWorldMarker};

use super::{Dynamic, SaveLoadConfig};

#[derive(Event)]
pub struct LoadRequest {
    pub path: String,
}

#[derive(Event)]
pub struct LoadingFinished;

#[derive(Resource, Default)]
pub struct LoadRequested {
    pub path: String,
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct CleanupScene;

pub fn should_load(mut load_requests: EventReader<LoadRequest>) -> bool {
    // return load_requests.len() > 0;
    let mut valid = false;
    for load_request in load_requests.read() {
        if load_request.path != "" {
            valid = true;
            break;
        }
    }
    return valid;
}

pub fn unload_world(mut commands: Commands, gameworlds: Query<Entity, With<GameWorldTag>>) {
    for e in gameworlds.iter() {
        info!("--loading: despawn old world/level");
        commands.entity(e).despawn_recursive();
    }
}

pub fn load_game(
    mut commands: Commands,
    models: Res<Assets<bevy::gltf::Gltf>>,
    asset_server: Res<AssetServer>,
    // load_request: Res<LoadRequested>,
    mut load_requests: EventReader<LoadRequest>,
    save_load_config: Res<SaveLoadConfig>,
) {
    info!("--loading: load dynamic data");
    //let save_path = load_request.path.clone();
    let mut save_path: String = "".into();
    for load_request in load_requests.read() {
        if load_request.path != "" {
            save_path = load_request.path.clone();
        }
    }

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
    let scene_data = asset_server.load(save_path);
    // let input = std::fs::read(&path)?;

    let dynamic_data = commands
        .spawn((
            DynamicSceneBundle {
                // Scenes are loaded just like any other asset.
                scene: scene_data,
                ..default()
            },
            bevy::prelude::Name::from("dynamic"),
            DynamicEntitiesRoot,
            CleanupScene, // we mark this scene as needing a cleanup
        ))
        .id();

    // commands.entity(world_root).add_child(static_data);
    commands.entity(world_root).add_child(dynamic_data);

    info!("--loading: loaded saved scene");
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct TestMarker;

pub fn load_static(
    foo: Query<(Entity, &StaticWorldMarker), (Added<StaticWorldMarker>)>,
    world_root: Query<(Entity), With<GameWorldTag>>,
    mut commands: Commands,
    mut loading_finished: EventWriter<LoadingFinished>,
) {
    for (entity, marker) in foo.iter() {
        println!("gna gna gna {:?}", marker.0);

        let static_data = commands
            .spawn((
                bevy::prelude::Name::from("static"),
                BluePrintBundle {
                    blueprint: BlueprintName(marker.0.clone()),
                    ..Default::default()
                },
            ))
            .id();

        let world_root = world_root.get_single().unwrap();
        println!("root {:?}", world_root);
        commands.entity(world_root).add_child(static_data);
        info!("load static");
        loading_finished.send(LoadingFinished);
        break;
    }
}
/*
pub fn re_create_hierarchies(
    with_parents: Query<(Entity, &Parent), (Added<Parent>, With<Dynamic>)>,
    all_children: Query<(Entity, &Children)>,
    mut commands: Commands,
) {
    for (e, parent) in with_parents.iter(){
        println!("re-create hierarchy");
        if !all_children.contains(parent.get()){
            commands.entity(parent.get()).add_child(e);
        }
    }
}*/

pub fn cleanup_loaded_scene(
    loaded_scenes: Query<
        Entity,
        (
            With<CleanupScene>,
            Added<SceneInstance>,
            With<DynamicEntitiesRoot>,
        ),
    >,
    mut commands: Commands,
) {
    for loaded_scene in loaded_scenes.iter() {
        info!("REMOVING SCENE");
        commands
            .entity(loaded_scene)
            .remove::<Handle<DynamicScene>>()
            .remove::<SceneInstance>()
            .remove::<CleanupScene>();
    }
}
