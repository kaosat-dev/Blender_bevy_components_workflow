pub mod spawn_from_blueprints;
pub use spawn_from_blueprints::*;

pub mod spawn_post_process;
pub(crate) use spawn_post_process::*;

pub mod animation;
pub use animation::*;

pub mod aabb;
pub use aabb::*;

pub mod materials;
pub use materials::*;

pub mod copy_components;
pub use copy_components::*;

use core::fmt;
use std::path::PathBuf;

use bevy::{
    prelude::*,
    render::{primitives::Aabb, view::VisibilitySystems},
    utils::HashMap,
};
use bevy_gltf_components::{ComponentsFromGltfPlugin, GltfComponentsSet};

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
/// set for the two stages of blueprint based spawning :
pub enum GltfBlueprintsSet {
    Spawn,
    AfterSpawn,
}

#[derive(Bundle)]
pub struct BluePrintBundle {
    pub blueprint: BlueprintName,
    pub spawn_here: SpawnHere,
}
impl Default for BluePrintBundle {
    fn default() -> Self {
        BluePrintBundle {
            blueprint: BlueprintName("default".into()),
            spawn_here: SpawnHere,
        }
    }
}

#[derive(Clone, Resource)]
pub struct BluePrintsConfig {
    pub(crate) format: GltfFormat,
    pub(crate) library_folder: PathBuf,
    pub(crate) aabbs: bool,
    pub(crate) aabb_cache: HashMap<String, Aabb>, // cache for aabbs

    pub(crate) material_library: bool,
    pub(crate) material_library_folder: PathBuf,
    pub(crate) material_library_cache: HashMap<String, Handle<StandardMaterial>>,
}

#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash, Default)]
pub enum GltfFormat {
    #[default]
    GLB,
    GLTF,
}

impl fmt::Display for GltfFormat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            GltfFormat::GLB => {
                write!(f, "glb",)
            }
            GltfFormat::GLTF => {
                write!(f, "gltf")
            }
        }
    }
}

#[derive(Debug, Clone)]
/// Plugin for gltf blueprints
pub struct BlueprintsPlugin {
    pub legacy_mode: bool, // flag that gets passed on to bevy_gltf_components

    pub format: GltfFormat,
    /// The base folder where library/blueprints assets are loaded from, relative to the executable.
    pub library_folder: PathBuf,
    /// Automatically generate aabbs for the blueprints root objects
    pub aabbs: bool,
    ///
    pub material_library: bool,
    pub material_library_folder: PathBuf,
}

impl Default for BlueprintsPlugin {
    fn default() -> Self {
        Self {
            legacy_mode: true,
            format: GltfFormat::GLB,
            library_folder: PathBuf::from("models/library"),
            aabbs: false,
            material_library: false,
            material_library_folder: PathBuf::from("materials"),
        }
    }
}

fn aabbs_enabled(blueprints_config: Res<BluePrintsConfig>) -> bool {
    blueprints_config.aabbs
}

fn materials_library_enabled(blueprints_config: Res<BluePrintsConfig>) -> bool {
    blueprints_config.material_library
}

impl Plugin for BlueprintsPlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(ComponentsFromGltfPlugin {
            legacy_mode: self.legacy_mode,
        })
        .register_type::<BlueprintName>()
        .register_type::<MaterialInfo>()
        .register_type::<SpawnHere>()
        .register_type::<BlueprintAnimations>()
        .register_type::<InstanceAnimations>()
        .register_type::<AnimationInfo>()
        .register_type::<AnimationInfos>()
        .register_type::<Vec<AnimationInfo>>()
        .register_type::<AnimationMarkers>()
        .register_type::<HashMap<u32, Vec<String>>>()
        .register_type::<HashMap<String, HashMap<u32, Vec<String>>>>()
        .add_event::<AnimationMarkerReached>()
        .register_type::<BlueprintsList>()
        .register_type::<HashMap<String, Vec<String>>>()
        .insert_resource(BluePrintsConfig {
            format: self.format,
            library_folder: self.library_folder.clone(),

            aabbs: self.aabbs,
            aabb_cache: HashMap::new(),

            material_library: self.material_library,
            material_library_folder: self.material_library_folder.clone(),
            material_library_cache: HashMap::new(),
        })
        .configure_sets(
            Update,
            (GltfBlueprintsSet::Spawn, GltfBlueprintsSet::AfterSpawn)
                .chain()
                .after(GltfComponentsSet::Injection),
        )
        .add_systems(
            Update,
            (
                (
                    prepare_blueprints,
                    check_for_loaded,
                    spawn_from_blueprints,
                    apply_deferred,
                )
                    .chain(),
                (compute_scene_aabbs, apply_deferred)
                    .chain()
                    .run_if(aabbs_enabled),
                apply_deferred,
                (
                    materials_inject,
                    check_for_material_loaded,
                    materials_inject2,
                )
                    .chain()
                    .run_if(materials_library_enabled),
            )
                .chain()
                .in_set(GltfBlueprintsSet::Spawn),
        )
        .add_systems(
            PostUpdate,
            (spawned_blueprint_post_process, apply_deferred)
                .chain()
                .in_set(GltfBlueprintsSet::AfterSpawn)
                .before(VisibilitySystems::CheckVisibility),
        );
    }
}
