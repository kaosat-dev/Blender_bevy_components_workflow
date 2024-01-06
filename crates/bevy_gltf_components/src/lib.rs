pub mod utils;
pub use utils::*;

pub mod gltf_to_components;
pub use gltf_to_components::*;

pub mod process_gltfs;
pub use process_gltfs::*;

use bevy::prelude::{App, IntoSystemConfigs, Plugin, SystemSet, Update};

/// A Bevy plugin for extracting components from gltf files and automatically adding them to the relevant entities
/// It will automatically run every time you load a gltf file
/// Add this plugin to your Bevy app to get access to this feature
/// ```
/// # use bevy::prelude::*;
/// # use bevy::gltf::*;
/// # use bevy_gltf_components::ComponentsFromGltfPlugin;
///
/// //too barebones of an example to be meaningfull, please see https://github.com/kaosat-dev/Blender_bevy_components_workflow/examples/basic for a real example
/// fn main() {
///    App::new()
///         .add_plugins(DefaultPlugins)
///         .add_plugins(ComponentsFromGltfPlugin)
///         .add_systems(Update, spawn_level)
///         .run();
/// }
///
/// fn spawn_level(
///   asset_server: Res<AssetServer>,
///   mut commands: bevy::prelude::Commands,
///   keycode: Res<Input<KeyCode>>,

/// ){
/// if keycode.just_pressed(KeyCode::Return) {
///  commands.spawn(SceneBundle {
///   scene: asset_server.load("basic/models/level1.glb#Scene0"),
///   transform: Transform::from_xyz(2.0, 0.0, -5.0),
/// ..Default::default()
/// });
/// }
///}
/// ```

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
/// systemset to order your systems after the component injection when needed
pub enum GltfComponentsSet {
    Injection,
}

#[derive(Default)]
pub struct ComponentsFromGltfPlugin;
impl Plugin for ComponentsFromGltfPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(GltfLoadingTracker::new())
            .add_systems(Update, (track_new_gltf, process_loaded_scenes))
            .add_systems(
                Update,
                (process_loaded_scenes).in_set(GltfComponentsSet::Injection),
            );
    }
}
