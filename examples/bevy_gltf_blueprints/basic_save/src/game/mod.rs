pub mod in_game;
use bevy_gltf_save_load::{LoadRequest, LoadingFinished, SaveRequest};
pub use in_game::*;

pub mod in_main_menu;
pub use in_main_menu::*;

pub mod picking;
pub use picking::*;

use crate::{
    insert_dependant_component,
    state::{AppState, GameState},
};
use bevy::prelude::*;
use bevy_rapier3d::prelude::*;

// this file is just for demo purposes, contains various types of components, systems etc

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum SoundMaterial {
    Metal,
    Wood,
    Rock,
    Cloth,
    Squishy,
    #[default]
    None,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Player;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo component showing auto injection of components
pub struct ShouldBeWithPlayer;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Interactible;

fn player_move_demo(
    keycode: Res<Input<KeyCode>>,
    mut players: Query<&mut Transform, With<Player>>,
) {
    let speed = 0.2;
    if let Ok(mut player) = players.get_single_mut() {
        if keycode.pressed(KeyCode::Left) {
            player.translation.x += speed;
        }
        if keycode.pressed(KeyCode::Right) {
            player.translation.x -= speed;
        }

        if keycode.pressed(KeyCode::Up) {
            player.translation.z += speed;
        }
        if keycode.pressed(KeyCode::Down) {
            player.translation.z -= speed;
        }
    }
}

// collision tests/debug
pub fn test_collision_events(
    mut collision_events: EventReader<CollisionEvent>,
    mut contact_force_events: EventReader<ContactForceEvent>,
) {
    for collision_event in collision_events.read() {
        println!("collision");
        match collision_event {
            CollisionEvent::Started(_entity1, _entity2, _) => {
                println!("collision started")
            }
            CollisionEvent::Stopped(_entity1, _entity2, _) => {
                println!("collision ended")
            }
        }
    }

    for contact_force_event in contact_force_events.read() {
        println!("Received contact force event: {:?}", contact_force_event);
    }
}

pub fn request_save(mut save_requests: EventWriter<SaveRequest>, keycode: Res<Input<KeyCode>>) {
    if keycode.just_pressed(KeyCode::S) {
        save_requests.send(SaveRequest {
            path: "save.scn.ron".into(),
        })
    }
}

pub fn request_load(
    mut load_requests: EventWriter<LoadRequest>,
    keycode: Res<Input<KeyCode>>,

    mut next_app_state: ResMut<NextState<AppState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    if keycode.just_pressed(KeyCode::L) {
        println!("request to load");
        // next_app_state.set(AppState::LoadingGame);
        next_game_state.set(GameState::None);
        load_requests.send(LoadRequest {
            path: "save.scn.ron".into(),
        })
    }
}

pub fn on_loading_finished(
    mut loading_finished: EventReader<LoadingFinished>,
    mut next_app_state: ResMut<NextState<AppState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    for _ in loading_finished.read() {
        println!("loading finished, changing state");
        //next_app_state.set(AppState::AppRunning);
        next_game_state.set(GameState::InGame);
    }
}

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(PickingPlugin)
            .register_type::<Interactible>()
            .register_type::<SoundMaterial>()
            .register_type::<Player>()
            // little helper utility, to automatically inject components that are dependant on an other component
            // ie, here an Entity with a Player component should also always have a ShouldBeWithPlayer component
            // you get a warning if you use this, as I consider this to be stop-gap solution (usually you should have either a bundle, or directly define all needed components)
            .add_systems(
                Update,
                (
                    // insert_dependant_component::<Player, ShouldBeWithPlayer>,
                    player_move_demo, //.run_if(in_state(AppState::Running)),
                    // test_collision_events
                    spawn_test,
                    spawn_test_unregisted_components,
                    spawn_test_parenting,
                    flatten_scene,
                )
                    .run_if(in_state(GameState::InGame)),
            )
            .add_systems(
                Update,
                (unload_world, apply_deferred, setup_game)
                    .chain()
                    .run_if(should_reset)
                    .run_if(in_state(AppState::AppRunning)),
            )
            .add_systems(Update, (request_save, request_load, on_loading_finished))
            .add_systems(OnEnter(AppState::MenuRunning), setup_main_menu)
            .add_systems(OnExit(AppState::MenuRunning), teardown_main_menu)
            .add_systems(Update, main_menu.run_if(in_state(AppState::MenuRunning)))
            .add_systems(OnEnter(AppState::AppRunning), setup_game);
    }
}
