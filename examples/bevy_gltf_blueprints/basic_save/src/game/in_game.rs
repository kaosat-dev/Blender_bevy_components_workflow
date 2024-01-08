use bevy::prelude::*;
use bevy_gltf_save_load::{Dynamic, DynamicEntitiesRoot, StaticWorldMarker};

use crate::{
    assets::GameAssets,
    state::{GameState, InAppRunning},
};
use bevy_gltf_blueprints::{BluePrintBundle, BlueprintName, GameWorldTag, SpawnHere};

use bevy_rapier3d::prelude::Velocity;
use rand::Rng;

use super::Player;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct Flatten;

/*
commands.spawn((
    StaticStuff("world".into()),
    DynamicStuff("World_dynamic".into()),

    GameWorldTag,
    InAppRunning,

    TransformBundle::default()
));*/

pub fn setup_game(
    mut commands: Commands,
    game_assets: Res<GameAssets>,
    models: Res<Assets<bevy::gltf::Gltf>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    println!("INITIAL setting up all stuff");
    // here we actually spawn our game world/level
    /*SceneBundle {
        // note: because of this issue https://github.com/bevyengine/bevy/issues/10436, "world" is now a gltf file instead of a scene
        scene: models
            .get(game_assets.world.id())
            .expect("main level should have been loaded")
            .scenes[0]
            .clone(),
        ..default()
    },*/
    let world_root = commands
        .spawn((
            bevy::prelude::Name::from("world"),
            GameWorldTag,
            InAppRunning,
            TransformBundle::default(),
        ))
        .id();

    let static_data = commands
        .spawn((
            bevy::prelude::Name::from("static"),
            BluePrintBundle {
                blueprint: BlueprintName("World".to_string()),
                ..Default::default()
            },
            StaticWorldMarker("World".to_string()),
        ))
        .id();

    // and we fill it with dynamic data
    let dynamic_data = commands
        .spawn((
            bevy::prelude::Name::from("dynamic"),
            SceneBundle {
                scene: models
                    .get(game_assets.world_dynamic.id())
                    .expect("main level CONTENT should have been loaded")
                    .scenes[0]
                    .clone(),
                ..default()
            },
            /*BluePrintBundle {
                blueprint: BlueprintName("World_dynamic".to_string()),
                transform: TransformBundle::from_transform(Transform::from_xyz(0.0, 0.0, 0.0)),
                ..Default::default()
            },*/
            InAppRunning,
            DynamicEntitiesRoot,
            Flatten,
        ))
        .id();
    commands.entity(world_root).add_child(static_data);
    commands.entity(world_root).add_child(dynamic_data);

    next_game_state.set(GameState::InGame)
}

pub fn flatten_scene(
    matches: Query<(Entity, &Children), With<Flatten>>,
    all_children: Query<&Children>,
    mut commands: Commands,
    gameworld: Query<Entity, With<GameWorldTag>>,
) {
    for (original, children) in matches.iter() {
        let root_entity = children.first().unwrap();

        if let Ok(root_entity_children) = all_children.get(*root_entity) {
            for child in root_entity_children.iter() {
                // info!("copying child {:?} upward from {:?} to {:?}", names.get(*child), root_entity, original);
                // commands.entity(gameworld.get_single().unwrap()).add_child(*child);
                // commands.entity(*child).remove_parent_in_place();// .remove::<>();
                commands.entity(original).add_child(*child);

                // commands.entity(*root_entity).add_child(*child);
            }
        }
        // commands.entity(original).despawn();
        commands.entity(original).remove::<Flatten>();
        commands.entity(*root_entity).despawn();
    }
}

// TODO: Same as in load, reuse
pub fn unload_world(mut commands: Commands, gameworlds: Query<Entity, With<GameWorldTag>>) {
    for e in gameworlds.iter() {
        info!("--loading: despawn old world/level");
        commands.entity(e).despawn_recursive();
    }
}

