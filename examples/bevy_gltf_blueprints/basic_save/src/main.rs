use bevy::prelude::*;
use bevy_editor_pls::prelude::*;

mod core;
use crate::core::*;

pub mod assets;
use assets::*;

pub mod state;
use state::*;

mod game;
use game::*;

mod test_components;
use test_components::*;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins.set(AssetPlugin::default()),
            // editor
            EditorPlugin::default(),
            // our custom plugins
            StatePlugin,
            AssetsPlugin,
            CorePlugin,           // reusable plugins
            GamePlugin,           // specific to our game
            ComponentsTestPlugin, // Showcases different type of components /structs
        ))
        .run();
}
