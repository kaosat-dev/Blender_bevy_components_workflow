use bevy::prelude::*;

#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash, Default, States)]
pub enum AppState {
    CoreLoading,
    #[default]
    MenuRunning,
    AppLoading,
    AppRunning,
    AppEnding,
}

#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash, Default, States)]
pub enum GameState {
    #[default]
    None,

    InMenu,
    InGame,

    InGameOver,

    InSaving,
    InLoading,
}

// tag components for all entities within a certain state (for despawning them if needed) , FIXME: seems kinda hack-ish
#[derive(Component)]
pub struct InCoreLoading;
#[derive(Component, Default)]
pub struct InMenuRunning;
#[derive(Component)]

pub struct InAppRunning;

// components for tagging in game vs in game menu stuff
#[derive(Component, Default)]
pub struct InMainMenu;

#[derive(Component, Default)]
pub struct InMenu;

#[derive(Component, Default)]
pub struct InGame;

#[derive(Component, Default)]
pub struct InGameSaving;

#[derive(Component, Default)]
pub struct InGameLoading;

pub struct StatePlugin;
impl Plugin for StatePlugin {
    fn build(&self, app: &mut App) {
        app.init_state::<AppState>().init_state::<GameState>();
    }
}