pub fn should_reset(
    keycode: Res<Input<KeyCode>>,
    //save_requested_events: EventReader<SaveRequest>,
) -> bool {
    //return save_requested_events.len() > 0;

    return keycode.just_pressed(KeyCode::N);
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct UnregisteredComponent;

pub fn spawn_test(
    keycode: Res<Input<KeyCode>>,
    mut commands: Commands,

    mut game_world: Query<(Entity, &Children), With<DynamicEntitiesRoot>>,
) {
    if keycode.just_pressed(KeyCode::T) {
        let world = game_world.single_mut();
        let world = world.0; //.1[0];

        let mut rng = rand::thread_rng();
        let range = 5.5;
        let x: f32 = rng.gen_range(-range..range);
        let y: f32 = rng.gen_range(-range..range);

        let mut rng = rand::thread_rng();
        let range = 0.8;
        let vel_x: f32 = rng.gen_range(-range..range);
        let vel_y: f32 = rng.gen_range(2.0..2.5);
        let vel_z: f32 = rng.gen_range(-range..range);

        let name_index: u64 = rng.gen();

        let new_entity = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintName("Health_Pickup".to_string()),
                    transform: TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                    ..Default::default()
                },
                bevy::prelude::Name::from(format!("test{}", name_index)),
                // BlueprintName("Health_Pickup".to_string()),
                // SpawnHere,
                // TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                Velocity {
                    linvel: Vec3::new(vel_x, vel_y, vel_z),
                    angvel: Vec3::new(0.0, 0.0, 0.0),
                },
            ))
            .id();
        commands.entity(world).add_child(new_entity);
    }
}

pub fn spawn_test_unregisted_components(
    keycode: Res<Input<KeyCode>>,
    mut commands: Commands,

    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,
) {
    if keycode.just_pressed(KeyCode::U) {
        let world = game_world.single_mut();
        let world = world.1[0];

        let mut rng = rand::thread_rng();
        let range = 5.5;
        let x: f32 = rng.gen_range(-range..range);
        let y: f32 = rng.gen_range(-range..range);

        let mut rng = rand::thread_rng();
        let range = 0.8;
        let vel_x: f32 = rng.gen_range(-range..range);
        let vel_y: f32 = rng.gen_range(2.0..2.5);
        let vel_z: f32 = rng.gen_range(-range..range);

        let name_index: u64 = rng.gen();

        let new_entity = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintName("Health_Pickup".to_string()),
                    transform: TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                    ..Default::default()
                },
                bevy::prelude::Name::from(format!("test{}", name_index)),
                // BlueprintName("Health_Pickup".to_string()),
                // SpawnHere,
                // TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                Velocity {
                    linvel: Vec3::new(vel_x, vel_y, vel_z),
                    angvel: Vec3::new(0.0, 0.0, 0.0),
                },
                UnregisteredComponent,
            ))
            .id();
        commands.entity(world).add_child(new_entity);
    }
}

pub fn spawn_test_parenting(
    keycode: Res<Input<KeyCode>>,
    players: Query<Entity, With<Player>>,
    mut commands: Commands,

    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,

    mut names: Query<(Entity, &Name)>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    if keycode.just_pressed(KeyCode::P) {
        let world = game_world.single_mut();
        let world = world.1[0];

        let mut rng = rand::thread_rng();
        let range = 5.5;
        let x: f32 = rng.gen_range(-range..range);
        let y: f32 = rng.gen_range(-range..range);

        let mut rng = rand::thread_rng();
        let range = 0.8;
        let vel_x: f32 = rng.gen_range(-range..range);
        let vel_y: f32 = rng.gen_range(2.0..2.5);
        let vel_z: f32 = rng.gen_range(-range..range);

        let name_index: u64 = rng.gen();

        let child_test = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintName("Sphero".to_string()),
                    transform: TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                    ..Default::default()
                },
                bevy::prelude::Name::from(format!("SubParentingTest")),
                Dynamic(true),
            ))
            .id();

        /*let child_test = commands.spawn((
            PbrBundle {
                mesh: meshes.add(Mesh::from(shape::Cube { size: 1.0 })),
                material: materials.add(Color::rgb_u8(124, 144, 255).into()),
                transform: Transform::from_xyz(2.0, 0.0, 0.0),
                ..default()
            },
            bevy::prelude::Name::from(format!("SubParentingTest")),
        ))
        .id()
        ;*/

        let parenting_test_entity = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintName("Container".to_string()),
                    transform: TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                    ..Default::default()
                },
                bevy::prelude::Name::from(format!("ParentingTest")),
                Dynamic(true),
                // BlueprintName("Health_Pickup".to_string()),
                // SpawnHere,
                // TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
            ))
            .id();

        commands.entity(parenting_test_entity).add_child(child_test);

        for player in players.iter() {
            commands.entity(player).add_child(parenting_test_entity);
        }
        for (e, name) in names.iter() {
            if name.to_string() == "Player" {
                commands.entity(e).add_child(parenting_test_entity);
            }
        }
    }
}
