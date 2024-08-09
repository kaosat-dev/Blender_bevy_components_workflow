pub mod in_game;
use bevy_gltf_worlflow_examples_common_rapier::{AppState, GameState};
pub use in_game::*;

pub mod in_main_menu;
pub use in_main_menu::*;

pub mod in_game_loading;
pub use in_game_loading::*;

pub mod in_game_saving;
pub use in_game_saving::*;

use bevy::prelude::*;
use blenvy::{LoadRequest, LoadingFinished, SavingRequest, SavingFinished};

pub fn request_save(
    mut save_requests: EventWriter<SavingRequest>,
    keycode: Res<ButtonInput<KeyCode>>,

    current_state: Res<State<GameState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    if keycode.just_pressed(KeyCode::KeyS)
        && (current_state.get() != &GameState::InLoading)
        && (current_state.get() != &GameState::InSaving)
    {
        next_game_state.set(GameState::InSaving);
        save_requests.send(SavingRequest {
            path: "save.scn.ron".into(),
        });
    }
}

pub fn on_saving_finished(
    mut saving_finished: EventReader<SavingFinished>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    for _ in saving_finished.read() {
        next_game_state.set(GameState::InGame);
    }
}

pub fn request_load(
    mut load_requests: EventWriter<LoadRequest>,
    keycode: Res<ButtonInput<KeyCode>>,
    current_state: Res<State<GameState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    if keycode.just_pressed(KeyCode::KeyL)
        && (current_state.get() != &GameState::InLoading)
        && (current_state.get() != &GameState::InSaving)
    {
        next_game_state.set(GameState::InLoading);
        load_requests.send(LoadRequest {
            path: "save.scn.ron".into(),
        });
    }
}

pub fn on_loading_finished(
    mut loading_finished: EventReader<LoadingFinished>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    for _ in loading_finished.read() {
        next_game_state.set(GameState::InGame);
    }
}

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(
            Update,
            (
                spawn_test,
                spawn_test_unregisted_components,
                spawn_test_parenting,
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
        .add_systems(
            Update,
            (
                request_save,
                request_load,
                on_saving_finished,
                on_loading_finished,
            ),
        )
        .add_systems(OnEnter(AppState::MenuRunning), setup_main_menu)
        .add_systems(OnExit(AppState::MenuRunning), teardown_main_menu)
        .add_systems(Update, main_menu.run_if(in_state(AppState::MenuRunning)))
        .add_systems(OnEnter(GameState::InLoading), setup_loading_screen)
        .add_systems(OnExit(GameState::InLoading), teardown_loading_screen)
        .add_systems(OnEnter(GameState::InSaving), setup_saving_screen)
        .add_systems(OnExit(GameState::InSaving), teardown_saving_screen)
        .add_systems(OnEnter(AppState::AppRunning), setup_game);
    }
}
