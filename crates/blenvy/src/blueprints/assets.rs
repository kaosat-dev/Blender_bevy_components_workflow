use bevy::{asset::LoadedUntypedAsset, prelude::*};
use serde::Deserialize;

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug, Deserialize)]
#[reflect(Component)]
pub struct BlueprintAsset {
    pub name: String,
    pub path: String,
}

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
/// these are only the DIRECT dependencies of a blueprint, does not contain the indirect assets (ie assets of sub blueprints, etc)
#[derive(Component, Reflect, Default, Debug, Deserialize)]
#[reflect(Component)]
pub struct BlueprintAssets {
    /// only this field should get filled in from the Blender side
    pub assets: Vec<BlueprintAsset>,
    /// set to default when deserializing
    #[serde(default)]
    #[reflect(default)]
    pub loaded: bool,
    /// set to default when deserializing
    #[serde(default)]
    #[reflect(default)]
    pub progress: f32,
    #[reflect(ignore)]
    #[serde(skip)]
    pub asset_infos: Vec<AssetLoadTracker>,
}
//(pub Vec<BlueprintAsset>);

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug, Deserialize)]
pub struct BlueprintAllAssets {
    /// only this field should get filled in from the Blender side
    pub assets: Vec<BlueprintAsset>,
}

////////////////////////
///
/// flag component, usually added when a blueprint is loaded
#[derive(Component)]
pub(crate) struct BlueprintAssetsLoaded;
/// flag component
#[derive(Component)]
pub(crate) struct BlueprintAssetsNotLoaded;

/// helper component, for tracking loaded assets's loading state, id , handle etc
#[derive(Debug, Reflect)]
pub struct AssetLoadTracker {
    #[allow(dead_code)]
    pub name: String,
    pub path: String,
    pub id: AssetId<LoadedUntypedAsset>,
    pub loaded: bool,
    #[allow(dead_code)]
    pub handle: Handle<LoadedUntypedAsset>,
}

/// helper component, for tracking loaded assets
#[derive(Component, Debug)]
pub(crate) struct BlueprintAssetsLoadState {
    pub all_loaded: bool,
    pub asset_infos: Vec<AssetLoadTracker>,
    pub progress: f32,
}
impl Default for BlueprintAssetsLoadState {
    fn default() -> Self {
        Self {
            all_loaded: Default::default(),
            asset_infos: Default::default(),
            progress: Default::default(),
        }
    }
}

// for preloading asset files
#[derive(serde::Deserialize, bevy::asset::Asset, bevy::reflect::TypePath, Debug)]
pub(crate) struct File{
    pub(crate) path: String,
}

#[derive(serde::Deserialize, bevy::asset::Asset, bevy::reflect::TypePath, Debug)]
pub(crate) struct BlueprintPreloadAssets{
    pub(crate) assets: Vec<(String, File)>
}


#[derive(Component)]
pub(crate) struct BlueprintMetaHandle(pub Handle<BlueprintPreloadAssets>);

/// flag component, usually added when a blueprint is loaded
#[derive(Component)]
pub(crate) struct BlueprintMetaLoaded;


#[derive(Component)]
pub(crate) struct BlueprintMetaLoading;