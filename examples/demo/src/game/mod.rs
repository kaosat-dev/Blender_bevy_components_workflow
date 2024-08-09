pub mod in_game;
pub use in_game::*;

pub mod in_main_menu;
pub use in_main_menu::*;

pub mod level_transitions;
pub use level_transitions::*;

use bevy::prelude::*;
use bevy_gltf_worlflow_examples_common_rapier::{AppState, GameState};

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(LevelsPlugin)
            .add_systems(Update, (spawn_test).run_if(in_state(GameState::InGame)))
            .add_systems(OnEnter(AppState::MenuRunning), setup_main_menu)
            .add_systems(OnExit(AppState::MenuRunning), teardown_main_menu)
            .add_systems(Update, main_menu.run_if(in_state(AppState::MenuRunning)))
            .add_systems(OnEnter(AppState::AppRunning), setup_game);
    }
}
