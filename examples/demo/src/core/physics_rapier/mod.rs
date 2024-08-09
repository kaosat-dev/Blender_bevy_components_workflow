pub(crate) mod physics_replace_proxies;
pub(crate) use physics_replace_proxies::*;

pub(crate) mod utils;

pub(crate) mod controls;
pub(crate) use controls::*;

use bevy::prelude::*;
use blenvy::GltfBlueprintsSet;
use bevy_gltf_worlflow_examples_common::state::GameState;
use bevy_rapier3d::{
    prelude::{NoUserData, RapierPhysicsPlugin},
    render::RapierDebugRenderPlugin,
};

pub(crate) fn plugin(app: &mut App) {
    app.add_plugins((
        RapierPhysicsPlugin::<NoUserData>::default(),
        RapierDebugRenderPlugin::default(),
    ))
    .register_type::<AutoAABBCollider>()
    .register_type::<physics_replace_proxies::Collider>()
    .add_systems(
        Update,
        physics_replace_proxies.after(GltfBlueprintsSet::AfterSpawn),
    )
    .add_systems(Update, toggle_physics_debug)
    .add_systems(OnEnter(GameState::InGame), resume_physics)
    .add_systems(OnExit(GameState::InGame), pause_physics);
}
