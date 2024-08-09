use bevy::prelude::*;
// use bevy_gltf_worlflow_examples_common::CommonPlugin;
mod state;
use state::*;

mod core;
use crate::core::*;

mod game;
use game::*;

mod dupe_components;
mod test_components;
use test_components::*;

mod hierarchy_debug;
use hierarchy_debug::*;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins.set(AssetPlugin::default()),
            HiearchyDebugPlugin,
            // our custom plugins
            // CommonPlugin,
            StatePlugin,
            CorePlugin,           // reusable plugins
            GamePlugin,           // specific to our game
            ComponentsTestPlugin, // Showcases different type of components /structs
        ))
        .run();
}
