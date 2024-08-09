use crate::{GameState, InAppRunning};
use bevy::prelude::*;
use blenvy::{
    AddToGameWorld, BluePrintBundle, BlueprintInfo, DynamicBlueprintInstance, GameWorldTag,
    HideUntilReady, SpawnBlueprint,
};

//use bevy_rapier3d::prelude::Velocity;
use rand::Rng;

pub fn setup_game(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    // here we actually spawn our game world/level
    commands.spawn((
        BlueprintInfo::from_path("levels/World.glb"),
        HideUntilReady,
        SpawnBlueprint,
        GameWorldTag,
        InAppRunning,
    ));

    next_game_state.set(GameState::InGame)
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct UnregisteredComponent;

pub fn spawn_test(
    keycode: Res<ButtonInput<KeyCode>>,
    mut commands: Commands,

    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,
) {
    if keycode.just_pressed(KeyCode::KeyS) {
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
                    blueprint: BlueprintInfo {
                        name: "spawned".into(),
                        path: "blueprints/Blueprint 3.gltf".into(),
                    }, // FIXME
                    ..Default::default()
                },
                DynamicBlueprintInstance,
                bevy::prelude::Name::from(format!("test{}", name_index)),
                HideUntilReady,
                AddToGameWorld,
                TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                /*Velocity {
                    linvel: Vec3::new(vel_x, vel_y, vel_z),
                    angvel: Vec3::new(0.0, 0.0, 0.0),
                },*/
            ))
            .id();
        //commands.entity(world).add_child(new_entity);
    }
}
