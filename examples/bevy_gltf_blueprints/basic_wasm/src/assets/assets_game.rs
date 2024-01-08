use bevy::gltf::Gltf;
use bevy::prelude::*;
use bevy::utils::HashMap;
use bevy_asset_loader::prelude::*;

#[derive(AssetCollection, Resource)]
pub struct GameAssets {
    #[asset(key = "world")]
    pub world: Handle<Gltf>,

    #[asset(
        paths(
            "models/library/Container.glb",
            "models/library/Health_Pickup.glb",
            "models/library/MagicTeapot.glb",
            "models/library/Pillar.glb",
            "models/library/Player.glb",
            "models/library/Unused_in_level_test.glb"
        ),
        collection(typed)
    )]
    pub models: Vec<Handle<Gltf>>,
    /*
    #[asset(key = "models", collection(typed, mapped))]
    pub models: HashMap<String, Handle<Gltf>>,

    #[asset(key = "models", collection(typed))]
    pub models: Vec<Handle<Gltf>>,*/
}
