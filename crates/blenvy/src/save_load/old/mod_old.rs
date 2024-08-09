pub mod saveable;
use std::path::PathBuf;

pub use saveable::*;

pub mod saving;
pub use saving::*;

pub mod loading;
pub use loading::*;

use bevy::core_pipeline::core_3d::{Camera3dDepthTextureUsage, ScreenSpaceTransmissionQuality};
use bevy::prelude::*;
use bevy::prelude::{App, IntoSystemConfigs, Plugin};
use blenvy::GltfBlueprintsSet;

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum SavingSet {
    Save,
}

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum LoadingSet {
    Load,
}


#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct StaticEntitiesRoot;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct DynamicEntitiesRoot;

impl Plugin for SaveLoadPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<Dynamic>()
            .register_type::<StaticEntitiesRoot>()
            // TODO: remove these in bevy 0.13, as these are now registered by default
            .register_type::<Camera3dDepthTextureUsage>()
            .register_type::<ScreenSpaceTransmissionQuality>()
            .register_type::<StaticEntitiesStorage>()
            .add_event::<SavingRequest>()
            .add_event::<LoadingRequest>()
            .add_event::<LoadingFinished>()
            .add_event::<SavingFinished>()
            .configure_sets(
                Update,
                (LoadingSet::Load).chain().before(GltfBlueprintsSet::Spawn), //.before(GltfComponentsSet::Injection)
            )
            .add_systems(
                PreUpdate,
                (prepare_save_game, apply_deferred, save_game, cleanup_save)
                    .chain()
                    .run_if(should_save),
            )
            .add_systems(Update, mark_load_requested)
            .add_systems(
                Update,
                (unload_world, apply_deferred, load_game)
                    .chain()
                    .run_if(resource_exists::<LoadRequested>)
                    .run_if(not(resource_exists::<LoadFirstStageDone>))
                    .in_set(LoadingSet::Load),
            )
            .add_systems(
                Update,
                (load_static, apply_deferred, cleanup_loaded_scene)
                    .chain()
                    .run_if(resource_exists::<LoadFirstStageDone>)
                    // .run_if(in_state(AppState::LoadingGame))
                    .in_set(LoadingSet::Load),
            );
    }
}
