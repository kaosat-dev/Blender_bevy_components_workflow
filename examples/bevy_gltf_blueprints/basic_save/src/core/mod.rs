pub mod camera;
pub use camera::*;

pub mod lighting;
pub use lighting::*;

pub mod relationships;
pub use relationships::*;

pub mod physics;
pub use physics::*;

use bevy::{
    core_pipeline::tonemapping::Tonemapping,
    prelude::*,
    render::{camera::CameraRenderGraph, primitives::Frustum, view::VisibleEntities},
    utils::HashSet,
};
use bevy_rapier3d::dynamics::Velocity;
use std::any::TypeId;

use bevy_gltf_blueprints::*;
use bevy_gltf_save_load::*;

use crate::game::Pickable;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            LightingPlugin,
            CameraPlugin,
            PhysicsPlugin,
            SaveLoadPlugin {
                save_path: "scenes".into(),
                entity_filter: SceneFilter::Allowlist(HashSet::from([
                    TypeId::of::<Name>(),
                    TypeId::of::<Transform>(),
                    TypeId::of::<Velocity>(),
                    TypeId::of::<BlueprintName>(),
                    TypeId::of::<SpawnHere>(),
                    TypeId::of::<Dynamic>(),
                    TypeId::of::<InheritedVisibility>(),
                    TypeId::of::<Camera>(),
                    TypeId::of::<Camera3d>(),
                    TypeId::of::<Tonemapping>(),
                    TypeId::of::<CameraTrackingOffset>(),
                    TypeId::of::<Projection>(),
                    TypeId::of::<CameraRenderGraph>(),
                    TypeId::of::<Frustum>(),
                    TypeId::of::<GlobalTransform>(),
                    TypeId::of::<VisibleEntities>(),
                    TypeId::of::<Pickable>(),
                ])),
            },
            BlueprintsPlugin {
                library_folder: "models/library".into(),
                format: GltfFormat::GLB,
                aabbs: true,
                ..Default::default()
            },
        ));
    }
}
