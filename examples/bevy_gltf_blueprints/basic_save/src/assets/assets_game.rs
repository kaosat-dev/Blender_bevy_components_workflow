use bevy::gltf::Gltf;
use bevy::prelude::*;
use bevy::utils::HashMap;
use bevy_asset_loader::prelude::*;

#[derive(AssetCollection, Resource)]
pub struct GameAssets {
    #[asset(key = "world")]
    pub world: Handle<Gltf>,

    #[asset(key = "world_dynamic")]
    pub world_dynamic: Handle<Gltf>,

    #[asset(key = "models", collection(typed, mapped))]
    pub models: HashMap<String, Handle<Gltf>>,
}
