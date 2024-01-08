pub mod saveable;
use std::path::PathBuf;

use bevy::core_pipeline::core_3d::{Camera3dDepthTextureUsage, ScreenSpaceTransmissionQuality};
pub use saveable::*;

pub mod saving;
pub use saving::*;

pub mod loading;
pub use loading::*;

use bevy::prelude::*;
use bevy::prelude::{App, IntoSystemConfigs, Plugin};

//use bevy::asset::free_unused_assets_system;
//use bevy_gltf_components::GltfComponentsSet;

use bevy_gltf_blueprints::GltfBlueprintsSet;

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum LoadingSet {
    Load,
    PostLoad,
}

// Plugin configuration

#[derive(Clone, Resource)]
pub struct SaveLoadConfig {
    pub(crate) save_path: PathBuf,
    pub(crate) entity_filter: SceneFilter,
}

// define the plugin

pub struct SaveLoadPlugin {
    pub entity_filter: SceneFilter,
    pub save_path: PathBuf,
}

impl Default for SaveLoadPlugin {
    fn default() -> Self {
        Self {
            entity_filter: SceneFilter::default(),
            save_path: PathBuf::from("models/library"),
        }
    }
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct StaticWorldMarker(pub String);

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct DynamicEntitiesRoot;

impl Plugin for SaveLoadPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<Dynamic>()
            .register_type::<StaticWorldMarker>()
            // TODO: remove these in bevy 0.13, as these are now registered by default
            .register_type::<Camera3dDepthTextureUsage>()
            .register_type::<ScreenSpaceTransmissionQuality>()
            .add_event::<SaveRequest>()
            .add_event::<LoadRequest>()
            .add_event::<LoadingFinished>()
            .insert_resource(SaveLoadConfig {
                save_path: self.save_path.clone(),
                entity_filter: self.entity_filter.clone(),
            })
            .init_resource::<LoadRequested>()
            .configure_sets(
                Update,
                (LoadingSet::Load, LoadingSet::PostLoad)
                    .chain()
                    .before(GltfBlueprintsSet::Spawn), //.before(GltfComponentsSet::Injection)
            )
            .add_systems(
                PreUpdate,
                (prepare_save_game, apply_deferred, save_game)
                    .chain()
                    .run_if(should_save),
            )
            .add_systems(
                Update,
                (unload_world, apply_deferred, load_game)
                    .chain()
                    .run_if(should_load)
                    .in_set(LoadingSet::Load),
            )
            .add_systems(
                Update,
                (load_static, apply_deferred, cleanup_loaded_scene)
                    .chain()
                    //.run_if(should_load)
                    // .run_if(in_state(AppState::LoadingGame))
                    .in_set(LoadingSet::Load),
            );
    }
}
