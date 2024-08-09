use bevy::prelude::*;
use blenvy::{BluePrintBundle, BlueprintName, GameWorldTag, Library, NoInBlueprint};
use blenvy::{Dynamic, DynamicEntitiesRoot, StaticEntitiesRoot};
use bevy_gltf_worlflow_examples_common_rapier::{GameState, InAppRunning, Player};
use bevy_rapier3d::prelude::Velocity;
use rand::Rng;

pub fn setup_game(mut commands: Commands, mut next_game_state: ResMut<NextState<GameState>>) {
    info!("setting up game world");
    // here we actually spawn our game world/level
    let world_root = commands
        .spawn((
            Name::from("world"),
            GameWorldTag,
            InAppRunning,
            TransformBundle::default(),
            InheritedVisibility::default(),
            //StaticEntities("World"),
            //DynamicEntities("World_dynamic")
        ))
        .id();

    // and we fill it with static entities
    let static_data = commands
        .spawn((
            Name::from("static"),
            BluePrintBundle {
                blueprint: BlueprintName("World".to_string()),
                ..Default::default()
            },
            StaticEntitiesRoot,
            Library("models".into()),
        ))
        .id();

    // and we fill it with dynamic entities
    let dynamic_data = commands
        .spawn((
            Name::from("dynamic"),
            BluePrintBundle {
                blueprint: BlueprintName("World_dynamic".to_string()),
                ..Default::default()
            },
            DynamicEntitiesRoot,
            NoInBlueprint, // we do not want the descendants of this entity to be filtered out when saving
            Library("models".into()),
        ))
        .id();
    commands.entity(world_root).add_child(static_data);
    commands.entity(world_root).add_child(dynamic_data);

    next_game_state.set(GameState::InGame)
}

// TODO: Same as in load, reuse
pub fn unload_world(mut commands: Commands, gameworlds: Query<Entity, With<GameWorldTag>>) {
    for e in gameworlds.iter() {
        info!("--loading: despawn old world/level");
        commands.entity(e).despawn_recursive();
    }
}

pub fn should_reset(keycode: Res<ButtonInput<KeyCode>>) -> bool {
    keycode.just_pressed(KeyCode::KeyN)
}

pub fn spawn_test(
    keycode: Res<ButtonInput<KeyCode>>,
    mut dynamic_entities_world: Query<Entity, With<DynamicEntitiesRoot>>,
    mut commands: Commands,
) {
    if keycode.just_pressed(KeyCode::KeyT) {
        let world = dynamic_entities_world.single_mut();

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
                    ..Default::default()
                },
                // AddToGameWorld, // automatically added to entity (should be only one) that has the GameWorldTag
                bevy::prelude::Name::from(format!("test{}", name_index)),
                TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                Velocity {
                    linvel: Vec3::new(vel_x, vel_y, vel_z),
                    angvel: Vec3::new(0.0, 0.0, 0.0),
                },
            ))
            .id();
        commands.entity(world).add_child(new_entity);
    }
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct UnregisteredComponent;

pub fn spawn_test_unregisted_components(
    keycode: Res<ButtonInput<KeyCode>>,
    mut commands: Commands,

    mut dynamic_entities_world: Query<Entity, With<DynamicEntitiesRoot>>,
) {
    if keycode.just_pressed(KeyCode::KeyU) {
        let world = dynamic_entities_world.single_mut();

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
                    ..Default::default()
                },
                bevy::prelude::Name::from(format!("test{}", name_index)),
                // BlueprintName("Health_Pickup".to_string()),
                // SpawnHere,
                TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
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
    keycode: Res<ButtonInput<KeyCode>>,
    players: Query<Entity, With<Player>>,
    mut commands: Commands,

    names: Query<(Entity, &Name)>,
) {
    if keycode.just_pressed(KeyCode::KeyP) {
        let mut rng = rand::thread_rng();
        let range = 5.5;
        let x: f32 = rng.gen_range(-range..range);
        let y: f32 = rng.gen_range(-range..range);

        let child_test = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintName("Sphero".to_string()),
                    ..Default::default()
                },
                bevy::prelude::Name::from("SubParentingTest".to_string()),
                TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                Dynamic(true),
            ))
            .id();

        let parenting_test_entity = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintName("Container".into()),
                    ..Default::default()
                },
                bevy::prelude::Name::from("ParentingTest".to_string()),
                Dynamic(true),
                TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
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
