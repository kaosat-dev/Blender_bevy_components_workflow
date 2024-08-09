use bevy::{prelude::*, render::primitives::Aabb, utils::HashMap};
use std::path::PathBuf;

pub mod components;
pub use components::*;

pub mod registry;
pub use registry::*;

pub mod blueprints;
pub use blueprints::*;

pub mod save_load;
pub use save_load::*;

#[derive(Clone, Resource)]
pub struct BlenvyConfig {
    // registry
    pub(crate) export_registry: bool,
    pub(crate) registry_save_path: PathBuf,
    pub(crate) registry_component_filter: SceneFilter,
    #[allow(dead_code)]
    pub(crate) registry_resource_filter: SceneFilter,

    // blueprints
    pub(crate) aabb_cache: HashMap<String, Aabb>, // cache for aabbs
    pub(crate) materials_cache: HashMap<String, Handle<StandardMaterial>>, // cache for materials

    // save & load
    pub(crate) save_component_filter: SceneFilter,
    pub(crate) save_resource_filter: SceneFilter,
    //pub(crate) save_path: PathBuf,
    // save_path: PathBuf::from("saves"),
}

#[derive(Debug, Clone)]
/// Plugin for gltf blueprints
pub struct BlenvyPlugin {
    pub export_registry: bool,
    pub registry_save_path: PathBuf,

    pub registry_component_filter: SceneFilter,
    pub registry_resource_filter: SceneFilter,

    // for save & load
    pub save_component_filter: SceneFilter,
    pub save_resource_filter: SceneFilter,
}

impl Default for BlenvyPlugin {
    fn default() -> Self {
        Self {
            export_registry: true,
            registry_save_path: PathBuf::from("registry.json"), // relative to assets folder
            registry_component_filter: SceneFilter::default(),
            registry_resource_filter: SceneFilter::default(),

            save_component_filter: SceneFilter::default(),
            save_resource_filter: SceneFilter::default(),
        }
    }
}

impl Plugin for BlenvyPlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            ComponentsFromGltfPlugin::default(),
            #[cfg(not(target_arch = "wasm32"))]
            ExportRegistryPlugin::default(),
            BlueprintsPlugin::default(),
            SaveLoadPlugin::default()
        ))
        .insert_resource(BlenvyConfig {
            export_registry: self.export_registry,
            registry_save_path: self.registry_save_path.clone(),
            registry_component_filter: self.registry_component_filter.clone(),
            registry_resource_filter: self.registry_resource_filter.clone(),

            aabb_cache: HashMap::new(),

            materials_cache: HashMap::new(),

            save_component_filter: self.save_component_filter.clone(),
            save_resource_filter: self.save_resource_filter.clone(),
        });
    }
}
